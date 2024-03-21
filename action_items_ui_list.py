# Custom UI List : https://blender.stackexchange.com/questions/248440/is-it-possible-to-use-custom-class-for-uilist

import bpy

class ACTIONITEMS_ActionItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    action: bpy.props.PointerProperty(name="action", type=bpy.types.Action)
    looping: bpy.props.BoolProperty(name="looping", default=False)

class ACTIONITEMS_UL_ActionItemList(bpy.types.UIList):
    """UIList containing ActionItems"""
    bl_idname = "UI_UL_ActionItemList"
    layout_type = "DEFAULT"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(icon="ARMATURE_DATA")
            row.prop(data=item, property="looping", text="Looping")
            row.prop(data=item, property="action", text="")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class ACTIONITEMS_OT_List_Add(bpy.types.Operator):
    """Add an ActionItem to the ActionItemList"""
    bl_idname = "action_items.list_add"
    bl_label = "Add"
    bl_description = "Add an action to the list."

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object.data
        armature.action_items.add()
        return {'FINISHED'}

class ACTIONITEMS_OT_List_Remove(bpy.types.Operator):
    """Remove an ActionItem from the ActionItemList"""
    bl_idname = "action_items.list_remove"
    bl_label = "Remove"
    bl_description = "Remove an action from the list."

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        return (obj.type == 'ARMATURE'
                and obj.data.action_items
                and len(obj.data.action_items))

    def execute(self, context):
        armature = context.active_object.data
        index = armature.active_action_item_index
        armature.action_items.remove(index)
        armature.active_action_item_index = min(max(0, index - 1), len(armature.action_items) - 1)
        return {'FINISHED'}

classes = [ACTIONITEMS_ActionItem, ACTIONITEMS_UL_ActionItemList, ACTIONITEMS_OT_List_Add, ACTIONITEMS_OT_List_Remove]

def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    bpy.types.Armature.active_action_item_index = bpy.props.IntProperty(name="Index for action_items", default=0)
    bpy.types.Armature.action_items = bpy.props.CollectionProperty(type=ACTIONITEMS_ActionItem)

def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)

    del bpy.types.Armature.active_action_item_index
    del bpy.types.Armature.action_items
