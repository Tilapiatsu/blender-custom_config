import bpy
from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)
from . import bake_passes
from . import high_res_objects_manager
from . import collection_manager

view3d_header_draw = lambda s,c: None
#----#
# UI #
#----#   

class RENDER_PT_bbb_settings(bpy.types.Panel):
    bl_idname = "BGM_PT_bake"
    bl_label = "Bystedts Blender Baker - Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        title_size = 0.6

        properties = scene.BBB_props

        #=================
        # Save and Load presets 

        box = layout.box()
        col = box.column()
        col.label(text = "Save and Load presets")
        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.operator('bbb.read_preset_file', icon = 'FILE_FOLDER')

        grid.operator('bbb.write_preset_file', icon = 'FILE_NEW')

        #BOX==================

        col = layout.column()
        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text='General settings')
        props = grid.operator('bbb.open_internet_link', text = "", icon = 'QUESTION')
        props.internet_link = "https://youtu.be/T4GVVQjPi1Q?t=422"

        col.separator()

        col.prop(scene.BBB_props, "guided_ui", text = "Guided UI")



        box = layout.box()
        col = box.column()

        grid = col.grid_flow(row_major = True, columns = 2,)

        col.label(text = "Image settings")

        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text='Path')
        grid.prop(scene.BBB_props, "dir_path", text = "")

        if scene.BBB_props.guided_ui == True and scene.BBB_props.dir_path == "":
            return
        
        guided_ui_message = handle_guided_UI(context)
        if guided_ui_message['step']  == 1:
            return

        # Resolution
        grid.label(text='Resolution X')
        grid.prop(scene.BBB_props, "resolution_x", text="")

        grid.label(text='Resolution Y')
        grid.prop(scene.BBB_props, "resolution_y", text="")

        grid.label(text='Resolution %')
        grid.prop(scene.BBB_props, "resolution_percentage", text="", slider = True)


        col.separator(factor = 1.0)
        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text='Naming options')
        grid.prop(scene.BBB_props, "bake_image_naming_option", text="")

        grid.label(text='Naming separator')
        grid.prop(scene.BBB_props, "bake_image_separator", text = "")

        #=================
        # Bake settings

        box = layout.box()
        col = box.column(align = True)

        grid = col.grid_flow(row_major = True, columns = 2,)

        col.label(text = "Bake settings")

        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text='Bake workflow')
        grid.prop(scene.BBB_props, "bake_workflow", text = "")

        col.separator(factor = 1.0)
        grid = col.grid_flow(row_major = True, columns = 2,)

        if scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':

            grid.label(text='Cage')
            grid.prop(scene.BBB_props, "use_cage", text = "")           

            grid.label(text='Extrusion')
            grid.prop(scene.BBB_props, "cage_extrusion", text = "")

            col.separator(factor = 1.0)
            grid = col.grid_flow(row_major = True, columns = 2,)
        
        grid.label(text='Post process anti aliasing')
        grid.prop(scene.BBB_props, "use_post_process_anti_aliasing", text = "")

        grid.label(text='AA / Sub pixel sampling')
        grid.prop(scene.BBB_props, "sub_pixel_sample", text = "")

        average_resolution = (properties.resolution_x + properties.resolution_y) / 2
        margin_value = (max(int(average_resolution) / 128, 4)) * properties.margin_multiplier

        margin_value = int(margin_value)

        grid.label(text='Margin multiplier (' + str(margin_value) + " px)")
        grid.prop(properties, "margin_multiplier", text = "")

        col.separator(factor = 1.0)
        grid = col.grid_flow(row_major = True, columns = 2,)

        if scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':
            grid.label(text='Fix skewed normals method') 
            grid.prop(properties, "skew_normals_method", text = "")
            
            if scene.BBB_props.skew_normals_method == "ANGLE":
                grid.label(text='Skewed normal angle') 
                grid.prop(properties, "skew_normals_angle", text = "")

            grid.label(text='Optimize by joining high poly objects') 
            grid.prop(properties, "allow_high_poly_objects_to_join", text = "")            


        
class RENDER_PT_bbb_image_settings(bpy.types.Panel):
    
    bl_idname = "BGM_PT_image_format"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B B B'

    bl_parent_id = 'BGM_PT_bake'
    bl_label = "Image file settings"

    bl_options = {"HEADER_LAYOUT_EXPAND"}
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        BBB_props = context.scene.BBB_props.image_settings

        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text='file format')
        grid.prop(BBB_props, "file_format", text = "")

        grid.label(text='Color')
        grid.prop(BBB_props, "color_mode", text = "")

        grid.label(text='Color depth')
        grid.prop(BBB_props, "color_depth", text = "")

        if BBB_props.file_format in ['PNG']:
            grid.label(text='Compression')
            grid.prop(BBB_props, "compression", text = "") 

        if BBB_props.file_format in ['JPEG', 'JPEG2000', 'AVI_JPEG']:
            grid.label(text='Quality')
            grid.prop(BBB_props, "quality", text = "")              

        if BBB_props.file_format in ['TIFF']:
            grid.label(text='Compression')
            grid.prop(BBB_props, "tiff_codec", text = "") 

        if BBB_props.file_format in ['OPEN_EXR', 'OPEN_EXR_MULTILAYER']:
            grid.label(text='Compression')
            grid.prop(BBB_props, "exr_codec", text = "") 

def object_list_to_string(object_list, max_string_length = 30):
    
    list_string = ""
    string_length = 30
    for index, object in enumerate(object_list):
        if index > 0:
            list_string += ", "
        list_string += object.name
        
        if len(list_string) > max_string_length:
            list_string = list_string[0:string_length] + "..."
    
    return list_string

class OBJECT_PT_bake_collections(bpy.types.Panel):
    

    bl_idname = "BBB_PT_bake_collections"
    bl_label = "Bake collections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'

    def draw(self, context):

        layout = self.layout
        title_size = 0.6       
        col = layout.column()

        guided_ui_message = handle_guided_UI(context)
        if guided_ui_message['step'] == 1:
            col.label(text = guided_ui_message['message'])
            return

        box = layout.box()
        col = box.column()

        grid = col.grid_flow(row_major = True, columns = 2,)

        grid.label(text="Bake collections")
        props = grid.operator('bbb.open_internet_link', text = "", icon = 'QUESTION')
        props.internet_link = "https://youtu.be/T4GVVQjPi1Q?t=675"



        bake_collections = collection_manager.get_bake_collections_by_scene(context.scene)

        row = col.row()

        # Make the button big if there are no bake collections in order to call attention
        if len(bake_collections) == 0:
            row.scale_y = 2.0
            props = row.operator('collection.create_bake_collection', icon = 'ERROR')
        else:
            props = row.operator('collection.create_bake_collection')
        
        props.add_selected_objects = True
        
        for index, collection in enumerate(bake_collections):
           

            collection_box = col.box()
            
            #row = collection_box.row()

            collection_col = collection_box.column()



            grid = collection_col.grid_flow(row_major = True, columns = 2,)
            #grid.label(text = collection.name)
            grid.prop(data = collection, property = "name", text = "")


            props = grid.operator('collection.delete_collection_by_name', text = "", icon = 'X')
            props.collection_name = collection.name


            grid = collection_col.grid_flow(row_major = True, columns = 3,)

            props = grid.operator('render.bake_with_bake_passes', text = "Bake", icon = 'RESTRICT_RENDER_OFF')
            props.bake_scope = 'BAKE_SPECIFIC_BAKE_COLLECTION'  
            props.bake_collection_index = index 

            props = grid.operator('object.uv_pack_objects_in_collection', text = "UV pack", icon = 'UV')
            props.collection_name = collection.name
           
            props = grid.operator('file.open_bake_collection_folder', text = "Open", icon = 'FILE_FOLDER')
            props.collection_name = collection.name



        
        if context.scene.BBB_props.guided_ui == True and len(bake_collections) == 0:
            return


        row = col.row()
        row.scale_y = 2.0

        if len(bake_collections) > 0:
            props = row.operator('render.bake_with_bake_passes', text = "Bake all collections", icon = 'RESTRICT_RENDER_OFF')
            props.bake_scope = 'BAKE_ALL_BAKE_COLLECTIONS'    

        #BOX==================
        box = layout.box()
        col = box.column()


        props = col.operator('render.bake_selected_objects', text = "Bake selected objects", icon = 'RESTRICT_RENDER_OFF')
        props.bake_scope = 'BAKE_SELECTED_OBJECTS'

        col.operator('render.show_latest_baking_report', icon = 'INFO')

        col.operator('image.delete_bake_images', icon = 'EVENT_X')

        props = col.operator('object.create_bake_preview', icon = 'SHADING_TEXTURE')       
        props.preview_type = "PREVIEW_ON_SELECTED"

        props = col.operator('object.reset_location_of_lowres_and_highres', icon = 'ERROR')       

        props = col.operator('scene.delete_temporary_bake_scenes', icon = 'ERROR')       



class OBJECT_PT_high_res_objects(bpy.types.Panel):
    bl_idname = "BBB_PT_high_res_objects"
    bl_label = "Connect high res objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'

    def draw(self, context):
        layout = self.layout
        
        # Guided UI
        col = layout.column()
        guided_ui_message = handle_guided_UI(context)
        if guided_ui_message['step'] < 4:
            col.label(text = guided_ui_message['message'])
            return   

        #BOX==================
        box = layout.box()
        col = box.column()    



        # Active [pinned] object in UI
        UI_object = get_active_object_from_UI(context)

        grid = col.grid_flow(row_major = True, columns = 2,)

        if (context.scene.BBB_props.guided_ui == True 
            and context.scene.BBB_props.bake_workflow == 'LOWRES_ONLY'):
            col.label(text="Highres objects are not used in the current baking workflow")
            return

        grid.label(text="Active object")
        props = grid.operator('bbb.open_internet_link', text = "", icon = 'QUESTION')
        props.internet_link = "https://youtu.be/T4GVVQjPi1Q?t=1101"



        row = col.row()
        row.scale_y = 2.0
        if UI_object == None:
            row.label(text='No active object')
            return
        if active_object_in_UI_is_pinned(context):
            row.operator('object.pin_active_object', text = UI_object.name, icon = 'PINNED', depress = True)
        else:
            row.operator('object.pin_active_object', text = UI_object.name, icon = 'UNPINNED', depress = False)
        
        col.separator()

        # Linked high res objects
        high_res_objects_list = high_res_objects_manager.get_high_res_objects(context, [UI_object])
        col.label(text = "Linked high res objects: " + str(len(high_res_objects_list)))

        # UI list
        col.template_list("OBJECT_UL_high_res_objects", "", UI_object, "high_res_objects", UI_object, "active_high_res_object", rows = 3)

        # UI list buttons
        grid = col.grid_flow(row_major = True, columns = 2, even_columns = True)
        grid.operator('object.add_selected_objects_to_high_res_on_active', text = "Add selected", icon = 'ADD')
        grid.operator('object.remove_selected_objects_from_high_res_on_active', text = "Remove selected", icon = 'REMOVE')

        grid.operator('object.add_high_res_object_slot', text = "Add slot", icon = 'ADD')
        grid.operator('object.remove_empty_high_res_object_slots', text = "Remove empty slots", icon = 'REMOVE')
        
   
        #BOX==================
        box = layout.box()
        col = box.column()  

        grid = col.grid_flow(row_major = True, columns = 1, even_columns = True)
        grid.operator('object.popupwin_find_hipoly_by_bounding_box', icon='VIEWZOOM')
        grid.operator('object.select_high_res_objects', icon='RESTRICT_SELECT_OFF')
        grid.operator('object.clear_high_res_objects_from_selected', text = "Remove all high poly from selected", icon = 'CANCEL')

class OBJECT_UL_high_res_objects(bpy.types.UIList):
    # Code reference: UI_panel_simple in blender python templates
    # This creates an UI list with images in the blender file

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        image = item
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                #layout.prop(item, "name", text="", emboss=False, icon_value=icon)
                layout.prop(item, "high_res_object", text="", emboss=True, icon_value=icon)
            
            else:
                layout.label(text="test label", translate=False, icon_value=icon)
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def filter_items(self, context, data, propname): 
        """
        Code for using filter and order items in the UIList for 
        connected high res objects.
        """
        filtered = [] 
        ordered = [] 

        items = getattr(data, propname)
       

        # Initialize with all items visible
        filtered = [self.bitflag_filter_item] * len(items)    

        for i, item in enumerate(items):
            if item.high_res_object == None:
                continue
            object_name = item.high_res_object.name.upper()
            filter_string = self.filter_name.upper()
            if object_name.find(filter_string) == -1:
                filtered[i] &= ~self.bitflag_filter_item            
        
        #TODO:
        # I can't seem to get sorting to work. Ignore for now
        if self.use_filter_sort_alpha:
            sort_items = bpy.types.UI_UL_list.sort_items_helper
        else:
            pass
        
        return filtered, ordered


class OBJECT_PT_bbb_bake_passes(bpy.types.Panel):
    bl_idname = "CGM_PT_bake_passes"
    bl_label = "Bake passes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        title_size = 0.6

        panel_col = layout.column()

        grid = panel_col.grid_flow(row_major = True, columns = 2,)

        grid.label(text="")
        props = grid.operator('bbb.open_internet_link', text = "", icon = 'QUESTION')
        props.internet_link = "https://youtu.be/T4GVVQjPi1Q?t=842"


        guided_ui_message = handle_guided_UI(context)
        if guided_ui_message['step'] < 3:
            panel_col.label(text = guided_ui_message['message'])
            return 

        row = panel_col.row()
        row.scale_y = 2.0
        if len(context.scene.bake_passes) == 0:
            row.operator('ui.add_bake_pass', icon = 'ERROR')
        else:
            row.operator('ui.add_bake_pass')
        

        for index, bake_pass in enumerate(context.scene.bake_passes):
           
            layout.separator(factor = 1.0)

            bake_pass_box = layout.box()
            main_col = bake_pass_box.column()
           
            
            grid = main_col.grid_flow(row_major = True, columns = 2, even_columns = True)

            grid.label(text = "Bake type")          
            grid.prop(bake_pass, "bake_type", text="")

            

            main_col.separator(factor = 1.0)

            if bake_pass.bake_type == "DISPLACEMENT" and context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':
                main_col.label(text = "PLEASE NOTE:")
                main_col.label(text = "Displacement values are only projected")
                main_col.label(text = "and not recalculated in this baking workflow")

            grid = main_col.grid_flow(row_major = True, columns = 3, even_columns = True)

            #row = main_col.row()
            
            grid.scale_y = 1.5

            props = grid.operator('render.bake_selected_objects', text = "Bake", icon = 'RESTRICT_RENDER_OFF')
            props.bake_scope = 'BAKE_SELECTED_WITH_SPECIFIC_BAKE_PASS'  
            props.bake_pass_index = index 

            depress = bake_pass.preview_bake_texture
            props = grid.operator('object.preview_bake_texture', text = "", icon = 'HIDE_OFF', depress = depress)
            props.bake_pass_index = index   

            props = grid.operator('render.delete_bake_pass', text = "", icon = 'PANEL_CLOSE')
            props.bake_pass_index = index   

            #main_col.separator(factor = 1.0)

            row = main_col.row()
            row.scale_y = 0.9
            if not context.scene.bake_passes[index].ui_display:
                # Expand
                props = main_col.operator('render.toggle_bake_pass_ui_display', text = "", icon = 'TRIA_DOWN')
                props.bake_pass_index = index             
                continue
            else:
                # Collapse
                props = main_col.operator('render.toggle_bake_pass_ui_display', text = "", icon = 'TRIA_UP', depress = True)
                props.bake_pass_index = index                 

            grid = main_col.grid_flow(row_major = True, columns = 2,)
            grid.label(text = "Name")          
            grid.prop(bake_pass, "name", text="")

            # Normal 
            if bake_pass.bake_type == "NORMAL":
                grid.label(text = "Space")
                grid.prop(bake_pass, "normal_space", text="")
                
                
                if bake_pass.normal_space == "TANGENT":
                    grid.label(text = "Normal map type")
                    grid.prop(bake_pass, "normal_map_type", text="")
                elif bake_pass.normal_space == "OBJECT":
                    grid.label(text = "Swzzle X")
                    grid.prop(bake_pass, "normal_r", text="")   
                    grid.label(text = "Swzzle Y")
                    grid.prop(bake_pass, "normal_g", text="")
                    grid.label(text = "Swzzle Z")
                    grid.prop(bake_pass, "normal_b", text="")
                ''''''

            # AOV 
            if bake_pass.bake_type == "AOV":
                grid.label(text = "AOV name")
                grid.prop(bake_pass, "aov_name", text="")

                grid.label(text = "AOV data type")
                grid.prop(bake_pass, "aov_data_type", text="")

            # AOV 
            if bake_pass.bake_type == "POINTINESS":
                grid.label(text = "Pointiness contrast")
                grid.prop(bake_pass, "pointiness_contrast", text="")

            # Channel transfer
            if bake_pass.bake_type == "CHANNEL_TRANSFER":
                grid.label(text = "Image name override")
                grid.prop(bake_pass, "image_name_override", text = "")

                main_col.separator()
                main_col.label(text = "Note that channel override output ")
                main_col.label(text = "is forced to open EXR for correct values")
                main_col.separator()


                # Red
                main_col.label(text = "Red channel")
                grid = main_col.grid_flow(row_major = True, columns = 2,)

                props = grid.operator('object.popupwin_select_bake_pass', text = "Set R source")
                props.bake_pass_index = index 
                props.channel = "R_source"
                grid.label(text = bake_pass.R_source)     

                grid.label(text = "R source channel")
                grid.prop(bake_pass, "transfer_source_channelR", text = "")

                main_col.separator()

                # Green
                main_col.label(text = "Green channel")
                grid = main_col.grid_flow(row_major = True, columns = 2,)

                props = grid.operator('object.popupwin_select_bake_pass', text = "Set G source")
                props.bake_pass_index = index 
                props.channel = "G_source"
                grid.label(text = bake_pass.G_source)  

                grid.label(text = "G source channel")
                grid.prop(bake_pass, "transfer_source_channelG", text = "")

                main_col.separator()

                # Blue
                main_col.label(text = "Blue channel")
                grid = main_col.grid_flow(row_major = True, columns = 2,)

                props = grid.operator('object.popupwin_select_bake_pass', text = "Set B source")
                props.bake_pass_index = index 
                props.channel = "B_source"
                grid.label(text = bake_pass.B_source)                                             
 
                grid.label(text = "B source channel")
                grid.prop(bake_pass, "transfer_source_channelB", text = "")
 
                # Alpha
                main_col.label(text = "Alpha channel")
                grid = main_col.grid_flow(row_major = True, columns = 2,)

                props = grid.operator('object.popupwin_select_bake_pass', text = "Set A source")
                props.bake_pass_index = index 
                props.channel = "A_source"
                grid.label(text = bake_pass.A_source)                                             
 
                grid.label(text = "Alpha source channel")
                grid.prop(bake_pass, "transfer_source_channelA", text = "")
 
                continue

            # Bake locations
            if context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':
                grid.label(text = "Bake locations")
                grid.prop(bake_pass, "bake_locations", text="")
            
            # Sample type
            grid.label(text = "Sample type")
            grid.prop(bake_pass, "sample_type", text="")

            if bake_pass.sample_type == 'SET':
                grid2 = main_col.grid_flow(row_major = True, columns = 2)
                grid2.label(text = "  ")
                grid2.prop(bake_pass, "samples", text = "Samples")


            grid = main_col.grid_flow(row_major = True, columns = 2)

            grid.label(text = "Bake scene")
            grid.prop(bake_pass, "bake_scene", text="")

            grid.label(text = "Post process")
            grid.prop(bake_pass, "post_process", text="")




class OBJECT_PT_bbb_report(bpy.types.Panel):
    bl_idname = "CGM_PT_report"
    bl_label = "Links"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'

    def draw(self, context):
        layout = self.layout
        title_size = 0.6
        
        col = layout.column()

        col.label(text = "Support Blender development")

        props = col.operator('bbb.open_internet_link', text = "Blender dev fund" )
        props.internet_link =internet_link = 'https://fund.blender.org/'


        col.label(text = "Tutorial")

        props = col.operator('bbb.open_internet_link', text = "Quick start tutorial" )
        props.internet_link =internet_link = 'https://youtu.be/T4GVVQjPi1Q'

        col.separator()

        col.label(text = "Suggestions and bugs")

        props = col.operator('bbb.open_internet_link', text = "Suggest feature" )
        props.internet_link =internet_link = 'https://docs.google.com/forms/d/e/1FAIpQLSej7HguOiZqDrjidCi6IqWifC4yI9Qxn8owW4n4PTLoJ1zYdA/viewform?usp=pp_url&entry.235238798=Feedback+or+suggestion'
        
        props = col.operator('bbb.open_internet_link', text = "Report bug")
        props.internet_link =internet_link = 'https://docs.google.com/forms/d/e/1FAIpQLSej7HguOiZqDrjidCi6IqWifC4yI9Qxn8owW4n4PTLoJ1zYdA/viewform?usp=pp_url&entry.235238798=Bug'


        col.label(text = "Other (no support)")

        props = col.operator('bbb.open_internet_link', text = "Gumroad")
        props.internet_link =internet_link = 'https://3dbystedt.gumroad.com/'

        props = col.operator('bbb.open_internet_link', text = "Twitter")
        props.internet_link =internet_link = 'https://twitter.com/3dbystedt'

        props = col.operator('bbb.open_internet_link', text = "YouTube")
        props.internet_link =internet_link = 'https://www.youtube.com/user/morriscowboy'

        props = col.operator('bbb.open_internet_link', text = "Artstation")
        props.internet_link =internet_link = 'https://www.artstation.com/dbystedt'


class OBJECT_PT_bbb_debug_panel(bpy.types.Panel):
    bl_idname = "CGM_PT_bake_objects"
    bl_label = "CGM debug"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = 'B B B'

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        title_size = 0.6
        
        col = layout.column()
        
        guided_ui_message = handle_guided_UI(context)
        if guided_ui_message['step'] < 3:
            col.label(text = guided_ui_message['message'])
            return 

        #BOX==================
        box = layout.box()
        col = box.column()



        col.label(text='Test operators during dev')
        col.operator('object.test_a_function')
        

class UI_OT_cgm_add_bake_pass(bpy.types.Operator):
    '''
    Add bake pass to UI
    '''
    bl_idname = "ui.add_bake_pass"
    bl_label = "Add bake pass"

    print_string : StringProperty()

    def execute(self, context):
        #import bake_passes
        bake_passes.add_bakepass(context, bake_passes.BakeType.DIFFUSE)
        return {'FINISHED'}

class UI_OT_cgm_remove_bake_pass(bpy.types.Operator):
    '''
    Remove bake pass from UI
    '''
    bl_idname = "ui.remove_bake_pass"
    bl_label = "Remove bake pass"

    def execute(self, context):
        return {'FINISHED'}   

class OBJECT_OT_test_a_function(bpy.types.Operator):
    '''
    Test a function
    '''
    
    bl_idname = "object.test_a_function"
    bl_label = "Test a function for DEV"

    def execute(self, context):
        from . import object_manager
        from . import bake_manager
        from . import settings_manager
        import mathutils

        print("Init test a function")
        import time
        print(time.asctime())

        source_object = bpy.data.objects['a']
        target_object = bpy.data.objects['b']
        bake_manager.fix_skew_normals(
            context, 
            [source_object], 
            [target_object], 
            )

        return {'FINISHED'}  

#---------------#
# POPUP windows #
#---------------# 
              

class OBJECT_OT_popupwin_promp_yes_no(bpy.types.Operator):
    '''
    Ask user yes/no
    '''
    # This is displayed as a popup window with buttons yes/no

    bl_idname = "object.popupwin_promp_yes_no"
    bl_label = ""
    bl_description = ""


    def execute(self, context): 
        def draw(self, context):

            col = self.layout.column()

            col.label(text = "my text")

        menu_title = "User prompt"    
        context.window_manager.popup_menu(draw, title = menu_title, icon = 'INFO')
        
        return {'FINISHED'}



class OBJECT_OT_popupwin_find_hipoly_by_bounding_box(bpy.types.Operator):
    '''
    Find matching hipoly objects based on each selected objects bounding box
    '''
    # This is displayed as a popup window

    bl_idname = "object.popupwin_find_hipoly_by_bounding_box"
    bl_label = "Find highpoly by bounding box"
    bl_description = "Find the first matching hipoly object based on each selected objects bounding box."

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context): 
        def draw(self, context):
            scene_names = bpy.data.scenes.keys()
            my_list = ['All scenes'] + scene_names
            
            for scene in my_list:
                col = self.layout.column_flow(columns = 3, align = True)

                # Scene
                col.label(text = scene, icon = "SCENE_DATA")

                # World space
                props = col.operator('object.find_hipoly_by_bounding_box',
                    text= "World space",
                    emboss = True
                )
                props.source_scene = scene
                props.space = "WORLD"

                # Object space
                props = col.operator('object.find_hipoly_by_bounding_box',
                    text= "Object space",
                    emboss = True
                )
                props.source_scene = scene
                props.space = "OBJECT"    


        menu_title = "Select scene and space"      
        context.window_manager.popup_menu(draw, title = menu_title, icon = 'INFO')
        
        return {'FINISHED'}


class OBJECT_OT_popupwin_select_bake_pass(bpy.types.Operator):
    '''
    Select bake pass for channel transfer etc
    '''

    bl_idname = "object.popupwin_select_bake_pass"
    bl_label = "Show popup select bake pass"
    bl_description = "Show popup select bake pass"
    #bl_options = {'REGISTER', 'UNDO'}

    bake_pass_index: IntProperty(
        default = -1
    )

    channel: StringProperty(
        default = ""
    )

    def execute(self, context):
        
        # Temporary storing variables in window_manager
        # since I can't figure out how to use them as arguments in 'draw'
        wm = context.window_manager
        wm['bake_pass_index'] = self.bake_pass_index
        wm['channel'] = self.channel

        def draw(self, context,):
            col = self.layout.column_flow(columns = 1, align = True)

            wm = context.window_manager

            for bake_pass in context.scene.bake_passes:
                if bake_pass.bake_type == "CHANNEL_TRANSFER":
                    continue
                
                props = col.operator("object.select_bake_pass", text = bake_pass.bake_type)
                
                print("test " + str(wm['bake_pass_index']))
                props.bake_pass_index = wm['bake_pass_index']
                props.channel = wm['channel']
                props.value = bake_pass.bake_type

            del wm['bake_pass_index']
            del wm['channel']

        menu_title = "Select bake pass"
        # TODO: Solve error on row below
        #draw_function = draw(self = self, context = context, operator = self, bake_pass_index = self.bake_pass_index, channel = self.channel)
        
        
        #context.window_manager.popup_menu(draw_function, title = menu_title, icon = 'INFO')
        context.window_manager.popup_menu(draw, title = menu_title, icon = 'INFO')

        return {'FINISHED'}

class OBJECT_OT_select_bake_pass(bpy.types.Operator):
    '''
    Select bake pass for channel transfer etc
    '''

    bl_idname = "object.select_bake_pass"
    bl_label = "Select bake pass"
    bl_description = "Select bake pass"
    #bl_options = {'REGISTER', 'UNDO'}

    bake_pass_index: IntProperty(
        default = -1
    )

    channel: StringProperty(
        default = ""
    )

    value: StringProperty(
        default = ""
    )

    def execute(self, context):
        
        # Bake pass where we set values (i.e. bake pass with channel transfer)
        bake_pass = context.scene.bake_passes[self.bake_pass_index]
        
        # Image name that we transfer channel from
        bake_pass[self.channel] = self.value

        return {'FINISHED'}

def show_info_window(context, info_text = "", info_title = "Info", icon = 'INFO'):
    '''
    Shows info window
    Assumes that info_text is a string array and makes one text row per item
    '''
    def draw(self, context):
        for row_info in info_text:
            self.layout.label(text=row_info)

    context.window_manager.popup_menu(draw, title = info_title, icon = icon)

#------------#
# PROPERTIES #
#------------#  

class RENDER_PG_bbb_image_settings(bpy.types.PropertyGroup):

    items = [('PNG', 'PNG', ""),
            ('JPEG', 'JPEG', ""),
            ('TARGA', 'TGA', ""),
            ('TIFF', 'TIF', ""),
            ('DPX', 'DPX', ""),
            ('BMP', 'BMP', ""),
            ('OPEN_EXR', 'OpenEXR', ""),
            ('OPEN_EXR_MULTILAYER', 'OpenEXR MultiLayer', ""),
    ]

    file_format: EnumProperty(
        name="Image format",
        description="Choose which file format that images are saved to ",
        items=items,
        )   


    exr_codec_items = [
            ('DWAA', 'DWAA (lossy)', ""),
            ('ZIPS', 'ZIPS (Lossless)', ""),
            ('RLE', 'RLE (Lossless', ""),
            ('PIZ', 'PIZ (Lossless', ""),
            ('ZIP', 'ZIP (Lossless', ""),
            ('PXR24', 'Pxr24 (lossy)', ""),
    ]

    exr_codec: EnumProperty(
    name="Exr codec",
    description="Compression mode for EXR",
    items=exr_codec_items,
    default = 'ZIP'
    )   

    tiff_codec_items = [
            ('PACKBITS', 'Pack bits', ""),
            ('LZW', 'LZW', ""),
            ('DEFLATE', 'DEFLATE', ""),
            ('NONE', 'None', ""),
    ]
    
    tiff_codec: EnumProperty(
    name="Tiff codec",
    description="Compression mode for TIFF",
    items=tiff_codec_items,
    default = 'LZW'
    )   

    jpeg2000_codec_items = [
            ('JP2', 'JP2', ""),
            ('J2K', 'J2K', ""),
    ]
    
    jpeg2k_codec: EnumProperty(
    name="JPEG 2000 codec",
    description="Compression mode for JPEG 2000",
    items=jpeg2000_codec_items
    )   

    def item_callback(self, context):
        
        if self.file_format in ['BMP', 'JPEG', 'CINEON', 'HDR', 'AVI_JPEG', 'AVI_RAW', 'FFMPEG']:
            return [
                ('RGB', 'RGB', ''),
                ('BW', 'BW', '')
            ]
        else:
            return [
                ('RGB', 'RGB', ''),
                ('RGBA', 'RGBA', ''),
                ('BW', 'BW', ''),
            ]



    color_mode: EnumProperty(
    name="Color",
    description= "Choose BW for saving grayscale images, \
        RGB for saving red, green and blue channels, \
        and RGB for saving red, green, blue and alpha channels",
    items=item_callback,

    )   

    def item_callback(self, context):
        
        if self.file_format in ['BMP', 'IRIS', 'JPEG', 'TARGA', 'TARGA_RAW', 'AVI_JPEG', 'AVI_RAW', 'FFMPEG']:
            return [('8', '8', "")
                ]
        elif self.file_format in ['PNG', 'TIFF', ]:
            return [('8', '8', ""),
                ('16', '16', "")
                ]
        elif  self.file_format in ['CINEON',]:
            return [('10', '10', "")]
        elif self.file_format in ['OPEN_EXR_MULTILAYER', 'OPEN_EXR', ]:
            return [('16', '16', ""),
                ('32', '32', "")
                ]
        elif self.file_format in ['EXR']:
            return [('32', '32', "")
            ]
        elif self.file_format in ['DPX']:
            return [('8', '8', ""),
                ('10', '10', ""),
                ('12', '12', ""),
                ('16', '16', "")
                ]
        else:
            return [('8', '8', ""),
                ('16', '16', ""),
                ('32', '32', "")
                ]
                

    color_depth: EnumProperty(
    name="Color depth",
    description= "Bit depth per channel",
    items=item_callback
    )     

    compression: IntProperty(
    name="Compression",
    description= "Amount of time to determine best compression: "\
        "0= no compression with fast file output, \
        100 = maximum lossless compression with slow file output",
    subtype = 'PERCENTAGE',
    min = 0,
    max = 100,
    default = 15

    )       

    quality: IntProperty(
    name="Compression",
    description= "Quality for image formats that support lossy compression",
    subtype = 'PERCENTAGE',
    min = 0,
    max = 100,
    default = 90
    )   


class RENDER_PG_bystedts_blender_baker(bpy.types.PropertyGroup):
    
    samples: IntProperty(
        name="Samples",
        description="Render samples",
        min=1, max=512,
        default=1,
    )

    dir_path: StringProperty(
        name="directory path",
        subtype="DIR_PATH",
    )

    number_of_stored_high_res_objects: IntProperty(
        name = "Number of stored high res objects"
    )

    use_bake_scene: BoolProperty(
        name = "Use bake scene",
        description = "Create a temporary scene and do the bake there, since it's faster"

    )

    bake_scene_items = [
        ("CURRENT", "Current scene", "", 0),
        ("TEMPORARY", "Temporary scene", "", 1),
    ]    
    bake_scene_type: bpy.props.EnumProperty(
        name="Bake scene type", 
        default = "TEMPORARY", 
        items = bake_scene_items
        )
    
    
    bake_image_naming_option_items = [
        ("TYPE_COLLECTION", "Bake pass type + collection name", "This creates on texture per collection", 0),
        ("NAME_COLLECTION", "Bake pass name + collection name", "This creates on texture per collection", 2),
        ("COLLECTION_TYPE", "Collection name + bake pass type", "This creates on texture per collection", 4),
        ("COLLECTION_NAME", "Collection name + bake pass name", "This creates on texture per collection", 6),
    ]   

    bake_image_naming_option: bpy.props.EnumProperty(
        name="Bake image naming options", 
        default = "TYPE_COLLECTION", 
        items = bake_image_naming_option_items,
        description = "Naming format for bake textures"
        )

    bake_image_separator_items = [
        ("_", "Underscore _", "", 0),
        (".", "Period .", "", 1),
        ("-", "Dash -", "", 3)
    ]   
    
    bake_image_separator: bpy.props.EnumProperty(
        name="Bake image name separator", 
        default = "_", 
        items = bake_image_separator_items,
        description = "The separator string to put in the name of the bake image"
        )

    bake_workflow_items = [
        ('HIGHRES_TO_LOWRES', "Highres to lowres", "Bake from connected high res object to selected lowres objects", 0),
        ('LOWRES_ONLY', "Bake lowres surface", "Bake the shaded surface from each selected \"lowres\" object", 1),
    ]   

    bake_workflow: bpy.props.EnumProperty(
        name="Bake workflow", 
        default = 'HIGHRES_TO_LOWRES', 
        items = bake_workflow_items,
        description = "Choose which workflow should be used during baking"
        )    

    sub_pixel_sample_items = [
        ("1", "X 1", "", 0),
        ("2", "X 2", "", 1),
        ("4", "X 4", "", 2),       
    ]

    use_post_process_anti_aliasing: BoolProperty(
        name = "Post process anti aliasing",
        description = "Apply anti aliasing with compositor after baking. This option is fast",
        default = True
    )

    sub_pixel_sample: bpy.props.EnumProperty(
        name="Sub pixel sample", 
        description = "Higher sub pixel sample improves anti aliasing. Increases render time significantly", 
        items = sub_pixel_sample_items
        )
    
    use_cage: BoolProperty(
        name = "Generate cage",
        description = "Generating a cage can remove artefacts when baking objects with sharp edges",
        default = True
    )

    cage_extrusion: bpy.props.FloatProperty(
        name="Extrusion", 
        description = "Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes.", 
        default = 0.2
        )

    margin_multiplier: bpy.props.FloatProperty(
        name="Margin multiplier", 
        description = "Multiplies the margin. Lower this if the pixel values bleeds over to other uv islands", 
        default = 1,
        max = 1,
        min = 0
        )

    skew_normals_items = [
        ('NONE', 'No skew angle fix', "Don't try to fix skewed normals"),
        ('ANGLE', 'Angle', "Fix skewed normals by angle"),
        ('WEIGHT', 'Bevel weight', 'Fix skewed normals by bevel weight')
    ]

    skew_normals_method: EnumProperty(
        name="Skew normals method",
        description="Fix skewed normals by angle or weight",
        default = 'NONE',
        items=skew_normals_items
    )   

    skew_normals_angle: IntProperty(
        name="Skew normals angle",
        description="Fix skewed normals on edges above this angle",
        subtype = 'ANGLE',
        default = 30,
        min = 0,
        max = 180
    )      

    allow_high_poly_objects_to_join: BoolProperty(
        name="Optimize by joining high poly objects",
        description="Optimize baking time by joining high res objects. "\
            "This can cause issues when using GENERATED as texture mapping"\
            " since joining will change the object bounding box. This will in turn affect"\
            " auto texture space. Consider using OBJECT as texture mapping instead of GENERATED if possible",
        default = True,   
    )


    def item_callback(self, context):
        # value, ui label, mouse hover info
        my_list = []
        for name in bpy.data.scenes.keys():
            my_list.append((name, name, ""))
        return(
            my_list
        )


    scene_names: EnumProperty(
    items=item_callback, name="Scenes", description='Scene names'
    )

    items = [('WORLD', 'World', "Bake in world space"),
        ('OBJECT', 'Object', 'Bake in object space')
    ]

    bake_locations: EnumProperty(
    name="Bake space",
    description="Bake in object or world space",
    items=items
    )   


    items = [('WORLD', 'World', "Find match in world space"),
            ('OBJECT', 'Object', 'Find match in object space')
    ]

    match_space: EnumProperty(
    name="Bounding box space",
    description="Match objects by bounding box by using WORLD or OBJECT space",
    items=items
    )


    def execute(self, context):
        #self.resolution = 512
        pass



    resolution_x: IntProperty(
        name = "Resolution X",
        description = "Numbers of horisontal pixels in the baked image",
        min = 4,
        max = 8192,
        default = 512
    )

    resolution_y: IntProperty(
        name = "Resolution Y",
        description = "Numbers of vertical pixels in the baked image",
        min = 4,
        max = 8192,
        default = 512
    )

    resolution_percentage: IntProperty(
        name = "Resolution %",
        description = "Percentage scale for the baked image",
        min = 1,
        max = 500,
        soft_max = 100,
        default = 100
    )    

    def update_progress(self, context):  
        '''
        This function is called when the progress bar is updated.
        It redraws the area 'VIEW_3D'
        '''
        areas = context.window.screen.areas  
        for area in areas:  
            if area.type == 'VIEW_3D':  
                area.tag_redraw() 
    
    progress_percentage: IntProperty(
        name = "Progress",
        description = "Baking progress",
        min = 0,
        max = 100,
        default = 0,
        update = update_progress
    )    

    guided_ui: BoolProperty(
        name = "Guided UI",
        description = "Only show UI element that the user can interact with",
        default = True
    )

    image_settings: bpy.props.PointerProperty(type = RENDER_PG_bbb_image_settings)





############
# PROMPT MESSAGE
###############


def show_message_box(context, message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text = message)

    context.window_manager.popup_menu(draw, title = title, icon = icon)

def tag_redraw_all_areas(context):
    for area in context.screen.areas:
        area.tag_redraw

def handle_guided_UI(context):
    '''
    Check that certain property values are initiated and "hide" UI
    that is not needed until those values are filled out
    '''
    guided_ui_message = {'step': 100, 'message': ""}
    bake_collections = collection_manager.get_bake_collections_by_scene(context.scene)

    if (context.scene.BBB_props.guided_ui == True 
        and context.scene.BBB_props.dir_path == ""):

        guided_ui_message['step'] = 1
        guided_ui_message['message'] = "Set a directory path for file output first"
    
    elif (context.scene.BBB_props.guided_ui == True 
        and len(bake_collections) == 0):

        guided_ui_message['step'] = 2
        guided_ui_message['message'] = "Select objects and create a bake collection first"
       
    elif (context.scene.BBB_props.guided_ui == True 
        and len(context.scene.bake_passes) == 0):
        guided_ui_message['step'] = 3
        guided_ui_message['message'] = "Create bake passes first"

    return guided_ui_message



def get_active_object_from_UI(context):
    '''
    Returns the active object in the UI. 
    Respects "pinned object" in UI
    '''
    wm = context.window_manager
    pinned_active_object = wm.get('pinned_active_object')

    if pinned_active_object:
        return pinned_active_object
    else:
        return context.active_object

def active_object_in_UI_is_pinned(context):
    '''
    Returns True if the active object in the UI is pinned
    '''
    return not context.window_manager.get("pinned_active_object") == None

def view3d_newdraw(self, context):  
    '''
    New draw function for the 3d viewport that adds progress bar
    '''
    global view3d_header_draw  
    # first call the original stuff  
    view3d_header_draw(self, context)  
    # then add the prop that acts as a progress indicator  
    progress_bar = context.scene.BBB_props.progress_percentage

    if (progress_bar > 0 and progress_bar <= 100) :  
        self.layout.separator()
        col = self.layout.column()
        row = col.row()
          
        text = "Baking progress"  
        row.prop(context.scene.BBB_props,  
                            "progress_percentage",  
                            text=text,  
                            slider=True)  


classes = (
    RENDER_PT_bbb_settings,
    RENDER_PT_bbb_image_settings,
    OBJECT_PT_bake_collections,
    OBJECT_PT_bbb_bake_passes,
    OBJECT_PT_high_res_objects,
    OBJECT_PT_bbb_report,
    OBJECT_PT_bbb_debug_panel,
    RENDER_PG_bbb_image_settings,
    RENDER_PG_bystedts_blender_baker,
    OBJECT_OT_test_a_function,
    OBJECT_OT_popupwin_find_hipoly_by_bounding_box,
    OBJECT_OT_popupwin_select_bake_pass,
    OBJECT_OT_select_bake_pass,
    UI_OT_cgm_add_bake_pass,
    UI_OT_cgm_remove_bake_pass,
    OBJECT_UL_high_res_objects,    
)

def register():
    

    for clas in classes:
        bpy.utils.register_class(clas)
    
    bpy.types.Scene.BBB_props = bpy.props.PointerProperty(type = RENDER_PG_bystedts_blender_baker)

    # save the original draw method of the 3d view  
    global view3d_header_draw  
    view3d_header_draw = bpy.types.VIEW3D_HT_header.draw  
    # replace the draw method of the 3d view  
    bpy.types.VIEW3D_HT_header.draw = view3d_newdraw 


def unregister():
    
    #del bpy.types.Scene.BBB_props # TODO: I don't think this should be commented out
  
    for clas in classes:
        bpy.utils.unregister_class(clas)

    # Restore draw method of the 3d view
    global view3d_header_draw  
    bpy.types.VIEW3D_HT_header.draw = view3d_header_draw
    


    

    