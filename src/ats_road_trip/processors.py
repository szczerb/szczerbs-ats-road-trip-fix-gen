"""Configurable map-wide compatibility planners and safe resource composition."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
import re
from typing import Iterable

from .fuel_selection import FuelSelectionConfig
from .package import ResourceStack
from .petrol_policy import DEFAULT_REFERENCE, build_policy
from .petrol_prices import plan_petrol_prices


class Processor(str, Enum):
    FUEL = 'fuel'
    REST = 'rest'
    COURIER = 'courier'


class ParkingStrategy(str, Enum):
    NONE = 'none'
    TRUCK_AREAS = 'truck_areas'
    STATION_BAYS = 'station_bays'


class CompatibilityPreset(str, Enum):
    BROAD = 'broad'
    REALISTIC = 'realistic'


class ProcessorMode(str, Enum):
    GENERATE = 'generate'
    ANALYZE = 'analyze'


@dataclass(frozen=True)
class ProcessorConfig:
    """The ordered, independent fixes selected for one source map."""

    enabled: tuple[Processor, ...] = (Processor.FUEL,)
    rest_radius: float = 1000
    petrol_reference: str = DEFAULT_REFERENCE
    mode: ProcessorMode = ProcessorMode.GENERATE
    fuel_selection: FuelSelectionConfig = FuelSelectionConfig()
    parking_strategy: ParkingStrategy | None = None
    improve_existing_car_parking: bool = False

    def __post_init__(self) -> None:
        selected = tuple(Processor(value) for value in self.enabled)
        if not selected:
            raise ValueError('Select at least one map fix processor')
        if len(selected) != len(set(selected)):
            raise ValueError('Map fix processors must not be repeated')
        mode = ProcessorMode(self.mode)
        if Processor.COURIER in selected and mode is ProcessorMode.GENERATE:
            raise ValueError('Courier Jobs map-wide generation is not implemented')
        if isinstance(self.rest_radius, bool) or not isinstance(self.rest_radius, (int, float)) or not math.isfinite(self.rest_radius) or self.rest_radius < 0:
            raise ValueError('Rest radius must be a nonnegative finite coordinate distance')
        if not isinstance(self.fuel_selection, FuelSelectionConfig):
            raise ValueError('fuel_selection must be a FuelSelectionConfig')
        if Processor.FUEL not in selected and self.fuel_selection != FuelSelectionConfig():
            raise ValueError('Selective fuel configuration requires the fuel processor')
        parking = (ParkingStrategy.TRUCK_AREAS if Processor.REST in selected else ParkingStrategy.NONE
                   ) if self.parking_strategy is None else ParkingStrategy(self.parking_strategy)
        if (Processor.REST in selected) != (parking is not ParkingStrategy.NONE):
            raise ValueError('Select exactly one parking strategy with the rest processor, or none without it')
        if type(self.improve_existing_car_parking) is not bool:
            raise ValueError('improve_existing_car_parking must be a boolean')
        if self.improve_existing_car_parking and parking is not ParkingStrategy.STATION_BAYS:
            raise ValueError('Improving existing car parking requires rest with station_bays')
        object.__setattr__(self, 'parking_strategy', parking)
        object.__setattr__(self, 'enabled', selected)
        object.__setattr__(self, 'mode', mode)

    @classmethod
    def from_preset(cls, preset, **overrides):
        preset = CompatibilityPreset(preset)
        enabled = overrides.pop('enabled', (Processor.FUEL, Processor.REST))
        selection = (FuelSelectionConfig(mode='realistic', unknown='include', classifier='facilities')
                     if preset is CompatibilityPreset.REALISTIC and Processor.FUEL in tuple(Processor(value) for value in enabled)
                     else FuelSelectionConfig())
        parking = (ParkingStrategy.STATION_BAYS if preset is CompatibilityPreset.REALISTIC
                   else ParkingStrategy.TRUCK_AREAS)
        if Processor.REST not in tuple(Processor(value) for value in enabled):
            parking = ParkingStrategy.NONE
        return cls(enabled=tuple(enabled), fuel_selection=overrides.pop('fuel_selection', selection),
                   parking_strategy=overrides.pop('parking_strategy', parking), **overrides)

    @classmethod
    def from_names(cls, names: Iterable[str | Processor], **kwargs) -> ProcessorConfig:
        return cls(tuple(Processor(name) for name in names), **kwargs)


@dataclass
class PipelineResult:
    reports: dict[str, dict]
    resources: dict[str, bytes]
    blockers: list[dict]
    coverage: dict


def _fuel_plan(effective: ResourceStack, game_only: ResourceStack, *,
               source: str, map_name: str, petrol_reference: str,
               fuel_selection: FuelSelectionConfig = FuelSelectionConfig()) -> tuple[dict, dict[str, bytes]]:
    # Imported at call time so the legacy planner remains an independent unit
    # and can be substituted by focused tests or future planner revisions.
    from .bulk_fuel import plan_map_fuel

    report, station_resources = plan_map_fuel(effective,
                                              map_packages={source}, map_name=map_name,
                                              **({'fuel_selection': fuel_selection}
                                                 if fuel_selection != FuelSelectionConfig() else {}))
    policy, policy_report = build_policy(effective, game_only,
                                         target_packages={source},
                                         reference_path=petrol_reference)
    price_report, price_resources = plan_petrol_prices(effective,
                                                       target_packages={source},
                                                       policy=policy)
    price_report['policy'] = policy_report
    report['petrol_prices'] = price_report
    coverage = report.setdefault('coverage', {})
    blockers = list(coverage.get('blockers', report.get('blockers', [])))
    blockers.extend({'area': 'petrol_price_policy', **blocker}
                    for blocker in policy_report['coverage']['blockers'])
    blockers.extend({'area': 'petrol_prices', **blocker}
                    for blocker in price_report['coverage']['blockers'])
    conflicts = sorted(set(station_resources) & set(price_resources))
    blockers.extend({'area': 'resource_collision', 'path': path,
                     'reason': 'station and price planners emitted the same path'}
                    for path in conflicts)
    coverage['blockers'] = blockers
    coverage['complete'] = not blockers
    coverage['petrol_price_changed'] = price_report['coverage']['changed']
    return report, {**station_resources, **price_resources}


def run_processors(effective: ResourceStack, game_only: ResourceStack, *,
                   source: str, map_name: str, config: ProcessorConfig) -> PipelineResult:
    """Plan all requested fixes, refusing unacknowledged output collisions.

    Rest consumes the complete fuel overlay when both are enabled. Its planner
    must declare every overlapping resource it intentionally composed before
    its final bytes may replace an earlier processor's bytes.
    """
    reports: dict[str, dict] = {}
    resources: dict[str, bytes] = {}
    blockers: list[dict] = []
    transitions: list[tuple[str, str, bytes, bytes]] = []
    # Canonical order makes output identical even when callers specify a
    # different selection order. Fuel's edits are available to the rest pass.
    for processor in (Processor.FUEL, Processor.REST, Processor.COURIER):
        if processor not in config.enabled:
            continue
        if processor is Processor.FUEL:
            report, changes = _fuel_plan(effective, game_only, source=source,
                                         map_name=map_name,
                                         petrol_reference=config.petrol_reference,
                                         **({'fuel_selection': config.fuel_selection}
                                            if config.fuel_selection != FuelSelectionConfig() else {}))
        elif processor is Processor.REST:
            if config.parking_strategy is ParkingStrategy.STATION_BAYS:
                from .resource_overlay import OverlayResourceStack
                from .station_parking.mapwide import plan_map_station_parking
                staged = OverlayResourceStack(effective, resources)
                report, changes = plan_map_station_parking(staged, map_packages={source},
                    map_name=map_name, ownership_stack=effective,
                    improve_existing_car_parking=config.improve_existing_car_parking)
                # This pipeline emits the authoritative context lineage once,
                # after fuel and parking transitions have both been recorded.
                changes={path:data for path,data in changes.items()
                         if not re.fullmatch(r'def/data_context(?:\.[^/]+)?\.sii',path)}
            else:
                from .rest_stops import plan_rest_stops
                report, changes = plan_rest_stops(effective, map_packages={source},
                                                  map_name=map_name,
                                                  radius=config.rest_radius,
                                                  resource_overrides=dict(resources))
        else:
            from .courier_locations import plan_courier_report
            report = plan_courier_report(effective, map_packages={source}, map_name=map_name)
            changes = {}
        reports[processor.value] = report
        processor_coverage = report.get('coverage', {})
        reported_blockers = processor_coverage.get('blockers', report.get('blockers', []))
        blockers.extend({'processor': processor.value, **blocker}
                        for blocker in reported_blockers)
        if processor_coverage.get('complete') is False and not reported_blockers:
            blockers.append({'processor': processor.value, 'area': 'coverage',
                             'reason': 'planner reported incomplete coverage without a specific blocker'})
        composed = set(report.get('composed_resource_paths', [])) if processor is Processor.REST else set()
        for path in sorted(set(resources) & set(changes)):
            if path not in composed:
                blockers.append({'processor': processor.value, 'area': 'resource_collision',
                                 'path': path,
                                 'reason': 'processors emitted the same path without an explicit composed overlay'})
        if processor in (Processor.FUEL, Processor.REST) and effective is not None:
            for path, after in sorted(changes.items()):
                if not path.startswith('map/') or not path.endswith(('.base', '.aux')):
                    continue
                if path not in resources and path not in effective.resources:
                    # A planner may emit a new sector. If it also emits a
                    # private prefab alias, the context audit below will
                    # block that unproven alias before packaging.
                    continue
                before = resources[path] if path in resources else effective.read(path, max_bytes=64*1024*1024)
                transitions.append((processor.value, path, before, after))
        resources.update(changes)
    if config.mode is ProcessorMode.GENERATE and any(p in config.enabled for p in (Processor.FUEL, Processor.REST)):
        from .prefab_contexts import plan_prefab_contexts
        context_report, context_resources = plan_prefab_contexts(
            effective, resources, transitions, source=source, map_name=map_name)
        reports['context_preservation'] = context_report
        blockers.extend({'processor': 'context_preservation', **blocker}
                        for blocker in context_report['coverage']['blockers'])
        for path in context_resources:
            if path in resources:
                blockers.append({'processor': 'context_preservation', 'area': 'resource_collision',
                                 'path': path, 'reason': 'Context planner output collides with processor output'})
        resources.update(context_resources)
    coverage = {'complete': not blockers, 'blockers': blockers,
                'planned_resource_count': len(resources)}
    return PipelineResult(reports, resources, blockers, coverage)
