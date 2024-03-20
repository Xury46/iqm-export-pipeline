bl_info = {
    "name" : "IQM Export Pipeline",
    "author" : "Xury Greer",
    "version" : (1, 0),
    "blender" : (3, 6, 0),
    "location" : "Armature > Data > IQM",
    "description" : "A pipeline that offers quality-of-life improvements for using the IQM exporter",
    "category" : "Import-Export",
}

# Import / reload local modules (Required when using the "Reload Scripts" (bpy.ops.scripts.reload()) operator in Blender
if "bpy" in locals():
    import importlib
    importlib.reload(iqm_export_pipeline)
    importlib.reload(action_items_ui_list)
else:
    from . import iqm_export_pipeline
    from . import action_items_ui_list

import bpy

def register():
    iqm_export_pipeline.register()
    action_items_ui_list.register()

def unregister():
    iqm_export_pipeline.unregister()
    action_items_ui_list.unregister()

if __name__ == "__main__":
    register()
