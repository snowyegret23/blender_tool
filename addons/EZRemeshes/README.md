# EZRemeshes

Use **Split N-gons (Far)** or **Split N-gons (Close)** in the **EZRemeshes** sidebar tab. Both split faces with more than four sides without creating new vertices:

- **Far** tries a longer diagonal first.
- **Close** tries a shorter diagonal first.

In Object Mode this processes the active mesh; in Edit Mode it processes selected, visible faces only. Concave faces use valid candidate diagonals from a tessellation to avoid cutting outside the face. Faces with no usable split are reported and left alone. Triangles, quads, and the current mode are preserved.
