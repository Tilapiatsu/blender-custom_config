import bpy
import os
from . import bake_manager
from . import bake_passes

def get_bake_render_settings(context, bake_settings_scene = None, bake_pass = None):
    '''
    Get bake render settings from current scene, if no other scene is specified
    Specify bake pass to get the specific render settings for baking normal, diffuse etc
    '''

    if bake_settings_scene == None:
        bake_settings_scene = context.scene

    render_settings = {}

    props = bake_settings_scene.BBB_props
    render_settings['BBB_props'] = props

    extrusion = props.cage_extrusion

    settings = {
        'context.scene.render.engine' : 'CYCLES',
        'context.scene.render.filepath' : props.dir_path,
        'context.scene.render.bake.cage_extrusion' : extrusion,
        'context.scene.render.bake.use_cage' : props.use_cage,
        'context.scene.render.bake.use_clear' : False,
        'context.scene.render.image_settings.compression': 0,
        'context.scene.render.dither_intensity': 0
    }
    render_settings.update(settings)

    # Image format
    image_settings = context.scene.BBB_props.image_settings
    render_settings['image_settings'] = context.scene.BBB_props.image_settings
    render_settings['context.scene.render.image_settings.file_format'] = image_settings.file_format
    render_settings['context.scene.render.image_settings.color_mode'] = image_settings.color_mode
    render_settings['context.scene.render.image_settings.color_depth'] = image_settings.color_depth
    
    if image_settings.file_format == 'TIFF':
        render_settings['context.scene.render.image_settings.tiff_codec'] = image_settings.tiff_codec
    elif (image_settings.file_format == 'OPEN_EXR' 
        or image_settings.file_format == 'OPEN_EXR_MULTILAYER'):
        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
    elif image_settings.file_format == 'JPEG':
        bpy.context.scene.render.image_settings.quality = image_settings.quality
    elif image_settings.file_format == 'PNG':
        bpy.context.scene.render.image_settings.compression = image_settings.compression
    elif image_settings.file_format == 'JPEG2000':
        bpy.context.scene.render.image_settings.quality = image_settings.quality
        bpy.context.scene.render.image_settings.jpeg2k_codec = image_settings.jpeg2k_codec
    elif image_settings.file_format == 'AVI_JPEG':
        bpy.context.scene.render.image_settings.quality = image_settings.quality

    render_settings['file_extension'] = get_file_extention(image_settings.file_format)


    # Normal map type
    if bake_pass.bake_type == "NORMAL":
        if bake_pass.normal_map_type == 'OPEN_GL':
            render_settings['context.scene.render.bake.normal_g'] = 'POS_Y'
        else:
            render_settings['context.scene.render.bake.normal_g'] = 'NEG_Y'

    # Bake workflow
    render_settings['bake_workflow'] = props.bake_workflow
    if props.bake_workflow == 'HIGHRES_TO_LOWRES':
        render_settings['context.scene.render.bake.use_selected_to_active'] = True
    else:
        render_settings['context.scene.render.bake.use_selected_to_active'] = False

    # Set emit as bake type when the pass is not an option in cycles bake settings
    if bake_passes.is_non_default_bake_pass(bake_pass.bake_type):
        render_settings['context.scene.cycles.bake_type'] = 'EMIT'
    else:
        render_settings['context.scene.cycles.bake_type'] =  bake_pass.bake_type

    if bake_pass.bake_type == "DIFFUSE":
        bake_type_settings = {
            #'context.scene.cycles.bake_type' : 'DIFFUSE',
            'context.scene.render.bake.use_pass_direct' : False,
            'context.scene.render.bake.use_pass_indirect' : False,
            'context.scene.render.bake.use_pass_color' : True,
            'color_space' : 'sRGB',
            'bit_depth' : '8'            
        }
        render_settings.update(bake_type_settings)

    elif bake_pass.bake_type == "NORMAL":
        bake_type_settings = {
            #'context.scene.cycles.bake_type': 'NORMAL',
            'context.scene.render.bake.normal_space': 'TANGENT',
            'color_space': 'Non-Color',
            'bit_depth': '16'  
        }  
        render_settings.update(bake_type_settings)  

    elif bake_pass.bake_type == "METALLIC":
        bake_type_settings = {
            #'context.scene.cycles.bake_type': 'EMIT',
            'color_space': 'Non-Color',
            'bit_depth': '8'  
        }  
        render_settings.update(bake_type_settings)  

    elif bake_pass.bake_type == "DISPLACEMENT":
        bake_type_settings = {
            #'context.scene.cycles.bake_type': 'EMIT',
            'color_space': 'Non-Color',
            'bit_depth': '32'  
        }  
        render_settings.update(bake_type_settings)  

    elif bake_pass.bake_type == "BASE COLOR":
        bake_type_settings = {
            #'context.scene.cycles.bake_type': 'EMIT',
            'color_space': 'sRGB',
            'bit_depth': '8'  
        }  
        render_settings.update(bake_type_settings)  

    else:
        bake_type_settings = {
            #'context.scene.cycles.bake_type': bake_pass.bake_type,
            'color_space': 'Non-Color',
            'bit_depth': '8'       
        }
        render_settings.update(bake_type_settings)

    # Resolution
    percent = bake_settings_scene.BBB_props.resolution_percentage * 0.01
    render_settings['resolution_x'] = int(bake_settings_scene.BBB_props.resolution_x * percent)
    render_settings['resolution_y'] = int(bake_settings_scene.BBB_props.resolution_y * percent)
  
    # The bake type displayed in the bake pass (can be Metallic, which is not possible in cycles)
    render_settings['bake_type'] = bake_pass.bake_type 

    # Bake type used to set correct render settings in cycles
    render_settings['cycles_bake_type'] = render_settings['context.scene.cycles.bake_type'] 
   
    render_settings['base_color'] = bake_passes.get_base_color(bake_pass.bake_type)
    average_resolution = (render_settings['resolution_x'] + render_settings['resolution_y']) * 0.5
    render_settings['context.scene.render.bake.margin'] = max(average_resolution / 128, 4) * props.margin_multiplier
    
    # Bake scene
    if bake_pass.bake_scene == "AUTO":
        if bake_passes.is_temporary_scene_bake_pass(bake_pass):
            render_settings['bake_scene']='TEMPORARY' 
        else:
            render_settings['bake_scene'] = 'CURRENT'
    else:
        render_settings['bake_scene'] = bake_pass.bake_scene 

    # Bake space
    # Don't use exploded geometry when baking lowres geo only
    if props.bake_workflow == 'LOWRES_ONLY':
        render_settings['bake_locations'] = 'CURRENT_LOCATION'
    elif bake_pass.bake_locations == 'AUTO':
        if bake_passes.is_low_sample_pass(bake_pass):
            render_settings['bake_locations']='EXPLODED' 
        else:
            render_settings['bake_locations'] = 'CURRENT_LOCATION'
    else:
        render_settings['bake_locations'] = bake_pass.bake_locations  

    
    # Samples
    if bake_pass.sample_type == "AUTO":
        if bake_passes.is_low_sample_pass(bake_pass):
            render_settings['samples'] = 1 
        else:
            render_settings['samples'] = 32
    else:
        render_settings['samples'] = bake_pass.samples
    
    render_settings['context.scene.cycles.samples'] = render_settings['samples']

    # Sub pixel sample settings
    render_settings['sub_pixel_sample'] = int(props.sub_pixel_sample)

    # Post process
    if bake_pass.post_process == "NO_POST_PROCESS":
        render_settings['post_process'] = "" 
    elif bake_pass.post_process == "AUTO":
        if bake_passes.is_low_sample_pass(bake_pass):
            render_settings['post_process'] = "" 
        else:
            render_settings['post_process'] = "DENOISE"
    else:
        render_settings['post_process'] = bake_pass.post_process


    return render_settings

def get_file_extention(file_format):
    
    if file_format == 'BMP':
        return 'bmp'
    elif file_format == 'IRIS':
        return 'rgb'
    elif file_format == 'PNG':
        return 'png'
    elif file_format == 'JPEG':
        return 'jpg'
    elif file_format == 'JPEG2000':
        return 'jp2'        
    elif file_format == 'TARGA':
        return 'tga'
    elif file_format == 'CINEON':
        return 'cin'
    elif file_format == 'DPX':
        return 'dpx'
    elif file_format == 'OPEN_EXR_MULTILAYER':
        return 'exr'
    elif file_format == 'OPEN_EXR':
        return 'exr'
    elif file_format == 'HDR':
        return 'hdr'
    elif file_format == 'TIFF':
        return 'tif'
    elif file_format == 'TARGA':
        return 'tga'

    return "none"



def get_current_render_settings(context):
    render_settings = {
        'context.area.type': context.area.type,
        'context.area.ui_type': context.area.ui_type,
        'context.scene.render.image_settings.color_depth': context.scene.render.image_settings.color_depth,
        'context.scene.render.image_settings.file_format': context.scene.render.image_settings.file_format,
        'context.scene.render.filepath': context.scene.render.filepath,
        'context.scene.render.bake.use_selected_to_active': context.scene.render.bake.use_selected_to_active,
        'context.scene.cycles.samples': context.scene.cycles.samples,
        'context.scene.render.engine': context.scene.render.engine,
        'context.scene.render.bake.cage_extrusion': context.scene.render.bake.cage_extrusion,
        'context.scene.render.bake.use_clear': context.scene.render.bake.use_clear,
        'context.scene.render.bake.use_selected_to_active': context.scene.render.bake.use_selected_to_active,
        'context.scene.render.bake.max_ray_distance' : context.scene.render.bake.max_ray_distance,
        'context.scene.render.bake.use_clear': context.scene.render.bake.use_clear,
        'context.scene.render.bake.use_cage' : context.scene.render.bake.use_cage,
        'context.scene.render.bake.cage_object': context.scene.render.bake.cage_object
    }
    return render_settings


def set_settings(context, settings_dictionary):
    '''
    Set blenders settings. Expects dictionary as input \n
    Expects keys to be stored as full settings path but without 'bpy.' as prefix \n
    Key example:  'context.scene.cycles.samples'
    Key without '.' will be ignored
    '''

    for key, value in settings_dictionary.items():
        
        # If key can be used to change property directly (e.g. key contains '.')
        if key.find('.') > - 1:
            exec_string = key + ' = ' + repr(value)

            try:
                exec(exec_string)
            except:
                print("Could not set " + exec_string + " in function set_settings")
                    
