bl_info = {
    "name": "EZRemeshes Far and Close",
    "author": "Snowyegret",
    "version": (1, 1, 1),
    "blender": (5, 2, 0),
    "location": "View3D > N-Panel > EZRemeshes",
    "description": "Split n-gons with short or long diagonals",
    "category": "Mesh",
}

from . import ez_remeshes_panel
from . import ez_remeshes_operator_far
from . import ez_remeshes_operator_close

def register():
    ez_remeshes_operator_far.register()
    ez_remeshes_operator_close.register()
    ez_remeshes_panel.register()

def unregister():
    ez_remeshes_panel.unregister()
    ez_remeshes_operator_close.unregister()
    ez_remeshes_operator_far.unregister()

if __name__ == "__main__":
    register()
