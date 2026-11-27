from collections import defaultdict

import bmesh
import bpy
from bpy.types import Operator


def edge_paths(edges, continuation):
    """Connected pieces of mutually paired edges, in stable mesh index order."""
    remaining = set(edges)
    for seed in sorted(edges, key=lambda edge: edge.index):
        if seed not in remaining:
            continue
        remaining.remove(seed)
        path = [seed]
        for edge in path:
            for vert in edge.verts:
                other = continuation(edge, vert)
                if other in remaining:
                    remaining.remove(other)
                    path.append(other)
        yield sorted(edge.index for edge in path)


def selected_paths(faces, scope):
    if scope == 'BOUNDARY':
        counts = defaultdict(int)
        for face in faces:
            for edge in face.edges:
                if not edge.hide:
                    counts[edge] += 1
        edges = {edge for edge, count in counts.items() if count == 1}
        at_vertex = defaultdict(list)
        for edge in edges:
            for vert in edge.verts:
                at_vertex[vert].append(edge)

        def continuation(edge, vert):
            linked = at_vertex[vert]
            if len(linked) == 2:
                return linked[1] if linked[0] == edge else linked[0]

    else:
        edges = {edge for face in faces for edge in face.edges if not edge.hide}

        def continuation(edge, vert):
            linked = vert.link_edges
            quads = all(len(face.verts) == 4 for face in vert.link_faces)
            if not quads:
                return None
            if edge.is_boundary:
                boundary = [other for other in linked if other.is_boundary]
                if len(boundary) == 2 and len(linked) == len(vert.link_faces) + 1:
                    return boundary[1] if boundary[0] == edge else boundary[0]
            if len(linked) == 4 and all(other.is_manifold for other in linked):
                adjacent = set(edge.link_faces)
                return next((other for other in linked
                             if not adjacent.intersection(other.link_faces)), None)
            return None

    return list(edge_paths(edges, continuation))


class EZLOOPTOOLS_OT_Operation(Operator):
    bl_idname = "mesh.ezlooptools_operation"
    bl_label = "Apply LoopTools to Selected Faces"
    bl_description = "Run LoopTools on each edge path within the selected faces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            cls.poll_message_set("Enter Mesh Edit Mode and select faces")
            return False
        if len(context.objects_in_mode_unique_data) != 1:
            cls.poll_message_set("Edit one mesh at a time")
            return False
        return True

    def execute(self, context):
        operation = context.scene.ezlooptools_operation
        operator = getattr(bpy.ops.mesh, f"looptools_{operation.lower()}")
        try:
            operator.get_rna_type()
        except (KeyError, RuntimeError):
            self.report({'WARNING'}, "Install and enable the LoopTools extension in Preferences")
            return {'CANCELLED'}

        mesh = context.edit_object.data
        bm = bmesh.from_edit_mesh(mesh)
        faces = [face for face in bm.faces if face.select and not face.hide]
        if not faces:
            self.report({'WARNING'}, "Select faces first in Mesh Edit Mode")
            return {'CANCELLED'}

        bm.edges.index_update()
        minimum_edges = 2 if operation == 'FLATTEN' else 3
        paths = [path for path in selected_paths(faces, context.scene.ezlooptools_direction)
                 if len(path) >= minimum_edges]
        if not paths:
            self.report({'WARNING'}, "No edge paths long enough for this operation")
            return {'CANCELLED'}

        select_mode = tuple(context.tool_settings.mesh_select_mode)
        saved = [[item.select for item in elements]
                 for elements in (bm.verts, bm.edges, bm.faces)]
        bm.faces.index_update()
        bm.verts.index_update()
        history = [(type(item), item.index) for item in bm.select_history]
        active_face = bm.faces.active.index if bm.faces.active else None
        completed = 0
        try:
            context.tool_settings.mesh_select_mode = (False, True, False)
            previous = None
            for path in paths:
                bm = bmesh.from_edit_mesh(mesh)
                bm.edges.ensure_lookup_table()
                if previous is None:
                    for elements in (bm.faces, bm.edges, bm.verts):
                        for item in elements:
                            item.select = False
                else:
                    for index in previous:
                        edge = bm.edges[index]
                        edge.select = False
                        for vert in edge.verts:
                            vert.select = False
                bm.select_history.clear()
                for index in path:
                    bm.edges[index].select_set(True)
                bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
                if not operator.poll():
                    break
                result = operator()
                if 'FINISHED' in result:
                    completed += 1
                previous = path
        except RuntimeError as error:
            self.report({'WARNING'}, str(error))
        finally:
            context.tool_settings.mesh_select_mode = select_mode
            bm = bmesh.from_edit_mesh(mesh)
            elements = (bm.verts, bm.edges, bm.faces)
            for sequence, flags in zip(elements, saved):
                sequence.ensure_lookup_table()
                for item, flag in zip(sequence, flags):
                    item.select = flag
            bm.select_history.clear()
            sequence_by_type = dict(zip((bmesh.types.BMVert, bmesh.types.BMEdge,
                                         bmesh.types.BMFace), elements))
            for kind, index in history:
                bm.select_history.add(sequence_by_type[kind][index])
            bm.faces.active = bm.faces[active_face] if active_face is not None else None
            bmesh.update_edit_mesh(mesh, loop_triangles=True, destructive=False)

        if not completed:
            self.report({'WARNING'}, "LoopTools did not complete an operation")
            return {'CANCELLED'}
        self.report({'INFO'}, f"{operation.title()}: {completed}/{len(paths)} edge paths processed")
        return {'FINISHED'}
