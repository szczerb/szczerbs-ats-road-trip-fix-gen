from pathlib import Path
import tempfile
import unittest

from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.petrol_prices import plan_petrol_prices
from ats_road_trip.sii import parse_units


def country(name='bc', diesel='1.630', petrol=None, newline='\n'):
    lines = ['country_data: country.data.' + name, '{',
             '\tcountry_id: 202', '\tname: "British Columbia"',
             '\tfuel_price: ' + diesel + ' # dated diesel source']
    if petrol is not None:
        lines.append('\tpetrol_price: ' + petrol + ' # prior petrol source')
    lines += ['\tmass_limit_per_axle_count[]: 18200 # 2-axle',
              '\tmass_limit_per_axle_count[]: 26100 # 3-axle',
              '\tpos: (-93910, 0, -116700)', '}']
    return (newline.join(lines) + newline).encode()


class PetrolPricesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def package(self, name, files):
        root = self.root / name
        for path, data in files.items():
            output = root / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
        return Package(root)

    def plan(self, packages, target, policy):
        return plan_petrol_prices(ResourceStack(packages),
                                  target_packages={str(target.path)}, policy=policy)

    def test_connector_wins_and_insert_preserves_every_other_byte(self):
        lower = self.package('promods', {'def/country/bc.sui': country(petrol='1.502116')})
        source = country(newline='\r\n')
        connector = self.package('connector', {'def/country/bc.sui': source})
        policy = {'country.data.bc': {'value': '1.502116',
                                      'source': 'ProMods Canada Definitions 1.6.4, 2026-08-31',
                                      'reason': 'Restore the lower-layer petrol value erased by the connector'}}
        report, changes = self.plan([lower, connector], connector, policy)
        self.assertEqual(report['coverage']['blockers'], [])
        self.assertEqual(report['coverage']['changed'], 1)
        self.assertEqual(report['countries'][0]['package'], str(connector.path))
        expected = source.replace(b'\tfuel_price: 1.630 # dated diesel source\r\n',
                                  b'\tfuel_price: 1.630 # dated diesel source\r\n\tpetrol_price: 1.502116\r\n')
        self.assertEqual(changes['def/country/bc.sui'], expected)
        unit = parse_units(expected.decode())[0]
        self.assertEqual(unit.one('fuel_price'), '1.630')
        self.assertEqual(unit.values('mass_limit_per_axle_count'), ('18200', '26100'))

    def test_valid_existing_price_is_retained_byte_identical(self):
        raw = country(petrol='1.234500')
        target = self.package('source', {'def/country/bc.sui': raw})
        report, changes = self.plan([target], target, {})
        self.assertEqual(changes, {})
        self.assertEqual(report['coverage']['retained'], 1)
        self.assertEqual(target.read('def/country/bc.sui'), raw)

    def test_explicit_zero_and_nonfinite_are_bounded_replacements(self):
        for old in ('0.000', 'NaN', '-inf'):
            with self.subTest(old=old):
                raw = country(petrol=old)
                target = self.package('source_' + old.replace('-', '_'), {'def/country/bc.sui': raw})
                report, changes = self.plan([target], target, {
                    'def/country/bc.sui': {'value': '1.5', 'source': 'test fixture', 'reason': 'replace invalid token'}})
                self.assertEqual(report['coverage']['blockers'], [])
                self.assertEqual(changes['def/country/bc.sui'], raw.replace(
                    ('petrol_price: ' + old).encode(), b'petrol_price: 1.5'))

    def test_complete_policy_coverage_and_numeric_guards(self):
        target = self.package('source', {'def/country/bc.sui': country(),
                                         'def/country/ab.sui': country('ab')})
        good = {'value': '1.5', 'source': 'documented value', 'reason': 'explicit choice'}
        report, changes = self.plan([target], target, {'country.data.bc': good})
        self.assertEqual(changes, {})
        self.assertIn('needs an explicit policy', report['coverage']['blockers'][0]['reason'])
        for bad in ('0', '-1', 'NaN', 'inf', '1e999999', '1e-999999', '1e999999x', True):
            with self.subTest(bad=bad):
                report, changes = self.plan([target], target,
                                            {'country.data.bc': {**good, 'value': bad},
                                             'country.data.ab': good})
                self.assertEqual(changes, {})
                self.assertTrue(report['coverage']['blockers'])
        report, changes = self.plan([target], target,
                                    {'country.data.bc': good, 'country.data.ab': good,
                                     'country.data.ghost': good})
        self.assertEqual(changes, {})
        self.assertIn('policy entry matches no effective target country',
                      report['coverage']['blockers'][-1]['reason'])

    def test_ambiguous_units_includes_and_bad_diesel_block_output(self):
        good = {'country.data.bc': {'value': '1.5', 'source': 'fixture', 'reason': 'test'}}
        cases = [country() + country('ab'), country().replace(b'}\n', b'@include "other.sui"\n}\n'),
                 country(diesel='0'), country().replace(b'\tfuel_price: 1.630', b'\tfuel_price[]: 1.630')]
        for index, raw in enumerate(cases):
            with self.subTest(index=index):
                target = self.package('bad_' + str(index), {'def/country/bc.sui': raw})
                report, changes = self.plan([target], target, good)
                self.assertEqual(changes, {})
                self.assertTrue(report['coverage']['blockers'])

    def test_root_direct_unit_and_generated_override_are_idempotent(self):
        target = self.package('root', {'def/country.sii': country()})
        policy = {'country.data.bc': {'value': '1.5', 'source': 'fixture', 'reason': 'test'}}
        report, changes = self.plan([target], target, policy)
        self.assertEqual(report['coverage']['blockers'], [])
        self.assertIn('def/country.sii', changes)
        generated = self.package('generated', changes)
        second, again = self.plan([target, generated], generated, policy)
        self.assertEqual(second['coverage']['blockers'], [])
        self.assertEqual(second['coverage']['retained'], 1)
        self.assertEqual(again, {})

    def test_wrapped_fragment_duplicate_unit_and_unresolved_root_include(self):
        wrapped = b'SiiNunit\n{\n' + country() + b'}\n'
        target = self.package('wrapped', {'def/country/bc.sui': wrapped})
        policy = {'country.data.bc': {'value': '1.5', 'source': 'fixture', 'reason': 'test'}}
        report, changes = self.plan([target], target, policy)
        self.assertEqual(report['coverage']['blockers'], [])
        self.assertEqual(changes['def/country/bc.sui'].count(b'petrol_price: 1.5'), 1)

        duplicate = self.package('duplicate', {'def/country/bc.sui': country(),
                                                'def/country/other.sui': country()})
        report, changes = self.plan([duplicate], duplicate, policy)
        self.assertEqual(changes, {})
        self.assertTrue(any('duplicate country unit' in b['reason']
                            for b in report['coverage']['blockers']))

        root = self.package('unresolved', {'def/country.sii': b'SiiNunit {\n@include "country/missing.sui"\n}\n'})
        report, changes = self.plan([root], root, {})
        self.assertEqual(changes, {})
        self.assertTrue(report['coverage']['blockers'])


if __name__ == '__main__':
    unittest.main()
