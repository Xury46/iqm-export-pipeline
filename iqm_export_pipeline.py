import os
import bpy
from iqm_export import exportIQM

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
