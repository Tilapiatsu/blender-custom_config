from bpy.types import Menu
import bpy
import re

bl_info = {
    "name": "Tila : Distribute Pie",
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


class TILA_MT_pie_distribute(Menu):
    bl_idname = "TILA_MT_pie_distribute"
    bl_label = "Tila : Distribute Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left
        pie.operator("mesh.looptools_flatten", icon='MESH_PLANE', text="Flatten")

        # Right
        pie.operator("mesh.looptools_circle", icon='MESH_CIRCLE', text="Circle")
        
        # Bottom
        pie.operator("mesh.set_edge_flow", icon='IPO_EASE_IN_OUT', text="Set Flow")

        # Top
        pie.operator("mesh.looptools_gstretch", icon='IPO_LINEAR', text="Linear").method='irregular'

        # Top Left
        pie.operator("mesh.looptools_relax", icon='SEQ_LUMA_WAVEFORM', text="Relax")

        # Top Right
        pie.operator("mesh.looptools_space", icon='DRIVER_DISTANCE', text="Space")

        # Bottom Left
        pie.operator("mesh.looptools_curve", icon='MOD_CURVE', text="Curve")

        # Bottom Right
        pie.operator("machin3.unfuck", icon='MOD_SMOOTH', text="Unfuck")

classes = (
    TILA_MT_pie_distribute,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
