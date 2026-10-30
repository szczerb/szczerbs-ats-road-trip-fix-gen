from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch

from ats_road_trip.archive import ArchiveEntry, ArchiveError
from ats_road_trip.package import Package, PackageError, ResourceStack
from ats_road_trip.courier_audit import audit_courier


class FakeHashFsArchive:
    format = 'hashfs_v2'

    def __init__(self, members):
        self.members = dict(members)
        self.extract_calls = []

    def entries(self):
        return [ArchiveEntry(path, None, False) for path in self.members]

    def extract(self, names, dest, *, max_bytes):
        names = list(names)
        self.extract_calls.append((names, max_bytes))
        for name in names:
            data = self.members[name]
            size = data if isinstance(data, int) else len(data)
            if size > max_bytes:
                raise ArchiveError(f'{name}: exceeds {max_bytes} byte read limit')
            target = Path(dest) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise FileExistsError(target)
            if isinstance(data, int):
                with target.open('wb') as stream:
                    stream.truncate(data)
            else:
                target.write_bytes(data)

    def close(self):
        pass


class PackagesAndAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def put(self, package, path, text):
        file = self.root / package / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)
        return file

    def test_conditional_mount_and_explicit_override(self):
        self.put('a', 'base/def/a.sii', 'first')
        self.put('a', 'dlc_owned/def/owned.sii', 'owned')
        self.put('a', 'dlc_other/def/other.sii', 'absent')
        self.put('b', 'def/a.sii', 'last')
        with Package(self.root / 'a', dlcs=('dlc_owned',)) as a, Package(self.root / 'b') as b:
            stack = ResourceStack([a, b])
            self.assertEqual(stack.text('def/a.sii'), 'last')
            self.assertIn('def/owned.sii', stack.resources)
            self.assertNotIn('def/other.sii', stack.resources)
            self.assertEqual(len(stack.overrides), 1)

    def test_ambiguous_mount_fails(self):
        self.put('a', 'base/def/a.sii', 'base')
        self.put('a', 'dlc_owned/def/a.sii', 'dlc')
        with self.assertRaises(PackageError):
            Package(self.root / 'a', dlcs=('dlc_owned',))

    def test_symlink_escape_fails(self):
        outside = self.put('elsewhere', 'secret.sii', 'secret')
        target = self.root / 'a/def'
        target.mkdir(parents=True)
        (target / 'secret.sii').symlink_to(outside)
        with Package(self.root / 'a') as a:
            with self.assertRaises(PackageError):
                a.read('def/secret.sii')

    def test_disk_prefetch_uses_physical_paths_and_reuses_recorded_files(self):
        source = self.root / 'promods.scs'
        source.write_bytes(b'SCS#\x02\x00\x00\x00')
        original_hash = hashlib.sha256(source.read_bytes()).digest()
        fake = FakeHashFsArchive({
            'base/def/company/a.sii': b'alpha',
            'base/def/company/b.sii': b'beta',
        })
        cache = self.root / 'run-work/package-cache/mod-hash'
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                package.prefetch(['def/company/a.sii'], disk_cache=cache, max_bytes=64)
                self.assertEqual(package.read('def/company/a.sii', max_bytes=64), b'alpha')
                package.prefetch(['def/company/a.sii'], disk_cache=cache, max_bytes=64)
                # Memory-prefetch callers must reuse a recorded disk member,
                # avoiding another large-archive extractor invocation.
                package.prefetch(['def/company/a.sii'])
                self.assertEqual(package.read('def/company/a.sii'),b'alpha')
                self.assertEqual(len(fake.extract_calls), 1)
                self.assertEqual(fake.extract_calls[0][0], ['base/def/company/a.sii'])
                self.assertEqual(fake.extract_calls[0][1], 64)
        self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), original_hash)

    def test_disk_prefetch_batches_and_has_per_member_not_total_limit(self):
        source = self.root / 'many.scs'
        source.write_bytes(b'SCS#\x02\x00\x00\x00')
        members = {f'def/resource/file_{i:04d}_' + ('x' * 24) + '.sii': b'abcde'
                   for i in range(2100)}
        fake = FakeHashFsArchive(members)
        cache = self.root / 'cache'
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                package.prefetch(list(members), disk_cache=cache, max_bytes=5)
                self.assertGreater(len(fake.extract_calls), 1)
                self.assertTrue(all(limit == 5 for _, limit in fake.extract_calls))
                self.assertEqual(sum(len(names) for names, _ in fake.extract_calls), len(members))
                self.assertEqual(package.read(next(iter(members)), max_bytes=5), b'abcde')

        large_members = {
            'def/large-a.bin': 33 * 1024 * 1024,
            'def/large-b.bin': 33 * 1024 * 1024,
        }
        fake_large = FakeHashFsArchive(large_members)
        large_cache = self.root / 'large-cache'
        with patch('ats_road_trip.package.Archive', return_value=fake_large):
            with Package(source) as package:
                package.prefetch(list(large_members), disk_cache=large_cache,
                                 max_bytes=34 * 1024 * 1024)
        self.assertEqual(sum((large_cache / name).stat().st_size for name in large_members),
                         66 * 1024 * 1024)

    def test_disk_prefetch_enforces_per_member_extraction_limit(self):
        source = self.root / 'too-large.scs'
        source.write_bytes(b'SCS#\x02\x00\x00\x00')
        fake = FakeHashFsArchive({'base/def/a.sii': b'alpha'})
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                with self.assertRaisesRegex(ArchiveError, 'exceeds 4 byte read limit'):
                    package.prefetch(['def/a.sii'], disk_cache=self.root / 'small-cache', max_bytes=4)

    def test_disk_prefetch_rejects_foreign_files_and_symlink_members(self):
        source = self.root / 'mod.scs'
        source.write_bytes(b'SCS#\x02\x00\x00\x00')
        fake = FakeHashFsArchive({'base/def/a.sii': b'alpha'})
        cache = self.root / 'cache'
        foreign = cache / 'base/def/a.sii'
        foreign.parent.mkdir(parents=True)
        foreign.write_bytes(b'foreign')
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                with self.assertRaisesRegex(PackageError, 'unrecorded existing'):
                    package.prefetch(['def/a.sii'], disk_cache=cache)
        self.assertEqual(fake.extract_calls, [])

        outside = self.root / 'outside'
        outside.mkdir()
        link_cache = self.root / 'link-cache'
        link_cache.mkdir()
        (link_cache / 'base').symlink_to(outside, target_is_directory=True)
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                with self.assertRaisesRegex(PackageError, 'symlink disk cache member'):
                    package.prefetch(['def/a.sii'], disk_cache=link_cache)
        self.assertEqual(fake.extract_calls, [])

    def test_disk_read_enforces_limit_and_refuses_replaced_symlink(self):
        source = self.root / 'mod.scs'
        source.write_bytes(b'SCS#\x02\x00\x00\x00')
        fake = FakeHashFsArchive({'base/def/a.sii': b'alpha'})
        cache = self.root / 'cache'
        outside = self.root / 'outside.sii'
        outside.write_bytes(b'other')
        with patch('ats_road_trip.package.Archive', return_value=fake):
            with Package(source) as package:
                package.prefetch(['def/a.sii'], disk_cache=cache, max_bytes=5)
                with self.assertRaisesRegex(PackageError, 'exceeds 4 byte read limit'):
                    package.read('def/a.sii', max_bytes=4)
                cached = cache / 'base/def/a.sii'
                cached.unlink()
                cached.symlink_to(outside)
                with self.assertRaisesRegex(PackageError, 'symlink disk cache member'):
                    package.read('def/a.sii', max_bytes=10)

    def test_context_counts_are_not_availability_claims(self):
        self.put('baseline', 'def/data_context.sii', '''SiiNunit {
data_context : context.prefab.example {
target_data[]: prefab.example
tags[]: warehouse
}
# prefab.bad # excluded: spawn issue
}''')
        self.put('baseline', 'def/car_job_data.sii', '''SiiNunit {
car_job_data : car_job.example {
source_data_contexts[]: warehouse
target_data_contexts[]: factory
}
}''')
        for prefab in ('example', 'bad', 'unknown'):
            self.put('map', f'base/def/company/example/editor/{prefab}.sii', f'''SiiNunit {{
company_def : .{prefab} {{
city: sample
prefab: {prefab}
}}
}}''')
        with Package(self.root / 'baseline') as a, Package(self.root / 'map') as b:
            result = audit_courier(ResourceStack([a, b]), map_packages={str(b.path)})
        self.assertEqual(result['counts'], {'classified': 1, 'explicitly_excluded': 1, 'unclassified': 1})
        classified = next(r for r in result['company_definitions'] if r['status'] == 'classified')
        self.assertEqual(classified['source_job_definitions'], ['car_job.example'])
        self.assertEqual(classified['target_job_definitions'], [])
        self.assertIn('not in-game', result['limitations'][0])


if __name__ == '__main__':
    unittest.main()
