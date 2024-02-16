import bpy
import addon_utils
import os
import math
from mathutils import Vector
from . bagabatch_render_utils import Set_Scene, Set_Camera, Render_Preview,Set_Preview, Clean_Scene

class BAGABATCH_OP_batch_coll_preview(bpy.types.Operator):
    """Batch render preview for collections"""
    bl_idname = "bagabatch.batch_coll_preview"
    bl_label = "Batch Thumbernails"

    def execute(self, context):
        selected_scene = bpy.context.window_manager.scene_previews.removesuffix(".png")
        pref = context.preferences.addons['BagaBatch'].preferences
        original_scene = bpy.context.scene
        render_device = context.scene.render_device
        collections = []
        selected_collection = context.collection
        all_scene_collection = context.scene.collection.children_recursive

        if pref.render_all_assets_coll:
            for col in all_scene_collection:
                collections.append(col)
        else:
            collections.append(selected_collection)

        # GET VIEW
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
        for col in collections:
            # LINK OBJ TO BAGABATCH SCENE AND SET SCENE
            bpy.ops.object.make_links_scene(scene=selected_scene)
            context.window.scene = bpy.data.scenes[selected_scene]
            
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY' and obj.name.startswith("TEMP_BB_Empty_"):
                    # Sélectionne l'objet
                    empty = obj
            empty.instance_type='COLLECTION'
            empty.instance_collection = col
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = empty
            empty.select_set(True)

# CAM
            # SETUP CAMERA IF USE CURRENT VIEW IS TRUE
            Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal)

# RENDER
            # RENDER PREVIEW
            image_path = Render_Preview(self, context, col,render_device, user_view_orientation)
            
            Set_Preview(self, context,col,image_path)

# CLEANUP
            # REMOVE OBJ
            empty.instance_collection = None

            os.remove(image_path+".png")
        
            bpy.context.window.scene = original_scene

        Clean_Scene(self, context, selected_scene, original_scene)

        

        return{'FINISHED'}
