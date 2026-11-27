# EZDeleteChildBone

In Armature Edit Mode, select the bones you want to keep and click **Delete Child Bones** in the **EZDeleteChildBone** sidebar tab. The tool deletes their unselected descendants (including hidden descendants) in the active armature. If two selected bones are separated by a deleted bone, the surviving child is parented to the closest surviving ancestor without snapping its head. Unrelated bones and other armatures are not edited. Use Blender's Undo to revert the deletion.
