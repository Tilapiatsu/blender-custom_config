import bpy
import addon_utils
import os
import math
from mathutils import Vector
import re
import shutil

###################################################################################
#   SETUP SCENE
###################################################################################

def Set_Scene(self,context,scene_name):
    if scene_name not in bpy.context.scene:
        Import_Scene(self,context,scene_name)

def Import_Scene(self,context,scene_name):

    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "BagaBatch":
            filepath = mod.__file__
            file_path = filepath.replace("__init__.py","render_setup.blend")
        else: pass
    inner_path = "Scene"

    bpy.ops.wm.append(
        filepath = os.path.join(file_path, inner_path, scene_name),
        directory = os.path.join(file_path, inner_path),
        filename=scene_name
        )
    
###################################################################################
#   RENDER
###################################################################################
def Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal):
    pref = context.preferences.addons['BagaBatch'].preferences
    cam=bpy.context.scene.camera
    
    if pref.use_current_orientation == True:
        cam.rotation_euler = cam_rot
    else:
        cam.rotation_euler[2] = -(pref.camera_orientation/180)*3.1415

    if pref.use_view == False or pref.use_current_orientation == False:
        bpy.ops.view3d.camera_to_view_selected()
    else :
        cam.matrix_world = user_view_orientation
        cam.data.lens = user_view_focal
        if pref.force_focus_selected:
            bpy.ops.view3d.camera_to_view_selected()

def Cam_Rotation(self, context, user_view_orientation):
    pref = context.preferences.addons['BagaBatch'].preferences
    camera=bpy.context.scene.camera
    if pref.use_view==True and pref.use_current_orientation == True:
        cam_direction = user_view_orientation @ Vector((0.0, 0.0, -1.0))
    else:
        cam_direction = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    angle_rad = math.atan2(cam_direction.y, cam_direction.x)
    angle_deg = math.degrees(angle_rad)

    return(angle_rad)

def Render_Preview(self, context, obj,render_device, user_view_orientation):
    pref = context.preferences.addons['BagaBatch'].preferences
    # EEVEE Render settings :
    if pref.render_engine:
        bpy.context.scene.eevee.taa_render_samples = pref.eevee_samples
        bpy.context.scene.eevee.use_gtao = pref.eevee_ao
        bpy.context.scene.eevee.use_ssr = pref.eevee_ssr
        bpy.context.scene.eevee.use_ssr_refraction = pref.eevee_refract
        bpy.context.scene.render.film_transparent = pref.eevee_transparent_background
        bpy.context.scene.render.resolution_x = pref.render_resolution
        bpy.context.scene.render.resolution_y = pref.render_resolution
        bpy.context.scene.view_settings.exposure = pref.render_exposition
    # Cycles Render settings :
    else:
        bpy.context.scene.cycles.samples = pref.cycles_samples
        bpy.context.scene.cycles.transparent_max_bounces = pref.cycles_transp_bounces
        bpy.context.scene.cycles.use_denoising = pref.cycles_denoise
        bpy.context.scene.cycles.device = render_device
        bpy.context.scene.render.film_transparent = pref.cycles_transparent_background
        bpy.context.scene.cycles.film_transparent_glass = pref.cycles_transparent_background
        bpy.context.scene.render.resolution_x = pref.render_resolution
        bpy.context.scene.render.resolution_y = pref.render_resolution
        bpy.context.scene.view_settings.exposure = pref.render_exposition

    # Lighting sun orientation
    cam_rot = Cam_Rotation(self, context, user_view_orientation)
    orientation = pref.sun_orientation
    for node in bpy.context.scene.world.node_tree.nodes:
        sun_offset = -1.5707
        if pref.use_current_orientation:
            sun_offset = 1.5707
            if pref.use_view == False:
                orientation = orientation+180
            
        if node.label == "TEMP_BB_Sky":
            node.sun_rotation = -cam_rot+sun_offset+math.radians(orientation)
            break

    user_output = bpy.context.scene.render.filepath

    addon_location = os.path.dirname(os.path.realpath(__file__))
    temp_thumb_path = os.path.join(addon_location, 'temp_thumb')
    temp_thumb_path_full = os.path.join(temp_thumb_path, obj.name)

    bpy.context.scene.render.filepath = temp_thumb_path_full

    bpy.ops.render.render(write_still = True)
    
    bpy.context.scene.render.filepath =user_output

    return(temp_thumb_path_full)

###################################################################################
#   ASSET BROWSER
###################################################################################
def Set_Preview(self, context, obj, image_path):
    obj.asset_mark()
    with bpy.context.temp_override(id=obj):
        bpy.ops.ed.lib_id_load_custom_preview(
            filepath=image_path+".png"
        )

def Save_Preview_External(self,context,image_path):
    pref = context.preferences.addons['BagaBatch'].preferences
    destination = pref.preview_filepath
    shutil.copy(image_path+".png", destination)

###################################################################################
#   REMOVE BAGABATCH SCENE AND RESTORE ORIGINAL SCENE
###################################################################################
def Clean_Scene(self, context, scene, original_scene):

    delete_cameras()
    delete_objects()
    delete_collections()
    delete_worlds()

    bpy.context.window.scene = bpy.data.scenes[scene]
    bpy.ops.scene.delete()
    bpy.context.window.scene = original_scene


def to_delete(name):
    pattern = r"^(TEMP_)?[A-Z]{2}_(Camera|World|CamObj|Coll|Empty)(_)?[0-9]*"
    return re.match(pattern, name) is not None

def delete_cameras():
    to_delete_cameras = [cam for cam in bpy.data.cameras if to_delete(cam.name)]
    for cam in to_delete_cameras:
        bpy.data.cameras.remove(cam, do_unlink=True)

def delete_objects():
    to_delete_objects = [obj for obj in bpy.data.objects if to_delete(obj.name)]
    for obj in to_delete_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

def delete_collections():
    to_delete_collections = [coll for coll in bpy.data.collections if to_delete(coll.name)]
    for coll in to_delete_collections:
        bpy.data.collections.remove(coll)

def delete_worlds():
    to_delete_worlds = [world for world in bpy.data.worlds if to_delete(world.name)]
    for world in to_delete_worlds:
        bpy.data.worlds.remove(world)