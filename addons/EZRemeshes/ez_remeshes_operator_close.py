import bpy
from .split_ngons import SplitNgons


class EZRemeshesOperatorClose(SplitNgons, bpy.types.Operator):
    bl_idname = "mesh.ez_remeshes_operator_close"
    bl_label = "Split N-gons (Close)"
    bl_description = "Split n-gons using the shortest usable diagonal first"
    far = False


def register():
    bpy.utils.register_class(EZRemeshesOperatorClose)


def unregister():
    bpy.utils.unregister_class(EZRemeshesOperatorClose)
