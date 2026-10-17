"""Audit effective country prices and prepare minimal, sourced petrol overrides.

The caller supplies the source stack in game priority order and an explicit policy
for every missing or invalid petrol price. This module never invents a price.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import math
import re

from .package import ResourceStack
from .sii import DefinitionError, _HEADER, _mask_strings, parse_units, strip_comments


_COUNTRY_PATH = re.compile(r'def/country/[^/]+\.sui')
_NUMBER = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')


def _price(value: object) -> tuple[str, str]:
    """Return a status and original numeric spelling, without coercing NaN."""
    if value is None:
        return 'missing', ''
    if not isinstance(value, str) or not _NUMBER.fullmatch(value.strip()):
        return 'invalid', str(value)
    raw = value.strip()
    try:
        number = Decimal(raw)
    except InvalidOperation:
        return 'invalid', raw
    if not number.is_finite():
        return 'nonfinite', raw
    if number <= 0:
        return 'zero' if number == 0 else 'invalid', raw
    try:
        engine_number = float(number)
    except (OverflowError, ValueError):
        return 'nonfinite', raw
    if not math.isfinite(engine_number):
        return 'nonfinite', raw
    if engine_number == 0:
        return 'zero', raw
    return 'positive', raw


def _policy_value(entry: object) -> tuple[str, str, str]:
    if not isinstance(entry, dict) or set(entry) != {'value', 'source', 'reason'}:
        raise ValueError('policy entry requires exactly value, source, and reason')
    value = entry['value']
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError('policy value must be a positive finite number')
    spelling = str(value)
    if _price(spelling)[0] != 'positive':
        raise ValueError('policy value must be a positive finite number')
    source, reason = entry['source'], entry['reason']
    if not isinstance(source, str) or not source.strip() or not isinstance(reason, str) or not reason.strip():
        raise ValueError('policy source and reason must be nonempty strings')
    return spelling, source.strip(), reason.strip()


def _unit_body(text: str, path: str) -> tuple[int, int]:
    """Locate the sole country unit while retaining original string offsets."""
    masked = _mask_strings(strip_comments(text))
    headers = list(_HEADER.finditer(masked))
    if len(headers) != 1 or headers[0].group(1) != 'country_data':
        raise ValueError(f'{path}: expected exactly one country_data unit')
    start = headers[0].end()
    depth, end = 1, start
    while end < len(masked) and depth:
        depth += (masked[end] == '{') - (masked[end] == '}')
        end += 1
    if depth:
        raise ValueError(f'{path}: unbalanced country unit')
    return start, end - 1


def _field(text: str, body: tuple[int, int], field: str) -> list[re.Match[str]]:
    """Find line-oriented scalar attributes, ignoring comments and strings."""
    start, end = body
    masked = _mask_strings(strip_comments(text))
    pattern = re.compile(r'(?m)^[ \t]*' + field + r'[ \t]*:[ \t]*([^\s#/]*)')
    return [m for m in pattern.finditer(masked) if start <= m.start() < end]


def _edit(text: str, path: str, value: str, *, missing: bool) -> str:
    body = _unit_body(text, path)
    if missing:
        diesel = _field(text, body, 'fuel_price')
        if len(diesel) != 1:
            raise ValueError(f'{path}: cannot locate one diesel price line')
        line_end = text.find('\n', diesel[0].end())
        if line_end < 0 or line_end > body[1]:
            raise ValueError(f'{path}: diesel price line has no insertion boundary')
        newline = '\r\n' if text[line_end - 1:line_end + 1] == '\r\n' else '\n'
        indent = re.match(r'[ \t]*', text[diesel[0].start():diesel[0].end()]).group()
        insertion = indent + 'petrol_price: ' + value + newline
        return text[:line_end + 1] + insertion + text[line_end + 1:]
    petrol = _field(text, body, 'petrol_price')
    if len(petrol) != 1 or not petrol[0].group(1):
        raise ValueError(f'{path}: cannot isolate one petrol price token')
    token_start, token_end = petrol[0].span(1)
    return text[:token_start] + value + text[token_end:]


def plan_petrol_prices(stack: ResourceStack, *, target_packages: set[str],
                       policy: dict[str, dict]) -> tuple[dict, dict[str, bytes]]:
    """Return an audit report and changed country resources.

    Policy keys are mounted paths or country unit names. Every replacement needs
    ``value``, ``source``, and ``reason``. Any blocker clears the resource map so
    a caller cannot accidentally package incomplete coverage.
    """
    report = {'schema_version': 1, 'analysis': 'effective_country_petrol_prices',
              'package_order': [str(package.path) for package in stack.packages],
              'target_packages': sorted(target_packages), 'countries': [],
              'source_resources': [],
              'coverage': {'blockers': [], 'inspected': 0, 'retained': 0,
                           'changed': 0, 'missing': 0, 'invalid': 0}}
    coverage = report['coverage']
    blockers = coverage['blockers']
    changes: dict[str, bytes] = {}
    used_policy: set[str] = set()
    seen_units: dict[str, str] = {}
    paths = stack.matching(r'def/country/[^/]+\.sui')
    # Some mods define a country directly in this root instead of including a
    # .sui fragment. A normal include-only root is left to its fragments.
    if 'def/country.sii' in stack.resources:
        paths.append('def/country.sii')
    for path in sorted(paths):
        package, resource = stack.resources[path]
        if str(package.path) not in target_packages:
            continue
        try:
            data = stack.read(path)
            text = data.decode('utf-8')
            clean = _mask_strings(strip_comments(text))
            if path == 'def/country.sii' and not _HEADER.search(clean):
                # A country root can contain only includes. Resolve them so an
                # incomplete source stack cannot appear to have full coverage.
                parse_units(text, source=path, include_reader=stack.text)
                continue
            if '@include' in clean:
                raise ValueError('includes in an edited country file are unsupported')
            units = parse_units(text, source=path)
            if len(units) != 1 or units[0].kind != 'country_data':
                raise ValueError('expected exactly one country_data unit')
            unit = units[0]
            if unit.name in seen_units:
                raise ValueError(f'duplicate country unit also in {seen_units[unit.name]}')
            seen_units[unit.name] = path
            # A fragment must own its own country fields. Arrays and duplicate
            # scalar declarations cannot be safely represented by one edit.
            if unit.attribute_errors:
                raise ValueError('ambiguous attributes: ' + ', '.join(sorted(unit.attribute_errors)))
            diesel_status, diesel_raw = _price(unit.one('fuel_price'))
            petrol_status, petrol_raw = _price(unit.one('petrol_price'))
            if diesel_status != 'positive':
                raise ValueError(f'fuel_price is {diesel_status}')
            if petrol_status == 'invalid' and petrol_raw.lower() in {'nan', '+nan', '-nan', 'inf', '+inf', '-inf', 'infinity', '+infinity', '-infinity'}:
                petrol_status = 'nonfinite'
            record = {'path': path, 'unit': unit.name, 'package': resource.package,
                      'physical_path': resource.physical_path,
                      'source_sha256': hashlib.sha256(data).hexdigest(),
                      'fuel_price': {'status': diesel_status, 'value': diesel_raw},
                      'petrol_price': {'status': petrol_status, 'value': petrol_raw}}
            report['countries'].append(record)
            report['source_resources'].append({'path': path, 'package': resource.package,
                                                'physical_path': resource.physical_path,
                                                'sha256': record['source_sha256']})
            coverage['inspected'] += 1
            keys = [key for key in (path, unit.name) if key in policy]
            if len(keys) > 1:
                raise ValueError('policy specifies both path and unit name')
            if keys:
                used_policy.add(keys[0])
                validated_policy = _policy_value(policy[keys[0]])
            if petrol_status == 'positive':
                coverage['retained'] += 1
                continue
            coverage['missing' if petrol_status == 'missing' else 'invalid'] += 1
            if not keys:
                raise ValueError(f'{petrol_status} petrol_price needs an explicit policy')
            value, source, reason = validated_policy
            edited = _edit(text, path, value, missing=petrol_status == 'missing')
            parsed = parse_units(edited, source=path)
            if len(parsed) != 1 or parsed[0].kind != unit.kind or parsed[0].name != unit.name:
                raise ValueError('edited country unit did not round-trip')
            expected = dict(unit.attributes)
            expected['petrol_price'] = (value,)
            if parsed[0].attributes != expected or parsed[0].attribute_errors:
                raise ValueError('edited country attributes did not round-trip')
            output = edited.encode('utf-8')
            changes[path] = output
            record['policy'] = {'key': keys[0], 'value': value, 'source': source, 'reason': reason}
            record['output_sha256'] = hashlib.sha256(output).hexdigest()
            coverage['changed'] += 1
        except (UnicodeDecodeError, DefinitionError, ValueError, KeyError) as exc:
            blockers.append({'path': path, 'package': resource.package, 'reason': str(exc)})
    for key in sorted(set(policy) - used_policy):
        blockers.append({'policy_key': key, 'reason': 'policy entry matches no effective target country'})
    if blockers:
        changes.clear()
    return report, changes
