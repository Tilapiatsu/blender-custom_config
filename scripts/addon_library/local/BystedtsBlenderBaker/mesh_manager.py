import bpy
import bmesh
import math
from . import object_manager
from . import settings_manager

def set_normals_to_outside(context, objects, only_recalculate_if_flagged = True):
    '''
    Set normals of objects so that they point outside of the mesh 
    (convex direction).

    Set normals is an issue with planes, since it can invert normals. 
    Do not recalculate normals if:
    - object has a dimension that is close to zero (i.e. flat plane)
    Make sure normals are set BEFORE joining objects, since joining
    changes bounding box!

    '''
    orig_mode = settings_manager.get_mode(context)
    selection_data = settings_manager.get_selection_data(context)

    for object in objects:
        # Continue if this object should not be included in normal recalculation
        if only_recalculate_if_flagged:
            if not object.get('recalculate_normals'):
                continue

        # Select object
        bpy.ops.object.mode_set(mode = 'OBJECT')
        object_manager.select_objects(context, 'REPLACE', [object], True)

        # Select all elements in edit mode
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        print("set normal to outside on object " + object.name)
        bpy.ops.mesh.normals_make_consistent(inside=False)
 
    # Restore mode, selection and active object
    bpy.ops.object.mode_set(mode = orig_mode)   
    settings_manager.restore_selected_objects(context, selection_data)

def apply_custom_split_normal(context, objects):
    '''
    Apply custom split normal to each object
    '''
    selected_objects = context.selected_objects
    active_object = context.active_object
    
    # Apply custom split normals per object
    for object in objects:
        context.view_layer.objects.active = object
        bpy.ops.mesh.customdata_custom_splitnormals_add()
        object.data.use_auto_smooth = True

    # Restore selection and active object
    object_manager.select_objects(context, 'REPLACE', objects)
    context.view_layer.objects.active = active_object

def handle_uv_naming_before_joining_objects(context, objects):
    '''
    # Rename uv maps if needed for the join process
    # Make sure all objects active UV has same name so that it is not lost during the join process
    '''

    # Check if renaming of uv maps is needed
    uv_renaming_needed = False 
    main_uv_name = ""
    for object in objects:
        for uv in object.data.uv_layers:
            if uv.active_render == True:
                active_uv_name = uv.name
                if object == objects[0]:
                    main_uv_name = uv.name
                if not active_uv_name == main_uv_name:
                    uv_renaming_needed = True

    # Rename uv's if all active uv's on objects don't share the same name
    if uv_renaming_needed:
        for object in objects:
            for uv in object.data.uv_layers:
                if uv.active_render == True:
                    uv.name = "active uv"

def get_meshes_list_from_objects(objects, exclude_objects = []):
    meshes = []

    for object in objects:
        if not object.type == "MESH":
            continue
        if object in exclude_objects:
            continue
        meshes.append(object.data)

    return meshes

def delete_meshes(context, meshes):
    for mesh in meshes:
        try:
            bpy.data.meshes.remove(mesh)
        except:
            pass

def set_sharp_edges_from_auto_smooth(context, objects, set_max_smooth_angle = False):
    '''
    Set hard edges on each objects mesh data based on settings in normal auto smooth
    Also force auto smooth with max angle setting

    Note: I found that it was much better to use split custom normal instead
    so this function is not used any longer. Keeping it just in case
    '''
    # Ensure objects is list
    if not type(objects) == list:
        objects = [objects]

    for object in objects:
        if object.data.use_auto_smooth == True:
            auto_smooth_angle = object.data.auto_smooth_angle
        else:
            # Set to max auto_smooth_angle
            auto_smooth_angle = 3.14159

        bm = bmesh.new()

        bm.from_mesh(object.data)
        bm.edges.ensure_lookup_table()

        for edge in bm.edges:
            if not edge.smooth:
                continue 
            if not edge.is_manifold:
                edge.smooth = False
                continue
            angle = edge.calc_face_angle()
            #angle = math.degree(angle)
            if angle > auto_smooth_angle:
                edge.smooth = False
            else:
                edge.smooth = True
                      
        # Write bmesh to data
        bm.to_mesh(object.data)

        # Force auto smooth with max angle setting
        if set_max_smooth_angle:
            object.data.use_auto_smooth = True
            object.data.auto_smooth_angle = 3.14159

def create_cage_from_objects(context, objects, fatten_amount, cage_name = "cage_object"):
    '''
    Create a cage mesh object by joining duplicates of 
    multiple objects. Each vertex is moved in it's positive
    normal direction by the "fatten" value 
    '''
    orig_selection = context.selected_objects
    
    object_manager.select_objects(context, 'REPLACE', objects, True)
    bpy.ops.object.duplicate()
    cage_objects = context.selected_objects
    
    # Fatten
    if not context.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()
    
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.shrink_fatten(value = fatten_amount)
    bpy.ops.object.editmode_toggle()


    # Join objects
    bpy.ops.object.join()
    context.active_object.name = cage_name
    joined_cage_object = context.active_object

    # Restore selection
    object_manager.select_objects(context, 'REPLACE', orig_selection)

    # Return cage object
    return joined_cage_object


def create_vertex_color_if_missing_and_set_to_active(context, objects, vertex_color_name):

    for object in objects:
        vtx_color_found = False
        for index, vtx_color in enumerate(object.data.vertex_colors):
            if vtx_color.name == vertex_color_name:
                object.data.vertex_colors.active_index = index
                vtx_color_found = True
                continue
        
        if vtx_color_found:
            continue

        override = {'active_object': object, 'object': object}
        bpy.ops.mesh.vertex_color_add(override)
        
        # update depsgraph
        dg = context.evaluated_depsgraph_get()
        dg.update()

        print("vertex color count after update on " + object.name + " = "  + str(len(object.data.vertex_colors)))
        index = max(0, len(object.data.vertex_colors) - 1)

        object.data.vertex_colors[index].name = vertex_color_name



def delete_vertex_color_by_name(context, objects, vertex_color_name):

    for object in objects:
        if not object.type == 'MESH':
            continue
        vtx_color_found = False
        for index, vtx_color in enumerate(object.data.vertex_colors):
            if vtx_color.name == vertex_color_name:
                object.data.vertex_colors.active_index = index
                vtx_col = object.data.vertex_colors[index]
                object.data.vertex_colors.remove(vtx_col)
                break


def RGBA_to_0123(channel):
    channels = "RGBA"
    return channels.find(channel)

def vertex_color_channel_transfer(context, objects, bake_pass):

    create_vertex_color_if_missing_and_set_to_active(context, objects, bake_pass.name)

    for object in objects:
      
        target = object.data.vertex_colors[bake_pass.name].data
        R_source = object.data.vertex_colors[bake_pass.R_source].data
        G_source = object.data.vertex_colors[bake_pass.G_source].data
        B_source = object.data.vertex_colors[bake_pass.B_source].data
        A_source = object.data.vertex_colors[bake_pass.A_source].data


        R_chan = RGBA_to_0123(bake_pass.transfer_source_channelR)
        G_chan = RGBA_to_0123(bake_pass.transfer_source_channelG)
        B_chan = RGBA_to_0123(bake_pass.transfer_source_channelB)
        A_chan = RGBA_to_0123(bake_pass.transfer_source_channelA)
  

        for i in range(0,len(target)):
            try:
                target[i].color[0] = R_source[i].color[R_chan]
                target[i].color[1] = G_source[i].color[G_chan]
                target[i].color[2] = B_source[i].color[B_chan]
                
                
                if A_source:
                    target[i].color[3] = A_source[i].color[A_chan]
                else:
                    target[i].color[3] = 1
                '''
                '''

            except:
                pass

    return 'FINISHED'

def delete_vertex_colors_by_bake_passes(context):
    '''
    Loop through all objects in the scene. Delete all vertex colors
    that matches the name of the bake passes
    '''

    for bake_pass in context.scene.bake_passes:
        delete_vertex_color_by_name(context, context.scene.objects, bake_pass.name)

    

class MESH_OT_delete_vertex_colors_by_bake_passes(bpy.types.Operator):
    '''
    Loop through all objects in the scene. Delete all vertex colors
    that matches the name of the bake passes
    '''
    bl_idname = "mesh.delete_vertex_colors_by_bake_passes"
    bl_label = "Delete vertex colors"
    bl_description = "Delete all vertex colors that matches the name of the bake passes"
    

    def execute(self, context):   
        for bake_pass in context.scene.bake_passes:
            delete_vertex_color_by_name(context, context.scene.objects, bake_pass.name)

        return {'FINISHED'}  

classes = (
    MESH_OT_delete_vertex_colors_by_bake_passes,
)

def register():
    for clas in classes:    
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)