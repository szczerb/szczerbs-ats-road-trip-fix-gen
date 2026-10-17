"""Sourced price policy for additive map-wide petrol definition overrides.

Existing effective prices win. Missing prices first reuse the nearest lower
definition of the same mounted path and country unit. Otherwise an estimated
price uses the unchanged target diesel price and a stock ATS petrol/diesel
ratio. Every input and choice is recorded for review.
"""

from __future__ import annotations

from decimal import Decimal, DecimalException, ROUND_HALF_UP
import hashlib

from .package import Package, ResourceStack
from .petrol_prices import _price
from .sii import DefinitionError, _HEADER, _mask_strings, parse_units, strip_comments


DEFAULT_REFERENCE = 'def/country/washington.sui'
_COUNTRY_PATTERN = r'def/country/[^/]+\.sui'


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _country(data: bytes, path: str):
    text = data.decode('utf-8')
    clean = _mask_strings(strip_comments(text))
    if '@include' in clean:
        raise ValueError('country definition includes another resource')
    units = parse_units(text, source=path)
    if len(units) != 1 or units[0].kind != 'country_data' or units[0].attribute_errors:
        raise ValueError('expected one unambiguous country_data unit')
    return units[0]


def _target_paths(stack: ResourceStack, target_packages: set[str]) -> list[str]:
    paths = stack.matching(_COUNTRY_PATTERN)
    if 'def/country.sii' in stack.resources:
        path = 'def/country.sii'
        package, _ = stack.resources[path]
        if str(package.path) in target_packages:
            data = stack.read(path)
            if _HEADER.search(_mask_strings(strip_comments(data.decode('utf-8')))):
                paths.append(path)
    return [path for path in sorted(paths)
            if str(stack.resources[path][0].path) in target_packages]


def _prefetch(stack: ResourceStack, paths: list[str]) -> None:
    wanted: dict[Package, set[str]] = {}
    for path in paths:
        winner, _ = stack.resources[path]
        for package in stack.packages:
            if path in package.files:
                wanted.setdefault(package, set()).add(path)
            if package is winner:
                break
    for package, names in wanted.items():
        package.prefetch(sorted(names))


def build_policy(stack: ResourceStack, game_stack: ResourceStack, *,
                 target_packages: set[str],
                 reference_path: str = DEFAULT_REFERENCE) -> tuple[dict[str, dict], dict]:
    """Choose explicit values for target country units requiring petrol prices.

    The reference path resolves only in ``game_stack``, so map overrides cannot
    change the fallback ratio. Returned policy keys are mounted resource paths.
    Blockers make the result unsuitable for packaging, even if some entries were
    selected successfully.
    """
    report = {'schema_version': 1, 'method': 'lower_layer_or_game_ratio',
              'reference_path': reference_path, 'reference': None,
              'entries': [], 'coverage': {'blockers': [], 'target_files': 0,
                                          'retained': 0, 'restored': 0, 'estimated': 0}}
    coverage = report['coverage']
    blockers = coverage['blockers']
    policy: dict[str, dict] = {}
    try:
        if reference_path not in game_stack.resources:
            raise ValueError('petrol reference is absent from the game-only stack')
        reference_package, reference_resource = game_stack.resources[reference_path]
        reference_package.prefetch([reference_path])
        reference_data = game_stack.read(reference_path)
        reference_unit = _country(reference_data, reference_path)
        reference_fuel = reference_unit.one('fuel_price')
        reference_petrol = reference_unit.one('petrol_price')
        if _price(reference_fuel)[0] != 'positive' or _price(reference_petrol)[0] != 'positive':
            raise ValueError('petrol reference needs positive finite diesel and petrol prices')
        if reference_path == DEFAULT_REFERENCE and (
                Decimal(reference_fuel) != Decimal('1.92132') or
                Decimal(reference_petrol) != Decimal('1.47197')):
            raise ValueError('stock Washington price inputs differ from the reviewed ATS 1.61.3.18 values')
        ratio = Decimal(reference_petrol) / Decimal(reference_fuel)
        report['reference'] = {'path': reference_path, 'package': reference_resource.package,
                               'physical_path': reference_resource.physical_path,
                               'sha256': _digest(reference_data), 'unit': reference_unit.name,
                               'fuel_price': reference_fuel, 'petrol_price': reference_petrol,
                               'petrol_to_diesel_ratio': str(ratio)}
    except (UnicodeDecodeError, DecimalException, DefinitionError, ValueError, KeyError) as exc:
        blockers.append({'path': reference_path, 'reason': str(exc)})
        return policy, report

    try:
        paths = _target_paths(stack, target_packages)
        _prefetch(stack, paths)
    except (UnicodeDecodeError, DefinitionError, ValueError, KeyError) as exc:
        blockers.append({'reason': str(exc)})
        return policy, report

    for path in paths:
        winner, winner_resource = stack.resources[path]
        try:
            target_data = stack.read(path)
            unit = _country(target_data, path)
            diesel = unit.one('fuel_price')
            petrol = unit.one('petrol_price')
            if _price(diesel)[0] != 'positive':
                raise ValueError('target diesel price is missing or invalid')
            entry = {'path': path, 'unit': unit.name, 'target_package': winner_resource.package,
                     'target_sha256': _digest(target_data), 'target_fuel_price': diesel,
                     'target_petrol_price': petrol}
            report['entries'].append(entry)
            coverage['target_files'] += 1
            if _price(petrol)[0] == 'positive':
                entry['decision'] = 'retain'
                coverage['retained'] += 1
                continue

            winner_index = stack.packages.index(winner)
            lower_source = None
            for lower in reversed(stack.packages[:winner_index]):
                if path not in lower.files:
                    continue
                lower_data = lower.read(path)
                lower_unit = _country(lower_data, path)
                lower_petrol = lower_unit.one('petrol_price')
                candidate = {'package': str(lower.path), 'physical_path': lower.files[path],
                             'sha256': _digest(lower_data), 'unit': lower_unit.name,
                             'petrol_price': lower_petrol}
                entry.setdefault('lower_candidates', []).append(candidate)
                if lower_unit.name == unit.name and _price(lower_petrol)[0] == 'positive':
                    lower_source = candidate
                    break
            if lower_source:
                value = lower_source['petrol_price']
                source = (f"Lower-priority {lower_source['package']}:{lower_source['physical_path']} "
                          f"sha256={lower_source['sha256']}")
                reason = 'Restore positive petrol price from the highest lower source with the same path and unit.'
                entry['decision'] = 'restore_lower_source'
                entry['selected_source'] = lower_source
                coverage['restored'] += 1
            else:
                try:
                    value = str((Decimal(diesel) * ratio).quantize(Decimal('0.00000001'),
                                                                  rounding=ROUND_HALF_UP))
                except DecimalException as exc:
                    raise ValueError('estimated petrol price cannot be rounded to 8 decimal places') from exc
                if _price(value)[0] != 'positive':
                    raise ValueError('estimated petrol price is not positive and finite')
                source = (f"Estimated from unchanged target fuel_price {diesel} and stock game "
                          f"{reference_path} ratio {report['reference']['petrol_to_diesel_ratio']}; "
                          f"reference sha256={report['reference']['sha256']}")
                reason = 'No positive same-unit lower price; use the reviewed game economy petrol/diesel ratio.'
                entry['decision'] = 'estimate_game_ratio'
                entry['formula'] = {'target_fuel_price': diesel,
                                    'target_sha256': entry['target_sha256'],
                                    'reference_petrol_price': reference_petrol,
                                    'reference_fuel_price': reference_fuel,
                                    'rounding': '8 decimal places, ROUND_HALF_UP'}
                coverage['estimated'] += 1
            policy[path] = {'value': value, 'source': source, 'reason': reason}
            entry['selected_petrol_price'] = value
        except (UnicodeDecodeError, DecimalException, DefinitionError, ValueError, KeyError) as exc:
            blockers.append({'path': path, 'package': winner_resource.package, 'reason': str(exc)})
    return policy, report
