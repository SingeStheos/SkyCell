# SkyCell 1.0.1 06/13/24
# Concept by SingeStheos
# NIF file import code by Bad Dog
#
#
#
# SkyCell is presented with the MIT license. 
# Bad Dog's PyNifly is licensed under GPL-3.0.
#
# SkyCell is a modification and reintegration of PyNifly's 
# import code to import whole Skyrim cells at once.

bl_info = {
    "name": "SkyCell",
    "blender": (2, 80, 0),
    "category": "Import-Export",
    "description": "Import Cells from Skyrim, the easy way. Requires NIF Import by Bad Dog.",
}

import bpy
import os
import re
from pathlib import Path

# Define properties for the addon
def init_properties():
    bpy.types.Scene.text_file_path = bpy.props.StringProperty(
        name="Text File Path",
        description="Path to the text file containing object data",
        default="",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.mesh_directory = bpy.props.StringProperty(
        name="Mesh Directory",
        description="Directory containing the .nif files",
        default="",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.ignore_position = bpy.props.BoolProperty(
        name="Ignore Position",
        description="Ignore position data from the text file",
        default=False
    )
    bpy.types.Scene.ignore_rotation = bpy.props.BoolProperty(
        name="Ignore Rotation",
        description="Ignore rotation data from the text file",
        default=False
    )
    bpy.types.Scene.ignore_scale = bpy.props.BoolProperty(
        name="Ignore Scale",
        description="Ignore scale data from the text file",
        default=False
    )
    bpy.types.Scene.override_scale = bpy.props.BoolProperty(
        name="Override Scale",
        description="Override all scale data with a fixed value",
        default=False
    )
    bpy.types.Scene.scale_override_value = bpy.props.FloatProperty(
        name="Scale Override Value",
        description="Value to override all scale data",
        default=1.0
    )

def clear_properties():
    del bpy.types.Scene.text_file_path
    del bpy.types.Scene.mesh_directory
    del bpy.types.Scene.ignore_position
    del bpy.types.Scene.ignore_rotation
    del bpy.types.Scene.ignore_scale
    del bpy.types.Scene.override_scale
    del bpy.types.Scene.scale_override_value

# UI Panel
class SkyrimNIFImporterPanel(bpy.types.Panel):
    bl_label = "SkyCell"
    bl_idname = "IMPORT_PT_skyrim_nif"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "text_file_path", text="Text File Path")
        layout.prop(scene, "mesh_directory", text="Mesh Directory")
        layout.prop(scene, "ignore_position", text="Ignore Position")
        layout.prop(scene, "ignore_rotation", text="Ignore Rotation")
        layout.prop(scene, "ignore_scale", text="Ignore Scale")
        layout.prop(scene, "override_scale", text="Override Scale")
        if scene.override_scale:
            layout.prop(scene, "scale_override_value", text="Scale Override Value")
        layout.operator("import_skyrim.nif", text="Import NIF Files")

# Operator for importing NIF files based on the text file
class ImportSkyrimNIFOperator(bpy.types.Operator):
    bl_idname = "import_skyrim.nif"
    bl_label = "Import Skyrim NIF"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        text_file_path = context.scene.text_file_path
        nif_directory = context.scene.mesh_directory
        ignore_position = context.scene.ignore_position
        ignore_rotation = context.scene.ignore_rotation
        ignore_scale = context.scene.ignore_scale
        override_scale = context.scene.override_scale
        scale_override_value = context.scene.scale_override_value

        if not os.path.exists(text_file_path):
            self.report({'ERROR'}, "Text file path does not exist.")
            return {'CANCELLED'}
        
        if not os.path.isdir(nif_directory):
            self.report({'ERROR'}, "NIF directory does not exist.")
            return {'CANCELLED'}
        
        lines = self.read_text_file(text_file_path)
        
        for line in lines:
            data = self.parse_line(line)
            if len(data) < 8:
                self.report({'WARNING'}, f"Line skipped due to incorrect format: {line}")
                continue

            object_name = data[0]
            pos = [float(data[1]), float(data[2]), float(data[3])]
            rot = [float(data[4]), float(data[5]), float(data[6])]
            scale = float(data[7])

            if ignore_position:
                pos = [0.0, 0.0, 0.0]
            if ignore_rotation:
                rot = [0.0, 0.0, 0.0]
            if ignore_scale:
                scale = 1.0
            if override_scale:
                scale = scale_override_value

            nif_file_path = self.get_nif_file_path(nif_directory, object_name)
            if nif_file_path:
                self.import_nif(nif_file_path, object_name)
                obj = bpy.context.selected_objects[0]
                self.set_transformations(obj, pos, rot, scale)
            else:
                self.report({'WARNING'}, f"NIF file for {object_name} not found.")
        
        return {'FINISHED'}
    
    def read_text_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        return lines[1:]  # Skip the header line

    def parse_line(self, line):
        return re.split(r'\s+', line.strip())

    def get_nif_file_path(self, directory, object_name):
        print(f"Searching for '{object_name}.nif' in directory: {directory}")

        if object_name[-3:].isdigit():
            object_name = object_name[:-3]  # Remove the last three characters
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == (object_name + '.nif').lower():
                    file_path = os.path.join(root, file)
                    print(f"Found NIF file: {file_path}")
                    return file_path
        print(f"NIF file '{object_name}.nif' not found in directory: {directory}")
        return None

    def import_nif(self, file_path, object_name):
        try:
            bpy.ops.import_scene.pynifly(filepath=file_path, rename_bones_niftools=True, 
                                         do_create_bones=False, use_blender_xf=True)
            print(f"Successfully imported NIF file for {object_name}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import NIF file for {object_name}: {str(e)}")

    def set_transformations(self, obj, pos, rot, scale):
        obj.location = (pos[0], pos[1], pos[2])
        obj.rotation_euler = (rot[0], rot[1], rot[2])
        obj.scale = (scale, scale, scale)

# Register and Unregister
classes = [SkyrimNIFImporterPanel, ImportSkyrimNIFOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    init_properties()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    clear_properties()

if __name__ == "__main__":
    register()
