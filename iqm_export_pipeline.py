import os
import bpy
from iqm_export import exportIQM

class IQMExportPipeline_Export(bpy.types.Operator):
    """Run the exportIQM function with pre-defined pipeline options"""
    bl_idname = "export.iqm_pipeline"
    bl_label = "Export IQM via pipeline"

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        file_directory = os.path.abspath(settings.export_directory)
        file_name = settings.file_name
        file_extention = ".iqm"

        animations_to_export = settings.animation_list

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

class IQMExportPipeline_Settings(bpy.types.PropertyGroup):
    """Properties to for exporting via the IQM Export Pipeline"""
    export_directory : bpy.props.StringProperty(name = "Output Path", subtype='DIR_PATH',  default = "/tmp\\")
    file_name :        bpy.props.StringProperty(name = "File Name",   subtype='FILE_NAME', default = "ExampleFile")
    animation_list :   bpy.props.StringProperty(name = "Animations",  default = "idle::::1, walk::::1, run::::1")

class IQMExportPipeline_Panel(bpy.types.Panel):
    """Creates a panel in the Output section of the Properties Editor"""
    bl_label = "IQM Export Pipeline"
    bl_idname = "PROPERTIES_PT_iqm_export_pipeline"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        layout = self.layout
        row = layout.row()
        row.prop(settings, "export_directory")
        row = layout.row()
        row.prop(settings, "file_name")
        row = layout.row()
        row.prop(settings, "animation_list")
        row = layout.row()
        row.operator("export.iqm_pipeline", text="Export")


classes = [IQMExportPipeline_Export, IQMExportPipeline_Settings, IQMExportPipeline_Panel]

def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    bpy.types.Scene.iqm_export_pipeline_settings = bpy.props.PointerProperty(type = IQMExportPipeline_Settings)

def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

    del bpy.types.Scene.iqm_export_pipeline_settings

if __name__ == "__main__":
    register()
