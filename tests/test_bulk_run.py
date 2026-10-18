"""Small archive fixtures for the one-source map-wide workflow."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import sys
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip import bulk_run


def archive(path: Path, files=None):
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in (files or {}).items():
            z.writestr(name, data)


class BulkRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / 'game'
        self.inputs = self.root / 'local_inputs'
        self.game.mkdir()
        self.inputs.mkdir()
        archive(self.game / 'version.scs',
                {'version.sii': 'SiiNunit\n{\nfs_pack_set : .test {\n application: ats\n version: "1.61.3.18"\n}\n}\n'})
        for name in (*bulk_run._BASE_PACKAGES, 'dlc_rt_ford.scs'):
            archive(self.game / name)
        archive(self.game / 'def.scs', {'def/country/washington.sui':
                b'country_data: country.data.washington {\n'
                b' fuel_price: 1.92132\n petrol_price: 1.47197\n}\n'})
        self.source = self.inputs / 'ATS_Expansion_v23.0_1.61.scs'
        archive(self.source, {'map/usa/sec+0000+0000.base': b'placeholder'})

    def test_courier_analysis_writes_audit_but_never_calls_mod_writer(self):
        for suffix, blockers in (('10', []), ('11', [{'reason': 'unknown definition'}])):
            plan = SimpleNamespace(reports={'courier': {'analysis_only': True}},
                                   resources={'must-not-be-written': b'candidate'},
                                   blockers=blockers,
                                   coverage={'complete': not blockers, 'blockers': blockers})
            stamp = '2026-10-18_03-00-' + suffix
            with patch.object(bulk_run, 'REPO_ROOT', self.root), \
                 patch.object(bulk_run, 'run_processors', return_value=plan) as run, \
                 patch.object(bulk_run, 'write_mod') as writer:
                report = bulk_run.analyze_map(self.source, game_dir=self.game, run_id=stamp)
            writer.assert_not_called()
            self.assertEqual(run.call_args.kwargs['config'].mode.value, 'analyze')
            self.assertEqual(report['status'], 'reported_partial' if blockers else 'reported')
            self.assertTrue(report['analysis_only'])
            self.assertEqual(report['generated_mod_count'], 0)
            self.assertNotIn('output', report)
            self.assertEqual(json.loads(Path(report['report_path']).read_text()), report)
            self.assertFalse((self.root / 'local_outputs/generated').exists())
            self.assertEqual(report['workflow']['processors_enabled'], ['courier'])

    def test_analysis_report_cannot_overwrite_an_existing_audit(self):
        stamp = '2026-10-18_03-00-12'
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            work, output, _ = bulk_run._run_paths('ATS Expansion', 3, stamp,
                                                 analysis_only=True)
            self.assertIsNone(output)
            work.mkdir(parents=True)
            (work / 'audit.json').write_text('retain original')
            with self.assertRaises(FileExistsError):
                bulk_run.analyze_map(self.source, game_dir=self.game, run_id=stamp)
        self.assertEqual((work / 'audit.json').read_text(), 'retain original')

    def test_game_version_from_version_archive_and_refuses_other_release(self):
        self.assertEqual(bulk_run._game_version(self.game, None), '1.61.3.18')
        archive(self.game / 'version.scs',
                {'version.sii': 'SiiNunit\n{\n application: ats\n version: "1.62.0"\n}\n'})
        with self.assertRaisesRegex(ValueError, 'ATS 1.61'):
            bulk_run._game_version(self.game, None)

    def test_dependency_profiles_and_output_paths(self):
        resource = self.inputs / 'Reforma_MegaResources_v3.scs'
        reforma = self.inputs / 'Reforma_3.scs'
        for path in (resource, reforma):
            archive(path)
        self.assertEqual(bulk_run._map_packages(reforma, []), [resource, reforma])
        siblings = [self.inputs / f'promods-ats-{role}-v164.scs'
                    for role in ('assets', 'models', 'def', 'map')]
        for path in siblings:
            archive(path)
        wce = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        archive(wce)
        self.assertEqual(bulk_run._profile(wce)[0], 'Western Canada Expansion')
        self.assertEqual(bulk_run._profile(self.inputs / 'Alaska_Expansion_v1.2.3.scs')[0],
                         'Alaska Expansion')
        self.assertEqual(bulk_run._map_packages(siblings[-1], []), siblings)
        self.assertEqual(bulk_run._map_packages(wce, []), [*siblings, wce])
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            work, output, stamp = bulk_run._run_paths('ProMods Canada', 3, '2026-10-17_22-11-10')
        self.assertEqual(work, self.root / 'local_outputs/work/2026-10-17_22-11-10/promods-canada')
        self.assertEqual(output.name,
                         'szczerbs-road-trip-gas-stations-fix-promods-canada-1.61-r3-experimental.scs')
        self.assertEqual(stamp, '2026-10-17_22-11-10')

    def test_connector_source_only_stacks_and_distinct_labels(self):
        reforma_resources = self.inputs / 'Reforma_MegaResources_v3_0_1_161.scs'
        reforma = self.inputs / 'Reforma_3_0_1_161.scs'
        reforma_patch = self.inputs / 'Reforma_OtherMaps_Patch_40_161.scs'
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        western_patch = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        for path in (reforma_resources, reforma, reforma_patch, *promods, western, western_patch):
            archive(path)
        self.assertEqual(bulk_run._profile(reforma_patch)[0], 'Reforma OtherMaps Patch')
        self.assertEqual(bulk_run._profile(western_patch)[0],
                         'Western Canada ProMods Connections')
        self.assertEqual(bulk_run._map_packages(reforma_patch, []),
                         [reforma_resources, reforma, reforma_patch])
        self.assertEqual(bulk_run._map_packages(western_patch, []),
                         [western, promods[1], promods[0], promods[3], promods[2],
                          western_patch])
        # A main-map invocation must never pick the OtherMaps patch as Reforma.
        self.assertEqual(bulk_run._map_packages(reforma, []), [reforma_resources, reforma])
        self.assertEqual(bulk_run._map_packages(western, []), [*promods, western])
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            _, output, _ = bulk_run._run_paths('Reforma OtherMaps Patch', 1,
                                               '2026-10-17_22-11-10')
        self.assertIn('reforma-othermaps-patch-1.61-r1-experimental', output.name)

    def test_connector_explicit_order_and_missing_or_ambiguous_companions(self):
        reforma_resources = self.inputs / 'Reforma_MegaResources_v3.scs'
        reforma = self.inputs / 'Reforma_3.scs'
        reforma_patch = self.inputs / 'Reforma_OtherMaps_Patch_40_161.scs'
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        western_patch = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        for path in (reforma_resources, reforma_patch, *promods, western, western_patch):
            archive(path)
        with self.assertRaisesRegex(ValueError, 'Reforma_\\[0-9\\]'):
            bulk_run._map_packages(reforma_patch, [])
        archive(reforma)
        self.assertEqual(bulk_run._map_packages(reforma_patch, [str(reforma)]),
                         [reforma_resources, reforma, reforma_patch])
        self.assertEqual(bulk_run._map_packages(western_patch,
                         [str(western), str(promods[3])]),
                         [western, promods[1], promods[0], promods[3],
                          promods[2], western_patch])
        with self.assertRaisesRegex(ValueError, 'Source archive must be highest'):
            bulk_run._map_packages(western_patch, [str(western_patch)])
        # The user can explicitly choose another priority; inference never
        # reorders their supplied archives.
        self.assertEqual(bulk_run._map_packages(western_patch,
                         [str(promods[3]), str(western)]),
                         [promods[1], promods[0], promods[3], western,
                          promods[2], western_patch])
        other = self.inputs / 'Reforma_4.scs'
        archive(other)
        with self.assertRaisesRegex(ValueError, 'Expected exactly one sibling Reforma_'):
            bulk_run._map_packages(reforma_patch, [])
        # An explicit choice resolves sibling ambiguity without pulling both.
        self.assertEqual(bulk_run._map_packages(reforma_patch, [str(reforma)]),
                         [reforma_resources, reforma, reforma_patch])

    def test_connector_does_not_pull_unrelated_or_incomplete_maps(self):
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        connector = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        alaska = self.inputs / 'Alaska_Expansion_v1.2.3.scs'
        for path in (*promods, western, connector, alaska):
            archive(path)
        self.assertNotIn(alaska, bulk_run._map_packages(connector, []))
        promods[2].unlink()
        with self.assertRaisesRegex(ValueError, 'promods-ats-def'):
            bulk_run._map_packages(connector, [])
        # Explicit dependencies can reside outside the source directory.
        separate = self.root / 'separate'
        separate.mkdir()
        explicit_def = separate / promods[2].name
        archive(explicit_def)
        self.assertEqual(bulk_run._map_packages(connector, [str(explicit_def)]),
                         [western, promods[1], promods[0], promods[3], explicit_def,
                          connector])

    def test_full_explicit_live_order_is_unchanged(self):
        names = ('Reforma_MegaResources_v3.scs', 'Reforma_3.scs',
                 'ATS_Expansion_v23.0_1.61.scs',
                 'Western_Canada_Expansion_v1.7.3.scs',
                 'promods-ats-models-v164.scs', 'promods-ats-assets-v164.scs',
                 'promods-ats-map-v164.scs', 'promods-ats-def-v164.scs',
                 'Reforma_OtherMaps_Patch_40_161.scs',
                 'Western_Canada_Promods_Connections_v1.7.3.scs')
        paths = [self.inputs / name for name in names]
        for path in paths:
            archive(path)
        self.assertEqual(bulk_run._map_packages(paths[-1], [str(p) for p in paths[:-1]]),
                         paths)

    def test_connector_generation_uses_distinct_metadata_and_existing_icons(self):
        source_icons = bulk_run.REPO_ROOT / 'assets/mod-icons'
        target_icons = self.root / 'assets/mod-icons'
        target_icons.mkdir(parents=True)
        for base in ('reforma', 'western-canada-expansion'):
            (target_icons / f'{base}-c.jpg').write_bytes(
                (source_icons / f'{base}-c.jpg').read_bytes())
        names = ('Reforma_MegaResources_v3.scs', 'Reforma_3.scs',
                 'Reforma_OtherMaps_Patch_40_161.scs',
                 'promods-ats-assets-v164.scs', 'promods-ats-models-v164.scs',
                 'promods-ats-def-v164.scs', 'promods-ats-map-v164.scs',
                 'Western_Canada_Expansion_v1.7.3.scs',
                 'Western_Canada_Promods_Connections_v1.7.3.scs')
        for name in names:
            archive(self.inputs / name)
        module = SimpleNamespace(plan_map_fuel=lambda *args, **kwargs:
                                 ({'blockers': []}, {'map/usa/fixture.base': b'fixture'}))
        cases = (('Reforma_OtherMaps_Patch_40_161.scs',
                  'Reforma OtherMaps Patch', 'reforma', '2026-10-17_22-11-10'),
                 ('Western_Canada_Promods_Connections_v1.7.3.scs',
                  'Western Canada ProMods Connections', 'western-canada-expansion',
                  '2026-10-17_22-11-11'))
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': module}):
            for source_name, label, icon_base, run_id in cases:
                audit = bulk_run.generate_map_fuel(self.inputs / source_name,
                                                   game_dir=self.game, run_id=run_id)
                self.assertEqual(audit['status'], 'generated')
                self.assertEqual(audit['workflow']['map_name'], label)
                with zipfile.ZipFile(audit['output']) as z:
                    self.assertIn(f'for {label}', z.read('manifest.sii').decode())
                    self.assertEqual(z.read('mod_icon.jpg'),
                                     (target_icons / f'{icon_base}-c.jpg').read_bytes())
                    report = json.loads(z.read('road_trip_fix_report.json'))
                    self.assertEqual(report['workflow']['target_map_package'],
                                     str((self.inputs / source_name).resolve()))

    def test_combined_connector_packages_own_icon_with_short_cache_name(self):
        original = bulk_run.REPO_ROOT / 'assets/mod-icons/map-compatibility/western-canada-promods-connections.jpg'
        preset = self.root / 'assets/mod-icons/map-compatibility' / original.name
        preset.parent.mkdir(parents=True)
        preset.write_bytes(original.read_bytes())
        for name in ('Western_Canada_Expansion_v1.7.3.scs',
                     'promods-ats-models-v164.scs', 'promods-ats-assets-v164.scs',
                     'promods-ats-map-v164.scs', 'promods-ats-def-v164.scs',
                     'Western_Canada_Promods_Connections_v1.7.3.scs'):
            archive(self.inputs / name)
        source = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        plan = SimpleNamespace(reports={}, resources={'map/usa/fixture.base': b'unchanged'},
                               blockers=[], coverage={'complete': True, 'blockers': []})
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.object(bulk_run, 'run_processors', return_value=plan):
            audit = bulk_run.generate_map_fix(source, game_dir=self.game,
                                              processors=('fuel', 'rest'),
                                              run_id='2026-10-18_17-04-30')
        output = Path(audit['output'])
        self.assertEqual(output.name,
                         'szczerbs-road-trip-map-fix-western-canada-promods-connections-1.61-r9-experimental.scs')
        # Reproduce the cache-name transformation observed in the user's log.
        # This checks our mitigation's path budget, not the game's Win32 code.
        home = 'C:/Users/guest/Documents/American Truck Simulator'
        cache_path = home + '/cache/mod_icons/' + output.stem.encode().hex() + '.jpg'
        self.assertLess(len(cache_path) + 1, 260)
        with zipfile.ZipFile(output) as z:
            self.assertIn('icon: "mod_icon.jpg"', z.read('manifest.sii').decode())
            self.assertEqual(z.read('mod_icon.jpg'), original.read_bytes())
            self.assertEqual(z.read('map/usa/fixture.base'), b'unchanged')
            self.assertIsNone(z.testzip())

    def _run_with_plan(self, planner):
        module = SimpleNamespace(plan_map_fuel=planner)
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': module}):
            return bulk_run.generate_map_fuel(self.source, game_dir=self.game,
                                              run_id='2026-10-17_22-11-10')

    def test_blockers_write_audit_and_refuse_package(self):
        def planner(stack, *, map_packages, map_name):
            self.assertEqual(map_packages, {str(self.source.resolve())})
            self.assertEqual(map_name, 'ATS Expansion')
            return {'blockers': [{'reason': 'unknown sector layout'}]}, {'map/usa/x.base': b'x'}

        with self.assertRaisesRegex(ValueError, 'coverage blocker'):
            self._run_with_plan(planner)
        audit_path = self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json'
        audit = json.loads(audit_path.read_text())
        self.assertEqual(audit['status'], 'blocked')
        self.assertEqual(audit['planned_resource_count'], 1)
        self.assertFalse((self.root / 'local_outputs/generated/2026-10-17_22-11-10').exists())

    def test_already_covered_has_explicit_no_output(self):
        audit = self._run_with_plan(lambda *args, **kwargs: ({'blockers': []}, {}))
        self.assertEqual(audit['status'], 'already_covered')
        self.assertNotIn('output', audit)

    def test_planner_error_writes_failure_audit_without_archive(self):
        def planner(*args, **kwargs):
            raise ValueError('invalid source unit fixture')
        with self.assertRaisesRegex(ValueError, 'invalid source unit'):
            self._run_with_plan(planner)
        path = self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json'
        report = json.loads(path.read_text())
        self.assertEqual(report['status'], 'failed')
        self.assertIn('invalid source unit', report['error'])
        self.assertFalse(list(self.root.rglob('szczerbs-*.scs')))

    def test_source_drift_prevents_packaging(self):
        def planner(*args, **kwargs):
            self.source.write_bytes(self.source.read_bytes() + b'changed fixture')
            return {'coverage': {'blockers': []}}, {'map/usa/fixture.base': b'fixture'}
        with self.assertRaisesRegex(ValueError, 'changed during generation'):
            self._run_with_plan(planner)
        self.assertFalse(list(self.root.rglob('szczerbs-*.scs')))

    def test_generates_package_with_map_metadata_and_audit(self):
        audit = self._run_with_plan(
            lambda *args, **kwargs: ({'blockers': [], 'covered_count': 1},
                                     {'map/usa/fixture.base': b'fixture'}))
        self.assertEqual(audit['status'], 'generated')
        output = Path(audit['output'])
        self.assertTrue(output.is_file())
        with zipfile.ZipFile(output) as z:
            self.assertEqual(z.read('map/usa/fixture.base'), b'fixture')
            manifest = z.read('manifest.sii').decode()
            self.assertIn('for ATS Expansion', manifest)
            self.assertIn('1.61-r2-experimental', manifest)
            report = json.loads(z.read('road_trip_fix_report.json'))
            self.assertEqual(report['workflow']['target_map_package'], str(self.source.resolve()))
        self.assertTrue((self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json').is_file())

    def test_generation_combines_station_and_sourced_petrol_resources(self):
        source_country = (b'country_data: country.data.ak {\n'
                          b' fuel_price: 1.250 # source diesel\n'
                          b' name: "Alaska"\n}\n')
        archive(self.source, {'map/usa/sec+0000+0000.base': b'placeholder',
                              'def/country/ak.sui': source_country})
        audit = self._run_with_plan(lambda *args, **kwargs:
                                    ({'coverage': {'blockers': []}},
                                     {'map/usa/fixture.base': b'fixture'}))
        self.assertEqual(audit['status'], 'generated')
        self.assertTrue(audit['planner']['coverage']['complete'])
        self.assertEqual(audit['planner']['coverage']['petrol_price_changed'], 1)
        self.assertEqual(audit['planner']['petrol_prices']['policy']['coverage']['estimated'], 1)
        with zipfile.ZipFile(audit['output']) as z:
            self.assertEqual(z.read('map/usa/fixture.base'), b'fixture')
            price = z.read('def/country/ak.sui')
            self.assertIn(b'fuel_price: 1.250 # source diesel\n petrol_price: ', price)
            self.assertIn(b'name: "Alaska"', price)
            report = json.loads(z.read('road_trip_fix_report.json'))
            self.assertEqual(report['petrol_prices']['policy']['reference']['fuel_price'], '1.92132')
            self.assertEqual(report['package_metadata']['package_version'], '1.61-r2-experimental')

    def test_price_coverage_blocker_prevents_station_package(self):
        archive(self.source, {'map/usa/sec+0000+0000.base': b'placeholder',
                              'def/country/ak.sui': b'country_data: country.data.ak {\n fuel_price: 0\n}\n'})
        with self.assertRaisesRegex(ValueError, 'coverage blocker'):
            self._run_with_plan(lambda *args, **kwargs:
                                ({'coverage': {'blockers': []}}, {'map/usa/fixture.base': b'fixture'}))
        audit_path = self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json'
        audit = json.loads(audit_path.read_text())
        self.assertEqual(audit['status'], 'blocked')
        self.assertFalse(audit['planner']['coverage']['complete'])
        self.assertTrue(any(item['area'] == 'petrol_price_policy'
                            for item in audit['planner']['coverage']['blockers']))
        self.assertFalse((self.root / 'local_outputs/generated/2026-10-17_22-11-10').exists())

    def test_generic_rest_only_uses_rest_branding_and_no_fuel_icon(self):
        module = SimpleNamespace(plan_rest_stops=lambda *args, **kwargs:
                                 ({'coverage': {'blockers': []}},
                                  {'map/usa/rest.base': b'rest'}))
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.rest_stops': module}):
            audit = bulk_run.generate_map_fix(self.source, processors=('rest',),
                                              game_dir=self.game,
                                              run_id='2026-10-17_22-11-10')
        self.assertEqual(audit['status'], 'generated')
        self.assertEqual(audit['workflow']['processors_enabled'], ['rest'])
        self.assertIn('rest-stops-fix', audit['output'])
        with zipfile.ZipFile(audit['output']) as z:
            self.assertIn('Rest Stops Fix', z.read('manifest.sii').decode())
            self.assertNotIn('mod_icon.jpg', z.namelist())
            self.assertIn('map/usa/rest.base', z.namelist())
            report = json.loads(z.read('road_trip_fix_report.json'))
            self.assertEqual(report['processors_enabled'], ['rest'])
            self.assertEqual(report['package_metadata']['fix_topics'], ['rest'])

    def test_generic_mixed_uses_composed_resource_and_accurate_branding(self):
        fuel = SimpleNamespace(plan_map_fuel=lambda *args, **kwargs:
                               ({'coverage': {'blockers': []}},
                                {'map/usa/sec+0000+0000.base': b'fuel'}))

        def rest(stack, *, map_packages, map_name, radius, resource_overrides):
            self.assertEqual(resource_overrides['map/usa/sec+0000+0000.base'], b'fuel')
            return ({'coverage': {'blockers': []},
                     'composed_resource_paths': ['map/usa/sec+0000+0000.base']},
                    {'map/usa/sec+0000+0000.base': b'fuel+rest'})

        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': fuel,
                                      'ats_road_trip.rest_stops': SimpleNamespace(plan_rest_stops=rest)}):
            audit = bulk_run.generate_map_fix(self.source, processors=('rest', 'fuel'),
                                              game_dir=self.game,
                                              run_id='2026-10-17_22-11-10')
        self.assertEqual(audit['status'], 'generated')
        self.assertEqual(audit['workflow']['processors_enabled'], ['fuel', 'rest'])
        self.assertIn('map-fix', audit['output'])
        with zipfile.ZipFile(audit['output']) as z:
            self.assertEqual(z.read('map/usa/sec+0000+0000.base'), b'fuel+rest')
            self.assertIn('Map Compatibility Fix', z.read('manifest.sii').decode())

    def test_generic_mixed_blocker_writes_audit_without_partial_package(self):
        fuel = SimpleNamespace(plan_map_fuel=lambda *args, **kwargs:
                               ({'coverage': {'blockers': []}}, {'same.path': b'fuel'}))
        rest = SimpleNamespace(plan_rest_stops=lambda *args, **kwargs:
                               ({'coverage': {'blockers': []}}, {'same.path': b'rest'}))
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': fuel,
                                      'ats_road_trip.rest_stops': rest}):
            with self.assertRaisesRegex(ValueError, 'coverage blocker'):
                bulk_run.generate_map_fix(self.source, processors=('fuel', 'rest'),
                                          game_dir=self.game,
                                          run_id='2026-10-17_22-11-10')
        audit = json.loads((self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json').read_text())
        self.assertEqual(audit['status'], 'blocked')
        self.assertTrue(any(b.get('area') == 'resource_collision'
                            for b in audit['planner']['coverage']['blockers']))
        self.assertFalse((self.root / 'local_outputs/generated/2026-10-17_22-11-10').exists())


if __name__ == '__main__':
    unittest.main()
