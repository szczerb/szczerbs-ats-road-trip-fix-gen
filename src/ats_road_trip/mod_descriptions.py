"""Player-facing descriptions for the experimental ATS 1.61 packages."""

from __future__ import annotations

import math


_STACK = (
    ('Alaska Expansion', 'Alaska Expansion'),
    ('Western Canada ProMods Connections', 'Western Canada ProMods Connections'),
    ('Reforma OtherMaps Patch', 'Reforma OtherMaps Patch'),
    ('ProMods Canada', 'ProMods Canada Map Package'),
    ('Western Canada Expansion', 'Western Canada Expansion'),
    ('ATS Expansion', 'ATS Expansion'),
    ('Reforma', 'Reforma'),
)
_KNOWN_NAMES = {name.casefold(): name for name, _ in _STACK}


def _load_order(map_name: str) -> str:
    known = _KNOWN_NAMES.get(map_name.casefold())
    lines = [
        'Load order for the supplied ATS 1.61 map combination (top to bottom). '
        'Enable only fixes for maps and connectors you use:',
        'North America Background Map (optional)',
        'Job Types Compat Mustang',
        'Food Courier Jobs, Medical Courier Jobs, Rideshare Jobs (optional)',
    ]
    for fix, source in _STACK:
        marker = ' (THIS MOD)' if fix == known else ''
        lines.append(f'{fix} fix{marker}')
        lines.append(source)
        if fix == 'Reforma OtherMaps Patch':
            lines.append('ProMods Canada Definition Package')
        elif fix == 'ProMods Canada':
            lines.extend(('ProMods Canada Assets Package', 'ProMods Canada Models Package'))
    lines.append('Reforma Mega Resources')
    if known is None:
        return (f'Place (THIS MOD) directly above {map_name}. The following is the '
                'supplied map combination as an example; use only the entries that match '
                'your installed maps.\n' + '\n'.join(lines))
    return '\n'.join(lines)


def map_description(
    map_name: str,
    topics: tuple[str, ...] = ('fuel', 'rest'),
    *,
    version: str = '1.61-r9-experimental',
    rest_radius: int = 1000,
) -> str:
    """Describe a map package without claiming untested gameplay results."""
    if not map_name or not map_name.strip():
        raise ValueError('map_name must be nonempty')
    selected = frozenset(topics)
    if not selected or selected - {'fuel', 'rest'}:
        raise ValueError('topics must contain fuel, rest, or both')
    if isinstance(rest_radius, bool) or not isinstance(rest_radius, (int, float)) or not math.isfinite(rest_radius) or rest_radius < 0:
        raise ValueError('rest_radius must be finite and nonnegative')

    name = map_name.strip()
    paragraphs = [f'Road Trip compatibility for {name}\nVersion: {version}']
    if name.casefold() == 'reforma othermaps patch':
        paragraphs.append(
            'Fills in missing petrol prices for countries covered by this patch. '
            'The inspected OtherMaps Patch has no fuel station or rest area edits.'
        )
    else:
        if 'fuel' in selected:
            paragraphs.append(
                'Lets passenger cars refuel at supported truck fuel points while '
                'keeping the original truck interactions. Missing petrol prices use '
                'available map prices where possible or an experimental estimate. '
                'Check the displayed price, quantity, and bill in game.'
            )
        if 'rest' in selected:
            paragraphs.append(
                'Adds passenger-car rest access where the inspected nearby area has no '
                f'existing car rest within {rest_radius:,g} game-world units. '
                'Existing truck and bus rest access stays in place. Check parking icons, rest prompts '
                'and fatigue recovery in game.'
            )
    paragraphs.append(_load_order(name))
    if name.casefold() == 'reforma othermaps patch':
        checks = 'Petrol display and billing still need in-game confirmation.'
    elif selected == {'fuel'}:
        checks = 'Refueling, petrol display, and billing still need in-game confirmation.'
    elif selected == {'rest'}:
        checks = 'Parking icons, rest prompts and fatigue recovery still need in-game confirmation.'
    else:
        checks = ('Refueling, petrol display, billing, parking icons, rest prompts, and fatigue '
                  'recovery still need in-game confirmation.')
    paragraphs.append('Test with a copy of your profile. ' + checks)
    return '\n\n'.join(paragraphs) + '\n'


def courier_description(
    selected_job_count: int = 58,
    transfer_count: int = 9,
    *,
    version: str = '1.61-r3-experimental',
) -> str:
    """Describe the source-pinned Job Types Compat Mustang eligibility package."""
    if selected_job_count < 0 or transfer_count < 0:
        raise ValueError('definition counts must be nonnegative')
    paragraphs = [
        f'Job Types Compat Mustang\nVersion: {version}',
        f'Opens {selected_job_count} additional reviewed courier job types from the '
        'base game to your own Mustang. Also affects other cars in the same '
        'vehicle class and Quick Jobs. '
        f'All {transfer_count} vehicle-transfer jobs stay unchanged.',
        'LOAD ORDER (top to bottom):\nNorth America Background Map (if used)\n'
        'Job Types Compat Mustang (THIS MOD)\n'
        'Food Courier Jobs / Medical Courier Jobs / Rideshare Jobs (if used)\n'
        'Your map mods and their matching fixes\n\n'
        'Other mods replacing the base-game car job list require a compatibility check. '
        'Food Courier Jobs, Medical Courier Jobs, and Rideshare Jobs add their own '
        'jobs; this mod does not change their eligibility rules.',
        'Driver rating and job-list refresh still affect which offers appear. '
        'Does not change ratings, rewards or trip lengths. '
        'Experimental: please test pickup, cargo fit and completed delivery.',
    ]
    return '\n\n'.join(paragraphs) + '\n'
