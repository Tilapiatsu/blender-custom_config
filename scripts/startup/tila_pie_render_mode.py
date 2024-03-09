from bpy.types import Menu
import bpy
import re

bl_info = {
    "name": "Tila : Render Mode Pie",
    "description": "",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "Pie Menu"
}

bversion_string = bpy.app.version_string
bversion_reg = re.match("^(\d\.\d?\d)", bversion_string)
bversion = float(bversion_reg.group(0))


class TILA_MT_pie_render_mode(Menu):
    bl_idname = "TILA_MT_pie_render_mode"
    bl_label = "Tila : Render Mode Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left
        pie.operator("view3d.tila_toggle_shading", icon='SHADING_WIRE', text="Wireframe").type = 'WIREFRAME'

        # Right
        pie.operator("view3d.tila_toggle_shading", icon='SHADING_SOLID', text="Solid").type = 'SOLID'
        
        # Bottom
        pie.operator("view3d.tila_toggle_shading", icon='SHADING_TEXTURE', text="Material Preview").type = 'MATERIAL'

        # Top
        pie.operator("view3d.tila_toggle_shading", icon='SHADING_RENDERED', text="Rendered").type = 'RENDERED'

        # Top Left
        pie.operator("view3d.tila_toggle_shading", icon='VPAINT_HLT', text="Solid Vertex").type = 'SOLID_VERTEX'

        # Top Right
        pie.operator("view3d.tila_toggle_shading", icon='TEXTURE', text="Solid Texture").type = 'SOLID_TEXTURE'

        # Bottom Left
        pie.operator("view3d.tila_toggle_shading", icon='SELECT_EXTEND', text="Silhouette").type = 'SILHOUETTE'

        # Bottom Right
        pie.operator("view3d.tila_toggle_shading", icon='RNDCURVE', text="Random").type = 'RANDOM'


class TILA_OT_toggle_shading(bpy.types.Operator):
    bl_idname = "view3d.tila_toggle_shading"
    bl_label = "Tilapiatsu Toggle Shading"
    bl_options = {'REGISTER', 'UNDO'}

    type : bpy.props.EnumProperty(name='type', items=(('RENDERED', 'Rendered', ''), ('MATERIAL', 'Material Preview', ''), ('SOLID', 'Solid', ''), ('WIREFRAME', 'Wireframe', ''), ('SOLID_TEXTURE', 'Solid Texture', ''), ('RANDOM', 'Random', ''), ('SOLID_VERTEX', 'Solid Vertex', ''), ('SILHOUETTE', 'Silhouette', '')), default='RENDERED')
    
    def execute(self, context):
        if self.type in ['RENDERED', 'MATERIAL', 'SOLID', 'WIREFRAME']:
            bpy.context.space_data.shading.type = self.type
            if self.type == 'SOLID':
                bpy.context.space_data.shading.light = 'STUDIO'
                bpy.context.space_data.shading.background_type = 'THEME'
                bpy.context.space_data.shading.color_type = 'MATERIAL'
                bpy.context.space_data.shading.studio_light = 'TilaSculpt.sl'
                bpy.context.space_data.shading.wireframe_color_type = 'THEME'
                bpy.context.space_data.shading.show_object_outline = True
                bpy.context.space_data.overlay.show_face_orientation = True
            if self.type == 'WIREFRAME':
                bpy.context.space_data.shading.wireframe_color_type = 'RANDOM'
                bpy.context.space_data.shading.xray_alpha_wireframe = 0.75
                bpy.context.space_data.shading.background_color = (0.007, 0.007, 0.007)
                bpy.context.space_data.shading.background_type = 'VIEWPORT'
                bpy.context.space_data.shading.show_object_outline = True
                bpy.context.space_data.overlay.show_face_orientation = True
            if self.type in ['WIREFRAME', 'MATERIAL']:
                bpy.context.space_data.overlay.show_face_orientation = False

        else:
            bpy.context.space_data.shading.type = 'SOLID'
            if self.type == 'SOLID_TEXTURE':
                bpy.context.space_data.shading.color_type = 'TEXTURE'
                bpy.context.space_data.shading.light = 'STUDIO'
                bpy.context.space_data.shading.studio_light = 'paint.sl'
                bpy.context.space_data.shading.background_type = 'THEME'
                bpy.context.space_data.shading.wireframe_color_type = 'THEME'
                bpy.context.space_data.shading.show_object_outline = False
                bpy.context.space_data.overlay.show_face_orientation = False
            elif self.type == 'RANDOM':
                bpy.context.space_data.shading.color_type = 'RANDOM'
                bpy.context.space_data.shading.wireframe_color_type = 'THEME'
                bpy.context.space_data.shading.light = 'STUDIO'
                bpy.context.space_data.shading.studio_light = 'TilaSculpt.sl'
                bpy.context.space_data.shading.background_type = 'THEME'
                bpy.context.space_data.shading.show_object_outline = True
                bpy.context.space_data.overlay.show_face_orientation = True
            elif self.type == 'SOLID_VERTEX':
                bpy.context.space_data.shading.color_type = 'VERTEX'
                bpy.context.space_data.shading.light = 'STUDIO'
                bpy.context.space_data.shading.studio_light = 'paint.sl'
                bpy.context.space_data.shading.background_type = 'THEME'
                bpy.context.space_data.shading.wireframe_color_type = 'THEME'
                bpy.context.space_data.shading.show_object_outline = True
                bpy.context.space_data.overlay.show_face_orientation = False
            elif self.type == 'SILHOUETTE':
                bpy.context.space_data.shading.color_type = 'SINGLE'
                bpy.context.space_data.shading.light = 'FLAT'
                bpy.context.space_data.shading.background_type = 'VIEWPORT'
                bpy.context.space_data.shading.wireframe_color_type = 'THEME'
                bpy.context.space_data.shading.background_color = (0, 0, 0)
                bpy.context.space_data.shading.show_object_outline = False
                bpy.context.space_data.overlay.show_face_orientation = False



        return {'FINISHED'}

classes = (
    TILA_MT_pie_render_mode, TILA_OT_toggle_shading
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
