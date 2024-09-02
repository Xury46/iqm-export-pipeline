# Custom UI List : https://blender.stackexchange.com/questions/248440/is-it-possible-to-use-custom-class-for-uilist

import bpy
from bpy.types import Action, Collection, Operator, PropertyGroup, UIList
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, IntProperty, PointerProperty

SPLIT_FACTOR: float = 0.4


def set_action_item_props(action_item, context):

    if action_item.action:
        action_item.frame_start = int(action_item.action.frame_range[0])
        action_item.frame_end = int(action_item.action.frame_range[1])
        action_item.fps = context.scene.render.fps
    else:
        action_item.frame_start = 0
        action_item.frame_end = 0
        action_item.fps = 0
        action_item.looping = False


class ACTIONITEMS_ActionItemProp(PropertyGroup):
    """Group of properties representing an item in the list."""

    action: PointerProperty(name="action", type=Action, update=set_action_item_props)
    frame_start: IntProperty(name="start frame")
    frame_end: IntProperty(name="end frame")
    fps: FloatProperty(name="frames per second")
    looping: BoolProperty(name="looping", default=False)

    def __str__(self) -> str:
        """The "Animations" field contains a comma (",") separated list of action names to export.
        # The names can also have parameters of the form "name:X:Y:Z:L", where
        # X is the start frame number,
        # Y is the end frame number,
        # Z is the frames per second (floating-point), and
        # L is 0 or 1 to indicate looping.
        # Earlier parameters can be left empty as in "idle::::1" to specify only a later parameter, and
        # later parameters can be omitted if unnecessary as in "run:1:25".
        """

        name: str = self.action.name
        start: int = self.frame_start
        end: int = self.frame_end
        fps: float = self.fps
        looping: str = "1" if self.looping else "0"

        return f"{name}:{start}:{end}:{fps}:{looping}"


class ACTIONITEMS_UL_ActionItemList(UIList):
    """UIList containing ActionItems"""

    bl_idname = "UI_UL_ActionItemList"
    layout_type = "DEFAULT"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            action_prop_split = row.split(factor=SPLIT_FACTOR)

            action_side = action_prop_split.row()
            action_side.label(icon="ARMATURE_DATA")
            action_side.prop(data=item, property="action", text="")

            property_side = action_prop_split.grid_flow(row_major=False, columns=4, even_columns=True)
            property_side.prop(data=item, property="frame_start", text="")
            property_side.prop(data=item, property="frame_end", text="")
            property_side.prop(data=item, property="fps", text="")
            property_side.prop(data=item, property="looping", text="")

        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="")


class ACTIONITEMS_OT_List_Add(Operator):
    """Add an ActionItem to the ActionItemList"""

    bl_idname = "action_items.list_add"
    bl_label = "Add"
    bl_description = "Add an action to the list."

    @classmethod
    def poll(cls, context):
        settings = context.scene.iqm_export_pipeline_settings
        return settings.export_collection

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings
        export_collection = settings.export_collection
        export_collection.action_items.add()
        return {"FINISHED"}


class ACTIONITEMS_OT_List_Remove(Operator):
    """Remove an ActionItem from the ActionItemList"""

    bl_idname = "action_items.list_remove"
    bl_label = "Remove"
    bl_description = "Remove an action from the list."

    @classmethod
    def poll(cls, context):
        settings = context.scene.iqm_export_pipeline_settings
        export_collection = settings.export_collection
        # Check if an armature source has been selected, and if it has at least one action_item in the action_items list.
        return export_collection and hasattr(export_collection, "action_items") and export_collection.action_items

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings
        export_collection = settings.export_collection
        index = export_collection.active_action_item_index
        export_collection.action_items.remove(index)
        export_collection.active_action_item_index = min(max(0, index - 1), len(export_collection.action_items) - 1)
        return {"FINISHED"}


classes = [
    ACTIONITEMS_ActionItemProp,
    ACTIONITEMS_UL_ActionItemList,
    ACTIONITEMS_OT_List_Add,
    ACTIONITEMS_OT_List_Remove,
]


def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    Collection.active_action_item_index = IntProperty(name="Index for action_items", default=0)
    Collection.action_items = CollectionProperty(type=ACTIONITEMS_ActionItemProp)


def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

    del Collection.active_action_item_index
    del Collection.action_items
