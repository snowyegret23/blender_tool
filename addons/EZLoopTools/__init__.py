bl_info = {
    "name": "EZLoopTools",
    "author": "Snowyegret",
    "version": (1, 1, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > EZLooptools",
    "description": "Apply LoopTools to edge paths within selected faces",
    "category": "Mesh",
}

import bpy
from bpy.props import EnumProperty
from .ez_looptools_operation import EZLOOPTOOLS_OT_Operation
from .ez_looptools_panel import EZLOOPTOOLS_PT_Panel

def register():
    bpy.utils.register_class(EZLOOPTOOLS_OT_Operation)
    bpy.utils.register_class(EZLOOPTOOLS_PT_Panel)

    bpy.types.Scene.ezlooptools_direction = EnumProperty(
        name="Edge Paths",
        description="Choose the paths to process within the selected faces",
        items=[
            ('HORIZONTAL', "All Loops", "Process edge paths through the selected faces"),
            ('BOUNDARY', "Selection Boundary", "Process only the outer edges of the selected faces"),
        ],
        default='HORIZONTAL'
    )

    bpy.types.Scene.ezlooptools_operation = EnumProperty(
        name="Operation",
        description="Choose the LoopTools operation",
        items=[
            ('FLATTEN', "Flatten", "Flatten the loops"),
            ('RELAX', "Relax", "Relax the loops"),
            ('SPACE', "Space", "Space the loops evenly"),
        ],
        default='FLATTEN'
    )

def unregister():
    del bpy.types.Scene.ezlooptools_direction
    del bpy.types.Scene.ezlooptools_operation

    bpy.utils.unregister_class(EZLOOPTOOLS_PT_Panel)
    bpy.utils.unregister_class(EZLOOPTOOLS_OT_Operation)

if __name__ == "__main__":
    register()
