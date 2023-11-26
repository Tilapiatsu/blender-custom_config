from math import radians

import bmesh
import bpy
from bpy.props import EnumProperty, IntVectorProperty
from bpy.types import Operator
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from mathutils import Vector, Matrix
from .._utils import correct_normal, getset_transform, get_distance


class KeMouseSideofActive(Operator):
    bl_idname = "mesh.ke_mouse_side_of_active"
    bl_label = "Mouse Side of Active"
    bl_description = "Side of Active, but with active vert, edge or face and mouse position " \
                     "to calculate which side of the active element to select"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos : IntVectorProperty(size=2)

    axis_mode : EnumProperty(
        items=[("GLOBAL", "Global", "", 1),
               ("LOCAL", "Local", "", 2),
               ("NORMAL", "Normal", "", 3),
               ("GIMBAL", "Gimbal", "", 4),
               ("VIEW", "View", "", 5),
               ("CURSOR", "Cursor", "", 6),
               ("MOUSE", "Mouse Pick", "", 7)
               ],
        name="Axis Mode", default="MOUSE")

    axis_sign : EnumProperty(
        items=[("POS", "Positive Axis", "", 1),
               ("NEG", "Negative Axis", "", 2),
               ("ALIGN", "Aligned Axis", "", 3),
               ("MOUSE", "Mouse Pick", "", 4)
               ],
        name="Axis Sign", default="MOUSE")

    axis : EnumProperty(
        items=[("X", "X", "", 1),
               ("Y", "Y", "", 2),
               ("Z", "Z", "", 3),
               ("MOUSE", "Mouse Pick", "", 4)
               ],
        name="Axis", default="MOUSE")

    threshold : bpy.props.FloatProperty(min=0, max=10, default=0, name="Threshold")

    expand : bpy.props.BoolProperty(default=False, name="Extend", description="Extend selection / New selection")

    mouse_pick = ""

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.prop(self, "axis_mode")
        col.prop(self, "axis_sign")
        col.prop(self, "axis")
        col.prop(self, "threshold")
        col.prop(self, "expand", toggle=True)
        col.separator(factor=1)
        col = layout.column()
        col.active = False
        col.alignment = "RIGHT"
        col.label(text=self.mouse_pick)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode and
                context.space_data.type == "VIEW_3D")

    def invoke(self, context, event):
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        return self.execute(context)

    def execute(self, context):

        if self.axis_mode != "MOUSE":
            m_axis_mode = self.axis_mode
        else:
            m_axis_mode = getset_transform(setglobal=False)[0]

        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.object
        obj_mtx = obj.matrix_world
        tm = Matrix().to_3x3()

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        ae = bm.select_history.active
        og_ae = ae

        if ae is None:
            self.report({"INFO"}, "No active element selected")
            return {"CANCELLED"}

        sel_verts = [i for i in bm.verts if i.select]
        sel_edges = [i for i in bm.edges if i.select]
        sel_faces = [i for i in bm.faces if i.select]
        region = []
        region_data = []

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for r in area.regions:
                    if r.type == "WINDOW":
                        region = r
                        region_data = r.data

        # Very silly N-panel region compensation hack:
        if context.region.width != region.width:
            self.mouse_pos[0] = region.width

        # Set active vert to furthest from mouse if not vert mode
        if not isinstance(ae, bmesh.types.BMVert):
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action="DESELECT")

            candidate = []
            c_d = 0
            for v in ae.verts:
                sco = location_3d_to_region_2d(region, region_data, obj_mtx @ v.co)
                if sco is None:
                    # Just in case
                    print("3D to 2D view position failed. Zero position used.")
                    sco = Vector((0, 0))

                d = get_distance(self.mouse_pos, sco)
                if d > c_d or not candidate:
                    candidate = v
                    c_d = d

            bm.select_history.add(candidate)
            ae = candidate
        else:
            for v in bm.verts:
                v.select = False

        ae.select = True
        bmesh.update_edit_mesh(me)

        ae_wco = obj_mtx @ ae.co
        mouse_wpos = region_2d_to_location_3d(region, region_data, self.mouse_pos, ae_wco)

        # ORIENTATION
        if m_axis_mode == "LOCAL":
            tm = obj_mtx.to_3x3()

        elif m_axis_mode == "CURSOR":
            tm = context.scene.cursor.matrix.to_3x3()

        elif m_axis_mode == "NORMAL":
            normal = correct_normal(obj_mtx, ae.normal)
            # Blender default method (for tangent/rot mtx calc) in this case? IDFK, seems to match...
            tm = normal.to_track_quat('Z', 'Y').to_matrix().to_3x3()
            # ...with compensating rotation
            tm @= Matrix.Rotation(radians(180.0), 3, 'Z')

        elif m_axis_mode == "VIEW":
            tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()

        # else : GLOBAL default transf.mtx for the rest

        # AXIS CALC
        v = tm.inverted() @ Vector(mouse_wpos - ae_wco).normalized()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

        m_axis_sign = "POS"

        if x > y and x > z:
            m_axis = "X"
            if v[0] < 0:
                m_axis_sign = "NEG"
        elif y > x and y > z:
            m_axis = "Y"
            if v[1] < 0:
                m_axis_sign = "NEG"
        else:
            m_axis = "Z"
            if v[2] < 0:
                m_axis_sign = "NEG"

        # Check overrides
        if self.axis_sign != "MOUSE":
            sign = self.axis_sign
        else:
            sign = m_axis_sign
        if self.axis != "MOUSE":
            axis = self.axis
        else:
            axis = m_axis

        bpy.ops.mesh.select_axis(orientation=m_axis_mode, sign=sign, axis=axis, threshold=self.threshold)

        if sel_mode[1]:
            bpy.ops.mesh.select_mode(type='EDGE')
            if self.expand:
                for e in sel_edges:
                    e.select_set(True)
            bm.select_history.add(og_ae)
            og_ae.select_set(True)

        elif sel_mode[2]:
            bpy.ops.mesh.select_mode(type='FACE')
            if self.expand:
                for f in sel_faces:
                    f.select_set(True)
            bm.select_history.add(og_ae)
            og_ae.select_set(True)
        else:
            if self.expand:
                for v in sel_verts:
                    v.select_set(True)

        if m_axis_sign == "POS":
            rs = "+      "
        else:
            rs = "-      "
        self.mouse_pick = "Mouse Pick:  " + m_axis_mode.capitalize() + " " + m_axis + rs

        return {'FINISHED'}
