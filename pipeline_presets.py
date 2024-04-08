import os
import shutil
import filecmp
import bpy
from bpy.types import Menu, Operator, Panel
from bl_ui.utils import PresetPanel
from bl_operators.presets import AddPresetBase, ExecutePreset


def install_presets():
    # https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/
    bundled_presets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "presets")
    presets_install_dir = os.path.join(bpy.utils.user_resource("SCRIPTS"), "presets", "iqm_export_pipeline")

    if not os.path.isdir(presets_install_dir):
        os.makedirs(presets_install_dir)

    bundled_presets = os.listdir(bundled_presets_dir)

    for preset_file in bundled_presets:

        bundled_file = os.path.join(bundled_presets_dir, preset_file)
        installed_file = os.path.join(presets_install_dir, preset_file)

        # Check if the file is already installed.
        if os.path.isfile(installed_file):
            # Check if the installed file is up-to-date.
            if filecmp.cmp(bundled_file, installed_file):
                continue

        # Copy the file, overwrite the out-of-date file if it exists.
        shutil.copy2(os.path.join(bundled_presets_dir, preset_file), presets_install_dir)


class IQM_EXPORT_PIPELINE_MT_TransformOffsetPresets(Menu):
    bl_label = "Transform Offset Presets"
    preset_subdir = "iqm_export_pipeline"
    preset_operator = "script.execute_preset_tag_redraw"
    draw = Menu.draw_preset


class SCRIPT_OT_execute_preset_tag_redraw(ExecutePreset):
    """A wrapper operator to force a UI update after setting the preset values."""

    bl_idname = "script.execute_preset_tag_redraw"
    bl_label = "Execute a Python Preset and force a UI update"

    def execute(self, context):
        # The default script.execute_preset takes arguments for file_path and menu_idname
        # self.file_path is passed in when the preset menu calls this function
        # TODO figure out how self.menu_idname is normally passed in and get the value that way instead of hard-coding it here.
        self.menu_idname = "IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets"

        super().execute(context)  # Execute the preset via the default behavior in bpy.ops.script.execute_preset()

        # Force a UI update after applying the preset
        context.region.tag_redraw()

        return {"FINISHED"}


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
    preset_operator = "script.execute_preset_tag_redraw"
    preset_add_operator = "iqm_preset.add_transform_offset_preset"


classes = [
    IQM_EXPORT_PIPELINE_MT_TransformOffsetPresets,
    IQM_EXPORT_PIPELINE_OT_AddTransformOffsetPreset,
    IQM_EXPORT_PIPELINE_PT_TransformOffsetPresets,
    SCRIPT_OT_execute_preset_tag_redraw,
]


def register():
    for class_to_register in classes:
        bpy.utils.register_class(class_to_register)

    install_presets()


def unregister():
    for class_to_unregister in classes:
        bpy.utils.unregister_class(class_to_unregister)
