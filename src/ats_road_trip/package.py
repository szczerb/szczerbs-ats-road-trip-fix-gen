"""Read-only package mounts and explicit low-to-high virtual resource ordering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import re

from .archive import Archive


class PackageError(ValueError):
    pass


def virtual_path(name: str) -> str:
    if '\\' in name or '\x00' in name:
        raise PackageError(f'Invalid virtual path: {name!r}')
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or ':' in name:
        raise PackageError(f'Unsafe virtual path: {name!r}')
    return str(path)


@dataclass(frozen=True)
class Resource:
    package: str
    physical_path: str
    virtual_path: str


class Package:
    """Directory, ZIP, or HashFS package; DLC names must be explicitly supplied.

    Conditional directory parts are supported. Nested part ZIPs and ambiguous
    within-package collisions fail explicitly instead of guessing precedence.
    """

    def __init__(self, path: str | Path, *, extractor: str | Path | None = None,
                 dlcs: tuple[str, ...] = ()):
        self.path = Path(path).resolve()
        self._cache: dict[str, bytes] = {}
        self.archive = None if self.path.is_dir() else Archive(self.path, extractor=extractor)
        if self.path.is_dir():
            names = [str(p.relative_to(self.path).as_posix()) for p in self.path.rglob('*') if p.is_file()]
        else:
            names = [entry.path for entry in self.archive.entries() if not entry.is_dir]
        names = sorted(virtual_path(name) for name in names)
        tops = {name.split('/')[0] for name in names}
        active = {'base', *dlcs}
        for part in tops:
            if part.endswith('.zip') and part[:-4] in active:
                raise PackageError(f'{self.path}: nested package part {part} requires explicit extraction')
        parts_mode = 'base' in tops or any(t.startswith('dlc_') and '.' not in t for t in tops)
        self.files: dict[str, str] = {}
        for name in names:
            parts = name.split('/')
            if parts_mode:
                if len(parts) < 2 or parts[0] not in active:
                    continue
                mounted = '/'.join(parts[1:])
            else:
                mounted = name
            if mounted in self.files:
                raise PackageError(f'{self.path}: ambiguous mounted path {mounted}')
            self.files[mounted] = name

    def read(self, name: str, *, max_bytes: int = 8 * 1024 * 1024) -> bytes:
        if name in self._cache:
            data = self._cache[name]
            if len(data) > max_bytes:
                raise PackageError(f'{name}: exceeds {max_bytes} byte read limit')
            return data
        physical = self.files[virtual_path(name)]
        if self.archive:
            return self.archive.read(physical, max_bytes=max_bytes)
        file = self.path / physical
        if not file.resolve().is_relative_to(self.path) or file.is_symlink():
            raise PackageError(f'Refusing symlink escape: {file}')
        with file.open('rb') as stream:
            data = stream.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise PackageError(f'{name}: exceeds {max_bytes} byte read limit')
        return data

    def prefetch(self, names: list[str]) -> None:
        """Batch selected HashFS definitions rather than launch once per file."""
        if not self.archive or not self.archive.format.startswith('hashfs'):
            return
        pending = sorted(set(names) - self._cache.keys())
        if not pending:
            return
        with TemporaryDirectory(dir=self.archive._scratch_root()) as temporary:
            stage = Path(temporary)
            # Bound argument length as well as member size. All batches select
            # exact members, so unrelated models/textures are never requested.
            batches: list[list[str]] = [[]]
            length = 0
            for name in pending:
                physical = self.files[name]
                if batches[-1] and length + len(physical) + 2 > 48000:
                    batches.append([])
                    length = 0
                batches[-1].append(physical)
                length += len(physical) + 2
            for batch in batches:
                self.archive.extract(batch, stage, max_bytes=8 * 1024 * 1024)
            size = sum(len(data) for data in self._cache.values())
            for name in pending:
                data = (stage / self.files[name]).read_bytes()
                size += len(data)
                if size > 64 * 1024 * 1024:
                    raise PackageError('Selected definition cache exceeds 64 MiB; narrow the package scope')
                self._cache[name] = data

    def close(self) -> None:
        if self.archive:
            self.archive.close()

    def __enter__(self) -> Package:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class ResourceStack:
    """Caller-declared order, lowest priority first; no profile order inference."""

    def __init__(self, packages: list[Package]):
        self.packages = packages
        self.resources: dict[str, tuple[Package, Resource]] = {}
        self.overrides: list[dict[str, str]] = []
        for package in packages:
            for virtual, physical in package.files.items():
                resource = Resource(str(package.path), physical, virtual)
                previous = self.resources.get(virtual)
                if previous:
                    self.overrides.append({'path': virtual, 'previous': previous[1].package,
                                           'winner': resource.package})
                self.resources[virtual] = package, resource

    def read(self, path: str, *, max_bytes: int = 8 * 1024 * 1024) -> bytes:
        package, _ = self.resources[virtual_path(path)]
        return package.read(path, max_bytes=max_bytes)

    def text(self, path: str) -> str:
        return self.read(path).decode('utf-8-sig')

    def matching(self, pattern: str) -> list[str]:
        regex = re.compile(pattern)
        return sorted(path for path in self.resources if regex.fullmatch(path))

    def prefetch(self, pattern: str) -> None:
        grouped: dict[Package, list[str]] = {}
        for path in self.matching(pattern):
            package, _ = self.resources[path]
            grouped.setdefault(package, []).append(path)
        for package, paths in grouped.items():
            package.prefetch(paths)
