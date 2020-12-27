import bpy
import os
from bpy.props import BoolProperty, PointerProperty, StringProperty, EnumProperty, IntProperty, FloatProperty
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu
from .operators import scene_refresh, get_rendered_objects, find_tallest_object
from .addon_updater import Updater as updater
from .__init__ import bl_info

################################################################################################################
# PRESETS
################################################################################################################


class GRABDOC_MT_presets(Menu):
    bl_label = ""
    preset_subdir = "grabDoc"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class GRABDOC_PT_presets(PresetPanel, Panel):
    bl_label = 'GrabDoc Presets'
    preset_subdir = 'grab_doc'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'grab_doc.preset_add'


class GRABDOC_OT_add_preset(AddPresetBase, bpy.types.Operator):
    bl_idname = "grab_doc.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "GRABDOC_MT_presets"

    # Variable used for all preset values
    preset_defines = ["grabDoc = bpy.context.scene.grabDoc"]

    # Properties to store in the preset
    preset_values = [
        "grabDoc.collSelectable",
        "grabDoc.collVisible",
        "grabDoc.useGrid",
        "grabDoc.gridSubdivisions",
        "grabDoc.scalingSet",

        "grabDoc.exportPath",
        "grabDoc.exportName",
        "grabDoc.exportResX",
        "grabDoc.exportResY",
        "grabDoc.lockRes",
        "grabDoc.imageType",
        "grabDoc.colorDepth",
        "grabDoc.imageComp",
        "grabDoc.imageCompTIFF",

        "grabDoc.onlyRenderColl",
        "grabDoc.exportPlane",        
        "grabDoc.openFolderOnExport",

        "grabDoc.uiVisibilityNormals",
        "grabDoc.uiVisibilityCurvature",
        "grabDoc.uiVisibilityOcclusion",
        "grabDoc.uiVisibilityHeight",
        "grabDoc.uiVisibilityMatID",

        "grabDoc.autoExitCamera",

        "grabDoc.exportNormals",
        "grabDoc.reimportAsMatNormals",
        "grabDoc.flipYNormals",
        "grabDoc.samplesNormals",

        "grabDoc.exportCurvature",
        "grabDoc.ridgeCurvature",
        "grabDoc.valleyCurvature",
        "grabDoc.samplesCurvature",
        "grabDoc.contrastCurvature",

        "grabDoc.exportOcclusion",
        "grabDoc.reimportAsMatOcclusion",
        "grabDoc.gammaOcclusion",
        "grabDoc.distanceOcclusion",
        "grabDoc.samplesOcclusion",
        "grabDoc.contrastOcclusion",

        "grabDoc.exportHeight",
        "grabDoc.rangeTypeHeight",
        "grabDoc.guideHeight",
        "grabDoc.flatMaskHeight",
        "grabDoc.samplesHeight",

        "grabDoc.exportMatID",
        "grabDoc.methodMatID",
        "grabDoc.samplesMatID",

        "grabDoc.bakerType",
        "grabDoc.marmoExportPath",
        "grabDoc.marmoAutoBake",
        "grabDoc.marmoClosePostBake",
        "grabDoc.marmoSamples",
        "grabDoc.marmoAORayCount"]

    # Where to store the preset
    preset_subdir = "grab_doc"


############################################################
# USER PREFERENCES
############################################################


class GRABDOC_OT_check_for_update(bpy.types.Operator):
    bl_idname = "updater_gd.check_for_update"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        updater.check_for_update_now()
        return{'FINISHED'}


class GRABDOC_MT_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        if updater.update_ready == None:
            row.label(text = "Checking for an update...")

            updater.check_for_update_now()

        elif updater.update_ready:
            row.alert = True
            row.label(text = "There is a GrabDoc update available! Get it on Gumroad :D")

        elif not updater.update_ready:
            row.label(text = "You have the latest version of GrabDoc! There are no new versions available.")

            row.operator("updater_gd.check_for_update", text = "", icon = "FILE_REFRESH")

        #res = updater.run_update(force=False, revert_tag=None, callback=None)
        #if res == 0:
        #    print("Update ran successfully, restart blender")
        #else:
        #    print("Updater returned "+str(res)+", error occurred")


############################################################
# PROPERTY GROUP
############################################################


class GRABDOC_property_group(bpy.types.PropertyGroup):
    ## UPDATE FUNCTIONS ##

    def update_res_x(self, context):
        if self.lockRes:
            if self.exportResX != self.exportResY:
                self.exportResY = self.exportResX

        scene_refresh(self, context)

    def update_res_y(self, context):
        if self.lockRes:
            if self.exportResY != self.exportResX:
                self.exportResX = self.exportResY

        scene_refresh(self, context)

    def update_export_name(self, context):
        if not self.exportName:
            self.exportName = "untitled"

    def update_curvature(self, context):
        if self.modalState:
            scene_shading = bpy.data.scenes[str(context.scene.name)].display.shading

            scene_shading.cavity_ridge_factor = scene_shading.curvature_ridge_factor = self.ridgeCurvature
            scene_shading.curvature_valley_factor = self.valleyCurvature

    def update_flip_y(self, context):
        vec_multiply_node = bpy.data.node_groups["GD_Normals"].nodes.get('Vector Math')
        vec_multiply_node.inputs[1].default_value[1] = -.5 if self.flipYNormals else .5

    def update_occlusion_gamma(self, context):
        gamma_node = bpy.data.node_groups["GD_Ambient Occlusion"].nodes.get('Gamma')
        gamma_node.inputs[1].default_value = self.gammaOcclusion

    def update_occlusion_distance(self, context):
        # Update here so that it refreshes live in the VP
        if self.modalState:
            context.scene.eevee.gtao_distance = self.distanceOcclusion

    def update_manual_height_range(self, context):
        scene_refresh(self, context)

        if self.modalState:
            if self.rangeTypeHeight == 'AUTO':
                get_rendered_objects(self, context)

                find_tallest_object(self, context)
                
            bpy.data.objects["GD_Background Plane"].active_material = bpy.data.materials['GD_Material (do not touch contents)']

    def update_height_guide(self, context):
        map_range_node = bpy.data.node_groups["GD_Height"].nodes.get('Map Range')
        map_range_node.inputs[1].default_value = 4.9999 if self.flatMaskHeight else -self.guideHeight + 5
        map_range_node.inputs[2].default_value = 5

        if self.rangeTypeHeight == 'MANUAL':
            scene_refresh(self, context)

        # Update here so that it refreshes live in the VP
        if self.modalState:
            bpy.data.objects["GD_Background Plane"].active_material = bpy.data.materials['GD_Material (do not touch contents)']

    ## PROPERTIES ##

    # Setup
    collSelectable: BoolProperty(default = True, update = scene_refresh)
    collVisible: BoolProperty(default = True, update = scene_refresh)
                                       
    scalingSet: FloatProperty(name = "", default = 2, min = .1, soft_max = 10, precision = 3, subtype = 'DISTANCE', update = scene_refresh)
    refSelection: PointerProperty(type = bpy.types.Image, update = scene_refresh)
    useGrid: BoolProperty(default = True, update = scene_refresh)
    gridSubdivisions: FloatProperty(name = "", default = 0, min = 0, max = 64, step = 100, precision = 0, update = scene_refresh)

    # Baker settings
    bakerType: EnumProperty(items=(('Blender', "Blender (Built-in)", ""),
                                   ('Marmoset', "Toolbag 3 & 4", "")), name = "Baker")
                                   #('Painter', "Substance Painter", "")
    exportPath: StringProperty(name = "", default = " ", description = "", subtype = 'DIR_PATH')
    exportResX: IntProperty(name = "", default = 2048, min = 4, max = 8192, update = update_res_x)
    exportResY: IntProperty(name = "", default = 2048, min = 4, max = 8192, update = update_res_y)
    lockRes: BoolProperty(default = True, update = update_res_x)
    exportName: StringProperty(name = "", description = "File export name", default = "untitled", update = update_export_name)
    imageType: EnumProperty(items=(('PNG', "PNG", ""),
                                   ('TIFF', "TIFF", ""),
                                   ('TARGA', "TGA", "")), name = "Format")
    colorDepth: EnumProperty(items = (('16', "16", ""),
                                      ('8', "8", "")))
    imageComp: IntProperty(name = "Compression", default = 50, min = 0, max = 100, subtype = 'PERCENTAGE')
    imageCompTIFF: EnumProperty(items = (('NONE', "None", ""),
                                         ('DEFLATE', "Deflate", ""),
                                         ('LZW', "LZW", ""),
                                         ('PACKBITS', "Pack Bits", "")),
                                         name='Compression',
                                         default='DEFLATE')         
    onlyRenderColl: BoolProperty(update = scene_refresh, description = "Choose this option if your objects aren't visible in the renders. This will add a collection to the scene, and the add-on will ONLY render what is inside that collection. Read the documentation on why this can happen")
    exportPlane: BoolProperty(name = "Export Plane", description = "Exports the background plane as a .FBX for use in an external program")
    openFolderOnExport: BoolProperty(description = "This option will open up the folder path whenever you export maps")

    uiVisibilityNormals: BoolProperty(default = True)
    uiVisibilityCurvature: BoolProperty(default = True)
    uiVisibilityOcclusion: BoolProperty(default = True)
    uiVisibilityHeight: BoolProperty(default = True)
    uiVisibilityMatID: BoolProperty(default = True)

    # Bake map options
    exportNormals: BoolProperty(default = True)
    reimportAsMatNormals: BoolProperty(description = "This will reimport the Normal map as a material for use in Blender")
    flipYNormals: BoolProperty(name = "Flip Y (-Y)", description = "Flip the normal map Y direction", options = {'SKIP_SAVE'}, update = update_flip_y)
    samplesNormals: IntProperty(name = "", default = 128, min = 1, max = 500)

    exportCurvature: BoolProperty(default = True)
    ridgeCurvature: FloatProperty(name = "", default = 2, min = 0, max = 2, precision = 3, step = .1, update = update_curvature, subtype = 'FACTOR')
    valleyCurvature: FloatProperty(name = "", default = 1.5, min = 0, max = 2, precision = 3, step = .1, update = update_curvature, subtype = 'FACTOR')
    contrastCurvature: EnumProperty(items = (('None', "None (Medium)", ""),
                                             ('Very_High_Contrast', "Very High", ""),
                                             ('High_Contrast', "High", ""),
                                             ('Medium_High_Contrast', "Medium High", ""),
                                             ('Medium_High_Contrast', "Medium Low", ""),
                                             ('Low_Contrast', "Low", ""),
                                             ('Very_Low_Contrast', "Very Low", "")),
                                             name = "Curvature Contrast")
    samplesCurvature: EnumProperty(items = (('OFF', "No Anti-Aliasing", ""),
                                            ('FXAA', "Single Pass Anti-Aliasing", ""),
                                            ('5', "5 Samples", ""),
                                            ('8', "8 Samples", ""),
                                            ('11', "11 Samples", ""),
                                            ('16', "16 Samples", ""),
                                            ('32', "32 Samples", "")),
                                            default = "32", name = "Curvature Samples")

    exportOcclusion: BoolProperty(default = True)
    reimportAsMatOcclusion: BoolProperty(description = "This will reimport the Occlusion map as a material for use in Blender")
    gammaOcclusion: FloatProperty(default = 1, min = .001, max = 10, step = .17, name = "", description = "Intensity of AO (calculated with gamma)", update = update_occlusion_gamma)
    distanceOcclusion: FloatProperty(default = 1, min = 0, max = 100, step = .03, subtype = 'DISTANCE', name = "", description = "The distance AO rays travel", update = update_occlusion_distance)
    samplesOcclusion: IntProperty(name = "", default = 128, min = 1, max = 500)
    contrastOcclusion: EnumProperty(items = (('None', "None (Medium)", ""),
                                             ('Very_High_Contrast', "Very High", ""),
                                             ('High_Contrast', "High", ""),
                                             ('Medium_High_Contrast', "Medium High", ""),
                                             ('Medium_High_Contrast', "Medium Low", ""),
                                             ('Low_Contrast', "Low", ""),
                                             ('Very_Low_Contrast', "Very Low", "")),
                                             name = "Occlusion Contrast")                      

    exportHeight: BoolProperty(default = True, update = scene_refresh)
    flatMaskHeight: BoolProperty(description = "The height map will be exported with only fully white & black values for use as an alpha", update = update_height_guide)
    guideHeight: FloatProperty(name = "", default = 1, min = .01, max = 5, step = .03, subtype = 'DISTANCE', update = update_height_guide)
    samplesHeight: IntProperty(name = "", default = 128, min = 1, max = 500)
    rangeTypeHeight: EnumProperty(items = (('AUTO', "Auto", ""),
                                           ('MANUAL', "Manual", "")),
                                           update = update_manual_height_range,
                                           description = "Automatic or manual height range. Use manual if automatic is giving you incorrect results or if baking is really slow")

    exportMatID: BoolProperty(default = True)
    methodMatID: EnumProperty(items = (('RANDOM', "Random", ""),
                                       ('MATERIAL', "Material", "")))
    fakeMethodMatID: EnumProperty(items = (('RANDOM', "Random", ""),
                                           ('MATERIAL', "Material", "")),
                                           default = "MATERIAL")
    samplesMatID: EnumProperty(items=(('OFF', "No Anti-Aliasing", ""),
                                      ('FXAA', "Single Pass Anti-Aliasing", ""),
                                      ('5', "5 Samples", ""),
                                      ('8', "8 Samples", ""),
                                      ('11', "11 Samples", ""),
                                      ('16', "16 Samples", ""),
                                      ('32', "32 Samples", "")),
                                      default = "32", name = "Mat ID Samples")

    # Map Preview
    firstBakePreview: BoolProperty(default = True)
    
    autoExitCamera: BoolProperty()

    modalState: BoolProperty()
    modalPreviewType: EnumProperty(items=(('none', "None", ""),
                                          ('normals', "Normals", ""),
                                          ('curvature', "Curvature", ""),
                                          ('occlusion', "Ambient Occlusion", ""),
                                          ('height', "Height", ""),
                                          ('ID', "Material ID", "")))

    # Marmoset Baking
    marmoExportPath: StringProperty(name = "", description = "Changes the name of the exported file", default = "", subtype = 'FILE_PATH')
    marmoAutoBake: BoolProperty(name = "Auto bake", default = True)
    marmoClosePostBake: BoolProperty(name = "Close after baking")
    marmoSamples: EnumProperty(items=(('1', "1x", ""),
                                      ('4', "4x", ""),
                                      ('16', "16x", "")),
                                      default = "16", name = "Marmoset Samples")
    marmoAORayCount: IntProperty(default = 512, min = 32, max = 4096)


##################################
# REGISTRATION
##################################


classes = (GRABDOC_MT_presets,
           GRABDOC_PT_presets,
           GRABDOC_OT_add_preset,
           GRABDOC_property_group,
           GRABDOC_MT_addon_prefs,
           GRABDOC_OT_check_for_update)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.grabDoc = PointerProperty(type = GRABDOC_property_group)

    # Set the updaters repo
    updater.user = "oRazeD"
    updater.repo = "grabdoc"
    updater.current_version = bl_info["version"]

    # Initial check for repo updates
    updater.check_for_update_now()

    if updater.update_ready:
        print("There is a GrabDoc update available!")


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####