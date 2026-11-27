import bpy
from bpy.types import Operator


def looptools_operator(name):
    operator = getattr(bpy.ops.mesh, f"looptools_{name}")
    try:
        operator.get_rna_type()
    except (KeyError, RuntimeError):
        return None
    return operator


class LoopToolsShortcut:
    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            cls.poll_message_set("Enter Mesh Edit Mode")
            return False
        if len(context.objects_in_mode_unique_data) != 1:
            cls.poll_message_set("Edit one mesh at a time")
            return False
        return True

    def execute(self, context):
        operator = looptools_operator(self.operation)
        if operator is None:
            self.report({'WARNING'}, "Install and enable the LoopTools extension in Preferences")
            return {'CANCELLED'}
        if not operator.poll():
            self.report({'WARNING'}, "LoopTools cannot run on the current selection")
            return {'CANCELLED'}
        try:
            return operator()
        except RuntimeError as error:
            self.report({'WARNING'}, str(error))
            return {'CANCELLED'}


class EZLOOP_OT_Flatten(LoopToolsShortcut, Operator):
    bl_idname = "ezloop.flatten"
    bl_label = "Flatten"
    bl_description = "Apply LoopTools Flatten"
    bl_options = {'REGISTER', 'UNDO'}
    operation = 'flatten'


class EZLOOP_OT_Relax(LoopToolsShortcut, Operator):
    bl_idname = "ezloop.relax"
    bl_label = "Relax"
    bl_description = "Apply LoopTools Relax"
    bl_options = {'REGISTER', 'UNDO'}
    operation = 'relax'


class EZLOOP_OT_Space(LoopToolsShortcut, Operator):
    bl_idname = "ezloop.space"
    bl_label = "Space"
    bl_description = "Apply LoopTools Space"
    bl_options = {'REGISTER', 'UNDO'}
    operation = 'space'


classes = (EZLOOP_OT_Flatten, EZLOOP_OT_Relax, EZLOOP_OT_Space)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
