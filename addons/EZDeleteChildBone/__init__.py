bl_info = {
    "name": "EZDeleteChildBone",
    "author": "Snowyegret",
    "version": (1, 1, 1),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > EZDeleteChildBone",
    "description": "Delete unselected descendants of selected bones",
    "category": "Rigging",
}

from . import ezdeletecb_operation
from . import ezdeletecb_panel

def register():
    ezdeletecb_operation.register()
    ezdeletecb_panel.register()

def unregister():
    ezdeletecb_panel.unregister()
    ezdeletecb_operation.unregister()

if __name__ == "__main__":
    register()
