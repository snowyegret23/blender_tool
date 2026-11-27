# EZLoopTools

Install and enable [LoopTools](https://extensions.blender.org/add-ons/looptools/). In Mesh Edit Mode, select faces on one mesh and click **Apply** in the **EZLooptools** sidebar tab.

- **All Loops** follows edge loops in quad topology within the selected faces. Paths end at irregular topology rather than guessing which way to continue.
- **Selection Boundary** processes only the outline of the selected faces.

Choose **Flatten**, **Relax**, or **Space**. Short paths are skipped. The original selection, selection mode, and active face are restored afterward.
