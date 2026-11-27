from array import array
from math import cos, radians

import bpy
from bpy.types import Operator


def smooth_mesh(mesh, iterations, preserve_boundary, preserve_sharp):
    """Relax interior vertices without applying or touching object modifiers."""
    count = len(mesh.vertices)
    neighbors = [[] for _ in range(count)]
    face_counts = [0] * len(mesh.edges)
    creases = set()
    if preserve_boundary or preserve_sharp:
        indices = array('i', [0]) * len(mesh.loops)
        mesh.loops.foreach_get("edge_index", indices)
        if preserve_sharp:
            first_face = [-1] * len(mesh.edges)
            normals = [face.normal.copy() for face in mesh.polygons]
            cutoff = cos(radians(45.0))
            for face in mesh.polygons:
                for j in face.loop_indices:
                    edge = indices[j]
                    if face_counts[edge] == 0:
                        first_face[edge] = face.index
                    elif face_counts[edge] == 1:
                        if normals[face.index].dot(normals[first_face[edge]]) < cutoff:
                            creases.add(edge)
                    face_counts[edge] += 1
        else:
            for edge in indices:
                face_counts[edge] += 1
    fixed = set()
    for edge in mesh.edges:
        a, b = edge.vertices
        neighbors[a].append(b)
        neighbors[b].append(a)
        if ((preserve_boundary and face_counts[edge.index] != 2)
                or (preserve_sharp and (edge.use_edge_sharp or edge.index in creases))):
            fixed.update((a, b))
    movable = [(i, adjacent, 0.5 / len(adjacent))
               for i, adjacent in enumerate(neighbors) if adjacent and i not in fixed]

    coords = array('f', [0]) * (count * 3)
    mesh.vertices.foreach_get("co", coords)
    for _ in range(iterations):
        result = coords[:]
        for i, adjacent, weight in movable:
            for axis in range(3):
                result[3 * i + axis] = (0.5 * coords[3 * i + axis]
                                         + weight * sum(coords[3 * j + axis] for j in adjacent))
        coords = result
    mesh.vertices.foreach_set("co", coords)
    mesh.update()


class EZQUADREMESHES_OT_remesh(Operator):
    bl_idname = "ezquadremeshes.remesh"
    bl_label = "Quad Remesh"
    bl_description = "Replace the active mesh with QuadriFlow quads; mesh data such as UVs can change"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if context.mode != 'OBJECT' or not obj or obj.type != 'MESH':
            cls.poll_message_set("Select a mesh in Object Mode")
            return False
        if not obj.is_editable or not obj.data.is_editable:
            cls.poll_message_set("The active mesh must be editable")
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        props = context.scene.ez_quadremeshes_props
        if obj.data.shape_keys:
            self.report({'WARNING'}, "Quad remeshing would discard shape keys; use a separate copy without them")
            return {'CANCELLED'}
        if obj.data.users > 1 + int(obj.data.use_fake_user):
            self.report({'WARNING'}, "Make the mesh single-user before remeshing")
            return {'CANCELLED'}
        if not obj.data.polygons:
            self.report({'WARNING'}, "The active mesh has no faces")
            return {'CANCELLED'}

        try:
            result = bpy.ops.object.quadriflow_remesh(
                mode='FACES',
                target_faces=props.target_faces,
                use_preserve_sharp=props.preserve_sharp,
                use_preserve_boundary=props.preserve_boundary,
                smooth_normals=True,
            )
        except RuntimeError as error:
            self.report({'WARNING'}, str(error))
            return {'CANCELLED'}
        if 'FINISHED' not in result:
            return result
        if props.smooth_iterations:
            smooth_mesh(obj.data, props.smooth_iterations,
                        props.preserve_boundary, props.preserve_sharp)
        self.report({'INFO'}, f"QuadriFlow: {len(obj.data.polygons)} faces")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EZQUADREMESHES_OT_remesh)


def unregister():
    bpy.utils.unregister_class(EZQUADREMESHES_OT_remesh)
