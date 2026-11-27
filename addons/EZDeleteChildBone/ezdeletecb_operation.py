import bpy


class EZDELETECB_OT_delete_child_bones(bpy.types.Operator):
    bl_idname = "ezdeletecb.delete_child_bones"
    bl_label = "Delete Child Bones"
    bl_description = "Delete unselected descendants of the selected bones in the active armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE' and context.edit_object is not None

    def execute(self, context):
        bones = context.edit_object.data.edit_bones
        # Snapshot names before mutation; removing a connected bone can change its
        # children's parent and selection state.
        roots = {bone.name for bone in bones if bone.select and not bone.hide}
        children = {}
        for bone in bones:
            if bone.parent:
                children.setdefault(bone.parent.name, []).append(bone.name)

        queue = list(roots)
        seen = set(roots)
        descendants = []
        for parent in queue:
            for name in children.get(parent, ()):
                if name not in seen:
                    seen.add(name)
                    queue.append(name)
                    descendants.append(name)

        if not descendants:
            self.report({'INFO'}, "No unselected descendant bones to delete")
            return {'CANCELLED'}

        moving = set(descendants)
        for name in roots:
            bone = bones[name]
            parent = bone.parent
            if parent and parent.name in moving:
                while parent and parent.name in moving:
                    parent = parent.parent
                bone.use_connect = False
                bone.parent = parent

        for name in reversed(descendants):
            bones.remove(bones[name])
        self.report({'INFO'}, f"Deleted {len(descendants)} descendant bones")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EZDELETECB_OT_delete_child_bones)


def unregister():
    bpy.utils.unregister_class(EZDELETECB_OT_delete_child_bones)
