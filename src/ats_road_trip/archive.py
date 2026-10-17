"""Read ZIP and SCS HashFS archives without changing the source archives.

HashFS support uses the separately installed sk-zk Extractor command. Its
binary belongs under ignored ``local_outputs/tools`` and is never vendored.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Iterable
import os
import shutil
import stat
import subprocess
import zipfile


DEFAULT_MAX_BYTES = 16 * 1024 * 1024


class ArchiveError(RuntimeError):
    """An archive cannot be read or a selected member cannot be extracted."""


@dataclass(frozen=True)
class ArchiveEntry:
    path: str  # root-relative POSIX path, without a leading slash
    size: int | None
    is_dir: bool


def detect_format(path: str | os.PathLike[str]) -> str:
    """Return ``zip``, ``hashfs_v1``, or ``hashfs_v2`` by header bytes."""
    with open(path, "rb") as stream:
        header = stream.read(8)
    if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06"):
        return "zip"
    if header[:4] == b"SCS#" and len(header) >= 6:
        version = int.from_bytes(header[4:6], "little")
        if version in (1, 2):
            return f"hashfs_v{version}"
    raise ArchiveError(f"Unsupported archive signature: {Path(path)}")


def _safe_member(value: str) -> str:
    if "\\" in value:
        raise ArchiveError(f"Backslash archive member is unsupported: {value!r}")
    if value.startswith("/"):
        raise ArchiveError(f"Absolute archive member: {value!r}")
    if not value or "\x00" in value:
        raise ArchiveError(f"Unsafe archive member: {value!r}")
    parts = PurePosixPath(value).parts
    if any(part in ("", ".", "..") for part in value.split("/")) or ":" in value:
        raise ArchiveError(f"Unsafe archive member: {value!r}")
    return "/".join(parts)


def _safe_destination(root: Path, member: str) -> Path:
    current = root
    for part in member.split("/"):
        current = current / part
        if current.is_symlink():
            raise ArchiveError(f"Symlink in output path: {current}")
    return current


class Archive:
    """Read one archive, listing metadata and selecting individual files.

    ``extractor`` is required for HashFS unless the default ignored local tool
    path exists. ``read`` and ``extract`` enforce a per-member size limit.
    HashFS metadata does not expose sizes through this adapter, so its limit is
    checked after the external extractor writes into a temporary staging area.
    """

    def __init__(self, path: str | os.PathLike[str], extractor: str | os.PathLike[str] | None = None):
        self.path = Path(path)
        self.format = detect_format(self.path)
        self._zip: zipfile.ZipFile | None = None
        self._entries: list[ArchiveEntry] | None = None
        self._entry_index: dict[str, list[ArchiveEntry]] | None = None
        if extractor is None:
            repo = Path(__file__).resolve().parents[2]
            extractor = repo / "local_outputs/tools/extractor-2026-07-29/extractor"
        self.extractor = Path(extractor)

    def __enter__(self) -> "Archive":
        if self.format == "zip":
            self._zipfile()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Release an open ZIP handle (also safe to call repeatedly)."""
        if self._zip is not None:
            self._zip.close()
            self._zip = None

    def _zipfile(self) -> zipfile.ZipFile:
        if self._zip is None:
            self._zip = zipfile.ZipFile(self.path)
        return self._zip

    def _require_extractor(self) -> None:
        if not self.extractor.is_file() or not os.access(self.extractor, os.X_OK):
            raise ArchiveError(
                "HashFS requires a Linux sk-zk Extractor binary; install release "
                "2026-07-29 under local_outputs/tools/extractor-2026-07-29/extractor "
                "or pass extractor=..."
            )

    def entries(self) -> list[ArchiveEntry]:
        if self._entries is not None:
            return list(self._entries)
        entries: list[ArchiveEntry] = []
        if self.format == "zip":
            for info in self._zipfile().infolist():
                name = _safe_member(info.filename.rstrip("/"))
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ArchiveError(f"Symlink member is unsupported: {name}")
                entries.append(ArchiveEntry(name, None if info.is_dir() else info.file_size, info.is_dir()))
        else:
            self._require_extractor()
            result = subprocess.run(
                [str(self.extractor), str(self.path), "--list"],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                raise ArchiveError(f"Extractor list failed: {result.stderr.strip() or result.stdout.strip()}")
            # The command prints paths (files and directories), rooted at '/'.
            raw = [line.strip() for line in result.stdout.splitlines() if line.startswith("/") and line.strip() != "/"]
            paths = [_safe_member(line[1:]) for line in raw]
            directories: set[str] = set()
            for name in paths:
                parent = PurePosixPath(name).parent
                while str(parent) != ".":
                    directories.add(str(parent))
                    parent = parent.parent
            for name in paths:
                entries.append(ArchiveEntry(name, None, name in directories))
        self._entries = entries
        index: dict[str, list[ArchiveEntry]] = {}
        for entry in entries:
            index.setdefault(entry.path, []).append(entry)
        self._entry_index = index
        return list(entries)

    def _file_entry(self, name: str) -> ArchiveEntry:
        name = _safe_member(name)
        if self._entries is None:
            self.entries()
        assert self._entry_index is not None
        matches = [entry for entry in self._entry_index.get(name, []) if not entry.is_dir]
        if len(matches) != 1:
            raise ArchiveError(f"Expected one file member {name!r}; found {len(matches)}")
        return matches[0]

    def read(self, name: str, max_bytes: int = DEFAULT_MAX_BYTES) -> bytes:
        if max_bytes < 0:
            raise ValueError("max_bytes must be nonnegative")
        entry = self._file_entry(name)
        if entry.size is not None and entry.size > max_bytes:
            raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
        if self.format == "zip":
            with self._zipfile().open(entry.path) as stream:
                data = stream.read(max_bytes + 1)
        else:
            with TemporaryDirectory(dir=self._scratch_root()) as temporary:
                self._extract_hashfs([entry.path], Path(temporary))
                extracted = _safe_destination(Path(temporary), entry.path)
                if not extracted.is_file() or extracted.is_symlink():
                    raise ArchiveError(f"Extractor did not produce file: {entry.path}")
                if extracted.stat().st_size > max_bytes:
                    raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
                data = extracted.read_bytes()
        if len(data) > max_bytes:
            raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
        return data

    def extract(
        self,
        names: Iterable[str],
        dest: str | os.PathLike[str],
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> list[Path]:
        if max_bytes < 0:
            raise ValueError("max_bytes must be nonnegative")
        selected = [self._file_entry(name) for name in names]
        root = Path(dest)
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink():
            raise ArchiveError(f"Symlink output root: {root}")
        for entry in selected:
            target = _safe_destination(root, entry.path)
            if target.exists():
                raise FileExistsError(f"Extraction target already exists: {target}")
        result: list[Path] = []
        if self.format == "zip":
            for entry in selected:
                if entry.size is not None and entry.size > max_bytes:
                    raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
                target = _safe_destination(root, entry.path)
                target.parent.mkdir(parents=True, exist_ok=True)
                with self._zipfile().open(entry.path) as source, target.open("xb") as sink:
                    remaining = max_bytes + 1
                    while remaining:
                        chunk = source.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        sink.write(chunk)
                        remaining -= len(chunk)
                    if remaining == 0:
                        target.unlink()
                        raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
                result.append(target)
        else:
            with TemporaryDirectory(dir=self._scratch_root()) as temporary:
                stage = Path(temporary)
                self._extract_hashfs([entry.path for entry in selected], stage)
                for entry in selected:
                    source = _safe_destination(stage, entry.path)
                    if not source.is_file() or source.is_symlink():
                        raise ArchiveError(f"Extractor did not produce file: {entry.path}")
                    if source.stat().st_size > max_bytes:
                        raise ArchiveError(f"Member exceeds {max_bytes} byte limit: {entry.path}")
                    target = _safe_destination(root, entry.path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with source.open('rb') as reader, target.open('xb') as writer:
                        shutil.copyfileobj(reader, writer)
                    result.append(target)
        return result

    @staticmethod
    def _scratch_root() -> Path:
        root = Path(__file__).resolve().parents[2] / "local_outputs/extracted/.staging"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _extract_hashfs(self, names: list[str], stage: Path) -> None:
        self._require_extractor()
        if not names:
            return
        if any("," in name for name in names):
            raise ArchiveError("HashFS member names containing commas cannot be selected safely")

        batches: list[list[str]] = [[]]
        length = 0
        for name in names:
            if batches[-1] and length + len(name) + 2 > 48000:
                batches.append([])
                length = 0
            batches[-1].append(name)
            length += len(name) + 2
        for batch in batches:
            result = subprocess.run(
                [str(self.extractor), str(self.path), "--partial=" + ",".join("/" + name for name in batch),
                 "--dest=" + str(stage), "--quiet"],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                raise ArchiveError(f"Extractor failed: {result.stderr.strip() or result.stdout.strip()}")
