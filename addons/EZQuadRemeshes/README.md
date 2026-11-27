# EZQuadRemeshes

In Object Mode, select a single-user mesh and click **Quad Remesh** in the **EZQuadRemeshes** sidebar tab. Set an approximate face count and, optionally, smoothing iterations. **Preserve Boundary** and **Preserve Sharp** are passed to QuadriFlow; the additional smoothing leaves output boundary vertices and marked sharp edges fixed when requested.

QuadriFlow replaces the active mesh topology. Duplicate the object first if you need to keep the original topology, UVs, or other mesh data. Meshes with shape keys are blocked. Existing object modifiers are not applied or changed.
