import bpy
import functools
import webbrowser

from . import high_res_objects_manager
from . import object_manager
from . import bake_manager
from . import custom_properties
from . import UI
from . import scene_manager
from . import collection_manager
from . import settings_manager
from . import material_preview_manager
from . import file_manager
from . import bake_passes
from . import debug

from . import custom_properties

from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)

class OBJECT_OT_daby_silly_print(bpy.types.Operator):
    bl_idname = "object.silly_print_daby"
    bl_label = "silly print"

    def execute(self, context):
        from . import custom_properties
        custom_properties.silly_print('calling function probably from blender')
        return {'FINISHED'}

class OBJECT_OT_uv_pack_per_collection(bpy.types.Operator):
    '''
    Uv packs all objects that belong to the same collection as the selected object
    '''
    bl_idname = "object.uv_pack_per_collection"
    bl_label = "UV pack per collection"
    bl_description = "Uv packs all objects that belong to the same collection as the selected object"


    def execute(self, context):
        from . import uv_manager
        uv_manager.UV_pack_selected_per_collection()
        return {'FINISHED'}


class OBJECT_OT_uv_pack_objects_in_collection(bpy.types.Operator):
    '''
    UV pack all objects in the collection 
    '''
    bl_idname = "object.uv_pack_objects_in_collection"
    bl_label = "UV pack objects in collection"
    bl_description = "UV pack all objects in the collection "

    collection_name: StringProperty(
        name="Collection",
        description="Collection to uv pack",
    )    

    def execute(self, context):
        from . import uv_manager
        collection = bpy.data.collections[self.collection_name]
        uv_manager.UV_layout_per_collection(context, [collection])
        return {'FINISHED'}

class RENDER_OT_bake_selected_objects(bpy.types.Operator):
    '''
    Bake selected objects 
    '''
    # I need a separate operator in order to use the poll function

    bl_idname = "render.bake_selected_objects"
    bl_label = "Bake selected objects"
    bl_description = "Bake selected objects"

    bake_scope: EnumProperty(
        name="Bake scope",
        description="What objects/collections to bake",
        items=(
            ('BAKE_SELECTED_OBJECTS', "Bake selected objects", "Bake selected objects"),
            ('BAKE_SELECTED_WITH_SPECIFIC_BAKE_PASS', "Bake selected with specific bake pass", "Bake selected with specific bake pass"),
        ),
        default='BAKE_SELECTED_OBJECTS',
    )

    bake_pass_index: IntProperty(
        name="Bake pass index",
        description="Bake pass index",
        default=-1,
    )    

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):

        bake_collections = collection_manager.get_bake_collections_by_scene(context.scene)

        check_result = do_pre_bake_checks(context, context.selected_objects, bake_collections)
        
        if not check_result == None:
            self.report({check_result['error_type']}, check_result['message'])
            if check_result['cancel']:
                return {'CANCELLED'}

        bpy.ops.render.bake_with_bake_passes(bake_scope = self.bake_scope, bake_collection_index = -1, bake_pass_index = self.bake_pass_index)
        return {'FINISHED'}


class RENDER_OT_bake_with_bake_passes(bpy.types.Operator):
    '''
    Bakes images from bake passes 
    '''
    # Modal operator so that I can give info to the user during baking.
    
    bl_idname = "render.bake_with_bake_passes"
    bl_label = "Bake maps from selected"
    bl_description = "Bakes images from bake passes"

    bake_collections = None
    bake_passes = None
    objects = None
    original_selection = None
    original_render_settings = None


    bake_scope: EnumProperty(
        name="Bake scope",
        description="What objects/collections to bake",
        items=(
            ('BAKE_SELECTED_OBJECTS', "Bake selected objects", "Bake selected objects"),
            ('BAKE_ALL_BAKE_COLLECTIONS', "Bake all bake collections", "Bake all bake collections"),
            ('BAKE_SPECIFIC_BAKE_COLLECTION', "Bake specific bake collections", "Bake specific bake collections"),
            ('BAKE_SELECTED_WITH_SPECIFIC_BAKE_PASS', "Bake selected with specific bake pass", "Bake selected with specific bake pass"),
        ),
        default='BAKE_SELECTED_OBJECTS',
    )


    bake_collection_index: IntProperty(
        name="Bake collection index",
        description="Bake collection index",
        default=-1,
    )

    bake_pass_index: IntProperty(
        name="Bake pass index",
        description="Bake pass index",
        default=-1,
    )


    def main(self, context):

        selected_objects = context.selected_objects
        bake_manager.bake_all_passes_with_timer(context, selected_objects)

    def modal(self, context, event):
        wm = context.window_manager
        

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if wm.get('timer_registered') == False:
            wm['timer_registered'] = True

            bpy.app.timers.register(functools.partial(bake_manager.bake_specific_pass, context, self.objects , self.bake_collections, image_folder = '', bake_passes = self.bake_passes, area = context.area), first_interval=0.1)
        
        if wm.get('end_process'):
            self.finish(context)
            return {'FINISHED'}

        UI.tag_redraw_all_areas(context)

        return {'RUNNING_MODAL'}
        #return {'PASS_THROUGH'}


    def store_original_values(self, context):
        '''
        Store original values that will be restored after the operator is 
        finished or cancelled
        '''
        self.original_selection = context.selected_objects
        self.bake_passes = context.scene.bake_passes
        self.original_render_settings = settings_manager.get_current_render_settings(context)


    def restore_original_values(self, context):
        '''
        Restore original values
        '''
        try:
            object_manager.select_objects(context, 'REPLACE', self.original_selection)
        except:
            print("Could not restore original selection")
        settings_manager.set_settings(context, self.original_render_settings)
        context.scene.BBB_props.progress_percentage = 0

    def initialize_properties(self, context):
        '''
        Initialize properties in the window manager that keeps track of
        which bake pass and bake collection is being baked.
        '''
        # Store variables in operator class
        bake_collections = collection_manager.get_bake_collections_by_scene(context.scene)
        
        if self.bake_scope == 'BAKE_ALL_BAKE_COLLECTIONS':
            self.bake_collections = collection_manager.get_bake_collections_by_scene(context.scene)
            #self.objects = None
            object_list = []
            for collection in self.bake_collections:
                object_list += collection.objects
            self.objects = object_list
            self.bake_passes = bake_passes.get_sorted_bake_passes_list(context)

        
        elif self.bake_scope == 'BAKE_SPECIFIC_BAKE_COLLECTION':
            self.bake_collections = [bake_collections[self.bake_collection_index]]
            #self.objects = None
            object_list = []
            for collection in self.bake_collections:
                object_list += collection.objects
            self.objects = object_list
            self.bake_passes = bake_passes.get_sorted_bake_passes_list(context)

        
        elif self.bake_scope == 'BAKE_SELECTED_OBJECTS':
            self.bake_collections = collection_manager.get_bake_collections_by_objects(context, context.selected_objects, context.scene)
            self.bake_passes = bake_passes.get_sorted_bake_passes_list(context)
            self.objects = context.selected_objects
        
        elif self.bake_scope == 'BAKE_SELECTED_WITH_SPECIFIC_BAKE_PASS':
            self.bake_collections = collection_manager.get_bake_collections_by_objects(context, context.selected_objects, context.scene)
            self.bake_passes = [context.scene.bake_passes[self.bake_pass_index]]
            self.objects = context.selected_objects
    

        # Store properties in window manager used to iterate bake passes
        # and bake collections during baking with timer function
        wm = context.window_manager
        wm['bake_pass_count'] = len(self.bake_passes)
        wm['current_bake_pass'] = 0
        
        if self.bake_collections == None:
            wm['bake_collections_count'] = 0
        else:
            wm['bake_collections_count'] = len(self.bake_collections)

        wm['current_bake_collection'] = 0
       
        wm['timer_registered'] = False

        wm['end_process'] = False
    
        import time
        wm['start_process_time'] = time.time()

        context.scene.BBB_props.progress_percentage = 5

    def delete_properties(self, context):
        
        wm = context.window_manager
        try:
            del wm['bake_pass_count'] 
            del wm['current_bake_pass']
            
            del wm['bake_collections_count'] 
            del wm['current_bake_collection']
        
            del wm['timer_registered']

            del wm['end_process']
        except:
            print("Could not delete temporary custom bake properties in window manager ")

    def finish(self, context):

        self.delete_properties(context)
        self.restore_original_values(context)

        debug.print_image_node_image_names_in_objects_materials(context, self.objects)
     
        material_preview_manager.update_all_bake_preview_materials()

        debug.print_image_node_image_names_in_objects_materials(context, self.objects)
        
        if debug.allow_cleanup()['scenes']:
            scene_manager.remove_temporary_scenes_after_bake(context)

        return {'FINISHED'}

    def cancel(self, context):
        self.delete_properties(context)
        self.restore_original_values(context)
                

    def execute(self, context):
        
        # Enter object mode
        if not context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        self.store_original_values(context)

        self.initialize_properties(context)

        check_result = do_pre_bake_checks(context, self.objects, self.bake_collections)
        
        if not check_result == None:
            self.report({check_result['error_type']}, check_result['message'])
            if check_result['cancel']:
                return {'CANCELLED'}
    
        wm = context.window_manager
        wm.modal_handler_add(self)

        bake_manager.initialize_bake_report(context, self.objects, self.bake_passes, self.bake_collections)
        UI.show_info_window(context, ["Baking initializing"], "Baking initializing")
        
        return {'RUNNING_MODAL'}
   
def do_pre_bake_checks(context, bake_target_objects, bake_collections):
    '''
    Do a bunch of pre bake checks. Return message and warning type so that the
    user can be notified from the operator that is called. Note that
    Multiple operators use this (bake selected and bake collection), so therefore
    I need to do the checks in a function outside of each operator.
    '''

    high_res_objects = high_res_objects_manager.get_high_res_objects(context, bake_target_objects)

    # Ensure there are valid values in the image settings
    if str(context.scene.BBB_props.image_settings.color_mode) == '':
        context.scene.BBB_props.image_settings.color_mode = 'RGB'
    if str(context.scene.BBB_props.image_settings.color_depth) == '':
        context.scene.BBB_props.image_settings.color_depth = '8'
    

    # Check if directory path is set
    if context.scene.BBB_props.dir_path == "":
        message = "You need to set an output directory before baking"
        #UI.show_info_window(context, [message], "Output directory missing")
        return {    
            "error_type": 'ERROR',
            "message": message,
            "cancel": True
        }

    # Check if bake passes are added
    elif len(context.scene.bake_passes) == 0:
        message = "No bake passes found. Please add bake passes"
        #UI.show_info_window(context, [message], "Bake passes missing")
        return {    
            "error_type": 'ERROR',
            "message": message,
            "cancel": True
        }

    # If baking with highres to lowres workflow - 
    # Check if any object is missing connected high res object
    elif context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':
        objects_missing_high_res_objects = []
        message = ""

        for object in bake_target_objects:
            if object == None:
                continue
            connected_high_res_objects = high_res_objects_manager.get_high_res_objects(context, [object])
            if len(connected_high_res_objects) == 0:
                objects_missing_high_res_objects.append(object)
        
        for object in objects_missing_high_res_objects:
            if message == "":
                message = "The following objects has no connected high res objects: "
            message += object.name + ", "
            
        if not message == "":
            return {    
                "error_type": 'INFO',
                "message": message,
                "cancel": False
            }            

    # Check if objects are missing in any bake pass
    else: 
        for bake_collection in bake_collections:
            if len(bake_collection.objects) == 0:
                message = "Objects missing in bake collection " + bake_collection.name
                #message.append("Please add objects to the bake collection")
                #UI.show_info_window(context, message, "Bake passes missing")
                #return
                #self.cancel(context)
                #return {'CANCELLED'}
                return {    
                    "error_type": 'INFO',
                    "message": message,
                    "cancel": False
                }      

    # Check if highres objects has material with non BSDF at the end
    if context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES': 
        objects_to_check = high_res_objects
    else:
        objects_to_check = bake_target_objects

    message = ""
    for object in objects_to_check:
        if not object_manager.object_has_bsdf_connected_to_material_output(object):
            message = object.name + " does not have a BSDF principal connected to material output. This might cause issues"
    
    #self.report({'WARNING'}, message)
    if not message == "":
        return {    
            "error_type": 'WARNING',
            "message": message,
            "cancel": False
        }       

    '''
    Check if any non bakable objects are connected to the selected
    objects and warn the user
    '''
    message = ""
    
    for object in high_res_objects:
        if not object_manager.can_be_bakable_high_res_object(object):
            if message == "":
                message = "The following objects are not bakable: "
            message += object.name + ", "
    
    if not message == "":
        #self.report({'ERROR'}, message)
        return {    
            "error_type": 'WARNING',
            "message": message,
            "cancel": False
        }  


    return None
    
class OBJECT_OT_list_high_res_objects_on_selected(bpy.types.Operator):
    '''
    Show message box with list of high res objects connected to selected objects
    '''

    bl_idname = "object.list_high_res_objects_on_selected"
    bl_label = "List high res from selected"
    bl_description = "Show message box with list of high res objects connected to selected objects"

    def execute(self, context):
        
        def draw(self, context):
            bake_objects = high_res_objects_manager.get_high_res_objects(context, context.selected_objects)

            if len(bake_objects) == 0:
                self.layout.label(text = "No bake objects")
            else:    
                i = 1
                for object in bake_objects:
                    self.layout.label(text = str(i) + ". " + object.name)
                    i = i + 1    

        context.window_manager.popup_menu(draw, title = "high res objects from selected objects", icon = 'INFO')
        
        return {'FINISHED'}



class OBJECT_OT_select_objects_with_missing_high_res(bpy.types.Operator):
    '''
    Select objects that does not have any objects in high res
    '''
    bl_idname = "object.select_objects_with_missing_high_res"
    bl_label = "Select missing high res"   
    bl_description = "Select objects that does not have any objects in high res"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        for object in context.view_layer.objects:
            if high_res_objects_manager.high_res_is_empty(context, object):
                object.select_set(state = True)
        return {'FINISHED'}
 
class OBJECT_OT_delete_bake_images(bpy.types.Operator):
    '''
    Delete all bake images
    '''
    bl_idname = "image.delete_bake_images"
    bl_label = "delete bake images"
    bl_description = "Delete all bake images"

    @classmethod
    def poll(cls, context):
        return bake_manager.get_bake_image_count(context) > 0

    def execute(self, context): 
        bake_manager.delete_bake_images(context, )
        return {'FINISHED'}

class IMAGE_OT_delete_image_by_index(bpy.types.Operator):
    '''
    Delete image by index
    '''
    bl_idname = "image.delete_image_by_index"
    bl_label = "Delete image by index"
    bl_description = "Delete image by index"

    image_index: IntProperty(
        name="Index of image to delete",
        description="Index of image to delete",
        min=-1, 
    )       

    def execute(self, context):   
        bpy.data.images.remove(bpy.data.images[self.image_index])
        return {'FINISHED'}    

class RENDER_OT_show_latest_baking_report(bpy.types.Operator):
    '''
    Show latest baking report
    '''
    bl_idname = "render.show_latest_baking_report"
    bl_label = "Show latest baking report"
    bl_description = "Show latest baking report"
    
    @classmethod
    def poll(cls, context):
        return context.window_manager.get('bake_report')

    def execute(self, context):   
        latest_report = context.window_manager.get('bake_report') # new win manager report
        if latest_report == None:
            latest_report = ["Baking report missing"]
        UI.show_info_window(context, latest_report, "Latest baking report")
        return {'FINISHED'}    

class OBJECT_OT_explode_selected_lowres_and_linked_high_res(bpy.types.Operator):
    '''
    Explode selected low res objects and linked high res objects
    '''
    bl_idname = "object.explode_selected_lowres_and_linked_high_res"
    bl_label = "Explode lowres and linked highres"
    bl_description = "Explode selected low res objects and linked high res objects"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None    

    def execute(self, context):   
        objects = context.selected_objects
        object_manager.explode_locations_of_objects_and_highres_objects(context, objects, 'EXPLODED')

        return {'FINISHED'}    

class OBJECT_OT_reset_location_of_lowres_and_highres(bpy.types.Operator):
    '''
    Reset location of lowres and highres after exploding objects
    '''
    bl_idname = "object.reset_location_of_lowres_and_highres"
    bl_label = "Reset location of selected objects after explosion"
    bl_description = "Reset location of selected objects after reposition (explosion) during the baking process"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None    

    def execute(self, context):   
        objects = context.selected_objects
        object_manager.reset_objects_original_locations(objects)
        return {'FINISHED'}    

class OBJECT_OT_pin_active_object(bpy.types.Operator):
    '''
    Adds active object to a property in window manager. 
    This property will be used to display "active object" in the UI
    '''
    bl_idname = "object.pin_active_object"
    bl_label = "Pin active object"
    bl_description = "Keeps the active object pinned in the UI"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None    

    def execute(self, context):   
        wm = context.window_manager
        if wm.get("pinned_active_object"):
            del wm["pinned_active_object"]
        else:
            wm["pinned_active_object"] = context.active_object

        return {'FINISHED'}   


class FILE_OT_open_bake_collection_folder(bpy.types.Operator):
    '''
    Open the folder of the bake collection
    '''
    bl_idname = "file.open_bake_collection_folder"
    bl_label = "Open bake collection folder"
    bl_description = "Open bake collection folder"
    

    collection_name: StringProperty(
        name="Bake collection name",
        default=""
    )    

    def execute(self, context):   
        
        try:
            file_manager.open_bake_collection_folder(context, self.collection_name)
        except:
            self.report({'ERROR'}, "Could not open folder")
        return {'FINISHED'}   



class BBB_OT_open_internet_link(bpy.types.Operator):
    '''
    Open internet link
    '''
    bl_idname = "bbb.open_internet_link"
    bl_label = "Open internet link"
    bl_description = "Open internet link"
    

    internet_link: StringProperty(
        name="Internet_link",
        default=""
    )    

    def execute(self, context):   
        
        try:
            webbrowser.open(self.internet_link)        
        except:
            self.report({'ERROR'}, "Could not open link")
        return {'FINISHED'}   

classes = (
    #RENDER_OT_bake_all_passes_in_collection,
    OBJECT_OT_uv_pack_per_collection,
    OBJECT_OT_uv_pack_objects_in_collection,
    #OBJECT_OT_bake_bake_pass_by_index,
    RENDER_OT_bake_with_bake_passes,
    RENDER_OT_bake_selected_objects,
    #RENDER_OT_bake_all_bake_collections,
    #OBJECT_OT_store_high_res_objects,
    #OBJECT_OT_select_stored_high_res_objects,
    #OBJECT_OT_add_stored_objects_to_high_res_on_selected,
    OBJECT_OT_list_high_res_objects_on_selected,
    #OBJECT_OT_list_stored_high_res_objects,
    #OBJECT_OT_delete_high_res_on_selected,
    OBJECT_OT_select_objects_with_missing_high_res,
    OBJECT_OT_delete_bake_images,
    IMAGE_OT_delete_image_by_index,
    RENDER_OT_show_latest_baking_report,
    OBJECT_OT_explode_selected_lowres_and_linked_high_res,
    OBJECT_OT_reset_location_of_lowres_and_highres,
    OBJECT_OT_pin_active_object,
    FILE_OT_open_bake_collection_folder,
    BBB_OT_open_internet_link
    
)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)

        