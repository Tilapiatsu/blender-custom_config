import bpy
import addon_utils
import os
import math
from mathutils import Vector
from . bagabatch_render_utils import Set_Scene, Set_Camera, Render_Preview,Set_Preview, Clean_Scene, Save_Preview_External

class BAGABATCH_OP_batch_preview(bpy.types.Operator):
    """Batch render preview for each selected objects"""
    bl_idname = "bagabatch.batch_preview"
    bl_label = "Batch Thumbernails"

    @classmethod
    def poll(cls, context):
        o = context.object
        return (o is not None and o.type in ['MESH','CURVE','EMPTY'])

    def execute(self, context):
        selected_scene = bpy.context.window_manager.scene_previews.removesuffix(".png")
        pref = context.preferences.addons['BagaBatch'].preferences
        original_scene = bpy.context.scene
        objs =context.selected_objects
        render_device = context.scene.render_device

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                break
        space = area.spaces.active
        view_matrix = space.region_3d.view_matrix
        user_view_orientation = view_matrix.inverted()
        user_view_focal = bpy.context.space_data.lens

        cam_rot = [0,0,0]
        if pref.use_current_orientation == True and bpy.context.scene.camera is not None:
            cam_rot=bpy.context.scene.camera.rotation_euler

        Set_Scene(self,context,selected_scene)
        
        # START GENERATE OBJECT PREVIEW HERE
        for obj in objs:
            try:
                # LINK OBJ TO BAGABATCH SCENE AND SET SCENE
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.make_links_scene(scene=selected_scene)
                bpy.context.window.scene = bpy.data.scenes[selected_scene]

                # SETUP CAMERA IF USE CURRENT VIEW IS TRUE
                Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal)

                # RENDER PREVIEW
                image_path = Render_Preview(self, context, obj,render_device, user_view_orientation)
                
                Set_Preview(self, context,obj,image_path)

                if pref.save_preview == True and pref.preview_filepath != "":
                    Save_Preview_External(self, context, image_path)

                # REMOVE OBJ
                obj.select_set(True)
                bpy.ops.object.delete(use_global=False)

                os.remove(image_path+".png")
            
                bpy.context.window.scene = original_scene
            except:
                bpy.context.window.scene = original_scene

        Clean_Scene(self, context, selected_scene, original_scene)

        return{'FINISHED'}
    