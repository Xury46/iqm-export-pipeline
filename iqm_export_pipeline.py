import os
from dataclasses import dataclass
import traceback
import bpy
from math import radians
from mathutils import Euler, Matrix, Vector
from bpy.types import Collection, Operator, Panel, PropertyGroup, Scene
from bpy.props import EnumProperty, FloatVectorProperty, PointerProperty, StringProperty
from iqm_export import exportIQM
from .action_items_ui_list import SPLIT_FACTOR
from .pipeline_presets import IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets


class IQM_EXPORT_PIPELINE_OT_Export(Operator):
    """Run the exportIQM function with pre-defined pipeline options"""

    bl_idname = "export.iqm_pipeline"
    bl_label = "Export IQM via pipeline"

    @dataclass
    class DecomposedTransforms:
        """Cache location, rotation, and scale values before using them to compose a matrix.
        Particularly useful for storing and recalling rotation_euler angles since Euler values
        outside a -180 to 180 degree range aren't preserved through matrix composition/decomposition.
        """

        location: Vector
        rotation_euler: Euler
        scale: Vector

    @classmethod
    def poll(cls, context):
        # Ensure the scene contains an instance of the iqm_export_pipeline_settings PropertyGroup.
        if not hasattr(context.scene, "iqm_export_pipeline_settings"):
            return False

        settings = context.scene.iqm_export_pipeline_settings
        export_collection = settings.export_collection

        # Check if an export collection has been selected, and if it has objects in it.
        if not export_collection or not export_collection.all_objects:
            return False

        # Validate the action_list_source
        if settings.action_list_source == "string":
            # Make sure the action_list_string isn't blank
            if not settings.action_list_string:
                return False

        elif settings.action_list_source == "action_list":
            # Check if an export collection has been selected, and if it has at least one action_item in the action_items list.
            if not export_collection or not hasattr(export_collection, "action_items") or not export_collection.action_items:
                return False

            # Make sure that all action_items have been assigned an action.
            if any(action_item.action is None for action_item in export_collection.action_items):
                return False

        return True

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        file_directory = os.path.abspath(settings.export_directory)
        file_name = settings.export_collection.iqm_export_pipeline_file_name
        file_extention = ".iqm"

        animations_to_export = ""
        if settings.action_list_source == "string":
            animations_to_export = settings.action_list_string
        elif settings.action_list_source == "action_list":

            action_items = settings.export_collection.action_items
            for i, action_item in enumerate(action_items):
                animations_to_export += str(action_item)
                if i < len(action_items) - 1:
                    animations_to_export += ", "

        print(f"Actions to export: {animations_to_export}")

        # Build the offset matrix.
        offset_matrix = Matrix.LocRotScale(
            settings.offset_location,
            Euler(settings.offset_rotation, "XYZ"),
            settings.offset_scale,
        )

        # Temporarily override the selected objects with the objects from the export_collection
        with context.temp_override(selected_objects=settings.export_collection.all_objects):

            try:
                # Cache the original transforms, then offset them.
                original_transforms: dict[self.DecomposedTransforms] = {}
                for obj in context.selected_objects:
                    # Don't offset objects that are children of other objects (avoids double-transformations).
                    if obj.parent:
                        continue

                    original_transforms[obj.name] = self.DecomposedTransforms(
                        obj.location.copy(),
                        obj.rotation_euler.copy(),
                        obj.scale.copy(),
                    )

                    new_transform = offset_matrix @ obj.matrix_local
                    new_location, new_rotation, new_scale = new_transform.decompose()

                    obj.location = new_location
                    obj.rotation_euler = new_rotation.to_euler("XYZ")
                    obj.scale = new_scale

                # Force an update so that the transforms are correctly offset in time for export.
                context.view_layer.update()

                # Export
                exportIQM(
                    context=bpy.context,
                    filename=os.path.join(file_directory, file_name + file_extention),
                    usemesh=True,
                    usemods=True,
                    useskel=True,
                    usebbox=True,
                    usecol=False,
                    scale=1.0,
                    animspecs=animations_to_export,
                    matfun=(lambda prefix, image: prefix),
                    derigify=False,
                    boneorder=None,
                )

            except Exception:
                print(traceback.format_exc())

            finally:
                # Reset the transforms
                for obj_name, original in original_transforms.items():
                    obj = bpy.data.objects[obj_name]

                    obj.location = original.location
                    obj.rotation_euler = original.rotation_euler
                    obj.scale = original.scale

        return {"FINISHED"}


class IQM_EXPORT_PIPELINE_SettingsProp(PropertyGroup):
    """Properties to for exporting via the IQM Export Pipeline"""

    export_collection: PointerProperty(name="Export Collection", type=Collection)

    export_directory: StringProperty(name="Output Directory", subtype="DIR_PATH", default="/tmp\\")

    action_list_source: EnumProperty(
        name="Action List Source",
        description="What source should provide the list of actions to export",
        items=[
            ("none", "None", "Don't export an action list", 0, 0),
            ("string", "String", "Use a string to manually type an action list", 0, 1),
            ("action_list", "Action List", "Use a UI list of actions to generate the action list", 0, 2),
        ],
    )

    action_list_string: StringProperty(name="Animations", default="idle::::1, walk::::1, run::::1")

    offset_location: FloatVectorProperty(name="Location offset", default=(0, 0, -24), subtype="TRANSLATION")

    offset_rotation: FloatVectorProperty(name="Rotation offset", default=(0, 0, radians(90)), subtype="EULER")

    offset_scale: FloatVectorProperty(name="Scale offset", default=(32, 32, 32), subtype="XYZ")


class IQM_EXPORT_PIPELINE_PT_Panel(Panel):
    """Creates a panel in the Output section of the Properties Editor"""

    bl_label = "IQM Export Pipeline"
    bl_idname = "PROPERTIES_PT_iqm_export_pipeline"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        layout = self.layout
        row = layout.row()
        row.prop(settings, "export_collection")
        row = layout.row()
        row.prop(settings.export_collection, "iqm_export_pipeline_file_name")


class IQM_EXPORT_PIPELINE_PT_AnimationsSubpanel(Panel):
    """Creates a subpanel in the IQM Export Pipeline for storing animation properties."""

    bl_label = "Animations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_parent_id = "PROPERTIES_PT_iqm_export_pipeline"

    def draw(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        layout = self.layout

        row = layout.row(align=True)
        row.label(text="Action list source:")
        row.prop(settings, "action_list_source", text="Action list source", expand=True)

        if settings.action_list_source == "string":
            row = layout.row()
            row.prop(settings, "action_list_string")
        elif settings.action_list_source == "action_list":
            # Make a row to draw the header.
            # Property text labels go in left column, a spacer goes in the right column.
            action_items_header_row = layout.row()

            # The left column, containing the header labels.
            col = action_items_header_row.column(align=True)

            # Make a row to put the Action label in.
            action_prop_split = col.split(factor=SPLIT_FACTOR)
            action_side = action_prop_split.row(align=True)
            action_side.label(text="Action:")

            # Make a row to evenly space the properties in.
            property_side = action_prop_split.grid_flow(row_major=False, columns=4, even_columns=True)
            property_side.label(text="Start:")
            property_side.label(text="End:")
            property_side.label(text="FPS:")
            property_side.label(text="Loop:")

            # The right column, containing a spacer.
            col = action_items_header_row.column(align=True)
            col.separator(factor=3.35)  # Add a spacer that matches the width of the - and + icon buttons.

            # Make a row to draw the Action Items.
            # The ActionItemList goes in the left column, the UIList operator buttons go in the right column.
            action_items_ui_list_row = layout.row()

            # The left column, containing the ActionItemList.
            col = action_items_ui_list_row.column(align=True)

            # Draw the ActionItemList.
            col.template_list(
                listtype_name="UI_UL_ActionItemList",
                list_id="DATA_UL_actions",
                dataptr=settings.export_collection,
                propname="action_items",
                active_dataptr=settings.export_collection,
                active_propname="active_action_item_index",
            )

            # The right column, containing the controls.
            col = action_items_ui_list_row.column(align=True)
            col.operator("action_items.list_add", text="", icon="ADD")
            col.operator("action_items.list_remove", text="", icon="REMOVE")


class IQM_EXPORT_PIPELINE_PT_OutputSubpanel(Panel):
    """Creates a subpanel in the IQM Export Pipeline for storing output properties."""

    bl_label = "Output"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_parent_id = "PROPERTIES_PT_iqm_export_pipeline"

    def draw(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        layout = self.layout
        row = layout.row()
        row.prop(settings, "export_directory")

        row = layout.row()
        row.operator("export.iqm_pipeline", text="Export")


class IQM_EXPORT_PIPELINE_PT_TransformOffsetSubpanel(Panel):
    """Creates a subpanel in the IQM Export Pipeline for storing transform offset properties."""

    bl_label = "Transform Offset"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_parent_id = "PROPERTIES_PT_iqm_export_pipeline"

    def draw_header_preset(self, context):
        IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets.draw_panel_header(self.layout)

    def draw(self, context):
        settings = context.scene.iqm_export_pipeline_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()
        row.prop(settings, "offset_location", expand=True)
        row = layout.row()
        row.prop(settings, "offset_rotation", expand=True)
        row = layout.row()
        row.prop(settings, "offset_scale", expand=True)


classes = [
    IQM_EXPORT_PIPELINE_OT_Export,
    IQM_EXPORT_PIPELINE_SettingsProp,
    IQM_EXPORT_PIPELINE_PT_Panel,
    IQM_EXPORT_PIPELINE_PT_AnimationsSubpanel,
    IQM_EXPORT_PIPELINE_PT_TransformOffsetSubpanel,
    IQM_EXPORT_PIPELINE_PT_OutputSubpanel,
]


def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    Scene.iqm_export_pipeline_settings = PointerProperty(type=IQM_EXPORT_PIPELINE_SettingsProp)
    Collection.iqm_export_pipeline_file_name = StringProperty(name="File Name", subtype="FILE_NAME", default="ExampleFile")


def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

    del Scene.iqm_export_pipeline_settings
    del Collection.iqm_export_pipeline_file_name
