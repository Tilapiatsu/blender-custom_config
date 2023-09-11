import bpy
from . import bake_manager
from . import object_manager
from . import collection_manager
from . import UI
from . import bake_passes
from . import material_preview_manager

from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)

def ensure_viewport_shading_is_not_solid(context):
    '''
    Set all areas of type VIEW_3D to MATERIAL if it is SOLID or WIREFRAME
    '''
    
    for area in context.screen.areas:
        
        if not area.type == 'VIEW_3D':
            continue

        for space in area.spaces:

            if not space.type == 'VIEW_3D':
                continue

            if space.shading.type == 'SOLID' or space.shading.type == 'WIREFRAME':
                space.shading.type = 'MATERIAL'

def initialize_bake_preview_material(material_name):
    
    #Create a material for previewing baked textures and return it
    
    

    material = bpy.data.materials.new(name = material_name)
    material.use_nodes = True
    material['is_preview_material'] = True

    # Find BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf_node = node
            break
    
    # Find Output
    for node in material.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
            output_node = node
            break
    
    ao_mix_node = material.node_tree.nodes.new('ShaderNodeMixRGB')
    ao_mix_node['preview_type'] = 'AO_MIX'
    ao_mix_node.name = "AO_MIX"
    ao_mix_node.blend_type = 'MULTIPLY'
    ao_mix_node.inputs[0].default_value = 1
    ao_mix_node.inputs[2].default_value = (1,1,1,1)

    material.node_tree.links.new(ao_mix_node.outputs["Color"], bsdf_node.inputs["Base Color"])

    normal_map_node = material.node_tree.nodes.new(type = 'ShaderNodeNormalMap')
    material.node_tree.links.new(normal_map_node.outputs["Normal"], bsdf_node.inputs["Normal"])
    material.node_tree.links.new(ao_mix_node.outputs["Color"], bsdf_node.inputs["Base Color"])

    # Displacement
    disp_node = material.node_tree.nodes.new('ShaderNodeDisplacement')
    material.node_tree.links.new(disp_node.outputs["Displacement"], output_node.inputs["Displacement"])

    return material
'''
'''
def add_images_to_material(material, material_match_string):
    '''
    Removes existing images in materials and
    adds new versions of all relevant bake images to 
    material and connects them to the material nodes.
    Relevance is decided by comparing material_match_string with 
    image name. 
    '''
    # Remove all current images in the material
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            material.node_tree.nodes.remove(node)

    # Loop through images in bpy.data
    for image in bpy.data.images:
        # Check if image matches name with material_match_string
        if image.name.find(material_match_string) == - 1:
            continue
        
        # Add image to material
        image_node = material.node_tree.nodes.new(type = 'ShaderNodeTexImage')
        image_node.image = image

        # Get existing node types
        bsdf_node = None
        ao_mix_node = None
        normal_node = None
        disp_node = None

        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf_node = node
                node.location = [10, 300]
            if node.name.find("AO_MIX") > - 1:
                ao_mix_node = node
                node.location = [-900, 500]
            elif node.type == 'NORMAL_MAP':
                normal_node = node
                node.location = [-500, -500]
            elif node.type == 'DISPLACEMENT':
                disp_node = node
                node.location = [30, -700]  
            elif node.type == 'ALPHA':
                alpha_node = node
                node.location = [-500, -200]             

        if image.get('bake_type') == 'AO':
            material.node_tree.links.new(image_node.outputs["Color"], ao_mix_node.inputs["Color2"])
            image_node.location = [-1400, 250]
        elif image.get('bake_type') == 'NORMAL':
            material.node_tree.links.new(image_node.outputs["Color"], normal_node.inputs["Color"])
            normal_node.space = image.get('normal_space')
            image_node.location = [-1000, -700]
        elif image.get('bake_type') == 'DIFFUSE':
            material.node_tree.links.new(image_node.outputs["Color"], ao_mix_node.inputs["Color1"])
            image_node.location = [-1400, 500]
        elif image.get('bake_type') == 'BASE COLOR':
            material.node_tree.links.new(image_node.outputs["Color"], ao_mix_node.inputs["Color1"])
            image_node.location = [-1400, 500]
        elif image.get('bake_type') == 'METALLIC': 
            material.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Metallic"])
            image_node.location = [-850, 200]
        elif image.get('bake_type') == 'ROUGHNESS': 
            material.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Roughness"])
            image_node.location = [1000, -100]
        elif image.get('bake_type') == 'SPECULAR': 
            material.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Specular"])
            image_node.location = [-800, 80]
        elif image.get('bake_type') == 'EMIT':  
            material.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Emission"])
        elif image.get('bake_type') == 'ALPHA':  
            material.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Alpha"])
            material.blend_method = 'BLEND'
        elif image.get('bake_type') == 'DISPLACEMENT':  
            material.node_tree.links.new(image_node.outputs["Color"], disp_node.inputs["Height"])
            image_node.location = [disp_node.location[0] - 300, disp_node.location[1]]
        else:
            # Remove image node if it should not be connected 
            # in the material node tree
            material.node_tree.nodes.remove(image_node)
        
        '''
        '''

    # Connect AO, Base color, roughness, metallic, Emit, Normal by 
    # checking image bake_type
    return material

def set_viewport_shading_better_than_solid(context):
    '''
    Sets the 3dview shading to 'MATERIAL' if the current shading is 'SOLID'
    '''
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    if space.shading.type == 'SOLID':
                        space.shading.type = 'MATERIAL'


def get_preview_material_name(context, object):
    '''
    Returns the name of the preview material.
    Convenient way of getting the correct  name format
    '''

    collection_name = bake_manager.get_first_bake_collection_name_from_object(context, object)

    naming_option = context.scene.BBB_props.bake_image_naming_option

    if naming_option.find("COLLECTION") > - 1:
        preview_material_name = collection_name
    elif naming_option.find("OBJECT") > - 1:
        preview_material_name = object.name

    return preview_material_name

def get_materials_from_collections(collections):
    '''
    returns all materials of all objects in the collections
    '''
    material_list = []
    for collection in collections:
        for object in collection.objects:
            for material_slot in object.material_slots:
                if material_slot.material == None:
                    continue
                material = material_slot.material
                if not material in material_list:
                    material_list.append(material)

    return material_list

def create_bake_preview_material(context, objects):
    '''
    Create bake preview material 
    '''
    original_selection = context.selected_objects
    active_object = context.active_object

    object_manager.filter_objects_by_type(objects, ['MESH', 'META', 'CURVE', 'FONT', 'SURFACE'])
    # Apply material to all objects in objects
    for object in objects:
        collection_name = bake_manager.get_first_bake_collection_name_from_object(context, object)
        material_match_string = get_preview_material_name(context, object)
        material_name = material_match_string + " bake preview"
        material_found = False

        # Check if material with name exist, otherwise create it
        for material in bpy.data.materials:
            if material.name == material_name:
                material_found = True
                # Set collections for material. I had a bug where the connnectiont to the 
                # collection got lost, so I'm doing this often just to be sure it works
                collections = collection_manager.get_bake_collections_by_object(context, object)
                material['bake_collection'] = collections[0]
                break

        if not material_found:
            material = initialize_bake_preview_material(material_name)

        if len(object.material_slots) == 0:
            context.view_layer.objects.active = object
            bpy.ops.object.material_slot_add()
        
        object.material_slots[0].material = material
        
        # Connect image to the proper shading connection
        add_images_to_material(material, material_match_string)

        # Restore selection
        object_manager.select_objects(context, "REPLACE", original_selection)
        context.view_layer.objects.active = active_object

def get_objects_with_preview_material():
    '''
    return objects in the current scene that has an object which is has a preview material
    '''
    objects_with_preview_material = []

    for object in context.view_layer.objects:
        has_preview_material = False
        for material_slot in object.material_slots:
            try:
                material_slot.material['is_preview_material']
                has_preview_material = True
                break
            except:
                pass

        if has_preview_material:
            objects_with_preview_material.append(object)

    return objects_with_preview_material

def update_all_bake_preview_materials():
    '''
    Updates all bake preview materials and adds 
    textures that might not have yet been added
    '''
    for material in bpy.data.materials:
        if not material.get('is_preview_material'):
            continue
        if material.get('bake_collection') == None:
            continue

        bake_collection_name = material['bake_collection'].name
        add_images_to_material(material, bake_collection_name) 
            

def preview_bake_texture(context, bake_pass):
    '''
    Loops through all bake preview materials and connect the resulting texture of
    the bake pass to an emissive shader
    '''
    print("\n init preview_bake_texture")
    material_found = False
    bake_image = None
    bake_images = []
    BBB_props = context.scene.BBB_props

    bake_pass_type = bake_pass.bake_type
    
    # Find bake image that corresponds to bake_pass
    if BBB_props.target == 'IMAGE_TEXTURES':
        for image in bpy.data.images:
            
            if not image.get('bake_type') == bake_pass_type:
                continue

            if image.get('bake_type') == "AOV" and not image.get('aov_name') == bake_pass.aov_name:
                continue

            bake_images.append(image)

        # Return if no image was found
        if len(bake_images) == 0: 
            print("no bake image found")
            return


    collections = collection_manager.get_bake_collections_by_scene(context.scene)
    for collection in collections:

        object_manager.add_materials_to_objects_in_collections(context, collections)
        materials = get_materials_from_collections([collection]) 
        
        # Get image for this bake collection
        for image in bake_images:
            if image.get('image_folder') == collection.name:
                bake_image = image

        for material in materials:
            
            # Remove old preview material nodes 
            remove_preview_bake_texture(context, [material])

            # Store original surface input to material output node, so I can restore this later
            if material.get('orig_surface_input') == None:
                original_surface_input = get_name_of_node_connected_to_material_output(material)
                if not original_surface_input == None:
                    material['orig_surface_input'] = original_surface_input
                    pass
                
            # Add nodes to material
            if BBB_props.target == 'IMAGE_TEXTURES':
                image_node = material.node_tree.nodes.new(type = 'ShaderNodeTexImage')
                if not bake_image == None:
                    image_node.image = bake_image
            elif BBB_props.target == 'VERTEX_COLORS':
                image_node = material.node_tree.nodes.new(type = 'ShaderNodeVertexColor')
                image_node.layer_name = bake_pass.name


            # Create gamma node if image has color space "Non-Color"
            gamma_node = None
            if (not bake_passes.is_srgb_bake_pass(bake_pass) and 
                context.scene.display_settings.display_device == 'sRGB'):
                
                gamma_node = material.node_tree.nodes.new(type = 'ShaderNodeGamma')
                gamma_node['preview_bake_texture'] = True
                gamma_node.inputs['Gamma'].default_value = 2.2

                material.node_tree.links.new(image_node.outputs["Color"], gamma_node.inputs["Color"])        

            
            # Connect to emission node
            emission_node = material.node_tree.nodes.new(type = 'ShaderNodeEmission')

            if gamma_node == None:
                material.node_tree.links.new(image_node.outputs["Color"], emission_node.inputs["Color"]) 
            else:
                material.node_tree.links.new(gamma_node.outputs["Color"], emission_node.inputs["Color"])    
                    
            material_output_nodes = get_nodes_by_type(material, 'OUTPUT_MATERIAL')  
            
            if len(material_output_nodes) == 0:
                mat_node = material.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
                material_output_nodes.append(mat_node)

            # Connect preview image / emission to material output
            try:
                material.node_tree.links.new(emission_node.outputs["Emission"], material_output_nodes[0].inputs["Surface"])        
            except:
                print("Could not connect preview bake texture emission node to " + material_output_nodes[0].name)        
            
            # Store temprary flags on nodes and material
            image_node['preview_bake_texture'] = True
            emission_node['preview_bake_texture'] = True

            material['is_previewing_bake_texture'] = True
            
    ensure_viewport_shading_is_not_solid(context)


    

def get_socket_connected_to_material_output(material):
    '''
    Return the first found socket that is connected to a 
    material output nodes "surface" input
    '''

    return_socket = None
    material_output_nodes = get_nodes_by_type(material, 'OUTPUT_MATERIAL')
    
    for node in material_output_nodes:
        if len(node.inputs['Surface'].links) > 0:
            return_socket = node.inputs['Surface'].links[0].from_socket
            return return_socket

    return return_socket

def get_name_of_node_connected_to_material_output(material):
    '''
    Return the first found socket that is connected to a 
    material output nodes "surface" input
    '''
    material_output_nodes = get_nodes_by_type(material, 'OUTPUT_MATERIAL')
    
    for node in material_output_nodes:
        if len(node.inputs['Surface'].links) > 0:
            return_node = node.inputs['Surface'].links[0].from_node
            return return_node.name

    return None

def get_nodes_by_type(material, node_type):
    node_list = []
    
    for node in material.node_tree.nodes:
        if node.type == node_type:
            node_list.append(node)

    return node_list

def remove_preview_bake_texture(context, materials = None):
    '''
    Remove preview bake texture nodes from materials
    If materials == None, then check all materials in the file
    '''

    print("repr(materials) == " + repr(materials))

    if materials == None:
        materials = bpy.data.materials
    

    for material in materials:
        if not material.get('is_previewing_bake_texture'):
            continue

        del material['is_previewing_bake_texture']

        for node in material.node_tree.nodes:
            try:
                if node['preview_bake_texture'] > 0 :
                    material.node_tree.nodes.remove(node)
                    continue
            except:
                pass
            

            if node.type == 'OUTPUT_MATERIAL':
                output_node = node

        # Restore original connection to material output node
        try:
            orig_surface_input_node = material.node_tree.nodes[material['orig_surface_input']]
            material.node_tree.links.new(orig_surface_input_node.outputs[0], output_node.inputs["Surface"]) 
            del material['orig_surface_input']
        except:
            print("Could not reconnect original surface input node after removing bake preview image node")

class OBJECT_OT_create_bake_preview(bpy.types.Operator):
    '''
    Create bake preview 
    '''
    bl_idname = "object.create_bake_preview"
    bl_label = "Create bake preview material"
    bl_description = "Create a bake preview material on selected items. Textures assigned based on objects bake collection and bake passes"
    
    preview_type_items = [
        ("PREVIEW_ON_SELECTED", "Preview on selected objects", "Preview on selected objects", 0),
        ("PREVIEW_ON_DUPLICATE_OF_SELECTED", "Preview on duplicate of selected objects", "Preview on duplicate of selected objects", 1),
    ]    

    preview_type: bpy.props.EnumProperty(
        name="Preview workflow", 
        description = "Which way to create a preview of the bake", 
        items = preview_type_items
        )

    def execute(self, context):   

        bake_collections = collection_manager.get_bake_collections_by_objects(context, context.selected_objects)
        if len(bake_collections) == 0:
            UI.show_info_window(context, ["All selected objects must belong to a bake_collection when creating bake preview material(s)."], "Object(s) does not belong to bake collection")
            return {'FINISHED'}
        if self.preview_type == "PREVIEW_ON_SELECTED":
            create_bake_preview_material(context, context.selected_objects)
        
        material_preview_manager.set_viewport_shading_better_than_solid(context)
        return {'FINISHED'}   

class OBJECT_OT_preview_bake_texture(bpy.types.Operator):
    '''
    Preview bake texture
    '''
    bl_idname = "object.preview_bake_texture"
    bl_label = "Preview bake texture"
    bl_description = "Preview bake texture"

    bake_pass_index: bpy.props.IntProperty(
        name="Bake pass index", 
        description = "Bake pass index", 
        default = 0
        )

    def execute(self, context):   

        # Turn off all preview properties
        for index, bake_pass in enumerate(context.scene.bake_passes):
            if index == self.bake_pass_index:    
                # Set preview property          
                bake_pass.preview_bake_texture = not bake_pass.preview_bake_texture
                # preview bake texture or remove preview
                if bake_pass.preview_bake_texture == True:
                    preview_bake_texture(context, context.scene.bake_passes[index])
                else:
                    remove_preview_bake_texture(context)
            else:
                bake_pass.preview_bake_texture = False
        return {'FINISHED'}   



classes = (
    OBJECT_OT_create_bake_preview,
    OBJECT_OT_preview_bake_texture
)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)


def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)