import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from .._utils import flattened


def check_selection(bm, sel_mode):
    if sel_mode[2]:
        return [p for p in bm.faces if p.select]
    elif sel_mode[1]:
        return [e for e in bm.edges if e.select]
    else:
        return [v for v in bm.verts if v.select]


class KeSelectInvertLinked(Operator):
    bl_idname = "view3d.ke_select_invert_linked"
    bl_label = "Select Invert Linked"
    bl_description = "Inverts selection only on connected/linked mesh geo\n" \
                     "If selection is already fully linked, vanilla invert is used"
    bl_options = {'REGISTER', 'UNDO'}

    invert_type: EnumProperty(
        items=[("SAME", "Same As Selected Only", "", 1),
               ("ALL", "All types of Objects", "", 2),
               ],
        name="Type", description="Invert by Type or Invert All (- filter options below)",
        default="SAME")
    same_disp: BoolProperty(name="Same DisplayType Only", default=True,
                            description="JFYI: Lights are the same display-type as mesh ('textured') by default")
    same_coll: BoolProperty(name="Same Collection Only", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        if context.mode == "OBJECT":
            layout = self.layout
            layout.use_property_split = True
            layout.prop(self, "invert_type", expand=True)
            layout.prop(self, "same_coll")
            layout.prop(self, "same_disp")
            layout.separator()

    def execute(self, context):
        objmode = context.mode

        if context.object.type == 'MESH':
            if context.object.data.is_editmode:
                sel_mode = context.tool_settings.mesh_select_mode[:]
                me = context.object.data
                bm = bmesh.from_edit_mesh(me)

                og_sel = check_selection(bm, sel_mode)
                if og_sel:
                    bpy.ops.mesh.select_linked()
                    re_sel = check_selection(bm, sel_mode)

                    if len(re_sel) == len(og_sel):
                        bpy.ops.mesh.select_all(action='INVERT')
                    else:
                        for v in og_sel:
                            v.select = False

                bm.select_flush_mode()
                bmesh.update_edit_mesh(me)
                objmode = ""
            else:
                objmode = "OBJECT"

        if objmode == 'OBJECT':
            inv_objects = []

            # BASE LIST
            if self.invert_type == "ALL":
                inv_objects = [o for o in context.scene.objects]
            elif self.invert_type == "SAME":
                inv_objects = [o for o in context.scene.objects if o.type == context.object.type]

            # FILTERS
            if self.same_coll:
                f = flattened([c.objects for c in context.object.users_collection])
                print(f)
                inv_objects = [o for o in inv_objects if o in f]
            if self.same_disp:
                sel_type = context.object.display_type
                inv_objects = [o for o in inv_objects if o.display_type == sel_type]
            for o in inv_objects:
                o.select_set(True, view_layer=context.view_layer)
            context.object.select_set(False)

        return {'FINISHED'}
