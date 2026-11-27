# Blender Tools

Five independently installable extensions for Blender **5.2 LTS**. Tested with Blender **5.2.5 LTS** on Linux.

| Extension | What it does |
| --- | --- |
| [EZDeleteChildBone](addons/EZDeleteChildBone/) | Delete unselected descendant bones without deleting the selected bones. |
| [EZLoop](addons/EZLoop/) | Run LoopTools Flatten, Relax, or Space from the sidebar. |
| [EZLoopTools](addons/EZLoopTools/) | Run LoopTools on edge paths through selected faces, or just their boundary. |
| [EZQuadRemeshes](addons/EZQuadRemeshes/) | Run QuadriFlow and optionally smooth the output without touching existing modifiers. |
| [EZRemeshes](addons/EZRemeshes/) | Split n-gons into triangles and quads using long or short diagonals. |

## Installation

1. Disable any legacy copy of the same add-on before installing its replacement. They use the same operator IDs.
2. In Blender, choose **Edit → Preferences → Get Extensions → ▾ → Install from Disk**. Install each extension ZIP separately. Do not unzip the individual extension ZIPs.
3. For **EZLoop** and **EZLoopTools** only, install and enable the [LoopTools extension](https://extensions.blender.org/add-ons/looptools/) from Get Extensions.
4. Open the 3D Viewport sidebar with **N** and select the extension's tab.

To build the ZIPs from source, run this from the repository root with Python 3.11 or later:

```sh
python scripts/build_extensions.py --blender /path/to/blender
```

The builder writes and validates the five ZIPs in `dist/`.

## Testing

Run the source smoke tests against a clean Blender profile:

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/smoke.py
```

That run tests the fallback when LoopTools is absent. To test ZIP installation and the real LoopTools geometry operations, install and enable the five built ZIPs plus LoopTools in a test Blender profile, then run:

```sh
blender --background --python-exit-code 1 --python tests/smoke.py -- --installed --require-looptools
```

## History and licenses

The five original repositories were consolidated here. Each add-on retains its license and original default-branch history in this repository.
