bl_info = {
    "name": "MarkSceneAsBatchRender",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Scene",
    "description": "Adds a checkbox to mark scenes for automated rendering",
    "category": "Scene",
}

import bpy
from bpy.props import BoolProperty


# ------------------------------------------------------------
# UI Panel
# ------------------------------------------------------------


class RENDER_SCENE_PT_panel(bpy.types.Panel):
    bl_label = "Render Scene Marker"
    bl_idname = "SCENE_PT_render_scene_marker"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        layout.prop(scene, "batch_render_scene")


# ------------------------------------------------------------
# Register custom Scene property
# ------------------------------------------------------------


def register():
    bpy.types.Scene.batch_render_scene = BoolProperty(
        name="Batch Render Scene", description="Mark this scene for batch rendering", default=False
    )

    bpy.utils.register_class(RENDER_SCENE_PT_panel)


def unregister():
    bpy.utils.unregister_class(RENDER_SCENE_PT_panel)
    del bpy.types.Scene.render_scene
