# Custom UI List : https://blender.stackexchange.com/questions/248440/is-it-possible-to-use-custom-class-for-uilist

import bpy
from bpy.types import Action, Armature, Operator, PropertyGroup, UIList
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty


class ACTIONITEMS_ActionItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    action: PointerProperty(name="action", type=Action)
    looping: BoolProperty(name="looping", default=False)


class ACTIONITEMS_UL_ActionItemList(UIList):
    """UIList containing ActionItems"""

    bl_idname = "UI_UL_ActionItemList"
    layout_type = "DEFAULT"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.label(icon="ARMATURE_DATA")
            row.prop(data=item, property="looping", text="Looping")
            row.prop(data=item, property="action", text="")

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
        return settings.armature_source

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings
        armature = settings.armature_source
        armature.action_items.add()
        return {"FINISHED"}


class ACTIONITEMS_OT_List_Remove(Operator):
    """Remove an ActionItem from the ActionItemList"""

    bl_idname = "action_items.list_remove"
    bl_label = "Remove"
    bl_description = "Remove an action from the list."

    @classmethod
    def poll(cls, context):
        settings = context.scene.iqm_export_pipeline_settings
        armature = settings.armature_source
        return armature.action_items and len(armature.action_items)

    def execute(self, context):
        settings = context.scene.iqm_export_pipeline_settings
        armature = settings.armature_source
        index = armature.active_action_item_index
        armature.action_items.remove(index)
        armature.active_action_item_index = min(max(0, index - 1), len(armature.action_items) - 1)
        return {"FINISHED"}


classes = [ACTIONITEMS_ActionItem, ACTIONITEMS_UL_ActionItemList, ACTIONITEMS_OT_List_Add, ACTIONITEMS_OT_List_Remove]


def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    Armature.active_action_item_index = IntProperty(name="Index for action_items", default=0)
    Armature.action_items = CollectionProperty(type=ACTIONITEMS_ActionItem)


def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

    del Armature.active_action_item_index
    del Armature.action_items
