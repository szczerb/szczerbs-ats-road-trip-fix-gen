from pathlib import Path
from tempfile import TemporaryDirectory
import stat
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import zipfile

from ats_road_trip.archive import Archive, ArchiveError, detect_format


class ArchiveTests(unittest.TestCase):
    def test_zip_stored_and_deflated_selective_reads(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "mod.scs"
            with zipfile.ZipFile(path, "w") as output:
                output.writestr("def/a.sii", b"alpha", compress_type=zipfile.ZIP_STORED)
                output.writestr("def/b.sii", b"beta" * 100, compress_type=zipfile.ZIP_DEFLATED)
            self.assertEqual(detect_format(path), "zip")
            with Archive(path) as archive:
                entries = archive.entries()
                self.assertEqual([entry.path for entry in entries], ["def/a.sii", "def/b.sii"])
                self.assertEqual(archive.read("def/a.sii"), b"alpha")
                self.assertEqual(archive.read("def/b.sii"), b"beta" * 100)
                extracted = archive.extract(["def/a.sii"], root / "out")
                self.assertEqual(extracted[0].read_bytes(), b"alpha")
                self.assertFalse((root / "out/def/b.sii").exists())

    def test_size_limit_and_missing_entry(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "mod.scs"
            with zipfile.ZipFile(path, "w") as output:
                output.writestr("large", b"12345")
            with Archive(path) as archive:
                with self.assertRaises(ArchiveError):
                    archive.read("large", max_bytes=4)
                with self.assertRaises(ArchiveError):
                    archive.extract(["large"], Path(temporary) / "out", max_bytes=4)
                with self.assertRaises(ArchiveError):
                    archive.read("missing")

    def test_rejects_traversal_and_symlink_entries(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "mod.scs"
            with zipfile.ZipFile(path, "w") as output:
                output.writestr("../escape", b"bad")
            with Archive(path) as archive:
                with self.assertRaises(ArchiveError):
                    archive.entries()
            with zipfile.ZipFile(path, "w") as output:
                output.writestr("/absolute", b"bad")
            with Archive(path) as archive:
                with self.assertRaises(ArchiveError):
                    archive.entries()
            with zipfile.ZipFile(path, "w") as output:
                link = zipfile.ZipInfo("def/link")
                link.create_system = 3
                link.external_attr = (stat.S_IFLNK | 0o777) << 16
                output.writestr(link, "elsewhere")
            with Archive(path) as archive:
                with self.assertRaises(ArchiveError):
                    archive.entries()

    def test_rejects_output_symlink(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "mod.scs"
            with zipfile.ZipFile(path, "w") as output:
                output.writestr("def/file", b"good")
            out = root / "out"
            out.mkdir()
            (out / "def").symlink_to(root, target_is_directory=True)
            with Archive(path) as archive:
                with self.assertRaises(ArchiveError):
                    archive.extract(["def/file"], out)
            self.assertFalse((root / "file").exists())

    def test_hashfs_signature_and_missing_tool(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "mod.scs"
            path.write_bytes(b"SCS#\x02\x00\x00\x00")
            self.assertEqual(detect_format(path), "hashfs_v2")
            with Archive(path, extractor=Path(temporary) / "missing") as archive:
                with self.assertRaisesRegex(ArchiveError, "requires a Linux"):
                    archive.entries()

    def test_hashfs_v1_listing_uses_deep_scan_and_parses_paths(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "promods.scs"
            source.write_bytes(b"SCS#\x01\x00\x00\x00")
            extractor = root / "extractor"
            extractor.write_text("placeholder")
            extractor.chmod(0o755)
            output = SimpleNamespace(
                returncode=0,
                stdout=("Opened promods.scs: HashFS v1 archive; 3 entries\n"
                        "Top level directory is missing; use --deep to scan contents\n"
                        "/manifest.sii\n/prefab/gas/station.ppd\n"),
                stderr="",
            )
            with Archive(source, extractor=extractor) as archive, \
                 patch("ats_road_trip.archive.subprocess.run", return_value=output) as run:
                entries = archive.entries()

            self.assertEqual([entry.path for entry in entries], ["manifest.sii", "prefab/gas/station.ppd"])
            self.assertEqual([entry.is_dir for entry in entries], [False, False])
            command = run.call_args.args[0]
            self.assertIn("--deep", command)
            self.assertIn("--list", command)

    def test_hashfs_v2_listing_does_not_use_deep_scan(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "reforma.scs"
            source.write_bytes(b"SCS#\x02\x00\x00\x00")
            extractor = root / "extractor"
            extractor.write_text("placeholder")
            extractor.chmod(0o755)
            output = SimpleNamespace(returncode=0, stdout="/def/map_data.sii\n", stderr="")
            with Archive(source, extractor=extractor) as archive, \
                 patch("ats_road_trip.archive.subprocess.run", return_value=output) as run:
                entries = archive.entries()

            self.assertEqual([entry.path for entry in entries], ["def/map_data.sii"])
            self.assertNotIn("--deep", run.call_args.args[0])

    def test_hashfs_v1_empty_deep_listing_is_an_error(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "promods.scs"
            source.write_bytes(b"SCS#\x01\x00\x00\x00")
            extractor = root / "extractor"
            extractor.write_text("placeholder")
            extractor.chmod(0o755)
            output = SimpleNamespace(returncode=0, stdout="no paths found\n", stderr="")
            with Archive(source, extractor=extractor) as archive, \
                 patch("ats_road_trip.archive.subprocess.run", return_value=output):
                with self.assertRaisesRegex(ArchiveError, "deep listing returned no HashFS v1 members"):
                    archive.entries()

    def test_hashfs_v1_selective_extraction_uses_deep_scan(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "promods.scs"
            source.write_bytes(b"SCS#\x01\x00\x00\x00")
            with Archive(source) as archive, patch.object(archive, "_require_extractor"), \
                 patch("ats_road_trip.archive.subprocess.run",
                       return_value=SimpleNamespace(returncode=0)) as run:
                archive._extract_hashfs(["prefab/gas/station.ppd"], root / "stage")

            command = run.call_args.args[0]
            self.assertIn("--deep", command)
            self.assertIn("--partial=/prefab/gas/station.ppd", command)

    def test_archive_staging_uses_configured_work_root(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "run-work"
            try:
                Archive.configure_work_root(root)
                self.assertEqual(Archive._scratch_root(), root / "archive-staging")
                self.assertTrue((root / "archive-staging").is_dir())
            finally:
                Archive.configure_work_root(None)

    def test_extraction_preserves_existing_files_and_source_archive(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'mod.scs'
            with zipfile.ZipFile(path, 'w') as output:
                output.writestr('mod.scs', b'overwrite attempt')
                output.writestr('existing', b'new')
            original = path.read_bytes()
            (root / 'existing').write_bytes(b'keep')
            with Archive(path) as archive:
                for member in ('mod.scs', 'existing'):
                    with self.assertRaises(FileExistsError):
                        archive.extract([member], root)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual((root / 'existing').read_bytes(), b'keep')

    def test_hashfs_filters_are_batched_below_argument_limit(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'input.scs'
            source.write_bytes(b'SCS#\x02\x00\x00\x00')
            names = [f'def/company/example/editor/city_{i:06d}.sii' for i in range(3000)]
            with Archive(source) as archive, patch.object(archive, '_require_extractor'), \
                 patch('ats_road_trip.archive.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run:
                archive._extract_hashfs(names, root / 'stage')
            self.assertGreater(run.call_count, 1)
            filters = [call.args[0][2] for call in run.call_args_list]
            self.assertTrue(all(len(arg) < 65536 for arg in filters))
            selected = [item.lstrip('/') for arg in filters for item in arg.removeprefix('--partial=').split(',')]
            self.assertEqual(selected, names)


if __name__ == "__main__":
    unittest.main()
