from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ats_road_trip.context_generator import plan_context_aliases, render_context_patch
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.sii import DefinitionError, parse_units


def put(root: Path, name: str, content: str | bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)


BASE_PREFAB = '''SiiNunit
{
prefab_model : prefab.d_food_mkt5
{
 model_desc: "/prefab/depots/supermarket3/supermarket3.pmd"
 prefab_desc: "/prefab/depots/supermarket3/supermarket3.ppd"
}
}
'''
ALIAS_PREFAB = '''SiiNunit
{
prefab_model : prefab.ahorrara
{
 model_desc: "/prefab/depots/supermarket3/supermarket3.pmd"
 prefab_desc: "/prefab/depots/supermarket3/supermarket3.ppd"
}
}
'''
CONTEXT = '''SiiNunit
{
data_context : context.prefab.retail
{
 target_data[]: prefab.d_food_mkt5
 tags[]: retail
}
}
'''
JOBS = '''SiiNunit
{
car_job_data : car_job.test
{
 source_data_contexts[]: retail
 target_data_contexts[]: retail
}
}
'''
COMPANY = '''SiiNunit
{
company_def : .test
{
 city: testville
 prefab: ahorrara
}
}
'''


class ContextGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        root = Path(self.temp.name)
        self.game = root / "game"
        self.map = root / "map"
        self.game.mkdir()
        self.map.mkdir()
        put(self.game, "def/world/prefab.sii", BASE_PREFAB)
        put(self.game, "def/data_context.sii", CONTEXT)
        put(self.game, "def/car_job_data.sii", JOBS)
        put(self.game, "prefab/depots/supermarket3/supermarket3.pmd", b"model")
        put(self.game, "prefab/depots/supermarket3/supermarket3.ppd", b"descriptor")
        put(self.map, "def/world/prefab.map.sii", ALIAS_PREFAB)
        put(self.map, "def/company/ahorrara/editor/testville.sii", COMPANY)

    def tearDown(self):
        self.temp.cleanup()

    def plan(self):
        base = ResourceStack([Package(self.game)])
        effective = ResourceStack([Package(self.game), Package(self.map)])
        return plan_context_aliases(base, effective, {str(self.map.resolve())})

    def test_exact_pair_produces_additive_context(self):
        plan = self.plan()
        self.assertEqual(len(plan["aliases"]), 1)
        alias = plan["aliases"][0]
        self.assertEqual(alias["alias"], "prefab.ahorrara")
        self.assertEqual(alias["canonical"], "prefab.d_food_mkt5")
        self.assertEqual(alias["tags"], ["retail"])
        self.assertEqual(alias["companies"][0]["city"], "testville")
        patch = render_context_patch(plan)
        self.assertEqual(list(patch), ["def/data_context.rtfix.sii"])
        units = parse_units(patch["def/data_context.rtfix.sii"].decode())
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].values("target_data"), ("prefab.ahorrara",))
        self.assertEqual(units[0].values("tags"), ("retail",))
        self.assertTrue(all(len(segment) <= 12 for segment in units[0].name.split(".")))

    def test_classified_alias_is_noop(self):
        put(self.map, "def/data_context.map.sii", '''SiiNunit
{
data_context : context.prefab.map
{
 target_data[]: prefab.ahorrara
 tags[]: retail
}
}
''')
        plan = self.plan()
        self.assertEqual(plan["aliases"], [])
        self.assertEqual(plan["skipped"][0]["reason"], "already_classified")
        self.assertEqual(render_context_patch(plan), {})

    def test_different_model_or_descriptor_is_skipped(self):
        for field in ("model_desc", "prefab_desc"):
            with self.subTest(field=field):
                put(self.map, "def/world/prefab.map.sii",
                    ALIAS_PREFAB.replace(f'{field}: "/prefab/depots/supermarket3/supermarket3.',
                                         f'{field}: "/prefab/other.'))
                self.assertEqual(self.plan()["skipped"][0]["reason"],
                                 "no_exact_classified_canonical_pair")

    def test_map_descriptor_override_is_skipped(self):
        put(self.map, "prefab/depots/supermarket3/supermarket3.ppd", b"map override")
        self.assertEqual(self.plan()["skipped"][0]["reason"],
                         "canonical_asset_overridden_by_map")

    def test_map_model_override_is_skipped(self):
        put(self.map, "prefab/depots/supermarket3/supermarket3.pmd", b"changed model")
        self.assertEqual(self.plan()["skipped"][0]["reason"], "canonical_asset_overridden_by_map")

    def test_generated_context_path_collision_is_refused(self):
        put(self.map, "def/data_context.rtfix.sii", "SiiNunit { }")
        with self.assertRaisesRegex(DefinitionError, "target already exists"):
            self.plan()

    def test_render_rejects_invalid_tags(self):
        plan = self.plan()
        plan['aliases'][0]['tags'] = ['retail\\nmalformed']
        with self.assertRaisesRegex(DefinitionError, 'context tag'):
            render_context_patch(plan)

    def test_explicit_exclusion_is_respected(self):
        put(self.game, "def/data_context.sii", CONTEXT.replace(" target_data[]: prefab.d_food_mkt5",
            " # prefab.ahorrara excluded: unsuitable spawn\n target_data[]: prefab.d_food_mkt5"))
        self.assertEqual(self.plan()["skipped"][0]["reason"], "explicitly_excluded")

    def test_duplicate_alias_unit_is_ambiguous(self):
        put(self.map, "def/world/prefab.extra.sii", ALIAS_PREFAB)
        self.assertEqual(self.plan()["skipped"][0]["reason"],
                         "missing_or_ambiguous_alias_definition")

    def test_duplicate_context_unit_fails_closed(self):
        put(self.map, "def/data_context.map.sii", CONTEXT)
        with self.assertRaisesRegex(DefinitionError, "Duplicate effective"):
            self.plan()


if __name__ == "__main__":
    unittest.main()
