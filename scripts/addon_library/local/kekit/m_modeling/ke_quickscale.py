import bpy
from bpy.props import EnumProperty, BoolProperty, FloatProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import get_prefs, average_vector


def calc_bbox(vpos):
    x, y, z = [], [], []
    for i in vpos:
        x.append(i[0])
        y.append(i[1])
        z.append(i[2])
    x, y, z = sorted(x), sorted(y), sorted(z)
    return (x[-1] - x[0], y[-1] - y[0], z[-1] - z[0]), (x, y, z)


def scale_mesh(new_dimensions, c_o):
    bpy.ops.transform.resize(
        value=new_dimensions, orient_type='GLOBAL', orient_matrix_type='GLOBAL', center_override=c_o,
        constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False,
        use_proportional_connected=False, use_proportional_projected=False, snap=False,
        gpencil_strokes=False, texture_space=False, remove_on_cancel=False, release_confirm=False)


class KeQuickScale(Operator):
    bl_idname = "view3d.ke_quickscale"
    bl_label = "Quick Scale"
    bl_description = "Set size and scale axis to fit. Object(s) & Edit mode (selection)"
    bl_options = {'REGISTER', 'UNDO'}

    user_axis : EnumProperty(
        items=[("0", "X", "", 1),
               ("1", "Y", "", 2),
               ("2", "Z", "", 3)],
        name="Axis",
        default=1)

    each : EnumProperty(
        items=[("SEPARATE", "Separate", "Each object uses its own Local Transform", 1),
               ("COMBINED", "Combined", "Using combined BBox in Global Transform (via Edit Mesh)", 2)],
        name="Process Objects",
        default=1)

    unit_size : BoolProperty(name="Unit Size", default=False,
                             description="Unit Size: Scales all axis as needed "
                                         "for selected axis to be desired size")
    user_value : FloatProperty(name="Size", default=1)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.prop(self, "each", expand=True)
        row = layout.row(align=True)
        row.prop(self, "user_axis", expand=True)
        row = layout.row(align=True)
        row.prop(self, "user_value")
        row = layout.row(align=True)
        row.prop(self, "unit_size", toggle=True)
        layout.separator()

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def scale_object(self, obj, dimension, user_axis, other_axis):
        obj_val = self.user_value / (dimension[user_axis] / obj.scale[user_axis])
        factor = obj_val / obj.scale[user_axis]

        new_scale = [1, 1, 1]
        if self.unit_size:
            new_scale[user_axis] = obj_val
            new_scale[other_axis[0]] = factor * obj.scale[other_axis[0]]
            new_scale[other_axis[1]] = factor * obj.scale[other_axis[1]]
            obj.scale = (new_scale[0], new_scale[1], new_scale[2])
        else:
            obj.scale[user_axis] = obj_val

    def execute(self, context):
        k = get_prefs()
        user_axis = int(self.user_axis)
        other_axis = [0, 1, 2]
        other_axis.pop(user_axis)

        # Check selections
        sel_obj = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if not sel_obj:
            context.object.select_set(True)
            sel_obj = [context.object]

        if len(sel_obj) == 1:
            self.each = "SEPARATE"

        tot_bb = []
        bb = [0, 0, 0]

        for obj in sel_obj:

            if self.each == "SEPARATE":

                vpos = []
                if context.mode == "OBJECT":
                    dimension = obj.dimensions
                else:
                    obj.update_from_editmode()
                    sel_verts = [v.index for v in obj.data.vertices if v.select]
                    if not sel_verts:
                        break

                    vpos.extend([obj.matrix_world @ obj.data.vertices[v].co for v in sel_verts])
                    dimension, bb = calc_bbox(vpos)

                if dimension[user_axis] == 0:
                    self.report({'INFO'}, "Cancelled: Zero dimension on selected axis")
                    return {'CANCELLED'}

                if context.mode == "OBJECT":
                    self.scale_object(obj, dimension, user_axis, other_axis)
                else:
                    edit_val = self.user_value / dimension[user_axis]
                    new_dimensions = [edit_val, edit_val, edit_val]
                    c = average_vector(vpos)
                    c_o = (c[0], c[1], bb[1][-1])

                    if not self.unit_size:
                        new_dimensions[other_axis[0]] = 1
                        new_dimensions[other_axis[1]] = 1

                    scale_mesh(new_dimensions, c_o)

            else:
                obj.update_from_editmode()
                if context.mode == "OBJECT":
                    bb = [obj.matrix_world @ Vector(co) for co in obj.bound_box]
                    tot_bb.extend(bb)
                else:
                    sel_verts = [v.index for v in obj.data.vertices if v.select]
                    if sel_verts:
                        tot_bb.extend([obj.matrix_world @ obj.data.vertices[v].co for v in sel_verts])

        if self.each == "COMBINED":
            dimension, bb = calc_bbox(tot_bb)
            edit_val = self.user_value / dimension[user_axis]
            new_dimensions = [edit_val, edit_val, edit_val]
            c_o = average_vector(tot_bb)

            if not self.unit_size:
                new_dimensions[other_axis[0]] = 1
                new_dimensions[other_axis[1]] = 1

            # Meh! Just gonna mashem up in edit mode ;P
            if context.mode == "OBJECT":
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="SELECT")
                scale_mesh(new_dimensions, c_o)
                bpy.ops.object.editmode_toggle()
            else:
                scale_mesh(new_dimensions, c_o)

        # Classic - To avoid undo issues n stuff
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        # Update stored values ( if tweaked in redo)
        k.qs_user_value = self.user_value
        k.qs_unit_size = self.unit_size

        return {'FINISHED'}
