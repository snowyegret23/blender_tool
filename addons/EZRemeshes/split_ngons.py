import bmesh
from mathutils.geometry import tessellate_polygon


def admissible_diagonals(face):
    """Return all diagonals on convex faces, tessellation diagonals otherwise."""
    verts = list(face.verts)
    count = len(verts)
    if not face.normal.length_squared or not face.calc_area():
        return []
    # Convexity in a projection perpendicular to the dominant normal axis.
    axis = max(range(3), key=lambda i: abs(face.normal[i]))
    x, y = (axis + 1) % 3, (axis + 2) % 3
    turns = []
    for i, vert in enumerate(verts):
        a = vert.co - verts[i - 1].co
        b = verts[(i + 1) % count].co - vert.co
        turns.append(a[x] * b[y] - a[y] * b[x])
    if all(t > 0 for t in turns) or all(t < 0 for t in turns):
        return [(i, j) for i in range(count) for j in range(i + 2, count)
                if (i, j) != (0, count - 1)]
    triangles = tessellate_polygon([[v.co.copy() for v in verts]])
    diagonals = set()
    for triangle in triangles:
        for i, j in zip(triangle, triangle[1:] + triangle[:1]):
            i, j = sorted((i, j))
            if 1 < j - i < count - 1:
                diagonals.add((i, j))
    return sorted(diagonals)


def split_face(bm, face, far):
    verts = list(face.verts)
    candidates = admissible_diagonals(face)
    candidates.sort(key=lambda pair: (verts[pair[0]].co - verts[pair[1]].co).length_squared,
                    reverse=far)
    for i, j in candidates:
        a, b = verts[i], verts[j]
        if bm.edges.get((a, b)) or (a.co - b.co).length_squared == 0:
            continue
        try:
            new_face, _ = bmesh.utils.face_split(face, a, b)
        except ValueError:
            continue
        if new_face is not None:
            face.normal_update()
            new_face.normal_update()
            return new_face
    return None


class SplitNgons:
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH' or not obj.is_editable or not obj.data.is_editable:
            return False
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def execute(self, context):
        obj = context.active_object
        if obj.data.users > 1 + int(obj.data.use_fake_user):
            self.report({'WARNING'}, "Make the mesh single-user before splitting n-gons")
            return {'CANCELLED'}
        edit = obj.mode == 'EDIT'
        bm = bmesh.from_edit_mesh(obj.data) if edit else bmesh.new()
        try:
            if not edit:
                bm.from_mesh(obj.data)
            bm.normal_update()
            # Preserve the original whole-object behavior in Object Mode.
            # Edit Mode restricts the operation to selected, visible faces.
            todo = [f for f in bm.faces if len(f.verts) > 4 and not f.hide
                    and (not edit or f.select)]
            splits = skipped = 0
            while todo:
                face = todo.pop()
                new_face = split_face(bm, face, self.far)
                if new_face is None:
                    skipped += 1
                    continue
                if edit:
                    face.select_set(True)
                    new_face.select_set(True)
                splits += 1
                todo.extend(f for f in (face, new_face) if len(f.verts) > 4)

            if splits:
                if edit:
                    bm.select_flush_mode()
                    bmesh.update_edit_mesh(obj.data, loop_triangles=True, destructive=True)
                else:
                    bm.to_mesh(obj.data)
                    obj.data.update()
        finally:
            if not edit:
                bm.free()
        if skipped:
            self.report({'WARNING'}, f"Inserted {splits} diagonals; skipped {skipped} n-gon(s) without a usable split")
        elif splits:
            self.report({'INFO'}, f"Inserted {splits} diagonals")
        else:
            self.report({'INFO'}, "No n-gons to split (select faces in Edit Mode)")
        return {'FINISHED'} if splits else {'CANCELLED'}
