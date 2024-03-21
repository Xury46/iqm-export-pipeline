import os
import bpy
from iqm_export import exportIQM

def is_armature_in_collection(settings, armature):
    """Check if the armature data is associated with any object in the export_collection"""
    if not settings.export_collection:
        return False

    return any(object.data == armature for object in settings.export_collection.all_objects)

def assign_armature_from_collection(settings, context):
    """Callback for when an Export Collection is chosen
    Automatically assign the first available armature data in the collection to the Armature Source
    """

    # If there is no export_collection selected, clear the armature_source
    if not settings.export_collection:
        settings.armature_source = None
        return

    # If there are no objects in the selected export_collection, clear the armature_source
    if not len(settings.export_collection.all_objects):
        settings.armature_source = None
        return

    # If there is currently an armature_source, check if its object is associated with the selected export_collection
    elif settings.armature_source:
        if any(object.data == settings.armature_source for object in settings.export_collection.all_objects):
            return

    # Check if there is an object with armature data in the export_collection, if so, assign the first one found to the armature_source
    for object in settings.export_collection.all_objects:
        if object.type == 'ARMATURE':
            settings.armature_source = object.data
            return
        else:
            settings.armature_source = None

class IQMExportPipeline_Export(bpy.types.Operator):
    """Run the exportIQM function with pre-defined pipeline options"""
    bl_idname = "export.iqm_pipeline"
    bl_label = "Export IQM via pipeline"

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        file_directory = os.path.abspath(settings.export_directory)
        file_name = settings.file_name
        file_extention = ".iqm"

        animations_to_export = ""
        if settings.action_list_source == 'string':
            animations_to_export = settings.action_list_string
        elif settings.action_list_source == 'action_list':

            action_items = settings.armature_source.action_items
            for i, action_item in enumerate(action_items):
                name: str = action_item.action.name
                looping: str = "1" if action_item.looping else "0"

                animations_to_export += f"{name}::::{looping}"
                if i < len(action_items) - 1:
                    animations_to_export += ", "

        print(f"Actions to export: {animations_to_export}")

        # Temporarily override the selected objects with the objects from the export_collection
        with context.temp_override(selected_objects=settings.export_collection.all_objects):

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
    export_collection: bpy.props.PointerProperty(name="Export Collection", type=bpy.types.Collection, update=assign_armature_from_collection)

    export_directory: bpy.props.StringProperty(name="Output Path", subtype='DIR_PATH',  default="/tmp\\")

    file_name: bpy.props.StringProperty(name="File Name", subtype='FILE_NAME', default="ExampleFile")

    action_list_source: bpy.props.EnumProperty(
        name="Action List Source",
        description="What source should provide the list of actions to export",
        items=[
            ('none', 'None', "Don't export an action list", 0, 0),
            ('string', 'String', "Use a string to manually type an action list", 0, 1),
            ('action_list', 'Action List', "Use a UI list of actions to generate the action list", 0, 2)
            ]
        )

    action_list_string: bpy.props.StringProperty(name="Animations",  default="idle::::1, walk::::1, run::::1")

    armature_source: bpy.props.PointerProperty(name="Armature source", type=bpy.types.Armature, poll=is_armature_in_collection)

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
        row.prop(settings, "export_collection")
        row = layout.row()
        row.prop(settings, "export_directory")
        row = layout.row()
        row.prop(settings, "file_name")
        row = layout.row(align=True)
        row.label(text="Action list source:")
        row.prop(settings, "action_list_source", text="Action list source", expand=True)

        if settings.action_list_source == 'string':
            row = layout.row()
            row.prop(settings, "action_list_string")
        elif settings.action_list_source == 'action_list':
            row = layout.row()
            row.prop(settings, "armature_source")

            row = layout.row()
            if settings.armature_source:
                # The left column, containing the list.
                col = row.column(align=True)

                col.template_list(
                    listtype_name ="UI_UL_ActionItemList",
                    list_id = "DATA_UL_actions",
                    dataptr = settings.armature_source,
                    propname = "action_items",
                    active_dataptr = settings.armature_source,
                    active_propname = "active_action_item_index")

                # The right column, containing the controls.
                col = row.column(align=True)
                col.operator("action_items.list_add", text="", icon="ADD")
                col.operator("action_items.list_remove", text="", icon="REMOVE")
            else:
                row.label(text="Choose an Armature to list its actions", icon="ERROR")

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
