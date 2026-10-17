from pathlib import Path
import tempfile
import unittest

from ats_road_trip.package import Package, PackageError, ResourceStack
from ats_road_trip.courier_audit import audit_courier


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
