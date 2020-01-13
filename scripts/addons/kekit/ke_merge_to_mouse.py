bl_info = {
    "name": "Merge To Mouse",
    "author": "Kjell Emanuelsson 2019",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector
from bpy.types import Operator

class MESH_OT_merge_to_mouse(Operator):
    bl_idname = "mesh.merge_to_mouse"
    bl_label = "Merge to Mouse"
    bl_description = "Merge SELECTED vertices to the (selected) vert CLOSEST to the Mouse Pointer"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))
    merge_point = []
    nearest = 100000

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):

        obj = bpy.context.active_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        sel_mode = [b for b in bpy.context.tool_settings.mesh_select_mode]

        sel = [v for v in bm.verts if v.select]
        if sel:
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)

            sel_verts = []
            for v in sel:
                for e in v.link_edges:
                    sel_verts.append(e.other_vert(v))

            sel_verts += sel
            sel_verts = list(set(sel_verts))

            for v in sel_verts:
                vpos = obj.matrix_world @ Vector(v.co)
                vscreenpos = location_3d_to_region_2d(context.region, context.space_data.region_3d, vpos)
                dist = (self.mouse_pos - vscreenpos).length
                if dist < self.nearest:
                    self.merge_point = v
                    self.nearest = dist

            if self.merge_point:
                bm.select_history.add(self.merge_point)
                bm.verts[self.merge_point.index].select = True
                bpy.ops.mesh.merge(type='LAST', uvs=True)

            bpy.context.tool_settings.mesh_select_mode = (sel_mode[0], sel_mode[1], sel_mode[2])

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    MESH_OT_merge_to_mouse,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
