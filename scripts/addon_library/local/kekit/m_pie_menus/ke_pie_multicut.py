from bpy.types import Menu
from .._utils import get_prefs


def get_props(p, preset="0"):
    v1, v2, v3, v4 = 0, 0, 0, 0
    if preset == "0":
        v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
    elif preset == "1":
        v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
    elif preset == "2":
        v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
    elif preset == "3":
        v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
    elif preset == "4":
        v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
    elif preset == "5":
        v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
    elif preset == "6":
        v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
    elif preset == "7":
        v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
    return v1, str(int(v2)), v3, bool(v4)


class KePieMultiCut(Menu):
    bl_label = "keMultiCut"
    bl_idname = "VIEW3D_MT_ke_pie_multicut"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        k = get_prefs()
        p = k.mc_prefs[:]
        mc = 'mesh.ke_multicut'
        layout = self.layout
        pie = layout.menu_pie()

        op = pie.operator(mc, text="%s" % k.mc_name0)
        v1, v2, v3, v4 = get_props(p, preset="0")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name1)
        v1, v2, v3, v4 = get_props(p, preset="1")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name2)
        v1, v2, v3, v4 = get_props(p, preset="2")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name3)
        v1, v2, v3, v4 = get_props(p, preset="3")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name4)
        v1, v2, v3, v4 = get_props(p, preset="4")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name5)
        v1, v2, v3, v4 = get_props(p, preset="5")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name6)
        v1, v2, v3, v4 = get_props(p, preset="6")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name7)
        v1, v2, v3, v4 = get_props(p, preset="7")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"
