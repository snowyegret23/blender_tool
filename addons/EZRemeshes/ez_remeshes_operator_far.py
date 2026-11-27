import bpy
from .split_ngons import SplitNgons


class EZRemeshesOperatorFar(SplitNgons, bpy.types.Operator):
    bl_idname = "mesh.ez_remeshes_operator_far"
    bl_label = "Split N-gons (Far)"
    bl_description = "Split n-gons using the longest usable diagonal first"
    far = True


def register():
    bpy.utils.register_class(EZRemeshesOperatorFar)


def unregister():
    bpy.utils.unregister_class(EZRemeshesOperatorFar)
