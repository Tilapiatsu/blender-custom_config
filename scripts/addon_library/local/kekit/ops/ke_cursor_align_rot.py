import bmesh
import bpy
from bpy.types import Operator
from mathutils import Vector
from .._utils import rotation_from_vector, mouse_raycast, is_tf_applied, get_prefs


class KeCursorAlignRot(Operator):
    bl_idname = "view3d.ke_cursor_align_rot"
    bl_label = "Align Cursor Rotation"
    bl_description = "Aligns the 3D Cursors rotation to a mouse-over element\nor resets if mouse is over nothing"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        set_cursor_tf = k.cursorfit

        og_mode = []
        if context.mode != "OBJECT":
            og_mode = context.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)
        # excluding if any modifier that deform/ change the mesh's location to avoid any None type error
        m_deform = ['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM',
                    'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM',
                    'WARP', 'WAVE']

        if hit_normal and hit_obj:
            mfs = []
            # Terrible workaround for raycast index issue
            if len(hit_obj.modifiers) > 0:
                for m in hit_obj.modifiers:
                    if m.show_viewport and m.type not in m_deform:
                        mfs.append(m)
                        m.show_viewport = False
                # casting again for unevaluated index (the "proper way" is bugged? IDK whatever)
                hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

            obj_mtx = hit_obj.matrix_world.copy()

            if not is_tf_applied(hit_obj)[2]:
                print("Cursor Rot Align: Object Scale is not applied. jfyi.")

            bm = bmesh.new()
            bm.from_mesh(hit_obj.data)
            bm.faces.ensure_lookup_table()

            normal = bm.faces[hit_face].normal
            tangent = bm.faces[hit_face].calc_tangent_edge()

            rot_mtx = rotation_from_vector(normal, tangent, rw=True)
            rot_mtx = obj_mtx @ rot_mtx

            q = rot_mtx.to_euler("XYZ")
            context.scene.cursor.rotation_mode = "XYZ"
            context.scene.cursor.rotation_euler = q
            # Floating point rounding - people prefer "clean zeros"
            crot = context.scene.cursor.rotation_euler
            crot.x = round(crot.x, 4)
            crot.y = round(crot.y, 4)
            crot.z = round(crot.z, 4)

            if mfs:
                for m in mfs:
                    m.show_viewport = True
        else:
            context.scene.cursor.rotation_euler = (0, 0, 0)

        if og_mode:
            if og_mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='EDIT')
            # There is no cursor in the other edit modes?

        if set_cursor_tf:
            bpy.ops.transform.select_orientation(orientation="CURSOR")
            context.tool_settings.transform_pivot_point = "CURSOR"

        return {"FINISHED"}
