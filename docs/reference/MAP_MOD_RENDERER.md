# ATS map-mod coverage and road images

Use the read-only renderer to inspect an archive's sector footprint, compare a connector with its expansions, or inspect which files win in a declared load order. The output is a PNG and a JSON summary. A comparison helps locate overlap and potential seams for inspection.

## Run the tool

Run these examples from the checkout root with Python 3.11+ and Pillow, which is included in the optional background dependencies. ZIP archives work directly. For HashFS, install the Linux Extractor described in the [tooling guide](TOOLING.md) or supply it with the global `--extractor` option before `render-map`.

Set `ATS_RENDER_ATLAS` to the original full-world PNG produced by the [r3 background generator](../examples/north-america-background/r3/README.md). Use its matching `config.json` with `--background-config`. The [r4 package repair](NORTH_AMERICA_BACKGROUND_1_61_R4.md) retains this artwork and registration. Use the full atlas from the generator output.

```sh
export PYTHONPATH=src
atlas_config=docs/examples/north-america-background/r3/config.json

# Set ATS_MAP, ATS_CONNECTOR, and ATS_RENDER_ATLAS to your inputs at runtime.
python3 -m ats_road_trip render-map "$ATS_MAP" \
  --background "$ATS_RENDER_ATLAS" --background-config "$atlas_config"

python3 -m ats_road_trip render-map --mode comparison "$ATS_MAP" "$ATS_CONNECTOR" \
  --background "$ATS_RENDER_ATLAS" --background-config "$atlas_config" \
  --name expansion-and-connector

# Pass selected mods from lowest to highest priority.
python3 -m ats_road_trip render-map --mode effective "$ATS_MAP" "$ATS_CONNECTOR" \
  --game-dir "$ATS_GAME_DIR" --background "$ATS_RENDER_ATLAS" \
  --background-config "$atlas_config" --name effective-stack
```

Supply additional packages with repeated `--dependency` flags in low-to-high order. These packages sit below the target archives. The standalone view draws the target's own roads, and the comparison draws each target's roads in its own color. Other selected archives are available as reference inputs in the comparison. The effective view applies load order per virtual resource, including each member of a sector, and draws nearby stock/DLC roads when an installed baseline is supplied. Set `--game-dir` or `ATS_GAME_DIR` for that baseline. Supply repeated `--dlc` options for a specific active DLC set. Without an explicit DLC list, the tool uses the DLC archives it finds in the supplied installation.

The renderer crops to the selected footprint with padding. Use `--bounds XMIN ZMIN XMAX ZMAX` to align the view with another image or inspect a seam. North is decreasing game Z. Use `--long-edge` to change the default 8,192-pixel image size. Each map namespace gets a separate image. The default output is in a Warsaw-timestamped ignored work directory. Use `--output-dir` and `--name` to choose a destination and basename for a batch. Existing outputs are protected from replacement.

## Read the images and summaries

- The shaded squares are the exact archive-supplied sector tiles. They include empty replacements, retain holes and detached tiles, and may contain unchanged roads. A paler tint indicates overlap with lower-priority sector data when a baseline is available. Gray areas outside the atlas retain their world coordinates.
- Solid lines are native road centerlines. Dashed lines are hidden roads. Light dotted segments mark a verified endpoint pair drawn without a supported curve or a prefab’s generated base links. Thin colored segments are authored prefab UI-map links. Authored road edges take precedence over generated base edges. Gray roads in an effective view come from the installed baseline.
- A colored corner mark flags a tile with a geometry diagnostic. The JSON includes road and prefab accounting, affected virtual members, reason codes, selected providers, and resources shadowed by a higher-priority archive. The effective view can have mixed providers inside one tile.
- `no_sector_geometry` is a clean skip with a summary and no PNG. `partial` supplies an image with reported limitations. `failed` means the requested view could not be produced, for example if an effective stack input is unreadable. An unsupported sector can still contribute to the footprint when its member name is readable.
- HashFS v1 deep discovery can return malformed path candidates. The renderer reports how many it discarded and only requests validated member paths. Archive generation and ordinary inspection retain strict discovery.
- Native map layouts and prefab versions have explicit parser limits. Prefab links describe the supported map-point graph. An incomplete dependency list can leave gaps even in an otherwise valid archive. Use the provider and omission records when examining a seam. Static geometry cannot establish runtime compatibility.

## Geometry evidence

**Documented** — The ATS editor derives road curvature from the direction of the road nodes. The renderer reconstructs centerlines from native endpoint quaternions and the serialized road length, using Hermite interpolation and bounded curve subdivision. [SCS road creation guide](https://modding.scssoft.com/wiki/Tutorials/Map_Editor/Roads/Creating_a_Simple_Road).

**Observed locally** — Native junction controls verify that supported prefab link endpoints meet the adjacent road endpoints. Tilted prefabs can use a checked 3D rigid placement when the planar check fails and the controls establish a unique fit.

**Observed locally** — Comparison with four registered ATS 1.61 road-mask screenshots supports the native-field reconstruction, especially on curved roads in the Yellowknife sample. This is a centerline comparison at sampled locations. [Upstream format research and provenance](../../THIRD_PARTY_NOTICES.md).

**Documented** — The prefab renderer reads reciprocal road links from the descriptor’s map-point graph. It excludes area polygons and styles generated base links as approximate where no authored road edges are available. [SCS prefab locator guide](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators), [SCS Blender Tools map-point exporter](https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/exp/pip/map_point.py).
