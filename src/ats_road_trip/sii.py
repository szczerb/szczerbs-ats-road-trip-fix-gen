"""Small read-only SII reader for the definition shapes used by this prototype.

This is not an engine serializer. It handles comments, quoted strings, includes,
units, and line-oriented attributes; it never rewrites original definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import PurePosixPath
import re
from typing import Callable


class DefinitionError(ValueError):
    """Definition syntax or include resolution is unsupported or invalid."""


_LEXEMES = re.compile(r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*|\#[^\n]*', re.S)
_HEADER = re.compile(r'\b([a-zA-Z_][\w]*)\s*:\s*([.\w]+)\s*\{')
_ATTRIBUTE = re.compile(r'\b([a-zA-Z_]\w*)(?:\[(\d*)\])?\s*:')
_INCLUDE = re.compile(r'^@include\s+"([^"\n]+)"\s*$', re.M)


def strip_comments(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        value = match.group()
        return value if value.startswith('"') else re.sub(r'[^\n]', ' ', value)
    return _LEXEMES.sub(replace, text)


@dataclass(frozen=True)
class Unit:
    kind: str
    name: str
    attributes: dict[str, tuple[str, ...]]
    source: str
    attribute_errors: dict[str, str] = field(default_factory=dict)

    def values(self, name: str) -> tuple[str, ...]:
        if name in self.attribute_errors:
            raise DefinitionError(self.attribute_errors[name])
        return self.attributes.get(name, ())

    def one(self, name: str, default: str | None = None) -> str | None:
        values = self.values(name)
        if len(values) > 1:
            raise DefinitionError(f'{self.source}: {self.name}.{name} is not scalar')
        return values[0] if values else default


def _unquote(value: str) -> str:
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise DefinitionError(f'Unsupported quoted SII value: {value!r}') from exc
        if not isinstance(decoded, str):
            raise DefinitionError('Expected a string')
        return decoded
    return value


def parse_units(text: str, *, source: str = '<text>',
                include_reader: Callable[[str], str] | None = None,
                _stack: tuple[str, ...] = ()) -> list[Unit]:
    """Read units; include paths are relative virtual paths, resolved by caller."""
    if source in _stack or len(_stack) >= 32:
        raise DefinitionError(f'Include cycle or depth limit at {source}')
    clean = strip_comments(text.lstrip('\ufeff'))

    def include(match: re.Match[str]) -> str:
        if include_reader is None:
            raise DefinitionError(f'{source}: @include requires a source reader')
        requested = match.group(1)
        base = PurePosixPath(source).parent
        virtual = str(base / requested) if not requested.startswith('/') else requested.lstrip('/')
        # Keep includes inside the mounted resource root, while allowing ../.
        parts: list[str] = []
        for part in PurePosixPath(virtual).parts:
            if part == '..':
                if not parts:
                    raise DefinitionError(f'{source}: include escapes resource root')
                parts.pop()
            elif part not in ('', '.'):
                parts.append(part)
        path = '/'.join(parts)
        content = include_reader(path)
        return _expand_includes(content, path, include_reader, (*_stack, source))

    clean = _INCLUDE.sub(include, clean)
    if '@include' in _mask_strings(clean):
        raise DefinitionError(f'{source}: unsupported @include syntax')
    return _parse_clean(clean, source)


def _expand_includes(text: str, source: str, reader: Callable[[str], str],
                     stack: tuple[str, ...]) -> str:
    if source in stack or len(stack) >= 32:
        raise DefinitionError(f'Include cycle or depth limit at {source}')
    clean = strip_comments(text.lstrip('\ufeff'))
    def replace(match: re.Match[str]) -> str:
        # Reuse the public resolver for normalization; no units are needed here.
        capture: list[str] = []
        def capture_reader(path: str) -> str:
            capture.append(path)
            return ''
        parse_units(match.group(), source=source, include_reader=capture_reader)
        path = capture[0]
        return _expand_includes(reader(path), path, reader, (*stack, source))
    clean = _INCLUDE.sub(replace, clean)
    if '@include' in _mask_strings(clean):
        raise DefinitionError(f'{source}: unsupported @include syntax')
    return clean


def _mask_strings(text: str) -> str:
    return re.sub(r'"(?:\\.|[^"\\])*"', lambda m: ' ' * len(m.group()), text)


def _parse_clean(clean: str, source: str) -> list[Unit]:
    masked = _mask_strings(clean)
    depth = 0
    for char in masked:
        depth += (char == '{') - (char == '}')
        if depth < 0:
            raise DefinitionError(f'{source}: unbalanced braces')
    if depth:
        raise DefinitionError(f'{source}: unbalanced braces')
    result: list[Unit] = []
    seen: set[str] = set()
    position = 0
    while match := _HEADER.search(masked, position):
        start = match.end()
        depth = 1
        end = start
        while depth and end < len(masked):
            depth += (masked[end] == '{') - (masked[end] == '}')
            end += 1
        body = clean[start:end - 1]
        if '{' in _mask_strings(body) or '}' in _mask_strings(body):
            raise DefinitionError(f'{source}: nested units are unsupported')
        kind, name = match.groups()
        if name in seen:
            raise DefinitionError(f'{source}: duplicate unit {name}')
        seen.add(name)
        raw: dict[str, list[tuple[str | None, str]]] = {}
        starts = list(_ATTRIBUTE.finditer(_mask_strings(body)))
        for index, attr in enumerate(starts):
            key, array_index = attr.groups()
            end_value = starts[index + 1].start() if index + 1 < len(starts) else len(body)
            value = body[attr.end():end_value].strip()
            if not value:
                raise DefinitionError(f'{source}: empty attribute {key}')
            raw.setdefault(key, []).append((array_index, _unquote(value)))
        attributes: dict[str, list[str]] = {}
        attribute_errors: dict[str, str] = {}
        for key, pairs in raw.items():
            indexed = [(int(i), v) for i, v in pairs if i not in (None, '')]
            if indexed:
                scalars = [v for i, v in pairs if i is None]
                if any(i == '' for i, _ in pairs) or len(scalars) > 1:
                    attribute_errors[key] = f'{source}: mixed array forms for {key}'
                if sorted(i for i, _ in indexed) != list(range(len(indexed))):
                    attribute_errors[key] = f'{source}: missing/duplicate array index for {key}'
                if scalars and scalars != [str(len(indexed))]:
                    # Some installed SCS prefab units have inconsistent corner
                    # array counts. Preserve the unrelated unit fields, but fail
                    # if a caller tries to interpret that ambiguous attribute.
                    attribute_errors[key] = f'{source}: {name}.{key} array count disagrees: {scalars} vs {len(indexed)} entries'
                attributes[key] = [v for _, v in sorted(indexed)]
            else:
                attributes[key] = [v for _, v in pairs]
        result.append(Unit(kind, name, {k: tuple(v) for k, v in attributes.items()}, source, attribute_errors))
        position = end
    return result
