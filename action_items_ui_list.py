# Custom UI List : https://blender.stackexchange.com/questions/248440/is-it-possible-to-use-custom-class-for-uilist

import bpy

class ACTIONITEMS_ActionItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    action: bpy.props.PointerProperty(name="action", type=bpy.types.Action)

class ACTIONITEMS_UL_ActionItemList(bpy.types.UIList):
    """UIList containing ActionItems"""
    bl_idname = "UI_UL_ActionItemList"
    layout_type = "DEFAULT"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(icon="ARMATURE_DATA")
            row.prop(data=item, property="action", text="")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

classes = [ACTIONITEMS_ActionItem, ACTIONITEMS_UL_ActionItemList]

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
