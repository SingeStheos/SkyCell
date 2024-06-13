# SkyCell 1.0.0 06/13/24
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

def clear_properties():
    del bpy.types.Scene.text_file_path
    del bpy.types.Scene.mesh_directory

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
        #layout.prop(text="SkyCell Menu")
        layout.prop(scene, "text_file_path", text="Text File Path")
        layout.prop(scene, "mesh_directory", text="Mesh Directory")
        layout.operator("import_skyrim.nif", text="Import NIF Files")
        #BELOW IS A DEVELOPER TEST BUTTON THAT ONLY WORKS ON DEVELOPER'S HARD DRIVE. this button tests one sole model to ensure nif import works - Singe
        #layout.operator("import_test.nif", text="Import Test Object")

# Operator for importing NIF files based on the text file
class ImportSkyrimNIFOperator(bpy.types.Operator):
    bl_idname = "import_skyrim.nif"
    bl_label = "Import Skyrim NIF"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        text_file_path = context.scene.text_file_path
        nif_directory = context.scene.mesh_directory

        if not os.path.exists(text_file_path):
            self.report({'ERROR'}, "Text file path does not exist.")
            return {'CANCELLED'}
        
        if not os.path.isdir(nif_directory):
            self.report({'ERROR'}, "NIF directory does not exist.")
            return {'CANCELLED'}
        
        lines = self.read_text_file(text_file_path)
        
        for line in lines:
            data = line.strip().split('\t')
            if len(data) < 8:
                self.report({'WARNING'}, f"Line skipped due to incorrect format: {line}")
                continue

            object_name = data[0]
            pos = [float(data[1]), float(data[2]), float(data[3])]
            rot = [float(data[4]), float(data[5]), float(data[6])]
            scale = float(data[7])

            nif_file_path = self.get_nif_file_path(nif_directory, object_name)
            if nif_file_path:
                self.import_nif(nif_file_path)
                obj = bpy.context.selected_objects[0]
                self.set_transformations(obj, pos, rot, scale)
            else:
                self.report({'WARNING'}, f"NIF file for {object_name} not found.")
        
        return {'FINISHED'}
    
    def read_text_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        return lines[1:]  # Skip the header line

    def get_nif_file_path(self, directory, object_name):
        print(f"Searching for '{object_name}.nif' in directory: {directory}")
    
        # Check if the last three characters are numeric
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

        return None

    def import_nif(self, file_path):
        bpy.ops.import_scene.pynifly(filepath=file_path, rename_bones_niftools=True, 
                                     do_create_bones=False, use_blender_xf=True)

    def set_transformations(self, obj, pos, rot, scale):
        obj.location = (pos[0], pos[1], pos[2])
        obj.rotation_euler = (rot[0], rot[1], rot[2])
        obj.scale = (scale, scale, scale)

# Operator for testing NIF import
class ImportTestNIFOperator(bpy.types.Operator):
    bl_idname = "import_test.nif"
    bl_label = "Test NIF Import"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nif_file_path = "G:\\skyrimstuff\\skyrimtextures\\meshes\\architecture\\farmhouse\\farmhouse01.nif"  #devtest nif file, works only if layout.operator("import_test.nif", text="Import Test Object") is uncommented. button doesnt exist otherwise.
        
        if not os.path.exists(nif_file_path):
            self.report({'ERROR'}, "NIF file path does not exist.")
            return {'CANCELLED'}
        
        bpy.ops.import_scene.pynifly(filepath=nif_file_path, rename_bones_niftools=True, 
                                     do_create_bones=False, use_blender_xf=True)
        
        return {'FINISHED'}

# Register and Unregister
classes = [SkyrimNIFImporterPanel, ImportSkyrimNIFOperator, ImportTestNIFOperator]

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
