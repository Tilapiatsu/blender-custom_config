import bpy
from . import custom_properties

import time

def allow_cleanup():
    
    cleanup_flags = {}
    cleanup_flags['objects'] = True
    cleanup_flags['scenes'] = True
    cleanup_flags['intermediate_bake_image'] = True
    cleanup_flags['image_nodes'] = True
    cleanup_flags['shading_nodes'] = True
    cleanup_flags['render_settings'] = True
    return cleanup_flags

def debug_flags():
    
    debug_flags = {}
    debug_flags['show_vertex_color_in_ui'] = False
    debug_flags['show_debug_panel_in_ui'] = False
    return debug_flags

def debug_set(context, value):
    context.window_manager['debug'] = value

def debug_get(context):
    return context.window_manager['debug']

def check_panic_timer(context):
    '''
    Stops the baking process if the process has run past the second_limit
    If seconds_limit is negative, the baking process runs until it is done
    '''
    wm = context.window_manager
    seconds_limit = 5
    
    if seconds_limit < 0:
        return

    seconds_passed = time.time() - wm['start_process_time']
    if seconds_passed > seconds_limit:
        print("\n======\Ending baking process via check_panic_timer\n======")
        end_bake_process(context)


def end_bake_process(context):
    # Debug procedure for ending bake process
    wm = context.window_manager
    wm['end_process'] = True
    return None

def print_list(list_to_print, list_name = '', use_info = False):
    for each in list_to_print:
        print(each)
        if use_info:
            pass

def print_render_settings(context, render_settings, all = False):

    print("\n=====================================")
    print("Render settings")
    print("=====================================")
    
    for key, value in render_settings.items():
        if all:
            print(str(key) + ":" + repr(value))
        else:
            if key.find('.') == - 1:
                print(str(key) + ":" + repr(value))

    print("\n")

def debug_print_dictionary(context, dictionary):
    print("\n============================")
    for item in dictionary:
        print(item + " = " + repr(dictionary[item]))
    print("============================\n")

def print_to_info(text_to_print):
    text_to_print = str(text_to_print)
    self.report({'INFO'}, text_to_print)


def print_image_node_image_names_in_objects_materials(context, objects):

    material_list = []

    # Get all materials from objects
    for object in objects:
        for material_slot in object.material_slots:
            material = material_slot.material
            if material == None:
                continue
            if not material in material_list:
                material_list.append(material)

    # get all image nodes from all materials
    image_node_list = []
    for material in material_list:
        print("\n====== Image nodes in material " + material.name)
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                if node.image == None:
                    continue
                print(node.image.name)
         
        print("=============================\n")
  

class OBJECT_OT_check_if_object_has_high_res(bpy.types.Operator):
    bl_idname = "object.check_if_object_has_bakeset"
    bl_label = "Check if object has bakeSet"

    def execute(self, context):
        if custom_properties.property_exists(context, context.active_object, "bakeSet"):
            message = str(context.active_object.name) + " has bakeSet"
        else:
            message = str(context.active_object.name) + " does NOT have bakeSet"
        self.report({'INFO'}, message)
        return {'FINISHED'}

class OBJECT_OT_print_high_res(bpy.types.Operator):
    bl_idname = "object.print_bakeset"
    bl_label = "Print bakeSet in info panel and print"


    def execute(self, context):
        if custom_properties.property_exists(context, context.active_object, "bakeSet"):
            message = str(custom_properties.get_value(context, context.active_object, "bakeSet"))
        else:
            message = str(context.active_object.name) + " does NOT have bakeSet"
        self.report({'INFO'}, message)
        return {'FINISHED'}

classes = (
    OBJECT_OT_check_if_object_has_high_res,
    OBJECT_OT_print_high_res,

)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)