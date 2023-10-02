from bpy.types import Menu
from .._utils import get_prefs


class KePieFitPrim(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_fitprim"
    bl_label = "ke.fit_prim"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_geo

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            w = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            w.ke_fitprim_option = "CYL"
            w.ke_fitprim_pieslot = "W"

            e = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"
            e.ke_fitprim_itemize = True

            s = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            s.ke_fitprim_option = "BOX"
            s.ke_fitprim_pieslot = "S"

            n = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"
            n.ke_fitprim_itemize = True

            col = pie.box().column()
            nw = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            nw.ke_fitprim_option = "SPHERE"
            nw.ke_fitprim_pieslot = "NW"
            nw2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            ne = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"
            ne.ke_fitprim_itemize = True
            ne2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            ne2.ke_fitprim_option = "QUADSPHERE"
            ne2.ke_fitprim_pieslot = "NE"
            ne2.ke_fitprim_itemize = True

            sw = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            sw.ke_fitprim_option = "PLANE"
            sw.ke_fitprim_pieslot = "SW"

            se = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"
            se.ke_fitprim_itemize = True

        if cm == "OBJECT":
            # W
            pie.separator()

            e = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"

            # S
            pie.separator()

            n = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"

            nw2 = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            ne = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"

            # SW
            pie.separator()

            se = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"


class KePieFitPrimAdd(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_fitprim_add"
    bl_label = "ke.fit_prim_add"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_geo

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            w = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            w.ke_fitprim_option = "CYL"
            w.ke_fitprim_pieslot = "W"

            e = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"
            e.ke_fitprim_itemize = True

            s = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            s.ke_fitprim_option = "BOX"
            s.ke_fitprim_pieslot = "S"

            n = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"
            n.ke_fitprim_itemize = True

            col = pie.box().column()
            nw = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            nw.ke_fitprim_option = "SPHERE"
            nw.ke_fitprim_pieslot = "NW"
            nw2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            ne = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"
            ne.ke_fitprim_itemize = True
            ne2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            ne2.ke_fitprim_option = "QUADSPHERE"
            ne2.ke_fitprim_pieslot = "NE"
            ne2.ke_fitprim_itemize = True

            sw = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            sw.ke_fitprim_option = "PLANE"
            sw.ke_fitprim_pieslot = "SW"

            se = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"
            se.ke_fitprim_itemize = True

        if cm == "OBJECT":
            # WEST
            op = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            op.ke_fitprim_option = "CYL"
            op.ke_fitprim_pieslot = "W"

            # EAST
            c = pie.row()
            s = c.column()
            s.separator(factor=27)
            box = s.box()
            box.emboss = "PULLDOWN_MENU"
            col = box.grid_flow(columns=2, even_columns=True, align=True)
            col.scale_x = 1.5
            col.scale_y = 0.9
            col.operator('object.empty_add', icon='EMPTY_AXIS').type = "PLAIN_AXES"
            col.menu_contents("VIEW3D_MT_mesh_add")
            col.menu_contents("VIEW3D_MT_add")

            # SOUTH
            op = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            op.ke_fitprim_option = "PLANE"
            op.ke_fitprim_pieslot = "S"

            # NORTH
            op = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            op.ke_fitprim_option = "BOX"
            op.ke_fitprim_pieslot = "N"

            # NORTHWEST
            op = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "SPHERE"
            op.ke_fitprim_pieslot = "NW"

            # NORTHEAST
            pie.separator()

            # SOUTHWEST
            op = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "QUADSPHERE"
            op.ke_fitprim_pieslot = "SW"
            # SOUTHEAST - BLANK
