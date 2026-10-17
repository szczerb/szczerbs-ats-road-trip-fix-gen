from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import tempfile
import unittest

from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.petrol_policy import build_policy
from ats_road_trip.petrol_prices import plan_petrol_prices


def country(name, diesel, petrol=None):
    fields = [f'country_data: country.data.{name}', '{', f'  fuel_price: {diesel}']
    if petrol is not None:
        fields.append(f'  petrol_price: {petrol}')
    fields.append('}')
    return ('\n'.join(fields) + '\n').encode()


class PetrolPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.package('game', {'def/country/washington.sui':
                                          country('washington', '1.92132', '1.47197')})
        self.game_stack = ResourceStack([self.game])

    def package(self, name, resources):
        root = self.root / name
        for path, content in resources.items():
            output = root / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        return Package(root)

    def test_restores_highest_lower_same_path_and_unit(self):
        old = self.package('old', {'def/country/bc.sui': country('bc', '1.8', '1.4')})
        promods = self.package('promods', {'def/country/bc.sui': country('bc', '1.833761', '1.502116')})
        connector = self.package('connector', {'def/country/bc.sui': country('bc', '1.630')})
        stack = ResourceStack([self.game, old, promods, connector])
        policy, report = build_policy(stack, self.game_stack,
                                      target_packages={str(connector.path)})
        self.assertEqual(report['coverage']['blockers'], [])
        self.assertEqual(report['coverage']['restored'], 1)
        self.assertEqual(policy['def/country/bc.sui']['value'], '1.502116')
        self.assertEqual(report['entries'][0]['selected_source']['package'], str(promods.path))
        self.assertEqual(report['entries'][0]['target_fuel_price'], '1.630')
        audit, resources = plan_petrol_prices(stack, target_packages={str(connector.path)}, policy=policy)
        self.assertEqual(audit['coverage']['blockers'], [])
        self.assertIn(b'fuel_price: 1.630\n  petrol_price: 1.502116', resources['def/country/bc.sui'])

    def test_other_unit_lower_source_is_not_reused_and_mod_reference_is_ignored(self):
        lower = self.package('lower', {'def/country/bc.sui': country('not_bc', '1.2', '9.0')})
        mod = self.package('mod', {'def/country/washington.sui': country('washington', '1', '9'),
                                    'def/country/bc.sui': country('bc', '1.630')})
        stack = ResourceStack([self.game, lower, mod])
        policy, report = build_policy(stack, self.game_stack,
                                      target_packages={str(mod.path)})
        expected = str((Decimal('1.630') * Decimal('1.47197') / Decimal('1.92132')).quantize(
            Decimal('0.00000001'), rounding=ROUND_HALF_UP))
        self.assertEqual(report['coverage']['blockers'], [])
        self.assertEqual(report['coverage']['estimated'], 1)
        self.assertEqual(report['coverage']['retained'], 1)
        self.assertEqual(policy['def/country/bc.sui']['value'], expected)
        self.assertEqual(report['reference']['petrol_price'], '1.47197')
        self.assertEqual(report['reference']['fuel_price'], '1.92132')
        self.assertEqual(report['entries'][0]['lower_candidates'][0]['unit'], 'country.data.not_bc')

    def test_valid_effective_price_is_retained_and_no_policy_entry(self):
        mod = self.package('mod', {'def/country/state.sui': country('state', '1.5', '1.1')})
        policy, report = build_policy(ResourceStack([self.game, mod]), self.game_stack,
                                      target_packages={str(mod.path)})
        self.assertEqual(policy, {})
        self.assertEqual(report['coverage']['retained'], 1)
        self.assertEqual(report['entries'][0]['decision'], 'retain')

    def test_reference_absent_or_changed_and_bad_target_diesel_block(self):
        mod = self.package('mod', {'def/country/state.sui': country('state', '0')})
        stack = ResourceStack([self.game, mod])
        policy, report = build_policy(stack, ResourceStack([]), target_packages={str(mod.path)})
        self.assertEqual(policy, {})
        self.assertTrue(report['coverage']['blockers'])
        changed = self.package('changed', {'def/country/washington.sui': country('washington', '2.0', '1.47197')})
        policy, report = build_policy(stack, ResourceStack([changed]), target_packages={str(mod.path)})
        self.assertEqual(policy, {})
        self.assertIn('reviewed ATS 1.61.3.18', report['coverage']['blockers'][0]['reason'])
        policy, report = build_policy(stack, self.game_stack, target_packages={str(mod.path)})
        self.assertEqual(policy, {})
        self.assertIn('target diesel price', report['coverage']['blockers'][0]['reason'])

    def test_extreme_finite_diesel_is_a_coverage_blocker(self):
        for price in ('1e100', '1e-300'):
            with self.subTest(price=price):
                mod = self.package('extreme_' + price.replace('-', '_'),
                                   {'def/country/state.sui': country('state', price)})
                policy, report = build_policy(ResourceStack([self.game, mod]), self.game_stack,
                                              target_packages={str(mod.path)})
                self.assertEqual(policy, {})
                self.assertEqual(len(report['coverage']['blockers']), 1)
                self.assertIn('estimated petrol price', report['coverage']['blockers'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
