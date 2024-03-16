bl_info = {
    "name" : "IQM Export Pipeline",
    "author" : "Xury Greer",
    "version" : (1, 0),
    "blender" : (3, 6, 0),
    "location" : "Armature > Data > IQM",
    "description" : "A pipeline that offers quality-of-life improvements for using the IQM exporter",
    "category" : "Import-Export",
}

import os
import bpy
from iqm_export import exportIQM

class IQMExportPipeline(bpy.types.Operator):
    """Run the exportIQM function with pre-defined pipeline options"""
    bl_idname = "export.iqm_pipeline"
    bl_label = "Export IQM via pipeline"

    def execute(self, context):
        file_directory = f"C:\\Users\\{os.environ.get('USERNAME')}\\Documents\\"
        file_name = "iqm_export_test"
        file_extention = ".iqm"

        animations_to_export = "idle::::1, walk::::1, run::::1"

        exportIQM(
            context = bpy.context,
            filename = os.path.join(file_directory, file_name + file_extention),
            usemesh = True,
            usemods = True,
            useskel = True,
            usebbox = True,
            usecol = False,
            scale = 1.0,
            animspecs = animations_to_export,
            matfun = (lambda prefix, image: prefix),
            derigify = False,
            boneorder = None
            )

        return {'FINISHED'}

classes = [IQMExportPipeline]

def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

if __name__ == "__main__":
    register()
