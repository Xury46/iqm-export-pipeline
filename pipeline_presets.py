import bpy
from bpy.types import Menu, Operator, Panel
from bl_ui.utils import PresetPanel
from bl_operators.presets import AddPresetBase


class IQM_EXPORT_PIPELINE_MT_TransformOffsetPresets(Menu):
    bl_label = "Transform Offset Presets"
    preset_subdir = "iqm_export_pipeline"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class IQM_EXPORT_PIPELINE_OT_AddTransformOffsetPreset(AddPresetBase, Operator):
    bl_idname = "iqm_preset.add_transform_offset_preset"
    bl_label = "Add a transform offset preset"
    preset_menu = "IQM_EXPORT_PIPELINE_MT_TransformOffsetPresets"

    # variable used for all preset values
    preset_defines = [
        "scene = bpy.context.scene",
    ]

    # properties to store in the preset
    preset_values = [
        "scene.iqm_export_pipeline_settings.offset_location",
        "scene.iqm_export_pipeline_settings.offset_rotation",
        "scene.iqm_export_pipeline_settings.offset_scale",
    ]

    # where to store the preset
    preset_subdir = "iqm_export_pipeline"


class IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets(PresetPanel, Panel):
    bl_label = "Transform Offset Presets"
    preset_subdir = "iqm_export_pipeline"
    preset_operator = "script.execute_preset"
    preset_add_operator = "iqm_preset.add_transform_offset_preset"


classes = [
    IQM_EXPORT_PIPELINE_MT_TransformOffsetPresets,
    IQM_EXPORT_PIPELINE_OT_AddTransformOffsetPreset,
    IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets,
]


def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)


def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)
