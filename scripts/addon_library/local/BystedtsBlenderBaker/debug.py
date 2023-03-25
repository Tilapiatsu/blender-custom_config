import bpy
from . import custom_properties


def allow_cleanup():
    
    cleanup_flags = {}
    cleanup_flags['objects'] = True
    cleanup_flags['scenes'] = True
    
    return cleanup_flags

def print_list(list_to_print, list_name = '', use_info = False):
    for each in list_to_print:
        print(each)
        if use_info:
            pass


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