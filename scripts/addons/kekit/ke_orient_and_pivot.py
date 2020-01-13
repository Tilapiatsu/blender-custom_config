bl_info = {
    "name": "ke Orient and Pivot",
    "author": "Kjell Emanuelsson 2019",
    "category": "Modeling",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from mathutils import Vector
from .ke_utils import rotation_from_vector, mouse_raycast, correct_normal


class VIEW3D_OT_orient_and_pivot_global(bpy.types.Operator):
    bl_idname = "view3d.orient_and_pivot_global"
    bl_label = "Orientation and Pivot Global"
    bl_description = "Sets Orientation to Global & Pivot to Median Point"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bpy.ops.transform.select_orientation(orientation='GLOBAL')
        bpy.context.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

        return {'FINISHED'}


class VIEW3D_OT_orient_and_pivot_local(bpy.types.Operator):
    bl_idname = "view3d.orient_and_pivot_local"
    bl_label = "Orientation and Pivot Local"
    bl_description = "Object Mode = Local & Ind.Origins,  Edit Mesh = Normal & Median Point"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        ctx_mode = bpy.context.mode

        if ctx_mode == "EDIT_MESH":
            bpy.ops.transform.select_orientation(orientation='NORMAL')
            bpy.context.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        elif ctx_mode == "OBJECT":
            bpy.ops.transform.select_orientation(orientation='LOCAL')
            bpy.context.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'

        return {'FINISHED'}


class VIEW3D_OT_orient_and_pivot_local_active(bpy.types.Operator):
    bl_idname = "view3d.orient_and_pivot_local_active"
    bl_label = "Orientation and Pivot Local (Active)"
    bl_description = "Object Mode = Local & Cursor,  Edit Mesh = Normal & Active Element"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        ctx_mode = bpy.context.mode

        if ctx_mode == "EDIT_MESH":
            bpy.ops.transform.select_orientation(orientation='NORMAL')
            bpy.context.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
        elif ctx_mode == "OBJECT":
            bpy.ops.transform.select_orientation(orientation='LOCAL')
            bpy.context.tool_settings.transform_pivot_point = 'CURSOR'

        return {'FINISHED'}


class VIEW3D_OT_orient_and_pivot_cursor(bpy.types.Operator):
    bl_idname = "view3d.orient_and_pivot_cursor"
    bl_label = "Orientation and Pivot Cursor"
    bl_description = "Sets both Orientation and Pivot to Cursor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bpy.ops.transform.select_orientation(orientation='CURSOR')
        bpy.context.tool_settings.transform_pivot_point = 'CURSOR'

        return {'FINISHED'}



class VIEW3D_OT_cursor_fit_selected_and_orient(bpy.types.Operator):
    bl_idname = "view3d.cursor_fit_selected_and_orient"
    bl_label = "Cursor snap to selected and orient"
    bl_description = "Snap Cursor to selected + orient to FACE normal. VERT/EDGE selection = No rotation. " \
                     "Note: Works with mouse over on faces, including Object mode."
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        # clear
        sel_check = False

        # set rot if in poly mode
        if bpy.context.mode == "EDIT_MESH":

            cursor = bpy.context.scene.cursor
            obj = bpy.context.edit_object
            bm = bmesh.from_edit_mesh(obj.data)

            sel_poly = [p for p in bm.faces if p.select]
            sel_edges = [e for e in bm.edges if e.select]
            sel_verts = [v for v in bm.verts if v.select]
            if sel_poly or sel_edges or sel_verts:
                sel_check = True

            if sel_poly:
                v_normals = [p.normal for p in sel_poly]
                face = sel_poly[-1]

                normal = correct_normal(obj.matrix_world, sum(v_normals, Vector()) / len(v_normals))
                tangent = correct_normal(obj.matrix_world, face.calc_tangent_edge())

                rot_mtx = rotation_from_vector(normal, tangent)
                # rot_mtx = obj.matrix_world @ rot_mtx
                q = rot_mtx.to_quaternion()

                cursor.rotation_mode = "QUATERNION"
                cursor.rotation_quaternion = q

            elif not sel_check:
                bpy.ops.object.mode_set(mode="OBJECT")
                hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

                if hit_normal and hit_obj:
                    cursor = bpy.context.scene.cursor

                    bm = bmesh.new()
                    bm.from_mesh(hit_obj.data)
                    bm.faces.ensure_lookup_table()

                    normal = hit_normal
                    tangent = bm.faces[hit_face].calc_tangent_edge()
                    pos = hit_obj.matrix_world @ bm.faces[hit_face].calc_center_median()

                    rot_mtx = rotation_from_vector(normal, tangent)
                    rot_mtx = hit_obj.matrix_world @ rot_mtx
                    q = rot_mtx.to_quaternion()

                    cursor.rotation_mode = "QUATERNION"
                    cursor.rotation_quaternion = q
                    cursor.location = pos

                else:
                    bpy.ops.view3d.snap_cursor_to_center()

                bpy.ops.object.mode_set(mode="EDIT")

            # set location
            if sel_check: bpy.ops.view3d.snap_cursor_to_selected()

        elif bpy.context.mode == "OBJECT":
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

            if hit_normal and hit_obj:
                cursor = bpy.context.scene.cursor

                bm = bmesh.new()
                bm.from_mesh(hit_obj.data)
                bm.faces.ensure_lookup_table()

                normal = hit_normal
                tangent = bm.faces[hit_face].calc_tangent_edge()
                pos = hit_obj.matrix_world @ bm.faces[hit_face].calc_center_median()

                rot_mtx = rotation_from_vector(normal, tangent)
                rot_mtx = hit_obj.matrix_world @ rot_mtx
                q = rot_mtx.to_quaternion()

                cursor.rotation_mode = "QUATERNION"
                cursor.rotation_quaternion = q
                cursor.location = pos

        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_orient_and_pivot_global,
           VIEW3D_OT_orient_and_pivot_local,
           VIEW3D_OT_orient_and_pivot_local_active,
           VIEW3D_OT_orient_and_pivot_cursor,
           VIEW3D_OT_cursor_fit_selected_and_orient,
           )


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
