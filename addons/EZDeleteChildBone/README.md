# EZDeleteChildBone

In Armature Edit Mode, select bones to keep and click **Delete Child Bones** in the **EZDeleteChildBone** sidebar tab. This removes visible, selectable, unselected descendants in the active armature. Hidden bones, bones in hidden collections, and bones with selection disabled are kept. A surviving bone whose parent is removed is reparented to the closest surviving ancestor without moving its head. Use Blender's Undo to revert the deletion.
