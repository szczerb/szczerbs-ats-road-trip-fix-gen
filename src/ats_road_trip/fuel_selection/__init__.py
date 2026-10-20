"""Opt-in, source-pinned suitability rules for added car fuel interactions.

Roles express reviewed suitability, never chemical fuel or ownership proof.
Unreviewed layouts remain uncertain; native map facilities are always retained.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import re

_ROLES = {'public_car', 'truck_lane', 'fleet_yard', 'uncertain'}
_CONFIDENCE = {'low', 'medium', 'high'}


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')


def _uint(value, name):
    if type(value) is not int or not 0 <= value < 2**64:
        raise ValueError(f'{name} must be an unsigned 64-bit integer')


def _keys(value, allowed, required, name):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise ValueError(f'Invalid {name} fields; required: {sorted(required)}, allowed: {sorted(allowed)}')


@dataclass(frozen=True)
class FuelGroupRule:
    spawn_index: int
    role: str
    confidence: str
    reason: str
    evidence: str

    def __post_init__(self):
        _uint(self.spawn_index, 'spawn_index')
        if (not isinstance(self.role, str) or not isinstance(self.confidence, str)
                or self.role not in _ROLES or self.confidence not in _CONFIDENCE):
            raise ValueError('Invalid fuel role or confidence')
        _text(self.reason, 'reason'); _text(self.evidence, 'evidence')

    @classmethod
    def from_dict(cls, value):
        fields = {'spawn_index', 'role', 'confidence', 'reason', 'evidence'}
        _keys(value, fields, fields, 'fuel group rule')
        return cls(**value)


@dataclass(frozen=True)
class FuelLayoutRule:
    id: str
    descriptor: str
    descriptor_sha256: str
    model_desc: str
    variant: int
    parts: tuple[int, ...]
    additional_parts: tuple[str, ...]
    groups: tuple[FuelGroupRule, ...]
    company_linked: bool | None = None

    def __post_init__(self):
        _text(self.id, 'rule id'); _text(self.model_desc, 'model_desc')
        if (not isinstance(self.descriptor, str) or not self.descriptor.endswith('.ppd')
                or self.descriptor.startswith('/') or '\\' in self.descriptor
                or any(part in ('', '.', '..') for part in self.descriptor.split('/'))):
            raise ValueError('descriptor must be a normalized relative PPD resource path')
        if not isinstance(self.descriptor_sha256, str) or not re.fullmatch('[0-9a-f]{64}', self.descriptor_sha256):
            raise ValueError('descriptor_sha256 must be a lowercase SHA256 digest')
        _uint(self.variant, 'variant')
        for name in ('parts', 'additional_parts', 'groups'):
            if not isinstance(getattr(self, name), tuple):
                raise ValueError(f'{name} must be an immutable tuple')
        for part in self.parts:
            _uint(part, 'parts token')
        for part in self.additional_parts:
            _text(part, 'additional_parts entry')
        if not self.groups or any(not isinstance(group, FuelGroupRule) for group in self.groups):
            raise ValueError('groups must contain FuelGroupRule entries')
        if len({g.spawn_index for g in self.groups}) != len(self.groups):
            raise ValueError('Duplicate spawn_index in layout rule')
        if self.company_linked is not None and type(self.company_linked) is not bool:
            raise ValueError('company_linked must be null or a boolean')

    @classmethod
    def from_dict(cls, value):
        required = {'id', 'descriptor', 'descriptor_sha256', 'model_desc', 'variant', 'parts', 'additional_parts', 'groups'}
        _keys(value, required | {'company_linked'}, required, 'fuel layout rule')
        for key in ('parts', 'additional_parts', 'groups'):
            if not isinstance(value[key], list):
                raise ValueError(f'{key} must be a JSON array')
        return cls(**{**value, 'parts': tuple(value['parts']), 'additional_parts': tuple(value['additional_parts']),
                      'groups': tuple(FuelGroupRule.from_dict(group) for group in value['groups'])})


@dataclass(frozen=True)
class FuelSelectionConfig:
    mode: str = 'broad'
    unknown: str = 'skip'
    rules: tuple[FuelLayoutRule, ...] = ()

    def __post_init__(self):
        if (not isinstance(self.mode, str) or not isinstance(self.unknown, str)
                or self.mode not in ('broad', 'realistic') or self.unknown not in ('skip', 'include')):
            raise ValueError('Fuel selection requires broad/realistic mode and skip/include unknown behavior')
        if not isinstance(self.rules, tuple) or any(not isinstance(rule, FuelLayoutRule) for rule in self.rules):
            raise ValueError('rules must be an immutable tuple of FuelLayoutRule entries')
        if self.mode == 'broad' and self.rules:
            raise ValueError('Broad compatibility does not consume selective rules')
        if len({rule.id for rule in self.rules}) != len(self.rules):
            raise ValueError('Duplicate fuel layout rule id')
        for index, a in enumerate(self.rules):
            for b in self.rules[index + 1:]:
                if (a.descriptor, a.model_desc, a.variant, a.parts, a.additional_parts) == (b.descriptor, b.model_desc, b.variant, b.parts, b.additional_parts):
                    if a.company_linked is None or b.company_linked is None or a.company_linked == b.company_linked:
                        raise ValueError('Overlapping fuel layout rules')

    @classmethod
    def from_dict(cls, value):
        fields = {'schema_version', 'mode', 'unknown', 'rules'}
        _keys(value, fields, fields, 'fuel selection configuration')
        if type(value['schema_version']) is not int or value['schema_version'] != 1:
            raise ValueError('Unsupported fuel selection schema_version; expected 1')
        if not isinstance(value['rules'], list):
            raise ValueError('rules must be a JSON array')
        return cls(value['mode'], value['unknown'], tuple(FuelLayoutRule.from_dict(rule) for rule in value['rules']))

    def summary(self):
        return {'schema_version': 1, 'mode': self.mode, 'unknown': self.unknown,
                'rule_ids': [rule.id for rule in self.rules]}


def load_fuel_selection_config(path: str | Path) -> FuelSelectionConfig:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON field {key}')
            result[key] = value
        return result
    return FuelSelectionConfig.from_dict(json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique))


def classify_groups(config: FuelSelectionConfig, *, descriptor, descriptor_sha256, model_desc,
                    variant, parts, additional_parts, gas_trucks, company_uids=(), garage_indices=()):
    """Return explainable per-truck decisions after structural graph validation.

    A source pin mismatch blocks a previously reviewed layout instead of quietly
    turning it into an uncertain inclusion. Company links establish context only.
    """
    candidates = [rule for rule in config.rules if rule.descriptor == descriptor
                  and (rule.company_linked is None or rule.company_linked == bool(company_uids))]
    matching = [rule for rule in candidates if rule.model_desc == model_desc
                and rule.variant == variant and rule.parts == tuple(parts)
                and rule.additional_parts == tuple(additional_parts)]
    if candidates and not matching:
        raise ValueError('Reviewed fuel layout model/variant/parts drift; refusing stale classification')
    if any(rule.descriptor_sha256 != descriptor_sha256 for rule in matching):
        raise ValueError('Reviewed fuel descriptor SHA256 drift; refusing stale classification')
    rule = matching[0] if matching else None
    roles = {group.spawn_index: group for group in rule.groups} if rule else {}
    indices = {spawn['index'] for spawn in gas_trucks}
    if set(roles) - indices:
        raise ValueError('Reviewed fuel rule references a non-truck GAS spawn index')
    results = []
    for spawn in gas_trucks:
        index = spawn['index']; group = roles.get(index)
        if group:
            role, confidence, reason, evidence = group.role, group.confidence, group.reason, group.evidence
        elif index in garage_indices:
            role, confidence = 'fleet_yard', 'medium'
            reason = 'Garage FuelPump is an original garage facility; no public car-fueling review'
            evidence = 'Observed locally: linked FuelPump map item kind 0x23 (garage facility)'
        else:
            role, confidence = 'uncertain', 'low'
            reason = 'No reviewed source-pinned rule establishes pump suitability'
            evidence = ('Observed locally: same-parent Company link establishes company context, not ownership'
                        if company_uids else 'Unknown: public/private pump suitability')
        selected = role == 'public_car' or (role == 'uncertain' and config.unknown == 'include')
        results.append({'spawn_index': index, 'role': role, 'confidence': confidence,
                        'reason': reason, 'evidence': evidence, 'selected_for_addition': selected,
                        'decision': 'include' if selected else 'skip', 'rule_id': rule.id if group else None,
                        'same_parent_company_uids': [hex(uid) for uid in company_uids]})
    return results
