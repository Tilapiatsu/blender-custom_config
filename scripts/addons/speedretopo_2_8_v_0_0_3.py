

'''
Copyright (C) 2016 Cedric lepiller
pitiwazou@gmail.com

Created by Cedric lepiller

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "SpeedRetopo",
    "description": "Addon for retopology",
    "author": "Cedric Lepiller, EWOC for Laprelax",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Object" }
    


import bpy
import bmesh
from mathutils import *
import math
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import Menu, Header  
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty)
from bpy.types import Operator, Macro
import os
import rna_keymap_ui


# def get_addon_preferences():
#     addon_name = os.path.basename(os.path.dirname(os.path.abspath(__file__).split("utils")[0]))
#     user_preferences = bpy.context.preferences
#     addon_prefs = user_preferences.addons[addon_name].preferences
#
#     return addon_prefs

    
    
# -----------------------------------------------------------------------------
#    Funtions
# -----------------------------------------------------------------------------
# bpy.types.WindowManager.speedretopo_ref_obj = bpy.props.PointerProperty(type=None, name="", description="", options={'ANIMATABLE'}, tags={}, poll=None, update=None)
bpy.types.WindowManager.speedretopo_ref_obj = StringProperty(description='Object reference for the Retopology')

# bpy.types.Scene.previews_obj : StringProperty()
# bpy.types.Scene.obj_mode : StringProperty()

# -----------------------------------------------------------------------------
#    Activate addons
# ----------------------------------------------------------------------------- 

class SPEEDRETOPO_OT_activate_bsurfaces(bpy.types.Operator):
    bl_idname = "speedretopo.activate_bsurfaces"
    bl_label = "Activate Bsurfaces"
    bl_description = "Activate Bsurfaces"
    bl_options = {"REGISTER"}

    def execute(self, context):
        # bpy.ops.wm.addon_enable(module="mesh_bsurfaces")
        bpy.ops.preferences.addon_enable(module="mesh_bsurfaces")
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}

class SPEEDRETOPO_OT_activate_looptools(bpy.types.Operator):
    bl_idname = "speedretopo.activate_looptools"
    bl_label = "Activate Lopptools"
    bl_description = "Activate Looptools"
    bl_options = {"REGISTER"}

    def execute(self, context):
        # bpy.ops.wm.addon_enable(module="mesh_looptools")
        bpy.ops.preferences.addon_enable(module="mesh_looptools")
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}

# -----------------------------------------------------------------------------
#    Scale Grid
# -----------------------------------------------------------------------------  

 
# class SPEEDRETOPO_OT_scale_grid(bpy.types.Operator):
#     bl_idname = "speedretopo.scale_grid"
#     bl_label = "Scale Grid"
#     bl_description = "Scale Grid"
#     bl_options = {"REGISTER", "UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         # autant s'assurer qu'on a bien un objet et que l'objet Retopo_Grid
#         # fait bien partie de la scène pour pouvoir lancer l'opérateur
#         return context.object is not None and "Retopo_Grid" in bpy.context.scene.objects
#
#     def execute(self, context):
#         obj = context.active_object
#
#         # on sauvegarde le mode objet
#         context.scene.obj_mode = context.object.mode
#         # on sauvegarde le nom du mesh actif pour qu'on puisse le récupérer le moment venu
#         context.scene.previews_obj = obj.name
#
#         bpy.ops.object.mode_set(mode = 'OBJECT')
#
#         # si il y a des chances qu'on ait plusieurs objets sélectionnés
#         bpy.ops.object.select_all(action = 'DESELECT')
#
#         # si au contraire on est certain qu'on aura qu'un seul de selectionné,
#         # autant utiliser cette ligne
#
#         retopo_grid = bpy.data.objects["Retopo_Grid"]
#         retopo_grid.hide_set(True)
#         context.view_layer.objects.active = retopo_grid
#         retopo_grid.select_set(state=True)
#         context.scene.tool_settings.use_snap = False
#
#         # on lance la macro à partir d'ici
#         bpy.ops.test.test_macro('INVOKE_DEFAULT')
#         # c'est la macro qui doit lancer l'opérateur TRANSFORM_OT_resize pour qu'elle
#         # puisse détecter la fin de l'invoke et lancer la suite du code
#         # une fois ce dernier terminé
#         return {"FINISHED"}
 
# class SPEEDRETOPO_OT_finalize(Operator):
#     bl_idname = "speedretopo.finalize"
#     bl_label = "Finalize"
#
#     def execute(self, context):
#         act_obj= context.active_object
#         context.scene.tool_settings.use_snap = True
#         retopo_grid = bpy.data.objects["Retopo_Grid"]
#         # bpy.data.objects["Retopo_Grid"].hide_select = True
#         retopo_grid.hide_set(True)
#
#         # on désélectionne Retopo_Grid
#         act_obj.select_set(state=False)
#         # bpy.context.active_object.select = False
#
#         # on récupère l'ancien objet grace à la variable dans laquelle on a stocké le nom
#         previewsObj = bpy.data.objects[context.scene.previews_obj]
#
#         context.view_layer.objects.active = previewsObj
#         previewsObj.select_set(state=True)
#         # bpy.context.scene.objects.active = previewsObj
#         # previewsObj.select = True
#
#         if context.scene.obj_mode != context.object.mode:
#             bpy.ops.object.mode_set(mode = context.scene.obj_mode)
#
#         # on clean les variables
#         context.scene.obj_mode = ""
#         context.scene.previews_obj = ""
#         return {'FINISHED'}
 
 
# Macro operator to concatenate transform and our finalization
# class SPEEDRETOPO_OT_test(Macro):
#     bl_idname = "speedretopo.test_macro"
#     bl_label = "Test"
    
# -----------------------------------------------------------------------------
#    Grid
# -----------------------------------------------------------------------------      

#Remove Grid  
# class SPEEDRETOPO_OT_remove_retopo_grid(bpy.types.Operator):
#     bl_idname = "speedretopo.remove_retopo_grid"
#     bl_label = "Remove Retopo Grid"
#     bl_description = "Remove Retopo Grid"
#     bl_options = {"REGISTER", "UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         # autant s'assurer qu'on a bien un objet
#         return context.object is not None
#
#     def execute(self, context):
#         obj = context.active_object
#
#         # on sauvegarde le mode objet
#         obj_mode = context.object.mode
#         # context.scene.obj_mode = context.object.mode
#         # on sauvegarde le nom du mesh actif pour qu'on puisse le récupérer le moment venu
#         context.scene.previews_obj = obj.name
#
#         ActObj_edit = False
#         if context.object.mode == "EDIT":
#             ActObj_edit = True
#             bpy.ops.object.mode_set(mode = 'OBJECT')
#
#         retopo_grid = bpy.data.objects["Retopo_Grid"]
#         bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap_Grid")
#         bpy.ops.object.select_all(action='DESELECT')
#         retopo_grid.hide_set(False)
#         retopo_grid.hide_select = False
#         context.view_layer.objects.active = retopo_grid
#         retopo_grid.select_set(state=True)
#         bpy.ops.object.delete(use_global=False)
#
#
#         # on récupère l'ancien objet grace à la variable dans laquelle on a stocké le nom
#         previewsObj = bpy.data.objects[context.scene.previews_obj]
#
#         context.view_layer.objects.active = previewsObj
#         previewsObj.select_set(state=True)
#
#
#         # if context.scene.obj_mode != context.object.mode:
#         if obj_mode != context.object.mode:
#             bpy.ops.object.mode_set(mode = context.scene.obj_mode)
#
#         # on clean les variables
#         # context.scene.obj_mode = ""
#         context.scene.previews_obj = ""
#
#         return {"FINISHED"}


#Create Grid    
# class SPEEDRETOPO_OT_recreate_grid(bpy.types.Operator):
#     bl_idname = "object.recreate_grid"
#     bl_label = "ReCreate Retopo Grid"
#     bl_description = "ReCreate Retopo Grid"
#     bl_options = {"REGISTER", "UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         # autant s'assurer qu'on a bien un objet
#         return context.object is not None
#
#     def execute(self, context):
#         act_obj = context.active_object
#
#         #Addon prefs
#         # addonPref = get_addon_preferences()
#         addonPref = context.preferences.addons[__name__].preferences
#         grid_color = addonPref.grid_color
#         grid_subdivisions= addonPref.grid_subdivisions
#         grid_show_wire= addonPref.grid_show_wire
#         grid_alpha= addonPref.grid_alpha
#
#         # on sauvegarde le mode objet
#         obj_mode = context.object.mode
#         # context.scene.obj_mode = context.object.mode
#         # on sauvegarde le nom du mesh actif pour qu'on puisse le récupérer le moment venu
#         context.scene.previews_obj = act_obj.name
#
#         ActObj_edit = False
#         if context.object.mode == "EDIT":
#             ActObj_edit = True
#
#
#         bpy.ops.object.mode_set(mode = 'OBJECT')
#
#         if not "Retopo_Grid" in bpy.data.objects :
#             #Create Plane
#             bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, 0))
#             grid = context.active_object
#             grid.name = "Retopo_Grid"
#
#
#             #Add Subsurf
#             subsurf = grid.modifier_add(type='SUBSURF')
#             subsurf.subdivision_type = 'SIMPLE'
#             subsurf.levels = grid_subdivisions
#
#             #Edit values
#             bpy.ops.transform.rotate(value=1.5708, axis=(0, 1, 0))
#             bpy.ops.transform.resize(value=(100, 100, 100))
#             # bpy.context.object.data.show_double_sided = True
#             # bpy.context.object.show_transparent = True
#             context.object.color[3] = 0.3
#
#             if grid_show_wire :
#                 context.object.show_wire = True
#                 context.object.show_all_edges = True
#
#             #Add Material
#             bpy.ops.object.material_slot_add()
#             if not "Retopo_Grid" in bpy.data.materials:
#                 myMat = bpy.data.materials.new("Retopo_Grid")
#                 myMat.use_nodes = True
#                 context.object.active_material = myMat
#             else:
#                 context.object.active_material = bpy.data.materials['Retopo_Grid']
#             context.object.active_material.alpha = grid_alpha
#             context.object.active_material.diffuse_color = grid_color
#             context.object.active_material.specular_color = (0, 0, 0)
#             bpy.ops.object.select_all(action='DESELECT')
#
#
#             # on récupère l'ancien objet grace à la variable dans laquelle on a stocké le nom
#             previewsObj = bpy.data.objects[context.scene.previews_obj]
#
#             context.scene.objects.active = previewsObj
#             previewsObj.select = True
#
#
#             if "Shrinkwrap_Grid" in act_obj.modifiers:
#                 context.object.modifiers["Shrinkwrap_Grid"].target = bpy.data.objects["Retopo_Grid"]
#
#             #If no modifier, create it
#             else:
#                 #Add Shrinkwrap Grid
#                 if not "Shrinkwrap" in act_obj.modifiers:
#                     shrinkwrap = act_obj.modifier_add(type='SHRINKWRAP')
#                     shrinkwrap.name = "Shrinkwrap_Grid"
#
#                     shrinkwrap.target = bpy.data.objects["Retopo_Grid"]
#                     shrinkwrap.wrap_method = 'PROJECT'
#                     shrinkwrap.use_project_x = True
#                     shrinkwrap.show_on_cage = True
#                     # shrinkwrap.use_keep_above_surface = True
#                     bpy.ops.object.modifier_move_up(modifier=shrinkwrap.name)
#
#             grid.hide_select = True
#
#             # if context.scene.obj_mode != context.object.mode:
#             if obj_mode != context.object.mode:
#                 bpy.ops.object.mode_set(mode = context.scene.obj_mode)
#
#             # on clean les variables
#             # context.scene.obj_mode = ""
#             context.scene.previews_obj = ""
#
#         return {"FINISHED"}


#Create Grid    
# class SPEEDRETOPO_OT_create_grid(bpy.types.Operator):
#     bl_idname = "object.create_grid"
#     bl_label = "Create Retopo Grid"
#     bl_description = "Create Retopo Grid"
#     bl_options = {"REGISTER", "UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         # autant s'assurer qu'on a bien un objet
#         return context.object is not None
#
#     def execute(self, context):
#         obj = context.active_object
#
#         #Addon prefs
#         # addonPref = get_addon_preferences()
#         addonPref = context.preferences.addons[__name__].preferences
#         grid_color = addonPref.grid_color
#         grid_subdivisions= addonPref.grid_subdivisions
#         grid_show_wire= addonPref.grid_show_wire
#         grid_alpha= addonPref.grid_alpha
#
#         # on sauvegarde le mode objet
#         # context.scene.obj_mode = context.object.mode
#         obj_mode = context.object.mode
#         # on sauvegarde le nom du mesh actif pour qu'on puisse le récupérer le moment venu
#         context.scene.previews_obj = obj.name
#
#
#         ActObj_edit = False
#         if context.object.mode == "EDIT":
#             ActObj_edit = True
#
#
#         bpy.ops.object.mode_set(mode = 'OBJECT')
#
#         #Create Grid
#         if not "Retopo_Grid" in bpy.data.objects:
#             #Create Plane
#             bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
#             grid = context.active_object
#             grid.name = "Retopo_Grid"
#             #Add Subsurf
#             subsurf = grid.modifier_add(type='SUBSURF')
#             subsurf.subdivision_type = 'SIMPLE'
#             subsurf.levels = grid_subdivisions
#
#
#
#             #Edit values
#             bpy.ops.transform.rotate(value=1.5708, axis=(0, 1, 0))
#             bpy.ops.transform.resize(value=(100, 100, 100))
#             context.object.data.show_double_sided = True
#             context.object.show_transparent = True
#             if grid_show_wire :
#                 context.object.show_wire = True
#                 context.object.show_all_edges = True
#
#             #Add Material
#             bpy.ops.object.material_slot_add()
#             if not "Retopo_Grid" in bpy.data.materials:
#                 myMat = bpy.data.materials.new("Retopo_Grid")
#                 myMat.use_nodes = True
#                 context.object.active_material = myMat
#             else:
#                 context.object.active_material = bpy.data.materials['Retopo_Grid']
#             context.object.active_material.alpha = grid_alpha
#             context.object.active_material.diffuse_color = grid_color
#             context.object.active_material.specular_color = (0, 0, 0)
#             bpy.ops.object.select_all(action='DESELECT')
#
#             # on récupère l'ancien objet grace à la variable dans laquelle on a stocké le nom
#             previewsObj = bpy.data.objects[context.scene.previews_obj]
#
#             context.scene.objects.active = previewsObj
#             previewsObj.select = True
#
#             bpy.data.objects["Retopo_Grid"].hide_select = True
#
#             # if context.scene.obj_mode != context.object.mode:
#             if obj_mode != context.object.mode:
#                 bpy.ops.object.mode_set(mode = context.scene.obj_mode)
#
#             # on clean les variables
#             # context.scene.obj_mode = ""
#             context.scene.previews_obj = ""
#
#         return {"FINISHED"}
#
# class SPEEDRETOPO_OT_hide_retopo_grid(bpy.types.Operator):
#     bl_idname = "object.hide_retopo_grid"
#     bl_label = "Hide Retopo Grid"
#     bl_description = "Hide Retopo Grid"
#     bl_options = {"REGISTER", "UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         return True
#
#     def execute(self, context):
#         obj = context.active_object
#         grid = bpy.data.objects["Retopo_Grid"]
#
#         if grid.hide_get(False):
#             grid.hide_set(True)
#
#             if "Shrinkwrap_Grid" in obj.modifiers :
#                 context.object.modifiers["Shrinkwrap_Grid"].show_viewport = False
#
#         else:
#             grid.hide_set(False)
#             if "Shrinkwrap_Grid" in obj.modifiers :
#                 context.object.modifiers["Shrinkwrap_Grid"].show_viewport = True
#
#         return {"FINISHED"}
               
# -----------------------------------------------------------------------------
#    Setup Retopo
# ----------------------------------------------------------------------------- 

# Setup Retopo
class SPEEDRETOPO_OT_create_speedretopo(bpy.types.Operator):
    bl_idname = "object.create_speed_retopo"
    bl_label = "Create Speed Retopo"
    bl_description = "Create Speed Retopo"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # addonPref = get_addon_preferences()
        addonPref = context.preferences.addons[__name__].preferences
        hidden_wire = addonPref.hidden_wire
        start_from = addonPref.start_from
        start_from_basic = addonPref.start_from_basic
        obj_color = addonPref.obj_color
        auto_add_mirror = addonPref.auto_add_mirror
        auto_add_shrinkwrap = addonPref.auto_add_shrinkwrap
        use_in_front = addonPref.use_in_front
        use_wireframe = addonPref.use_wireframe
        # use_grid = addonPref.use_grid

        act_obj = context.active_object

        bpy.ops.preferences.addon_enable(module="mesh_bsurfaces")
        bpy.ops.preferences.addon_enable(module="mesh_looptools")

        if hasattr(bpy.types, "GPENCIL_OT_surfsk_add_surface"):


            ref_obj = [obj for obj in context.scene.objects if obj.get("is_speedretopo_ref")]

            for obj in ref_obj:
                del obj["is_speedretopo_ref"]

            act_obj["is_speedretopo_ref"] = True

            context.window_manager.speedretopo_ref_obj = context.active_object.name

            #Prepare Grease Pencil
            context.scene.tool_settings.annotation_stroke_placement_view3d = 'SURFACE'

            #Add snap
            context.scene.tool_settings.use_snap = True
            context.scene.tool_settings.snap_elements = {'FACE'}
            context.scene.tool_settings.use_snap_translate = True

            #Create Empty mesh
            bpy.ops.mesh.primitive_plane_add(size=0.2, enter_editmode=True, location=(0, 0, 0))
            context.active_object.name= "Retopo_Mesh"
            self.act_obj = context.active_object

            # SHADING
            if use_wireframe:
                context.object.show_wire = True
                context.object.show_all_edges = True

            if use_in_front:
                context.object.show_in_front = True
                if (2, 81, 0) < bpy.app.version:
                    context.scene.bsurfaces.SURFSK_in_front = True

            if hidden_wire:
                context.space_data.overlay.show_occlude_wire = True

            context.object.color = obj_color
            if (2, 81, 0) < bpy.app.version:
                context.scene.bsurfaces.SURFSK_mesh_color = obj_color
            context.scene.tool_settings.use_mesh_automerge = True

            if hasattr(bpy.types, "MESH_OT_poly_quilt"):
                if start_from in {'BSURFACE', 'POLYQUILT'}:
                    bpy.ops.mesh.delete(type='VERT')
                elif start_from == 'POLYBUILD':
                    bpy.ops.mesh.delete(type='VERT')
                    bpy.ops.wm.tool_set_by_id(name="builtin.poly_build")
                elif start_from == 'VERTEX':
                    bpy.ops.mesh.merge(type='CENTER')
                    bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')

                if start_from == 'POLYQUILT':
                    bpy.ops.wm.tool_set_by_id(name="mesh_tool.poly_quilt")
                elif start_from in {'BSURFACE','VERTEX'}:
                    bpy.ops.wm.tool_set_by_id(name="builtin.select", cycle=False, space_type='VIEW_3D')
                elif start_from == 'POLYBUILD':
                    bpy.ops.wm.tool_set_by_id(name="mesh_tool.poly_build", cycle=False, space_type='VIEW_3D')
            else:
                if start_from_basic == 'BSURFACE':
                    bpy.ops.mesh.delete(type='VERT')
                elif start_from_basic == 'POLYBUILD':
                    bpy.ops.mesh.delete(type='VERT')
                    bpy.ops.wm.tool_set_by_id(name="builtin.poly_build")
                elif start_from_basic == 'VERTEX':
                    bpy.ops.mesh.merge(type='CENTER')
                    bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')

                if start_from_basic in {'BSURFACE', 'VERTEX'}:
                    bpy.ops.wm.tool_set_by_id(name="builtin.select", cycle=False, space_type='VIEW_3D')
                elif start_from_basic == 'POLYBUILD':
                    bpy.ops.wm.tool_set_by_id(name="mesh_tool.poly_build", cycle=False, space_type='VIEW_3D')




            bpy.ops.object.mode_set(mode = 'OBJECT')

            if (2, 81, 0) < bpy.app.version:
                context.scene.bsurfaces.SURFSK_mesh = self.act_obj
            elif (2, 80, 0) < bpy.app.version:
                context.scene.bsurfaces.SURFSK_object_with_retopology = self.act_obj

            #Add Grid
            # if use_grid:
            #     bpy.ops.object.create_grid()


            speedretopo_ref_obj = context.window_manager.speedretopo_ref_obj

            #Add Mirror
            if auto_add_mirror:
                mod_mirror = self.act_obj.modifiers.new("Mirror", 'MIRROR')
                mod_mirror.use_axis[0] = True
                mod_mirror.mirror_object = bpy.data.objects[speedretopo_ref_obj]
                mod_mirror.show_on_cage = True
                if start_from == 'BSURFACE':
                    mod_mirror.use_clip = True
                elif start_from_basic == 'BSURFACE':
                    mod_mirror.use_clip = True
                mod_mirror.merge_threshold = 0.05
                mod_mirror.use_mirror_merge = True
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")

            #Add Shrinkwrap
            if auto_add_shrinkwrap:
                mod_shrinkwrap = self.act_obj.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
                mod_shrinkwrap.target = bpy.data.objects[speedretopo_ref_obj]
                mod_shrinkwrap.wrap_method = 'PROJECT'
                mod_shrinkwrap.use_negative_direction = True
                mod_shrinkwrap.use_positive_direction = True
                mod_shrinkwrap.cull_face = 'OFF'
                mod_shrinkwrap.wrap_mode = 'ABOVE_SURFACE'
                mod_shrinkwrap.show_on_cage = True
                # bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")

            #Add Shrinkwrap Grid
            # if use_grid:
            #     mod_grid_shrinkwrap = self.act_obj.modifiers.new("Shrinkwrap_Grid", 'SHRINKWRAP')
            #     mod_grid_shrinkwrap.target = bpy.data.objects["Retopo_Grid"]
            #     mod_grid_shrinkwrap.wrap_method = 'PROJECT'
            #     mod_grid_shrinkwrap.use_project_x = True
            #     mod_grid_shrinkwrap.show_on_cage = True
            #     # mod_grid_shrinkwrap.use_keep_above_surface = True
            #     bpy.ops.object.modifier_move_up(modifier="Shrinkwrap_Grid")

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')


            if start_from == 'VERTEX' or start_from_basic == 'VERTEX':
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.transform.translate('INVOKE_DEFAULT')

                # CLEAR CURSOR
                context.scene.cursor.location[:] = context.scene.cursor.rotation_euler[:] = (0,0,0)
        else:
            self.report({'WARNING'}, "Activate Bsurfaces")
        return {"FINISHED"}

# -----------------------------------------------------------------------------
#    Align to X
# ----------------------------------------------------------------------------- 

#Align to X
class SPEEDRETOPO_OT_align_to_x(bpy.types.Operator):
    bl_idname = "object.align2x"  
    bl_label = "Align To X"
    bl_description = "Align To X"   
    bl_options = {'REGISTER', 'UNDO'}
  
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        for vert in context.object.data.vertices:
            if vert.select: 
                vert.co[0] = 0
        bpy.ops.object.editmode_toggle() 
        return {'FINISHED'}

# -----------------------------------------------------------------------------
#    SUBSURF
# -----------------------------------------------------------------------------

# Apply Subsurf
class SPEEDRETOPO_OT_add_subsurf(bpy.types.Operator):
    bl_idname = "speedretopo.add_subsurf"
    bl_label = "Add Subsurf"
    bl_description = "Add Subsurf Modifier to check result"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_obj = context.active_object

        mod_subsurf = act_obj.modifiers.new("Subsurf", 'SUBSURF')
        mod_subsurf.levels = 3
        mod_subsurf.show_only_control_edges = True
        shrinkwrap = context.active_object.modifiers.get("Shrinkwrap")
        if shrinkwrap:
            bpy.ops.object.modifier_move_up(modifier="Subsurf")
        return {'FINISHED'}

#Remove Subsurf
class SPEEDRETOPO_OT_remove_subsurf(bpy.types.Operator):
    bl_idname = "speedretopo.remove_subsurf"
    bl_label = "Remove Subsurf"
    bl_description = "Remove Subsurf Modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier="Subsurf")
        return {"FINISHED"}


# Apply Subsurf
class SPEEDRETOPO_OT_apply_subsurf(bpy.types.Operator):
    bl_idname = "speedretopo.apply_subsurf"
    bl_label = "Apply Subsurf"
    bl_description = "Apply Subsurf Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object.mode == "OBJECT":
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
        elif context.object.mode == "EDIT":
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
            bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}
# -----------------------------------------------------------------------------
#    Mirror
# -----------------------------------------------------------------------------  
class SPEEDRETOPO_OT_add_mirror(bpy.types.Operator):
    """ Automatically cut an object along an axis """
    bl_idname = "speedretopo.add_mirror"
    bl_label = "Add Mirror"
    bl_description = "Add Mirror Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        speedretopo_ref_obj = context.window_manager.speedretopo_ref_obj
        act_obj = context.active_object

        # Add Mirror
        mod_mirror = act_obj.modifiers.new("Mirror", 'MIRROR')
        mod_mirror.use_axis[0] = True
        if speedretopo_ref_obj == "":
            mod_mirror.mirror_object = None
        else:
            mod_mirror.mirror_object = bpy.data.objects[speedretopo_ref_obj]
        mod_mirror.show_on_cage = True
        mod_mirror.use_clip = True
        mod_mirror.merge_threshold = 0.05
        mod_mirror.use_mirror_merge = True
        shrinkwrap = context.active_object.modifiers.get("Shrinkwrap")
        subsurf = context.active_object.modifiers.get("Subsurf")
        if shrinkwrap:
            bpy.ops.object.modifier_move_up(modifier=mod_mirror.name)
        if subsurf:
            bpy.ops.object.modifier_move_up(modifier=mod_mirror.name)
        return {'FINISHED'}

#Apply Mirror
class SPEEDRETOPO_OT_apply_mirror(bpy.types.Operator):
    bl_idname = "speedretopo.apply_mirror"
    bl_label = "Apply Mirror" 
    bl_description = "Apply Mirror Modifier"
    bl_options = {'REGISTER', 'UNDO'}
  
    def execute(self, context):
        # if "Retopo_Grid" in bpy.data.objects:
        #     bpy.ops.object.remove_retopo_grid()
        
        if context.object.mode == "OBJECT":
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")

            
        elif context.object.mode == "EDIT":
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'} 

#Remove
class SPEEDRETOPO_OT_remove_mirror(bpy.types.Operator):
    bl_idname = "speedretopo.remove_mirror"
    bl_label = "Remove Mirror"
    bl_description = "Remove Mirror Modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier="Mirror")
        return {"FINISHED"}
            
 
    
# -----------------------------------------------------------------------------
#    Shrinkwrap
# -----------------------------------------------------------------------------  

#Remove
class SPEEDRETOPO_OT_remove_shrinkwrap(bpy.types.Operator):
    bl_idname = "speedretopo.remove_shrinkwrap"
    bl_label = "Remove Mirror"
    bl_description = "Remove Mirror Modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier="Shrinkwrap")
        return {"FINISHED"}

# Apply Shrinkwrap
class SPEEDRETOPO_OT_add_and_apply_shrinkwrap(bpy.types.Operator):
    bl_idname = "speedretopo.add_apply_shrinkwrap"
    bl_label = "Add and Apply Shrinkwrap"
    bl_description = "Add and Apply Shrinkwrap Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.speedretopo.add_shrinkwrap()
        bpy.ops.speedretopo.apply_shrinkwrap()
        return {'FINISHED'}

#Apply Shrinkwrap
class SPEEDRETOPO_OT_apply_shrinkwrap(bpy.types.Operator):
    bl_idname = "speedretopo.apply_shrinkwrap"
    bl_label = "Apply Shrinkwrap"
    bl_description = "Apply Shrinkwrap Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object.mode == "OBJECT":
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
        elif context.object.mode == "EDIT":
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}

#Add Shrinkwrap
class SPEEDRETOPO_OT_add_shrinkwrap(bpy.types.Operator):
    bl_idname = "speedretopo.add_shrinkwrap"
    bl_label = "Add Shrinkwrap"
    bl_description = "Add Shrinkwrap Modifier"
    bl_options = {"REGISTER", 'UNDO'}

    def execute(self, context):
        speedretopo_ref_obj = context.window_manager.speedretopo_ref_obj
        act_obj = context.active_object
        # Add Shrinkwrap
        mod_shrinkwrap = act_obj.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
        mod_shrinkwrap.wrap_method = 'PROJECT'
        mod_shrinkwrap.use_negative_direction = True
        mod_shrinkwrap.use_positive_direction = True
        mod_shrinkwrap.cull_face = 'OFF'
        mod_shrinkwrap.wrap_mode = 'ABOVE_SURFACE'
        mod_shrinkwrap.show_on_cage = True
        if speedretopo_ref_obj == "":
            mod_shrinkwrap.target = None
        else:
            mod_shrinkwrap.target = bpy.data.objects[speedretopo_ref_obj]

        return {"FINISHED"}

#Update Shrinkwrap
class SPEEDRETOPO_OT_update_shrinwrap(bpy.types.Operator):
    bl_idname = "speedretopo.update_shrinwrap"
    bl_label = "Update Shrinwrap Modifier"
    bl_description = "Update The Shrinwrap Modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.speedretopo.apply_shrinkwrap()
        bpy.ops.speedretopo.add_shrinkwrap()
        return {"FINISHED"}

#Update Shrinkwrap
class SPEEDRETOPO_OT_clean_normals(bpy.types.Operator):
    bl_idname = "speedretopo.clean_normals"
    bl_label = "Recalculate Normals"
    bl_description = "Recalculate Normals"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        act_obj = context.active_object
        mode = act_obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        me = act_obj.data
        bm = bmesh.from_edit_mesh(me)

        vert_selected = ([v for v in bm.verts if v.select])


        # RECALCULATE NORMAL OUTSIDE
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.select_all(action='DESELECT')

        for v in vert_selected:
            v.select = True

        bpy.ops.object.mode_set(mode=mode)

        # bpy.ops.gpencil.surfsk_add_surface()
        return {"FINISHED"}


# -----------------------------------------------------------------------------
#    LapRelax
# -----------------------------------------------------------------------------
from mathutils import Matrix, Vector
#LapRelax
class SPEEDRETOPO_OT_srrelax(bpy.types.Operator):
    bl_idname = "mesh.speed_retopo_relax"
    bl_label = "Relax"
    bl_description = "Smoothing mesh keeping volume"
    bl_options = {'REGISTER', 'UNDO'}

    Repeat : bpy.props.IntProperty(
        name = "Repeat",
        description = "Repeat how many times",
        default = 5,
        min = 1,
        max = 100)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):

        # smooth #Repeat times
        for i in range(self.Repeat):
            self.do_laprelax()

        bpy.ops.mesh.select_all(action='DESELECT')
        return {'FINISHED'}


    def do_laprelax(self):

        context = bpy.context
        region = context.region
        area = context.area
        selobj = bpy.context.active_object
        mesh = selobj.data
        bm = bmesh.from_edit_mesh(mesh)
        bmprev = bm.copy()
        vertices = [v for v in bmprev.verts if v.select]

        if not vertices:
            bpy.ops.mesh.select_all(action='SELECT')

        for v in bmprev.verts:

            if v.select:

                tot = Vector((0, 0, 0))
                cnt = 0
                for e in v.link_edges:
                    for f in e.link_faces:
                        if not(f.select):
                            cnt = 1
                    if len(e.link_faces) == 1:
                        cnt = 1
                        break
                if cnt:
                    # dont affect border edges: they cause shrinkage
                    continue

                # find Laplacian mean
                for e in v.link_edges:
                    tot += e.other_vert(v).co
                tot /= len(v.link_edges)

                # cancel movement in direction of vertex normal
                delta = (tot - v.co)
                if delta.length != 0:
                    ang = delta.angle(v.normal)
                    deltanor = math.cos(ang) * delta.length
                    nor = v.normal
                    nor.length = abs(deltanor)
                    bm.verts.ensure_lookup_table()
                    bm.verts[v.index].co = tot + nor


        mesh.update()
        bm.free()
        bmprev.free()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

#Space Relax
class SPEEDRETOPO_OT_space_relax(bpy.types.Operator):
    bl_idname = "object.space_relax"
    bl_label = "Space Relax"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.mesh.looptools_space()
        bpy.ops.mesh.looptools_relax()

        return {"FINISHED"}



# -----------------------------------------------------------------------------
#    Auto Mirror
# -----------------------------------------------------------------------------
bpy.types.Scene.AutoMirror_cut : bpy.props.BoolProperty(default= True, description="If enabled, cut the mesh in two parts and mirror it. If not, just make a loopcut")
#Auto Mirror
class SPEEDRETOPO_OT_mesh_align_vertices(bpy.types.Operator):
    """  """
    bl_idname = "object.mesh_align_vertices"
    bl_label = "Align Vertices on 1 Axis"

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')

        x1,y1,z1 = context.scene.cursor_location
        bpy.ops.view3d.snap_cursor_to_selected()

        x2,y2,z2 = context.scene.cursor_location

        context.scene.cursor_location[0],context.scene.cursor_location[1],context.scene.cursor_location[2]  = 0,0,0

        #Vertices coordinate to 0 (local coordinate, so on the origin)
        for vert in context.object.data.vertices:
            if vert.select:
                axis = 0
                vert.co[axis] = 0

        context.scene.cursor_location = x2,y2,z2

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        context.scene.cursor_location = x1,y1,z1

        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}

# class SPEEDRETOPO_OT_mesh_auto_mirror(bpy.types.Operator):
#     """ Automatically cut an object along an axis """
#     bl_idname = "object.mesh_automirror"
#     bl_label = "AutoMirror"
#     bl_options = {'REGISTER', 'UNDO'}
#
#
#     # def get_local_axis_vector(self, context, X, Y, Z, orientation):
#     #     loc = context.object.location
#     #     bpy.ops.object.mode_set(mode="OBJECT") # Needed to avoid to translate vertices
#     #
#     #     v1 = Vector((loc[0],loc[1],loc[2]))
#     #     bpy.ops.transform.translate(value=(X*orientation, Y*orientation, Z*orientation), constraint_axis=((X==1), (Y==1), (Z==1)), constraint_orientation='LOCAL')
#     #     v2 = Vector((loc[0],loc[1],loc[2]))
#     #     bpy.ops.transform.translate(value=(-X*orientation, -Y*orientation, -Z*orientation), constraint_axis=((X==1), (Y==1), (Z==1)), constraint_orientation='LOCAL')
#     #
#     #     bpy.ops.object.mode_set(mode="EDIT")
#     #     return v2-v1
#
#     def execute(self, context):
#         # X,Y,Z = 0,0,0
#         # X = 1
#         #
#         # current_mode = context.object.mode # Save the current mode
#         #
#         # if context.object.mode != "EDIT":
#         #     bpy.ops.object.mode_set(mode="EDIT") # Go to edit mode
#         # bpy.ops.mesh.select_all(action='SELECT') # Select all the vertices
#         #
#         # #Direction of the mirror
#         # orientation = 1
#         # cut_normal = self.get_local_axis_vector(context, X, Y, Z, orientation)
#         #
#         # bpy.ops.mesh.bisect(plane_co=(context.object.location[0], context.object.location[1], context.object.location[2]), plane_no=cut_normal, use_fill= False, clear_inner= context.scene.AutoMirror_cut, clear_outer= 0, threshold= 0.01) # Cut the mesh
#         #
#         # bpy.ops.object.mesh_align_vertices() # Use to align the vertices on the origin, needed by the "threshold"
#         #
#         # bpy.ops.object.mode_set(mode=current_mode) # Reload previous mode
#
#         #Add mirror
#         bpy.ops.object.modifier_add(type='MIRROR') # Add a mirror modifier
#         context.object.modifiers["Mirror"].use_clip = True
#         context.object.modifiers["Mirror"].use_mirror_merge = True
#         context.object.modifiers["Mirror"].show_on_cage = True
#         context.object.modifiers["Mirror"].merge_threshold = 0.05
#         return {'FINISHED'}

# -----------------------------------------------------------------------------
#    Threshold
# -----------------------------------------------------------------------------


#Double Threshold 0.1
class SPEEDRETOPO_OT_double_threshold_plus(bpy.types.Operator):
    bl_idname = "object.double_threshold_plus"
    bl_label = "Double Threshold 01"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tool_settings = context.tool_settings
        context.scene.tool_settings.double_threshold = 0.1
        return {'FINISHED'}

#Double Threshold 0.001
class SPEEDRETOPO_OT_double_threshold_minus(bpy.types.Operator):
    bl_idname = "object.double_threshold_minus"
    bl_label = "Double Threshold 0001"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tool_settings = context.tool_settings
        context.scene.tool_settings.double_threshold = 0.001
        return {'FINISHED'}

#Exit Retopo
class SPEEDRETOPO_OT_Exit_Retopo(bpy.types.Operator):
    bl_idname = 'object.exit_retopo'
    bl_label = "Exit Retopo"

    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if len([obj for obj in context.selected_objects if context.object is not None if obj.type == 'MESH' if
                context.object.mode == "OBJECT"]) == 1:
            return True

    def execute(self, context):
        # context.object.show_x_ray = False
        # context.space_data.show_occlude_wire = False

        # if "Retopo_Grid" in bpy.data.objects:
        #     bpy.ops.object.remove_retopo_grid()

        return {'FINISHED'}

# -----------------------------------------------------------------------------
#    UI
# -----------------------------------------------------------------------------

#Update Panels
# def speedretopo_update_panel_position(self, context):
#     try:
#         # bpy.utils.unregister_class(SPEEDRETOPO_PT_tools)
#         bpy.utils.unregister_class(SPEEDRETOPO_PT_ui)
#     except:
#         pass
#
#     try:
#         bpy.utils.unregister_class(SPEEDRETOPO_PT_ui)
#     except:
#         pass
#
#     if user_preferences.addons[addon_name].preferences.speedretopo_tab_location == 'tools':
#         SPEEDRETOPO_PT_ui.bl_category = user_preferences.addons[addon_name].preferences.category
#         bpy.utils.register_class(SPEEDRETOPO_PT_ui)
#
#     else:
#         bpy.utils.register_class(SPEEDRETOPO_PT_ui)

#Tools
# class SPEEDRETOPO_PT_tools(bpy.types.Panel):
#     bl_label = "SpeedRetopo"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "category"
#
#     def draw(self, context):
#         layout = self.layout
#         WM = context.window_manager
#         SpeedRetopo(self, context)

# UI
class SPEEDRETOPO_PT_ui(bpy.types.Panel):
    bl_label = "SpeedRetopo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        WM = context.window_manager
        if len(context.object is not None and context.selected_objects) == 1:
            SpeedRetopo(self, context)
        elif len(context.selected_objects) == 0:
            layout.label(text="Select An Object", icon='ERROR')
        else:
            layout.label(text="Selection Only One Object", icon='ERROR')


#Panel
def SpeedRetopo(self, context):
    layout = self.layout
    WM = context.window_manager
    obj = context.active_object
    view = context.space_data
    tool_settings = context.tool_settings

    addonPref = context.preferences.addons[__name__].preferences
    # hidden_wire = addonPref.hidden_wire
    # start_from = addonPref.start_from
    # obj_color = addonPref.obj_color
    # auto_add_mirror = addonPref.auto_add_mirror
    # use_in_front = addonPref.use_in_front
    # use_wireframe = addonPref.use_wireframe
    # mirror_axis = addonPref.mirror_axis

    # if context.object is not None :
    #     split = layout.split()
    #     col = split.column(align=True)
    #     row = col.row(align=True)
    #     row.label(text="Reference Object:")
    #     row = col.row(align=True)
    #     row.prop_search(WM, "speedretopo_ref_obj", bpy.data, 'objects', text='', icon='MESH_MONKEY')



        # if context.object is not None and context.object.mode == "EDIT":
            # row.scale_x = 1.2
            # row.prop(obj, "show_x_ray", text="", icon='UV_FACESEL')
            # row.prop("view3DShading.show_x_ray", text="", icon='UV_FACESEL')
            # bpy.data.screens["Scripting"].shading.show_xray = True

            # row.scale_x = 1.2
            # row.prop(view, "show_occlude_wire",text="", icon='LATTICE_DATA')

    #Object
    if context.object.mode == "OBJECT":
        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("object.create_speed_retopo", text="START RETOPO", icon='MOD_TRIANGULATE')

        box = layout.box()
        row = box.row(align=True)
        row.label(text="START RETOPO WITH", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        row.scale_y = 1.2
        if hasattr(bpy.types, "MESH_OT_poly_quilt"):
            row.prop(addonPref, "start_from", text="Start From", expand=True)
        else:
            row.prop(addonPref, "start_from_basic", text="Start From", expand=True)

        row = box.row(align=True)
        row.label(text="RETOPO SETTINGS", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "auto_add_mirror", text="Add Mirror Modifier")

        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "auto_add_shrinkwrap", text="Add Shrinkwrap Modifier")

        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "hidden_wire", text="Use Hidden Wire")

        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "use_in_front", text="Use In front")

        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "use_wireframe", text="Show Wireframe")

        row = box.row(align=True)
        row.scale_y = 1.2
        row.prop(addonPref, "obj_color", text="Object Color")

        box = layout.box()
        split = box.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row = col.row(align=True)
        row.label(text="CURRENT SHADING", icon='SHADING_WIRE')
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("speedretopo.clean_normals", text="Recalculate Normals")
        row = col.row(align=True)
        row.scale_y = 1.2
        shading = context.space_data.shading

        row = col.row(align=True)
        row.scale_y = 1.2
        if context.object.show_in_front == False:
            row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_OFF')
        elif context.object.show_in_front == True:
            row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_ON')

        row = col.row(align=True)
        row.scale_y = 1.2
        if context.object.show_wire == False:
            row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_OFF')
        elif context.object.show_wire == True:
            row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_ON')

        row = col.row(align=True)
        row.scale_y = 1.2
        if shading.show_backface_culling == False:
            row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_OFF')
        elif shading.show_backface_culling == True:
            row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_ON')




    if context.object.mode == "EDIT":
        # if context.object is not None :
        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.label(text="Reference Object:")
        row = col.row(align=True)
        row.prop_search(WM, "speedretopo_ref_obj", bpy.data, 'objects', text='', icon='MESH_MONKEY')

        #Bsurface
        if hasattr(bpy.types, "GPENCIL_OT_surfsk_add_surface"):
            row= layout.row(align=True)
            row.scale_y = 1.5
            row.scale_x = 1
            row.operator("gpencil.surfsk_add_surface", text="Add BSurface", icon='MESH_GRID')
            row.scale_x = 1.5
            # row.operator("wm.context_toggle", text="", icon="MESH_GRID").data_path = "space_data.use_occlude_geometry"
            row.operator("object.align2x", text="", icon='EMPTY_AXIS')
            # if hasattr(bpy.types, "MESH_OT_retopomt"):
            #     row = layout.row(align=True)
            #     row.scale_y = 1.5
            #     row.operator("mesh.retopomt", icon='VPAINT_HLT')

        else :
            row= layout.row(align=True)
            row.scale_y = 1.5
            row.label(text="Activate Bsurfaces", icon='ERROR')
            # row.operator("speedretopo.activate_bsurfaces", text="Activate Bsurfaces", icon='ERROR')

        #Shrinkwrap
        # split = layout.split()
        # col = split.column(align=True)
        # Mirror
        mirror = context.active_object.modifiers.get("Mirror")
        if mirror:
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.label(text="MIRROR", icon='MOD_MIRROR')
            row = col.row(align=True)
            row.scale_y = 1.3
            row.scale_x = 1.2
            if context.object.modifiers["Mirror"].show_viewport == False:
                row.prop(context.active_object.modifiers["Mirror"], "show_viewport", text="Show Mirror")
            elif context.object.modifiers["Mirror"].show_viewport == True:
                row.prop(context.active_object.modifiers["Mirror"], "show_viewport", text="Hide Mirror")
            row.prop(context.active_object.modifiers["Mirror"], "use_clip", text="", icon='UV_EDGESEL')
            row.operator("speedretopo.apply_mirror", text="", icon='FILE_TICK')
            row.operator("speedretopo.remove_mirror", text="", icon='X')
            row = col.row(align=True)
            row.prop(context.active_object.modifiers["Mirror"], "merge_threshold", text="Merge Limit")

        else:
            row = layout.row(align=True)
            row.scale_y = 1.3
            row.operator("speedretopo.add_mirror", text="Add Mirror", icon='MOD_MIRROR')

        #shrinkwrap
        shrinkwrap = context.active_object.modifiers.get("Shrinkwrap")
        if shrinkwrap :
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.label(text="SHRINKWRAP", icon='MOD_SHRINKWRAP')
            row = col.row(align=True)
            row.scale_y = 1.3
            row.scale_x = 1.2
            if context.object.modifiers["Shrinkwrap"].show_viewport == False:
                row.prop(context.active_object.modifiers["Shrinkwrap"], "show_viewport", text="Show Shrinkwrap")
            elif context.object.modifiers["Shrinkwrap"].show_viewport == True:
                row.prop(context.active_object.modifiers["Shrinkwrap"], "show_viewport", text="Hide Shrinkwrap")
            row.operator("speedretopo.update_shrinwrap", text="", icon='LOOP_FORWARDS')
            row.operator("speedretopo.apply_shrinkwrap", text="", icon='FILE_TICK')
            row.operator("speedretopo.remove_shrinkwrap", text="", icon='X')
            row = col.row(align=True)
            row.prop(context.active_object.modifiers["Shrinkwrap"], "offset", text = "Shrinkwrap Offset")
        else:
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.operator("speedretopo.add_shrinkwrap", text="Add shrinkwrap", icon = 'MOD_SHRINKWRAP')
            row.operator("speedretopo.add_apply_shrinkwrap", text="", icon='LOOP_FORWARDS')

        # Subsurf
        subsurf = context.active_object.modifiers.get("Subsurf")
        if subsurf:
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.label(text="SUBSURF", icon='MOD_SUBSURF')
            row = col.row(align=True)
            row.scale_y = 1.3
            row.scale_x = 1.2
            if context.object.modifiers["Subsurf"].show_viewport == False:
                row.prop(context.active_object.modifiers["Subsurf"], "show_viewport", text="Show Subsurf")
            elif context.object.modifiers["Subsurf"].show_viewport == True:
                row.prop(context.active_object.modifiers["Subsurf"], "show_viewport", text="Hide Subsurf")
            row.prop(context.active_object.modifiers["Subsurf"], "show_only_control_edges", text="", icon='MOD_TRIANGULATE')
            row.operator("speedretopo.apply_subsurf", text="", icon='FILE_TICK')
            row.operator("speedretopo.remove_subsurf", text="", icon='X')
            row = col.row(align=True)
            row.prop(context.active_object.modifiers["Subsurf"], "levels", text="Levels")

        else:
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.operator("speedretopo.add_subsurf", text="Add Subsurf", icon='MOD_SUBSURF')

        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.label(text="TOOLS", icon='MODIFIER_ON')

        #activate Looptools
        if hasattr(bpy.types, "MESH_OT_looptools_bridge"):

            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.5
            row.operator("mesh.looptools_gstretch", text="GStretch", icon = 'LINE_DATA')
            row.operator("object.space_relax", text="Space", icon = 'CENTER_ONLY')
            row = col.row(align=True)
            row.scale_y = 1.5
            row.operator("mesh.looptools_bridge", text="Bridge", icon = 'MOD_LATTICE')
            row.operator("mesh.fill_grid", text="Grid Fill", icon = 'OUTLINER_DATA_LATTICE')
        else:
            split = layout.split()
            col = split.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.operator("object.activate_looptools", text="Activate Looptools", icon='ERROR')

        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator("mesh.speed_retopo_relax", text="Relax", icon = 'LIGHTPROBE_GRID')

        # Threshold
        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.3
        if context.scene.tool_settings.use_mesh_automerge == False:
            row.prop(context.tool_settings, "use_mesh_automerge", text="Auto Merge", icon='RADIOBUT_OFF')
        elif context.scene.tool_settings.use_mesh_automerge == True:
            row.prop(context.tool_settings, "use_mesh_automerge", text="Auto Merge", icon='RADIOBUT_ON')
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop(tool_settings, "double_threshold", text="Threshold")
            row = col.row(align=True)
            row.scale_y = 1.3
            row.operator("object.double_threshold_minus", text="0.001")
            row.operator("object.double_threshold_plus", text="0.1")





        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator("speedretopo.clean_normals", text="Recalculate Normals")
        row.operator("mesh.flip_normals", text="", icon='LOOP_FORWARDS')
        row = col.row(align=True)
        row.scale_y = 1.3
        overlay = context.space_data.overlay
        shading = context.space_data.shading

        if overlay.show_occlude_wire == False:
            row.prop(overlay, "show_occlude_wire", text="Hidden Wire", icon='RADIOBUT_OFF')
        elif overlay.show_occlude_wire == True:
            row.prop(overlay, "show_occlude_wire", text="Hidden Wire", icon='RADIOBUT_ON')

        row = col.row(align=True)
        row.scale_y = 1.3
        if context.object.show_in_front == False:
            row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_OFF')
        elif context.object.show_in_front == True:
            row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_ON')

        row = col.row(align=True)
        row.scale_y = 1.3
        if context.object.show_wire == False:
            row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_OFF')
        elif context.object.show_wire == True:
            row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_ON')

        row = col.row(align=True)
        row.scale_y = 1.3
        if shading.show_backface_culling == False:
            row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_OFF')
        elif shading.show_backface_culling == True:
            row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_ON')



        #bpy.context.object.show_wire = False

        # #Grid
        # if not "Retopo_Grid" in bpy.data.objects :
        #     split = layout.split()
        #     col = split.column(align=True)
        #     row=col.row(align=True)
        #     row.scale_y = 1.3
        #     row.operator("object.recreate_grid", text="Add Retopo Grid", icon = 'OUTLINER_OB_LATTICE')
        #
        # elif not "Shrinkwrap_Grid" in obj.modifiers :
        #     split = layout.split()
        #     col = split.column(align=True)
        #     row=col.row(align=True)
        #     row.scale_y = 1.3
        #     row.operator("object.recreate_grid", text="Connect Grid", icon = 'OUTLINER_OB_LATTICE')
        # else :
        #     split = layout.split()
        #     col = split.column(align=True)
        #     row=col.row(align=True)
        #     row.scale_y = 1.3
        #     if bpy.data.objects["Retopo_Grid"].hide == True:
        #
        #         row.operator("object.hide_retopo_grid", text = "Show Grid", icon='RESTRICT_VIEW_ON')
        #
        #     elif bpy.data.objects["Retopo_Grid"].hide == False:
        #         row.operator("object.hide_retopo_grid", text = "Hide Grid", icon='RESTRICT_VIEW_OFF')
        #
        #     row.scale_x = 1.2
        #     row.prop(bpy.data.objects['Retopo_Grid'], "show_wire", text = "", icon='MESH_GRID')
        #     row.scale_x = 1.2
        #     row.operator("object.scale_grid", text="", icon='MAN_SCALE')
        #     row.scale_x = 1.2
        #     row.operator("object.remove_retopo_grid", text="", icon='X')
        #
        #     row = col.row(align=True)
        #     row.prop(bpy.data.objects['Retopo_Grid'].modifiers['Subsurf'], "levels", text="Grid Divisions")
        #     row = col.row(align=True)
        #     row.prop(bpy.data.materials['Retopo_Grid'], "diffuse_color", text = "")
        #     row.prop(bpy.data.materials['Retopo_Grid'], "alpha", text = "Alpha")




# class SPEEDRETOPO_OT_grid_options_menu(bpy.types.Operator):
#     bl_idname = "view3d.grid_options_menu"
#     bl_label = "Grid Settings"
#
#     def execute(self, context):
#         return {'FINISHED'}
#
#     def check(self, context):
#         return True
#
#     def invoke(self, context, event):
# #        AM = context.window_manager.asset_m
#         self.dpi_value = context.user_preferences.system.dpi
#
#         return context.window_manager.invoke_props_dialog(self, width=self.dpi_value*2.2, height=100)
#
#     def draw(self, context):
#         layout = self.layout
#
#         split = layout.split()
#         col = split.column(align=True)
#         row = col.row(align=True)
#         row.prop(bpy.data.objects['Retopo_Grid'].modifiers['Subsurf'], "levels", text="Grid Divisions")
#         row = col.row(align=True)
#         row.prop(bpy.data.materials['Retopo_Grid'], "diffuse_color", text = "")
#         row = col.row(align=True)
#         row.prop(bpy.data.materials['Retopo_Grid'], "alpha", text = "Alpha")

class SPEEDRETOPO_PT_start_retopo_settings(bpy.types.Operator):
    bl_idname = "view3d.start_retopo_settings"
    bl_label = "Start Retopo Settings"

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.object.mode == "OBJECT"

    def invoke(self, context, event):
        self.dpi_value = context.preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=self.dpi_value*2.2, height=100)

    def draw(self, context):
        layout = self.layout
        WM = context.window_manager

        addonPref = context.preferences.addons[__name__].preferences

        if context.object is not None and context.object.mode == "OBJECT":
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("object.create_speed_retopo", text="START RETOPO", icon='MOD_TRIANGULATE')
            box = layout.box()
            row = box.row(align=True)
            row.label(text="START RETOPO WITH", icon='TOOL_SETTINGS')
            row = box.row(align=True)
            row.scale_y = 1.2
            if hasattr(bpy.types, "MESH_OT_poly_quilt"):
                row.prop(addonPref, "start_from", text="Start From", expand=True)
            else:
                row.prop(addonPref, "start_from_basic", text="Start From", expand=True)

            row = box.row(align=True)
            row.label(text="RETOPO SETTINGS", icon='TOOL_SETTINGS')
            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "auto_add_mirror", text="Add Mirror Modifier")

            # if addonPref.auto_add_mirror:
            #     row = box.row(align=True)
            #     row.prop(addonPref, "mirror_axis_xyz", expand=True)

            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "auto_add_shrinkwrap", text="Add Shrinkwrap Modifier")

            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "hidden_wire", text="Use Hidden Wire")

            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "use_in_front", text="Use In front")

            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "use_wireframe", text="Show Wireframe")

            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(addonPref, "obj_color", text="Object Color")


# Pie Menu
class SPEEDRETOPO_MT_pie_menu(Menu):
    bl_label = "SPEEDRETOPO"

    @classmethod
    def poll(cls, context):
        return len(context.object is not None and context.selected_objects) == 1

    def draw(self, context):
        pie = self.layout.menu_pie()
        WM = context.window_manager
        obj = context.active_object
        view = context.space_data
        tool_settings = context.tool_settings

        if len(context.object is not None and context.selected_objects) == 1:
            # OBJECT_MODE
            if context.object.mode == "OBJECT":

                #4 - LEFT
                pie.separator()

                #6 - RIGHT
                pie.separator()

                #2 - BOTTOM
                split = pie.split()
                col = split.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("speedretopo.clean_normals", text="Recalculate Normals")
                # row.operator("mesh.flip_normals", text="", icon='LOOP_FORWARDS')
                row = col.row(align=True)
                row.scale_y = 1.2
                overlay = context.space_data.overlay
                shading = context.space_data.shading

                row = col.row(align=True)
                row.scale_y = 1.2
                if context.object.show_in_front == False:
                    row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_OFF')
                elif context.object.show_in_front == True:
                    row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_ON')

                row = col.row(align=True)
                row.scale_y = 1.3
                if context.object.show_wire == False:
                    row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_OFF')
                elif context.object.show_wire == True:
                    row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_ON')

                row = col.row(align=True)
                row.scale_y = 1.2
                if shading.show_backface_culling == False:
                    row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_OFF')
                elif shading.show_backface_culling == True:
                    row.prop(shading, "show_backface_culling", text="Back Face Culling", icon='RADIOBUT_ON')

                #8 - TOP
                pie.operator("object.create_speed_retopo", text="START RETOPO", icon='MOD_TRIANGULATE')

                #7 - TOP - LEFT
                pie.separator()
                # col = pie.column(align=True)
                # row=col.row(align=True)
                # row.label(text="Ref Object")
                # row=col.row(align=True)
                # row.scale_y = 1.2
                # row.prop_search(WM, "speedretopo_ref_obj", bpy.data, 'objects', text='', icon='MESH_MONKEY')

                #9 - TOP - RIGHT
                # col = pie.column(align=True)
                # row = col.row(align=True)
                # row.scale_y = 1.2
                pie.operator("view3d.start_retopo_settings", text="SETTINGS", icon='TOOL_SETTINGS')
                # if "Retopo_Grid" in bpy.data.objects == True:
                # # if any([context.object.show_x_ray, context.space_data.show_occlude_wire,
                # #         "Retopo_Grid" in bpy.data.objects]) == True:
                #     pie.operator("object.exit_retopo", text="Exit Retopo", icon='FILE_TICK')
                # pie.separator()

                #1 - BOTTOM - LEFT
                pie.separator()

                #3 - BOTTOM - RIGHT
                pie.separator()


            # EDIT_MODE
            if context.object.mode == "EDIT":
                #4 - LEFT
                #------Mirror
                col = pie.column(align=True)
                mirror = context.active_object.modifiers.get("Mirror")
                if mirror :
                    row=col.row(align=True)
                    row.label(text="", icon='MOD_MIRROR')
                    row.scale_x = 1.3
                    row.scale_y = 1.2
                    if context.object.modifiers["Mirror"].show_viewport == False :
                        row.prop(context.active_object.modifiers["Mirror"], "show_viewport", text="")
                    elif context.object.modifiers["Mirror"].show_viewport == True :
                        row.prop(context.active_object.modifiers["Mirror"], "show_viewport", text="")
                    # row.scale_x = 1.2
                    row.prop(context.active_object.modifiers["Mirror"], "use_clip", text="", icon='UV_EDGESEL')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.apply_mirror", text="", icon='FILE_TICK')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.remove_mirror", text="", icon='X')
                    # row.prop(context.active_object.modifiers["Mirror"], "merge_threshold", text="Mirror Merge Limit")


                #------shrinkwrap
                shrinkwrap = context.active_object.modifiers.get("Shrinkwrap")
                if shrinkwrap :
                    row = col.row(align=True)
                    row.label(text="", icon='MOD_SHRINKWRAP')
                    row.scale_x = 1.3
                    row.scale_y = 1.2
                    if context.object.modifiers["Shrinkwrap"].show_viewport == False:
                        row.prop(context.active_object.modifiers["Shrinkwrap"], "show_viewport", text="")
                    elif context.object.modifiers["Shrinkwrap"].show_viewport == True:
                        row.prop(context.active_object.modifiers["Shrinkwrap"], "show_viewport", text="")
                    row.operator("speedretopo.update_shrinwrap", text="", icon='LOOP_FORWARDS')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.apply_shrinkwrap", text="", icon='FILE_TICK')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.remove_shrinkwrap", text="", icon='X')


                # Subsurf
                subsurf = context.active_object.modifiers.get("Subsurf")
                if subsurf:
                    row = col.row(align=True)
                    row.label(text="", icon='MOD_SUBSURF')
                    row.scale_x = 1.3
                    row.scale_y = 1.2
                    if context.object.modifiers["Subsurf"].show_viewport == False:
                        row.prop(context.active_object.modifiers["Subsurf"], "show_viewport", text="")
                    elif context.object.modifiers["Subsurf"].show_viewport == True:
                        row.prop(context.active_object.modifiers["Subsurf"], "show_viewport", text="")
                    # row.scale_x = 1.2
                    row.prop(context.active_object.modifiers["Subsurf"], "show_only_control_edges", text="", icon='MOD_TRIANGULATE')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.apply_subsurf", text="", icon='FILE_TICK')
                    # row.scale_x = 1.2
                    row.operator("speedretopo.remove_subsurf", text="", icon='X')
                    # row.prop(context.active_object.modifiers["Subsurf"], "levels", text="Levels")



                if not mirror:
                    row=col.row(align=True)
                    row.scale_y = 1.2
                    row.operator("speedretopo.add_mirror", text="Add Mirror", icon = 'MOD_MIRROR')

                if not shrinkwrap:
                    row=col.row(align=True)
                    row.scale_y = 1.2
                    row.operator("speedretopo.add_shrinkwrap", text="Add shrinkwrap", icon = 'MOD_SHRINKWRAP')
                    row.operator("speedretopo.add_apply_shrinkwrap", text="", icon='LOOP_FORWARDS')
                    # row.prop(context.active_object.modifiers["Shrinkwrap"], "offset", text="Shrinkwrap Offset")

                if not subsurf:
                    row = col.row(align=True)
                    row.scale_y = 1.2
                    row.operator("speedretopo.add_subsurf", text="Add Subsurf", icon='MOD_SUBSURF')


                #6 - RIGHT
                pie.operator("object.align2x", text="Align to X", icon='EMPTY_AXIS')


                #2 - BOTTOM
                split = pie.split()
                col = split.column(align=True)
                # row.separator()
                # row = col.row(align=True)
                # row.separator()
                # row = col.row(align=True)
                # row.separator()
                # row = col.row(align=True)
                # row.separator()
                # row = col.row(align=True)
                # row.separator()
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("speedretopo.clean_normals", text="Recalculate Normals", icon='MOD_NORMALEDIT')
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("mesh.flip_normals", text="Flip Normals", icon='LOOP_FORWARDS')
                row = col.row(align=True)
                row.scale_y = 1.2
                overlay = context.space_data.overlay
                shading = context.space_data.shading

                if overlay.show_occlude_wire == False :
                    row.prop(overlay, "show_occlude_wire", text = "Hidden Wire", icon='RADIOBUT_OFF')
                elif overlay.show_occlude_wire == True :
                    row.prop(overlay, "show_occlude_wire", text = "Hidden Wire", icon='RADIOBUT_ON')

                row = col.row(align=True)
                row.scale_y = 1.2
                if context.object.show_in_front == False:
                    row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_OFF')
                elif context.object.show_in_front == True:
                    row.prop(context.object, "show_in_front", text="In Front", icon='RADIOBUT_ON')

                row = col.row(align=True)
                row.scale_y = 1.3
                if context.object.show_wire == False:
                    row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_OFF')
                elif context.object.show_wire == True:
                    row.prop(context.object, "show_wire", text="Wireframe", icon='RADIOBUT_ON')

                row = col.row(align=True)
                row.scale_y = 1.2
                if shading.show_backface_culling == False :
                    row.prop(shading, "show_backface_culling", text = "Back Face Culling", icon='RADIOBUT_OFF')
                elif shading.show_backface_culling == True :
                    row.prop(shading, "show_backface_culling", text = "Back Face Culling", icon='RADIOBUT_ON')
                #bpy.context.object.show_in_front = True


                # bpy.context.space_data.overlay.show_occlude_wire = False
                # bpy.context.space_data.shading.show_backface_culling = True
                # bpy.context.space_data.shading.show_xray = True

                # if hasattr(bpy.types, "MESH_OT_retopomt"):
                #     pie.operator("mesh.retopomt", icon='VPAINT_HLT')
                #
                # else:
                # if hasattr(bpy.types, "MESH_OT_looptools_bridge"):
                #     pie.operator("mesh.fill_grid", text="Grid Fill", icon = 'OUTLINER_DATA_LATTICE')
                # else:
                #     row= pie.row()
                #     row.scale_y = 1.5
                #     row.operator("object.activate_looptools", text="Activate Looptools", icon='ERROR')

                #8 - TOP
                if hasattr(bpy.types, "GPENCIL_OT_surfsk_add_surface"):

                    pie.operator("gpencil.surfsk_add_surface", text="Add BSurface", icon='MESH_GRID')
                    # row.operator("gpencil.layer_remove", text="", icon='X')
                else :
                    pie.label(text="Activate Bsurfaces", icon='ERROR')
                    # pie.operator("speedretopo.activate_bsurfaces", text="Activate Bsurface", icon='ERROR')


                #7 - TOP - LEFT
                col = pie.column(align=True)
                row=col.row(align=True)
                row.prop_search(WM, "speedretopo_ref_obj", bpy.data, 'objects', text='', icon='MESH_MONKEY')
                # row.scale_x = 1.2
                # row.prop(obj, "show_x_ray", text="", icon='UV_FACESEL')
                # row.scale_x = 1.2
                # row.prop(view, "show_occlude_wire",text="", icon='LATTICE_DATA')

                #------Threshold
                row=col.row(align=True)
                row.scale_y = 1.2
                row.scale_x = 1
                if context.scene.tool_settings.use_mesh_automerge == False :
                    row.prop(context.tool_settings, "use_mesh_automerge", text = "Auto Merge", icon='RADIOBUT_OFF')
                elif context.scene.tool_settings.use_mesh_automerge == True :
                    row.prop(context.tool_settings, "use_mesh_automerge", text = "Auto Merge", icon='RADIOBUT_ON')
                row.operator("object.double_threshold_plus", text="0.1")
                row.operator("object.double_threshold_minus", text="0.001")

                # #------Grid
                # if not "Retopo_Grid" in bpy.data.objects :
                #     row=col.row(align=True)
                #     row.scale_y = 1.3
                #     row.operator("object.recreate_grid", text="Add Retopo Grid", icon = 'OUTLINER_OB_LATTICE')
                #
                # elif not "Shrinkwrap_Grid" in obj.modifiers :
                #     row=col.row(align=True)
                #     row.scale_y = 1.3
                #     row.operator("object.recreate_grid", text="Connect Grid", icon = 'OUTLINER_OB_LATTICE')
                # else :
                #     row=col.row(align=True)
                #     row.scale_y = 1.3
                #     if bpy.data.objects["Retopo_Grid"].hide == True:
                #
                #         row.operator("object.hide_retopo_grid", text = "Show Grid", icon='RESTRICT_VIEW_ON')
                #
                #     elif bpy.data.objects["Retopo_Grid"].hide == False:
                #         row.operator("object.hide_retopo_grid", text = "Hide Grid", icon='RESTRICT_VIEW_OFF')
                #
                #     row.scale_x = 1.2
                #     row.prop(bpy.data.objects['Retopo_Grid'], "show_wire", text = "", icon='MESH_GRID')
                #     row.scale_x = 1.2
                #     row.operator("object.scale_grid", text="", icon='MAN_SCALE')
                #     row.scale_x = 1.2
                #     row.operator("view3d.grid_options_menu", icon='SCRIPTWIN', text='')
                #     row.scale_x = 1.2
                #     row.operator("object.remove_retopo_grid", text="", icon='X')

                #9 - TOP - RIGHT
                if hasattr(bpy.types, "MESH_OT_looptools_bridge"):
                    pie.operator("object.space_relax", text="Space", icon = 'CENTER_ONLY')
                else:
                    # row= pie.row()
                    # row.scale_y = 1.5
                    pie.operator("object.activate_looptools", text="Activate Looptools", icon='ERROR')

                #1 - BOTTOM - LEFT
                split = pie.split()
                col = split.column(align=True)
                if hasattr(bpy.types, "MESH_OT_looptools_bridge"):

                    # if hasattr(bpy.types, "MESH_OT_retopomt"):
                    #     row = col.row(align=True)
                    #     row.scale_y = 1.2
                    #     row.scale_x = 1.3
                    #     row.operator("mesh.fill_grid", text="Grid Fill", icon = 'OUTLINER_DATA_LATTICE')

                    row = col.row(align=True)
                    row.scale_y = 1.2
                    row.scale_x = 1.3
                    row.operator("mesh.looptools_gstretch", text="GStretch", icon = 'LINE_DATA')
                    row = col.row(align=True)
                    row.scale_y = 1.2
                    row.scale_x = 1.3
                    row.operator("mesh.looptools_bridge", text="Bridge", icon = 'MOD_LATTICE')
                    row = col.row(align=True)
                    row.scale_y = 1.2
                    row.scale_x = 1.3
                    row.operator("mesh.fill_grid", text="Grid Fill", icon='OUTLINER_DATA_LATTICE')

                else:
                    pie.operator("object.activate_looptools", text="Activate Looptools", icon='ERROR')

                #3 - BOTTOM - RIGHT
                pie.operator("mesh.speed_retopo_relax", text="Relax", icon = 'LIGHTPROBE_GRID')

        elif len(context.selected_objects) == 0:
            pie.separator()
            pie.separator()
            pie.separator()
            pie.operator("object.select_all", text="Select An Object", icon='ERROR').action = 'DESELECT'
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()

        else:
            pie.separator()
            pie.separator()
            pie.separator()
            pie.operator("object.select_all", text="Select Only One Object", icon='ERROR').action = 'DESELECT'
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()


# -----------------------------------------------------------------------------
#    Preferences      
# -----------------------------------------------------------------------------

keymaps_items_dict = { "Speedretopo Pie Menu":['wm.call_menu_pie', 'SPEEDRETOPO_MT_pie_menu',
                                      '3D View Generic', 'VIEW_3D', 'WINDOW',
                                       'RIGHTMOUSE', 'PRESS', False, True, False
                                      ]
                     }

def update_speedretopo_category(self, context):
    is_panel = hasattr(bpy.types, 'SPEEDRETOPO_PT_ui')

    if is_panel:
        try:
            bpy.utils.unregister_class(SPEEDRETOPO_PT_ui)
        except:
            pass
    SPEEDRETOPO_PT_ui.bl_category = self.category
    bpy.utils.register_class(SPEEDRETOPO_PT_ui)

# Preferences            
class SPEEDFLOW_MT_addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    prefs_tabs: EnumProperty(
        items=(('info', "Info", "ADDON INFO"),
               ('options', "Options", "ADDON OPTIONS"),
               ('keymaps', "Keymaps", "CHANGE KEYMAPS"),
               ('tutorials', 'Tutorials', 'Tutorials'),
               ('addons', "Addons", "Addons"),
               ('links', "Links", "LINKS")),
        default='options')

    hidden_wire : BoolProperty(name="Hidden Wire", default=True)

    start_from_basic: EnumProperty(
        items=(('BSURFACE', "BSurface", ""),
               ('VERTEX', "Vertex", ""),
               ('POLYBUILD', "Polybuild", "")),
        default='VERTEX')

    start_from: EnumProperty(
        items=(('BSURFACE', "BSurface", ""),
               ('VERTEX', "Vertex", ""),
               ('POLYBUILD', "Polybuild", ""),
               ('POLYQUILT', "PolyQuilt", "")),
        default='VERTEX')

    auto_add_mirror: BoolProperty(name="Auto Add Mirror", default=True)
    auto_add_shrinkwrap: BoolProperty(name="Auto Add Shrinkwrap", default=True)
    use_in_front: BoolProperty(name="Use In Front Setting", default=True)
    use_wireframe: BoolProperty(name="Use Wireframe", default=True)
    obj_color: FloatVectorProperty(name="", default=(0, 0.65, 1, 0.5), min=0, max=1, size=4, subtype='COLOR_GAMMA')
    mirror_axis: BoolVectorProperty(default=[True, False, False], size=3, name="")


    category : StringProperty(description="Choose a name for the category of the panel",default="Tools",update=update_speedretopo_category)


    # mirror_axis_xyz: EnumProperty(
    #     items=(('X', "X", ""),
    #            ('Y', "Y", ""),
    #            ('Z', "Z", "")),
    #     options={'ENUM_FLAG'},
    #     # default = {'X'}
    # )

    # category : bpy.props.StringProperty(
    #         name="Category",
    #         description="Choose a name for the category of the panel",
    #         default="Tools",
    #         update=speedretopo_update_panel_position)
    
    # use_pie_menu : BoolProperty(
    #         name="Use Pie Menu",
    #         default=True
    #         )
    
    #Grid Options
    # use_grid : BoolProperty(
    #         name="Use Grid",
    #         default=True
    #         )
    #
    # grid_color : FloatVectorProperty(
    #         name="Color:",
    #         default=(0.1, 0.3, 0.5),
    #         min=0, max=1,
    #         precision=3,
    #         subtype='COLOR'
    #         )
    #
    # grid_alpha : FloatProperty(
    #         default=0.5,
    #         min=0, max=1,
    #         precision=3
    #         )
    #
    # grid_show_wire : BoolProperty(
    #         name="Show wire",
    #         default=True
    #         )
    #
    # grid_subdivisions : IntProperty(
    #         name="",
    #         default=3,
    #         min=0, max=6
    #         )

                                         
    #Tab Location           
    # speedretopo_tab_location : EnumProperty(
    #     name = 'Panel Location',
    #     description = 'The 3D view shelf to use. (Save user settings and restart Blender)',
    #     items=(('tools', 'Tool Shelf', 'Places the Asset Management panel in the tool shelf'),
    #            ('ui', 'Property Shelf', 'Places the Asset Management panel in the property shelf.')),
    #            default='tools',
    #            update = speedretopo_update_panel_position,
    #            )
                                    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager


        row= layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)
        if self.prefs_tabs == 'info':
            layout.label(text="Welcome to SpeedRetopo, this addon allows you to create fast retopology")
            layout.label(text="To use is, activate Bsurface, Looptools and Automirror")

        if self.prefs_tabs == 'options':
            box = layout.box()

            row = box.row(align=True)
            row.label(text="Panel Category:")
            row.prop(self, "category", text="")

            box = layout.box()
            row = box.row(align=True)
            row.label(text="Start Retopo From")
            if hasattr(bpy.types, "MESH_OT_poly_quilt"):
                row.prop(self, "start_from", text="")
            else:
                row.prop(self, "start_from_basic", text="")
                # row.prop(self, "start_from", text="")

            row = box.row(align=True)
            row.label(text="Auto Add Mirror")
            row.prop(self, "auto_add_mirror", text="      ")

            # if self.auto_add_mirror:
            #     split = box.split()
            #     col = split.column()
            #     col.label(text="Mirror Axis:")
            #     col = split.column(align=True)
            #     col.prop(self, 'mirror_axis', expand=True)

            row = box.row(align=True)
            row.label(text="Auto Add Shrinkwrap")
            row.prop(self, "auto_add_shrinkwrap", text="      ")

            row = box.row(align=True)
            row.label(text="Use Hidden Wire")
            row.prop(self, "hidden_wire", text="      ")

            row = box.row(align=True)
            row.label(text="Use Wireframe")
            row.prop(self, "use_wireframe", text="      ")

            row = box.row(align=True)
            row.label(text="Use In Front")
            row.prop(self, "use_in_front", text="      ")

            row = box.row(align=True)
            row.label(text="Color")
            row.prop(self, "obj_color")

            # layout = self.layout
            #
            # box = layout.box()
            # box.label(text="Panel Location: ")
            #
            # # row= box.row(align=True)
            # # row.prop(self, 'speedretopo_tab_location', expand=True)
            # # row = box.row()
            # # if self.speedretopo_tab_location == 'tools':
            # #     split = box.split()
            # #     col = split.column()
            # #     col.label(text=text="Change Category:")
            # #     col = split.column(align=True)
            # #     col.prop(self, "category", text="")
            #
            # row= box.row(align=True)
            # row.prop(self, 'use_pie_menu', expand=True)
            #
            # #Keymap pie menu
            # if self.use_pie_menu :
            #     split = box.split()
            #     col = split.column()
            #     col.label(text='Setup Pie menu Hotkey')
            #     col.separator()
            #     wm = context.window_manager
            #     kc = wm.keyconfigs.user
            #     km = kc.keymaps['3D View Generic']
            #     kmi = get_hotkey_entry_item(km, 'wm.call_menu_pie', 'view3d.speed_retopo_pie_menu')
            #     if kmi:
            #         col.context_pointer_set("keymap", km)
            #         rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            #     else:
            #         col.label(text="No hotkey entry found")
            #         col.operator(SpeedRetopoAddHotkey.bl_idname, text = "Add hotkey entry", icon = 'ZOOMIN')


            # row = box.row(align=True)
            # row.label(text="Save preferences to apply these settings", icon='ERROR')

            # box = layout.box()
            # box.label(text="Grid Options: ")
            # # split = box.split()
            #
            # row = box.row(align=True)
            # row.prop(self, "use_grid", expand=True)
            #
            # row = box.row(align=True)
            # row.label(text="Grid Color:")
            # row.prop(self, "grid_color", text="")
            #
            # row = box.row(align=True)
            # row.label(text="Grid Alpha:")
            # row.prop(self, "grid_alpha", text="")
            #
            # row = box.row(align=True)
            # row.label(text="Grid Subdivisions:")
            # row.prop(self, "grid_subdivisions", text="")
            #
            # row = box.row(align=True)
            # row.prop(self, "grid_show_wire", expand=True)

        # KEYMAPS
        if self.prefs_tabs == 'keymaps':
            wm = bpy.context.window_manager
            draw_keymap_items(wm, layout)

        # TUTORIALS
        if self.prefs_tabs == 'tutorials':
            box = layout.box()
            box.label(text="Free Tutorials:", icon='COMMUNITY')
            box.operator("wm.url_open", text="Youtube Channel").url = "https://www.youtube.com/user/pitiwazou"
            box.label(text="Paid Tutorials:", icon='HAND')
            box.operator("wm.url_open",
                         text="Speedflow Basics").url = "https://gumroad.com/l/speedflow_basics"
            box.operator("wm.url_open",
                         text="Sony BSP10 Non - Destructive Workflow").url = "https://gumroad.com/l/sony_bsp10_non_destructive_tutorial"
            box.operator("wm.url_open",
                         text="Non - Destructive Workflow Tutorial 1").url = "https://gumroad.com/l/Non-Destructive_Workflow_Tutorial_1"
            box.operator("wm.url_open",
                         text="Non - Destructive Workflow Tutorial 2").url = "https://gumroad.com/l/Non-Destructive_Workflow_Tutorial_2"
            box.operator("wm.url_open",
                         text="Non - Destructive Workflow Tutorial 3").url = "https://gumroad.com/l/Non-Destructive_Workflow_Tutorial_3"
            box.operator("wm.url_open",
                         text="Hydrant Modeling Tutorial").url = "https://gumroad.com/l/hydrant_modeling_tutorial"
            box.operator("wm.url_open",
                         text="Hydrant Unwrapping Tutorial").url = "https://gumroad.com/l/hydrant_unwrapping_tutorial"
            box.operator("wm.url_open",
                         text="Furry Warfare Plane Modeling Tutorial").url = "https://gumroad.com/l/furry_warfare_plane_modeling_tutorial"

        # Addons
        if self.prefs_tabs == 'addons':
            box = layout.box()
            box.operator("wm.url_open", text="Addon's Discord").url = "https://discord.gg/ctQAdbY"
            box.separator()
            box.operator("wm.url_open", text="Asset Management").url = "https://gumroad.com/l/asset_management"
            box.operator("wm.url_open", text="Speedflow").url = "https://gumroad.com/l/speedflow"
            box.operator("wm.url_open", text="SpeedSculpt").url = "https://gumroad.com/l/SpeedSculpt"
            box.operator("wm.url_open", text="SpeedRetopo").url = "https://gumroad.com/l/speedretopo"
            box.operator("wm.url_open", text="Easyref").url = "https://gumroad.com/l/easyref"
            box.operator("wm.url_open", text="RMB Pie Menu").url = "https://gumroad.com/l/wazou_rmb_pie_menu_v2"
            box.operator("wm.url_open", text="Wazou's Pie Menu").url = "https://gumroad.com/l/wazou_pie_menus"
            box.operator("wm.url_open", text="Smart Cursor").url = "https://gumroad.com/l/smart_cursor"
            box.label(text="Archipack", icon='BLENDER')
            box.operator("wm.url_open", text="Archi Pack").url = "https://blender-archipack.org"
            box.operator("wm.url_open",
                         text="My 2.8 Theme").url = "https://www.dropbox.com/s/s95wj828l5mw8nf/wazou_red_280_001.xml?dl=0"

        # URls
        if self.prefs_tabs == 'links':
            box = layout.box()
            box.label(text="Support me:", icon='HAND')
            box.operator("wm.url_open", text="Patreon").url = "https://www.patreon.com/pitiwazou"
            box.operator("wm.url_open", text="Tipeee").url = "https://www.tipeee.com/blenderlounge"

            box.separator()
            box.label(text="Web:", icon='WORLD')
            box.operator("wm.url_open", text="Pitiwazou.com").url = "http://www.pitiwazou.com/"
            box.separator()
            box.label(text="Youtube:", icon='SEQUENCE')
            box.operator("wm.url_open", text="Youtube - Pitiwazou").url = "https://www.youtube.com/user/pitiwazou"
            box.operator("wm.url_open",
                         text="Youtube - Blenderlounge").url = "https://www.youtube.com/channel/UCaA3_WSE5A0H6YrS1SDfAQw/videos"
            box.separator()
            box.label(text="Social:", icon='USER')
            box.operator("wm.url_open", text="Artstation").url = "https://www.artstation.com/artist/pitiwazou"
            box.operator("wm.url_open", text="Twitter").url = "https://twitter.com/#!/pitiwazou"
            box.operator("wm.url_open",
                         text="Facebook").url = "https://www.facebook.com/Pitiwazou-C%C3%A9dric-Lepiller-120591657966584/"
            box.operator("wm.url_open", text="Google+").url = "https://plus.google.com/u/0/116916824325428422972"
            box.operator("wm.url_open", text="Blenderlounge's Discord").url = "https://discord.gg/MBDphac"
                            

# -----------------------------------------------------------------------------
#    Keymap
# -----------------------------------------------------------------------------
addon_keymaps = []

def draw_keymap_items(wm, layout):
    kc = wm.keyconfigs.user

    for name, items in keymaps_items_dict.items():
        kmi_name, kmi_value, km_name = items[:3]
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(text=name)
        col.separator()
        km = kc.keymaps[km_name]
        get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col)


def get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col):

    # for menus and pie_menu
    if kmi_value:
        for km_item in km.keymap_items:
            if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                return

        col.label(text=f"No hotkey entry found for {kmi_value}")
        col.operator(SPEEDRETOPO_OT_Add_Hotkey.bl_idname, icon='ADD')

    # for operators
    else:
        if km.keymap_items.get(kmi_name):
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi(
                    [], kc, km, km.keymap_items[kmi_name], col, 0)
        else:
            col.label(text=f"No hotkey entry found for {kmi_name}")
            col.operator(SPEEDRETOPO_OT_Add_Hotkey.bl_idname, icon='ADD')


class SPEEDRETOPO_OT_Add_Hotkey(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "template_rmb.add_hotkey"
    bl_label = "Add Hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey()

        self.report({'INFO'},
                    "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
        return {'FINISHED'}

def add_hotkey():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        return

    for items in keymaps_items_dict.values():
        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        eventType, eventValue, ctrl, shift, alt = items[5:]
        km = kc.keymaps.new(name = km_name, space_type = space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, eventType,
                                  eventValue, ctrl = ctrl, shift = shift,
                                  alt = alt

                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

    addon_keymaps.append((km, kmi))


def remove_hotkey():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''

    kmi_values = [item[1] for item in keymaps_items_dict.values() if item]
    kmi_names = [item[0] for item in keymaps_items_dict.values() if item not in ['wm.call_menu', 'wm.call_menu_pie']]

    for km, kmi in addon_keymaps:
        # remove addon keymap for menu and pie menu
        if hasattr(kmi.properties, 'name'):
            if kmi_values:
                if kmi.properties.name in kmi_values:
                    km.keymap_items.remove(kmi)

        # remove addon_keymap for operators
        else:
            if kmi_names:
                if kmi.name in kmi_names:
                    km.keymap_items.remove(kmi)

    addon_keymaps.clear()



CLASSES =  [SPEEDRETOPO_OT_activate_bsurfaces,
            SPEEDRETOPO_OT_activate_looptools,
            SPEEDRETOPO_OT_create_speedretopo,
            SPEEDRETOPO_OT_align_to_x,
            SPEEDRETOPO_OT_add_mirror,
            SPEEDRETOPO_OT_apply_mirror,
            SPEEDRETOPO_OT_remove_mirror,
            SPEEDRETOPO_OT_apply_shrinkwrap,
            SPEEDRETOPO_OT_add_shrinkwrap,
            SPEEDRETOPO_OT_update_shrinwrap,
            SPEEDRETOPO_OT_srrelax,
            SPEEDRETOPO_OT_space_relax,
            SPEEDRETOPO_OT_mesh_align_vertices,
            SPEEDRETOPO_OT_double_threshold_plus,
            SPEEDRETOPO_OT_double_threshold_minus,
            SPEEDRETOPO_OT_add_and_apply_shrinkwrap,
            SPEEDRETOPO_OT_remove_shrinkwrap,
            SPEEDRETOPO_OT_add_subsurf,
            SPEEDRETOPO_OT_apply_subsurf,
            SPEEDRETOPO_OT_remove_subsurf,
            SPEEDRETOPO_OT_clean_normals,
            SPEEDRETOPO_PT_start_retopo_settings,
            SPEEDRETOPO_PT_ui,
            SPEEDRETOPO_MT_pie_menu,
            SPEEDRETOPO_OT_Add_Hotkey,
            SPEEDFLOW_MT_addon_preferences]


# SPEEDRETOPO_OT_mesh_auto_mirror,
# SPEEDRETOPO_OT_Exit_Retopo,
# SPEEDRETOPO_OT_scale_grid,
# SPEEDRETOPO_OT_finalize,
# SPEEDRETOPO_OT_test,
# SPEEDRETOPO_OT_remove_retopo_grid,
# SPEEDRETOPO_OT_recreate_grid,
# SPEEDRETOPO_OT_create_grid,
# SPEEDRETOPO_OT_hide_retopo_grid,
# SPEEDRETOPO_OT_grid_options_menu,

def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            print(f"{cls.__name__} already registred")

    # Update Category
    context = bpy.context
    prefs = context.preferences.addons[__name__].preferences
    update_speedretopo_category(prefs, context)

    add_hotkey()

def unregister():
    for cls in CLASSES:
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)

    remove_hotkey()


            