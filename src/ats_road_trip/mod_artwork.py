"""Select reviewed, map-labelled artwork without runtime image generation."""
from pathlib import Path
import re


def map_icon(root, map_name, topics):
    folder = Path(root) / 'assets/mod-icons'
    slug = re.sub(r'[^a-z0-9]+', '-', map_name.lower()).strip('-')
    # Generic regional names can identify unrelated maps, not these sources.
    if slug in {'alaska', 'western-canada'}:
        return None
    selected = frozenset(topics)
    if selected == {'fuel', 'rest'}:
        candidate = folder / 'map-compatibility' / (slug + '.jpg')
    elif selected == {'fuel'}:
        slug = {'reforma-othermaps-patch': 'reforma',
                'western-canada-promods-connections': 'western-canada-expansion'}.get(slug, slug)
        candidate = folder / (slug + '-c.jpg')
    else:
        return None
    return candidate if candidate.is_file() else None


def courier_icon(root):
    candidate = Path(root) / 'assets/mod-icons/job-types-compat-mustang.jpg'
    return candidate if candidate.is_file() else None
