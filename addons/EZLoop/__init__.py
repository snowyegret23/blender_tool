bl_info = {
    "name": "EZLoop",
    "author": "Snowyegret",
    "version": (1, 1, 0),
    "blender": (5, 2, 0),
    "location": "View3D > N-Panel > EZLoop",
    "description": "Run LoopTools Flatten, Relax and Space from the sidebar",
    "category": "Mesh",
}

from . import ezloop_operation
from . import ezloop_panel

def register():
    ezloop_operation.register()
    ezloop_panel.register()

def unregister():
    ezloop_panel.unregister()
    ezloop_operation.unregister()

if __name__ == "__main__":
    register()
