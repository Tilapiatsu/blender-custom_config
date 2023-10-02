import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from mathutils import Vector


class KeSelectedToOrigin(Operator):
    bl_idname = "view3d.selected_to_origin"
    bl_label = "Selection to Origin"
    bl_description = "Places Selected Object Geo or Element Mode Selection at objects Origin (Location only)\n" \
                     "Object Mode function uses Set Origin - All options available in redo panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    o_type : EnumProperty(
        items=[("GEOMETRY_ORIGIN", "Geometry to Origin", "", 1),
               ("ORIGIN_GEOMETRY", "Origin to Geometry", "", 2),
               ("ORIGIN_CURSOR", "Origin to 3D Cursor", "", 3),
               ("ORIGIN_CENTER_OF_MASS", "Origin to Center of Mass (Surface)", "", 4),
               ("ORIGIN_CENTER_OF_VOLUME", "Origin to Center of Mass (Volume)", "", 5)
               ],
        name="Type",
        default="GEOMETRY_ORIGIN")

    o_center : EnumProperty(
        items=[("MEDIAN", "Median Center", "", 1),
               ("BOUNDS", "Bounds Center", "", 2)
               ],
        name="Center",
        default="MEDIAN")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            self.report({'INFO'}, "Selection Error: No object(s) selected?")
            return {"CANCELLED"}

        og_mode = str(context.mode)

        if og_mode != "OBJECT":
            if self.o_type == "GEOMETRY_ORIGIN":
                c = context.scene.cursor
                og_cursor_loc = Vector(c.location)
                og_cursor_mode = str(c.rotation_mode)
                c.rotation_mode = "XYZ"
                og_cursor_rot = Vector(c.rotation_euler)
                c.rotation_euler = 0, 0, 0

                bpy.ops.object.mode_set(mode='OBJECT')

                for o in sel_obj:
                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)
                    context.view_layer.objects.active = o
                    bpy.ops.object.mode_set(mode='EDIT')
                    if og_mode == "OBJECT":
                        bpy.ops.mesh.select_all(action="SELECT")
                    c.location = o.location
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                    o.select_set(False)
                    bpy.ops.object.mode_set(mode='OBJECT')

                c.location = og_cursor_loc
                c.rotation_euler = og_cursor_rot
                c.rotation_mode = og_cursor_mode

                for o in sel_obj:
                    o.select_set(True)

                bpy.ops.object.mode_set(mode='EDIT')
            else:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.origin_set(type=self.o_type, center=self.o_center)
        else:
            bpy.ops.object.origin_set(type=self.o_type, center=self.o_center)

        return {'FINISHED'}
