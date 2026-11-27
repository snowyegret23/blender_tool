import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty

class EZQuadRemeshesProperties(bpy.types.PropertyGroup):
    target_faces: IntProperty(
        name="Target Faces",
        description="Approximate target face count",
        default=4000,
        min=100,
        max=100000
    )
    
    smooth_iterations: IntProperty(
        name="Smooth Iterations",
        description="Number of smoothing iterations",
        default=3,
        min=0,
        max=20
    )

    preserve_boundary: BoolProperty(name="Preserve Boundary", default=True)
    preserve_sharp: BoolProperty(name="Preserve Sharp", default=True)


class EZQUADREMESHES_PT_main_panel(bpy.types.Panel):
    bl_label = "EZ Quad Remeshes"
    bl_idname = "EZQUADREMESHES_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EZQuadRemeshes'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ez_props = scene.ez_quadremeshes_props
        
        layout.prop(ez_props, "target_faces")
        layout.prop(ez_props, "smooth_iterations")
        
        layout.prop(ez_props, "preserve_boundary")
        layout.prop(ez_props, "preserve_sharp")
        if context.mode != 'OBJECT':
            layout.label(text="Switch to Object Mode", icon='INFO')
        layout.operator("ezquadremeshes.remesh")

def register():
    bpy.utils.register_class(EZQuadRemeshesProperties)
    bpy.types.Scene.ez_quadremeshes_props = PointerProperty(type=EZQuadRemeshesProperties)
    bpy.utils.register_class(EZQUADREMESHES_PT_main_panel)

def unregister():
    bpy.utils.unregister_class(EZQUADREMESHES_PT_main_panel)
    del bpy.types.Scene.ez_quadremeshes_props
    bpy.utils.unregister_class(EZQuadRemeshesProperties)