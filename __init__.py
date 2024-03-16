bl_info = {
    "name" : "IQM Export Pipeline",
    "author" : "Xury Greer",
    "version" : (1, 0),
    "blender" : (3, 6, 0),
    "location" : "Armature > Data > IQM",
    "description" : "A pipeline that offers quality-of-life improvements for using the IQM exporter",
    "category" : "Import-Export",
}

from . import iqm_export_pipeline

def register():
    iqm_export_pipeline.register()

def unregister():
    iqm_export_pipeline.unregister()

if __name__ == "__main__":
    register()
