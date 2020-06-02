bl_info = {
    "name": "keCollision",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}
import bpy
from .ke_utils import average_vector
from mathutils import Vector


class VIEW3D_OT_ke_collision(bpy.types.Operator):
    bl_idname = "view3d.ke_collision"
    bl_label = "Collision"
    bl_description = "Creates BOX or CONVEX HULL collision-style object from element or obj selection. Multi-object edit mode support."
    bl_options = {'REGISTER', 'UNDO'}

    col_type : bpy.props.EnumProperty(items=[("BOX", "Box", ""),
                                            ("CONVEX", "Convex Hull", ""),
                                            ], name="Collision Type", default="BOX")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        sel_count = len(sel_obj)
        og_obj = None

        if sel_count == 0:
            self.report({'INFO'}, "Selection Error: No valid/active object(s) selected?")
            return {"CANCELLED"}

        elif sel_count == 1:
            og_obj = context.active_object
            og_name = str(og_obj.name)

        mode = str(context.mode)

        if mode == "EDIT_MESH":
            all_obj = [o for o in context.scene.objects if o.type == "MESH"]

            if self.col_type == "CONVEX":
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type="SELECTED")
                new_obj = [o for o in context.scene.objects if o.type == "MESH" and o not in all_obj]

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action="DESELECT")
                for o in new_obj:
                    o.select_set(True)
                bpy.context.view_layer.objects.active = new_obj[0]
                if sel_count > 1:
                    bpy.ops.object.join('INVOKE_DEFAULT')
                col_obj = bpy.context.view_layer.objects.active
                col_obj.color = (0.20, 0.35, 1, 0.9)

                if og_obj:
                    col_obj.name = og_name + '_col'
                else:
                    col_obj.name = col_obj.name + '_col'

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.convex_hull(delete_unused=True, use_existing_faces=True, make_holes=False,
                                         join_triangles=True, face_threshold=0.10472, shape_threshold=0.698132,
                                         uvs=False, vcols=False, seam=False, sharp=False, materials=False)
                bpy.ops.object.mode_set(mode='OBJECT')


            elif self.col_type == "BOX":
                bpy.ops.object.mode_set(mode='OBJECT')

                bbx, bby, bbz = [], [], []
                for o in sel_obj:
                    vcos = [o.matrix_world @ v.co for v in o.data.vertices if v.select]
                    for co in vcos:
                        bbx.append(co[0])
                        bby.append(co[1])
                        bbz.append(co[2])

                bbx.sort()
                bby.sort()
                bbz.sort()

                sideX = bbx[-1] - bbx[0]
                sideY = bby[-1] - bby[0]
                sideZ = bbz[-1] - bbz[0]

                minmax = (Vector((bbx[0], bby[0], bbz[0])), Vector((bbx[-1], bby[-1], bbz[-1])))
                avg_pos = average_vector(minmax)

                bpy.ops.mesh.primitive_box_add(width=sideX/2, depth=sideY/2, height=sideZ/2,
                                               align='WORLD', location=avg_pos, rotation=(0,0,0))

                col_obj = [o for o in context.scene.objects if o.type == "MESH"][-1]
                if og_obj:
                    col_obj.name = og_name + '_col'
                else:
                    col_obj.name = col_obj.name + '_col'

                col_obj = bpy.context.view_layer.objects.active
                col_obj.color = (0.20, 0.35, 1, 0.9)


        elif mode == "OBJECT":
            new_sel = []

            if self.col_type == "CONVEX":

                for o in sel_obj:
                    bpy.context.view_layer.objects.active = o

                    all_obj = [o for o in context.scene.objects if o.type == "MESH"]

                    bpy.ops.object.select_all(action="DESELECT")

                    o.select_set(True)
                    og_name = str(o.name)

                    bpy.ops.object.duplicate()
                    o.select_set(False)

                    col_obj = [ob for ob in context.scene.objects if ob.type == "MESH" and ob not in all_obj][-1]
                    col_obj.select_set(True)

                    col_obj.color = (0.20, 0.35, 1, 0.9)
                    if og_obj:
                        col_obj.name = og_name + '_col'
                    else:
                        col_obj.name = col_obj.name + '_col'

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.mesh.convex_hull(delete_unused=True, use_existing_faces=True, make_holes=False,
                                             join_triangles=True, face_threshold=0.10472, shape_threshold=0.698132,
                                             uvs=False, vcols=False, seam=False, sharp=False, materials=False)

                    bpy.ops.object.mode_set(mode='OBJECT')
                    new_sel.append(col_obj)

            elif self.col_type == "BOX":
                for o in sel_obj:
                    vco = [o.matrix_world @ v.co for v in o.data.vertices]

                    bbx, bby, bbz = [], [], []
                    for co in vco:
                        bbx.append(co[0])
                        bby.append(co[1])
                        bbz.append(co[2])

                    bbx.sort()
                    bby.sort()
                    bbz.sort()

                    sideX = bbx[-1] - bbx[0]
                    sideY = bby[-1] - bby[0]
                    sideZ = bbz[-1] - bbz[0]

                    minmax = (Vector((bbx[0], bby[0], bbz[0])), Vector((bbx[-1], bby[-1], bbz[-1])))
                    avg_pos = average_vector(minmax)


                    bpy.ops.mesh.primitive_box_add(width=sideX / 2, depth=sideY / 2, height=sideZ / 2,
                                                   align='WORLD', location=avg_pos, rotation=(0, 0, 0))

                    col_obj = [o for o in context.scene.objects if o.type == "MESH"][-1]
                    if og_obj:
                        col_obj.name = og_name + '_col'
                    else:
                        col_obj.name = col_obj.name + '_col'

                    col_obj = bpy.context.view_layer.objects.active
                    col_obj.color = (0.20, 0.35, 1, 0.9)
                    new_sel.append(col_obj)


            for i in new_sel:
                i.select_set(True)

        return {"FINISHED"}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_collision,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
