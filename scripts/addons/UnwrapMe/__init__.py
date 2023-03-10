# Copyright (C) 2023 Elias V.
# SPDX-License-Identifier: GPL-3.0-only

bl_info = {
    "name": "Unwrap Me",
    "author": "Memm",
    "version": (0, 5),
    "blender": (3, 0, 0),
    "location": "View3D > UV",
    "description": "Automagically generate UV seams and more.",
    "tracker_url": "https://github.com/3e33/UnwrapMe/issues"
}

import bpy
import os
import sys
from pathlib import Path

from . import updater
from . import core

def getAddonFolderPath():
    return Path(os.path.dirname(os.path.realpath(__file__)))

def getAddonUpdatePath():
    return os.path.join(getAddonFolderPath(), "UnwrapMe")

def showPopup(icon, message):
    def popup(self, context):
        self.layout.label(text=message)
    
    bpy.context.window_manager.popup_menu(popup,
                                          title="UnwrapMe Message",
                                          icon=icon)

class UnwrapMeUpdate(bpy.types.Operator):
    bl_idname = "addon.upwrap_me_update"
    bl_label = "Check for updates"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        latestURL = updater.getLatestReleaseURL("3e33", "UnwrapMe")
        if(latestURL == None):
            showPopup("ERROR",
                      "Problem getting addon release URL.")

            return {'CANCELLED'}
            
        addonFolderPath = getAddonFolderPath()
        addonUpdatePath = getAddonUpdatePath()
        latestVersion = updater.getTupleFromString(latestURL.split("/")[-1])
        if(latestVersion > bl_info["version"]):
            addonZipFilePath = updater.downloadUrl(latestURL, addonFolderPath)

            if(addonZipFilePath == None):
                showPopup("ERROR",
                          "Problem downloading addon update.")

                return {'CANCELLED'}

            updater.extractAndRemoveZip(addonZipFilePath, addonFolderPath)
            moveFails = updater.moveAllFiles(addonUpdatePath, addonFolderPath)

            if(moveFails > 0):
                showPopup("INFO",
                          "Please close all Blender instances and re-open Blender to complete update.")
            else:
                os.rmdir(addonUpdatePath)

        else:
            showPopup("INFO",
                      "No new updates found.")

        return {'FINISHED'}

class UnwrapMeOpenUrl(bpy.types.Operator):
    bl_idname = "addon.upwrapme_open_url"
    bl_label = "OpenUrl"
    bl_options = {"INTERNAL"}
    bl_description = """
Will open your web browser."""

    url: bpy.props.StringProperty(name="")

    def execute(self, context):
        import webbrowser
        
        webbrowser.open(self.url)
        
        return {'FINISHED'}

class GrowCharts(bpy.types.Operator):
    bl_idname = "uv.grow_charts"
    bl_label = "Grow Charts"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """
Grow UV charts and create seams for UV unwrapping"""

    def execute(self, context):
        if(self.options.is_repeat):
            return {'PASS_THROUGH'}

        from . import fastcore

        core.initBlenderState()
        mesh = core.getActiveMesh()
        bm = core.getBMesh(mesh)

        props = context.active_object.unwrapMeProps
        if(props.mode == 'procedural'):
            fastcore.growRollingCharts(bm, props)
        else:
            fastcore.growCharts(bm, props)

        bpy.ops.object.mode_set(mode='OBJECT')
        bm.to_mesh(mesh)
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        props = context.active_object.unwrapMeProps
        layout.prop(props, 'mode', expand = True)
        if(props.mode == 'procedural'):
            layout.prop(props, 'startFromSelected')
            layout.prop(props, 'maxError')

            layout.prop(props, 'useMainAxis')
        else:
            layout.prop(props, 'growFromSelected')
            if(props.growFromSelected == False):
                layout.prop(props, 'chartsNumber')
                layout.prop(props, 'startFromSelected')

            layout.prop(props, 'maxError')
            layout.prop(props, 'maxIterations')

            if(props.chartsNumber > 1):
                layout.prop(props, 'maxExtraCharts')

            layout.prop(props, 'useMainAxis')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class UnwrapMeProps(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(name="Growth Algorithm",
                                 items = [('procedural',
                                           "Procedural",
                                           """
Charts will grow from a starting face one by one until the entire mesh is covered.
This is usually better for low poly meshes"""),
                                          ('lloyd',
                                           "Lloyd Iterations",
                                           """
Charts will grow using Lloyd iterations.
Uncovered sections will be filled in with more charts depending on Max Extra Charts.
This is usually better for high poly meshes""")])

    maxError: bpy.props.FloatProperty(name="Developability",
                                      default=0.10,
                                      step=1.0,
                                      description="""
Lower means less distortion but smaller charts""")

    maxExtraCharts: bpy.props.IntProperty(name="Max Extra Charts",
                                          default=100,
                                          step=1,
                                          description="""
Extra charts are created when there are uncovered areas.
Usually better to increase number of charts instead""")

    maxIterations: bpy.props.IntProperty(name="Lloyd Iterations Limit",
                                         default=15,
                                         step=1,
                                         description="""
In case of nonconvergence (it can go forever) we limit iterations.""")

    chartsNumber: bpy.props.IntProperty(name="Charts Amount",
                                        default=15,
                                        step=1,
                                        description = """
Usually better to have too many than too few to cover the entire mesh""")

    growFromSelected: bpy.props.BoolProperty(name="Grow From Selected Face Clusters",
                                             default = False,
                                             description = """
Start growing from selected face clusters, otherwise starting faces will be chosen using farthest-first traversal""")

    startFromSelected: bpy.props.BoolProperty(name="Start From Selected Face Cluster",
                                              default = True,
                                              description = """
Charts grow from initially selected face cluster, otherwise starting face will be random""")

    useMainAxis: bpy.props.BoolProperty(name="Use Axis",
                                        default = False,
                                        description = """
Give each chart its own axis to grow around.
Can produce better results, but charts that grow cylindrically
may need an additional seam to split them.""")

class OpenUnwrapMePie(bpy.types.Operator):
    bl_idname = "uv.unwrap_me_pie"
    bl_label = "Unwrap Me"
    bl_description = """
Open the Unwrap Me pie menu"""

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_unwrapme")

        return {'FINISHED'}

class MergeCharts(bpy.types.Operator):
    bl_idname = "uv.merge_charts"
    bl_label = "Merge Two Charts"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """
Merge two charts together by removing the seam between them"""

    def execute(self, context):
        core.initBlenderState()
        mesh = core.getActiveMesh()
        bm = core.getBMesh(mesh)

        try:
            core.opMergeCharts(mesh, bm)
        except:
            pass

        return {'FINISHED'}

class StraightenSeams(bpy.types.Operator):
    bl_idname = "uv.straighten_seams"
    bl_label = "Straighten Seams"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """
Straighten the seam inside the selected area of faces / edges"""

    def execute(self, context):
        core.initBlenderState()
        mesh = core.getActiveMesh()
        bm = core.getBMesh(mesh)

        try:
            core.opStraightenSeams(mesh, bm)
        except:
            pass

        return {'FINISHED'}

class RemoveUVOverlaps(bpy.types.Operator):
    bl_idname = "uv.remove_overlaps"
    bl_label = "Remove UV Chart Overlaps"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """
Will detect simple inner-chart overlaps and separate them into their own UV islands."""

    def execute(self, context):
        if(self.options.is_repeat):
            return {'PASS_THROUGH'}

        from . import fastcore

        core.initBlenderState()
        mesh = core.getActiveMesh()
        bm = core.getBMesh(mesh)

        for f in bm.faces:
            f.select = False

        import time
        tdata = time.perf_counter()
        ttotal = time.perf_counter()
        
        uv_layer = bm.loops.layers.uv.verify()
        uvFaces = fastcore.polyList()
        for f in bm.faces:
            polygon = fastcore.poly()

            for l in f.loops:
                uv = l[uv_layer].uv
                polygon.addPoint(uv[0], uv[1])

            polygon.addPoint(f.loops[0][uv_layer].uv[0],
                             f.loops[0][uv_layer].uv[1])

            uvFaces.append(polygon)

        print(f"uv data transferred in {time.perf_counter() - tdata:0.4f}s")

        faceIndexes = fastcore.getOverlappingClusters(bm, uvFaces)

        for i in faceIndexes:
            bm.faces[i].select = True

        bpy.ops.object.mode_set(mode='OBJECT')
        bm.to_mesh(mesh)
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.uv.select_all(action='DESELECT')

        print(f"Total time: {time.perf_counter() - ttotal:0.4f}s")

        return {'FINISHED'}
    

class VIEW3D_MT_unwrapme(bpy.types.Menu):
    bl_label = "Unwrap Me"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator(GrowCharts.bl_idname)
        pie.operator(MergeCharts.bl_idname)
        pie.operator(StraightenSeams.bl_idname)
        pie.operator(RemoveUVOverlaps.bl_idname)

class UnwrapMePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    bought: bpy.props.BoolProperty(
        name="I already purchased it.",
        default=False)

    def draw(self, context):
        layout = self.layout

        layout.operator(UnwrapMeUpdate.bl_idname)

        buyBox = layout.box()
        if(not self.bought):
            buyBox.label(text="--- Buy Unwrap Me ---", icon="HEART")

            props = buyBox.operator(UnwrapMeOpenUrl.bl_idname, text="Stripe (directly support developer!)", icon="URL")
            props.url = "https://buy.stripe.com/3cs8yNfhjb0maT6000"

            props = buyBox.operator(UnwrapMeOpenUrl.bl_idname, text="Blender Market", icon="URL")
            props.url = "https://blendermarket.com/creators/shiftatechnologies"

            buyBox.prop(self, "bought", icon="HEART")

        else:
            buyBox.prop(self, "bought", text="Thank you.", icon="HEART")

    
def unwrapmeMenu(self, context):
    layout = self.layout

    layout.separator()
    layout.operator(OpenUnwrapMePie.bl_idname)

classes = [
    UnwrapMePreferences,
    UnwrapMeUpdate,
    UnwrapMeProps,
    GrowCharts,
    OpenUnwrapMePie,
    MergeCharts,
    StraightenSeams,
    VIEW3D_MT_unwrapme,
    RemoveUVOverlaps,
    UnwrapMeOpenUrl
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.unwrapMeProps = bpy.props.PointerProperty(type=UnwrapMeProps)
    bpy.types.VIEW3D_MT_uv_map.append(unwrapmeMenu)

    addonPath = getAddonFolderPath()
    addonUpdatePath = getAddonUpdatePath()
    if(updater.getFileCount(addonUpdatePath) > 0):
        moveFailCount = updater.moveAllFiles(addonUpdatePath, addonPath)

        if(moveFailCount == 0):
           os.rmdir(addonUpdatePath) 

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Object.unwrapMeProps
    bpy.types.VIEW3D_MT_uv_map.remove(unwrapmeMenu)
