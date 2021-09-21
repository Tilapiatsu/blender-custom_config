import bpy
import json
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from . import settings_manager

def get_filepath(context):

    save_path = 'E:\\'
    file_path = os.path.join(save_path, "export_data.json")
    
    file_path = 'E:\\Users\\Daniel\\Desktop\\temp\\json test\\my_file.json'

    return file_path

def get_preset_data_from_UI(context, scene):
    preset_data = {}
    preset_data = get_settings_data_from_UI(context, scene)
    bake_passes_data = get_bake_passes_data_from_UI(context, scene)
    preset_data.update(bake_passes_data)
    return preset_data

def get_bake_passes_data_from_UI(context, scene):

    bake_pass_data = {}
    bake_pass_data['bake_passes_count'] = len(context.scene.bake_passes)

    for index, bake_pass in enumerate(context.scene.bake_passes):
        
        pre_string = "context.scene.bake_passes[" + str(index) + "]."
        for prop in bake_pass.bl_rna.properties:
            
                if prop.name == 'RNA':
                    continue
                
                prop_string = pre_string + prop.identifier
                prop_value = eval(prop_string)
                            
                bake_pass_data[prop_string] = prop_value    

    return bake_pass_data    

def get_settings_data_from_UI(context, scene):

    BBB_props = bpy.context.scene.BBB_props

    preset_data = {}

    pre_string = "context.scene.BBB_props."

    # BBB_props
    for prop in BBB_props.bl_rna.properties:
    
        if prop.name == 'RNA' or prop.name == 'Name':
            continue
        
        if not prop.identifier == 'image_settings':
            prop_string = pre_string + prop.identifier
            prop_value = eval(prop_string)
                        
            preset_data[prop_string] = prop_value

    pre_string = "context.scene.BBB_props.image_settings."


    # BBB_props.mage_settings
    for prop in BBB_props.image_settings.bl_rna.properties:
        
        if prop.name == 'RNA' or prop.name == 'Name':
            continue
        
        prop_string = pre_string + prop.identifier
        prop_value = eval(prop_string)
        
        
        preset_data[prop_string] = prop_value    

    return preset_data

def read_preset_data_from_file(context, filepath):

    # read JSON file
    with open(filepath, 'r') as fp:
        data_file = json.load(fp)

    return data_file

def update_UI_from_preset_data(context, scene, preset_data):
    
    context.scene.bake_passes.clear()

    for i in range(0, preset_data['bake_passes_count']):
        context.scene.bake_passes.add()
    settings_manager.set_settings(context, preset_data)


def write_preset_file_to_disc(context, preset_data, filepath):

    # dict with all your data
    preset_data = get_preset_data_from_UI(context, context.scene)

    print("filepath = " + filepath)
    # encode dict as JSON 
    data = json.dumps(preset_data, indent=1, ensure_ascii=True)

    # write JSON file
    with open(filepath, 'w') as outfile:
        outfile.write(data + '\n')

    pass

def force_extention(context, filepath, ext):

    start = filepath.find(".")
    if start < 0:
       return  filepath + "." + ext
    
    return filepath[0:start] + "." + ext
    

class BBB_OP_read_preset_file(bpy.types.Operator, ImportHelper):
    """Load a preset file from disk"""
    bl_idname = "bbb.read_preset_file"
    bl_label = "Load preset file"
    bl_options = {'PRESET', 'UNDO'}
    #bl_options = 'INTERNAL'

    filename_ext = '.bbb'

    filter_glob: StringProperty(
        default='*.bbb',
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        print('imported file: ', self.filepath)

        #filepath = get_filepath(context)
        filepath = self.filepath
        preset_data = read_preset_data_from_file(context, filepath)
        context.scene.bake_passes.clear()
        update_UI_from_preset_data(context, context.scene, preset_data)
        
        return {'FINISHED'}


class BBB_OP_write_preset_file(bpy.types.Operator, ImportHelper):
    """Save a preset file from disk"""
    bl_idname = "bbb.write_preset_file"
    bl_label = "Save preset file"
    bl_options = {'PRESET', 'UNDO'}
    #bl_options = 'INTERNAL'

    filename_ext = '.bbb'

    filter_glob: StringProperty(
        default='*.bbb',
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        print('imported file: ', self.filepath)

        preset_data = get_preset_data_from_UI(context, context.scene)
        #filepath = get_filepath(context)
        filepath = self.filepath
        filepath = force_extention(context, filepath, "bbb")
        write_preset_file_to_disc(context, preset_data, filepath)
        
        return {'FINISHED'}


classes = (
    BBB_OP_read_preset_file,
    BBB_OP_write_preset_file,

)

def register():
    
    for clas in classes:
        print("register + " + repr(clas))
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)