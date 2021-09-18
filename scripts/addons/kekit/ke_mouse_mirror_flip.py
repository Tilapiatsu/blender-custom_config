bl_info = {
    "name": "Mouse Mirror & Flip",
    "author": "Kjell Emanuelsson 2021",
    "version": (1, 1, 7),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_location_3d
from .ke_utils import average_vector, getset_transform, restore_transform, get_selected


class VIEW3D_OT_ke_mouse_mirror_flip(Operator):
    bl_idname = "view3d.ke_mouse_mirror_flip"
    bl_label = "Mouse Mirror & Flip"
    bl_description = "Mirror or Flip with Mouse pointer away from center (object, element or cursor) " \
                     "along intended axis. Based on current orientation (except view & gimbal). " \
                     "Note: Orientation will be recalculated!"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("FLIP", "Move", "", 1),
               ("MIRROR", "Duplicate", "", 2)
               ],
        name="Mode",
        default="MIRROR")

    linked: bpy.props.BoolProperty(name="Linked Duplicate", default=False)

    mouse_pos = Vector((0, 0))
    startpos = Vector((0, 0, 0))
    tm = Matrix().to_3x3()
    rv = None
    ot = "GLOBAL"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.enabled = not context.object.data.is_editmode and self.mode == "MIRROR"
        row.use_property_split = True
        row.prop(self, "linked", expand=True)
        layout.separator(factor=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @staticmethod
    def bbox_minmax(coords):
        x = [co[0] for co in coords]
        x.sort()
        y = [co[1] for co in coords]
        y.sort()
        z = [co[2] for co in coords]
        z.sort()
        return [x[0], y[0], z[0]], [x[-1], y[-1], z[-1]]

    @classmethod
    def get_mpos(cls, context, coord, pos):
        region = context.region
        rv3d = context.region_data
        return region_2d_to_location_3d(region, rv3d, coord, pos)

    def invoke(self, context, event):
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        return self.execute(context)

    def execute(self, context):
        cursor = context.scene.cursor
        cursor_mode = False
        normal_mode = False
        bbcoords, bbmin, bbmax = [], [], []

        og = getset_transform(setglobal=False)
        self.ot = og[0]

        if context.object.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}:
            em = bool(context.object.data.is_editmode)
        else:
            em = False

        if context.active_object is not None:
            og_obj = [context.active_object]
        else:
            og_obj = [context.object]

        if self.mode == "MIRROR":
            if em and og[0] != "NORMAL":
                bpy.ops.mesh.duplicate()
            elif not em:
                bpy.ops.object.duplicate()

        active_obj = get_selected(context, use_cat=True)

        # Mouse vec start
        if og[0] == "CURSOR":
            self.startpos = self.get_mpos(context, self.mouse_pos, cursor.location)
        else:
            self.startpos = self.get_mpos(context, self.mouse_pos, active_obj.location)

        # Fallback for Normal in Object Mode
        if og[0] == "NORMAL" and not em:
            og[0] = "LOCAL"

        # GLOBAL -------------------------------------------------------------------------------------------
        if og[0] == "GLOBAL":
            if not em:
                avg_pos = active_obj.location
            else:
                bbcoords = [active_obj.matrix_world @ v.co for v in active_obj.data.vertices if v.select]
                avg_pos = average_vector(bbcoords)

        # CURSOR -------------------------------------------------------------------------------------------
        elif og[0] == "CURSOR":
            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            self.tm = cursor.matrix.to_3x3()
            avg_pos = cursor.location
            cursor_mode = True

        # LOCAL -------------------------------------------------------------------------------------------
        elif og[0] == "LOCAL":
            # AKA BBOX MODE

            if em:
                # EDIT MODE
                self.tm = Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

                active_obj.update_from_editmode()
                if not bbcoords:
                    bbcoords = [active_obj.matrix_world @ v.co for v in active_obj.data.vertices if v.select]
            else:
                # OBJECT MODE
                if og[1] != "INDIVIDUAL_ORIGINS":
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                self.tm = active_obj.matrix_world.to_3x3()

                for b in active_obj.bound_box:
                    bbcoords.append(b[:])

            if not bbcoords:
                self.report({"INFO"}, "No elements selected?")
                return {'CANCELLED'}

            self.ot = "GLOBAL"
            bpy.ops.transform.select_orientation(orientation="GLOBAL")
            bpy.context.scene.tool_settings.transform_pivot_point = "BOUNDING_BOX_CENTER"

            bbmin, bbmax = self.bbox_minmax(bbcoords)

            if not em:
                bbmin = active_obj.matrix_world @ Vector(bbmin)
                bbmax = active_obj.matrix_world @ Vector(bbmax)

            if self.mode == "FLIP" and og[0] == "LOCAL":
                # resetting to flip in place instead of BBOX
                bbmin, bbmax = [], []
                if em:
                    avg_pos = average_vector([Vector(i) for i in bbcoords])
                else:
                    avg_pos = active_obj.matrix_world @ average_vector([Vector(i) for i in bbcoords])

            elif em:
                avg_pos = average_vector([Vector(i) for i in bbcoords])
            else:
                avg_pos = active_obj.matrix_world @ average_vector([Vector(i) for i in bbcoords])


        # NORMAL -------------------------------------------------------------------------------------------
        elif og[0] == "NORMAL" and em:

            sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
            mesh = active_obj.data
            bm = bmesh.from_edit_mesh(mesh)
            og_sel = []

            # 1st CHECK FOR ACTIVE ELEMENT
            try:
                active = bm.select_history[-1]
            except IndexError:
                self.report({"INFO"}, "No Active Element?")
                return {'CANCELLED'}

            bpy.context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'

            # store og selection, and deselect everything but active (used for transform)
            if sel_mode[0]:
                bm.verts.ensure_lookup_table()
                active_verts = [active]
                for v in bm.verts:
                    if v.select:
                        og_sel.append(v)
                    if v not in active_verts:
                        v.select = False

            elif sel_mode[1]:
                bm.edges.ensure_lookup_table()
                active_verts = active.verts[:]
                for e in bm.edges:
                    if e.select:
                        og_sel.append(e)
                    if e != active:
                        e.select = False
            else:
                bm.faces.ensure_lookup_table()
                active_verts = active.verts[:]
                for f in bm.faces:
                    if f.select:
                        og_sel.append(f)
                    if f != active:
                        f.select = False

            bmesh.update_edit_mesh(mesh)

            try:
                bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
                self.tm = context.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
                bpy.ops.transform.delete_orientation()
                restore_transform(og)
            except RuntimeError:
                print("Fallback: Invalid selection for Orientation - Using Local")
                # Normal O. with a entire cube selected will fail create_o.
                bpy.ops.transform.select_orientation(orientation='LOCAL')
                self.tm = context.object.matrix_world.to_3x3()

            # reselect original selection (to encompass all element islands )
            for i in og_sel:
                i.select = True
            bmesh.update_edit_mesh(mesh)

            bpy.ops.mesh.select_linked(delimit=set())

            if self.mode == "MIRROR":
                bpy.ops.mesh.duplicate()

            avg_pos = active_obj.matrix_world @ (average_vector([v.co for v in active_verts]))

            normal_mode = True

        # UNSUPPORTED -------------------------------------------------------------------------------------
        else:
            self.report({"INFO"}, "Unsupported Orientation Mode")
            return {'CANCELLED'}

        # AXIS CALC ---------------------------------------------------------------------------------------
        v = self.tm.inverted() @ Vector(self.startpos - avg_pos).normalized()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
        if normal_mode:
            x, y, z = 0, 0, 1

        if x > y and x > z:
            axis = True, False, False
            scale_value = (-1, 1, 1)
            if bbmax:
                if v[0] < 0:
                    avg_pos = Vector(bbmin)
                else:
                    avg_pos = Vector(bbmax)

        elif y > x and y > z:
            axis = False, True, False
            scale_value = (1, -1, 1)
            if bbmax:
                if v[1] < 0:
                    avg_pos = Vector(bbmin)
                else:
                    avg_pos = Vector(bbmax)

        else:
            axis = False, False, True
            scale_value = (1, 1, -1)
            if bbmax:
                if v[2] < 0:
                    avg_pos = Vector(bbmin)
                else:
                    avg_pos = Vector(bbmax)

        # Global offset fix
        if og[0] == "GLOBAL":
            avg_pos = Vector((0, 0, 0))

        # PROCESS
        if not em and cursor_mode:
            bpy.ops.transform.mirror(orient_type=self.ot, orient_matrix=self.tm,
                                     orient_matrix_type=self.ot, constraint_axis=axis)
        else:
            bpy.ops.transform.resize(value=scale_value, orient_type=self.ot,
                                     orient_matrix=self.tm,
                                     orient_matrix_type=self.ot, constraint_axis=axis, mirror=True,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                     proportional_size=1.0, use_proportional_connected=False,
                                     use_proportional_projected=False, snap=False,
                                     snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                     snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                     remove_on_cancel=False, center_override=avg_pos, release_confirm=False,
                                     use_accurate=False)

        if em:
            bpy.ops.mesh.flip_normals()

        if not em:
            restore_transform(og)

        if self.linked and not em and self.mode == "MIRROR":
            og_obj[0].select_set(True)
            bpy.context.view_layer.objects.active = og_obj[0]
            bpy.ops.object.make_links_data(type='OBDATA')
            og_obj[0].select_set(False)
            bpy.context.view_layer.objects.active = active_obj

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_mouse_mirror_flip)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_mouse_mirror_flip)

if __name__ == "__main__":
    register()
