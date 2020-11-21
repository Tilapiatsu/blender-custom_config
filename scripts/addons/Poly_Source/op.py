import bpy
import bmesh
from bpy.types import Operator



class PS_OT_clear_dots(Operator):
    bl_idname = "ps.clear_dots"
    bl_label = "Clear Dots"
    bl_description="To Remove A Single Vertex"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        vCount = 0

        uniques = context.selected_objects
        for obj in uniques:
            me = obj.data
            mesh = bmesh.from_edit_mesh(me)

            vDots = []
            for v in mesh.verts:
                if v.is_wire: #is_manifold:
                    #if len(v.link_edges) < 2:
                    vDots.append(v)
                    vCount += 1


            bmesh.ops.delete(mesh, geom=vDots, context='VERTS')

            bmesh.update_edit_mesh(me)
        
        self.report({'INFO'}, "Clear Dots - " + str(vCount))
        return {'FINISHED'}
    


classes = [
    PS_OT_clear_dots,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)