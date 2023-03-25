import bpy
import bmesh
from bpy.types import Operator


class KeNiceProject(Operator):
    bl_idname = "view3d.ke_nice_project"
    bl_label = "Nice Project"
    bl_description = "'Knife Project', but nice. \n" \
                     "Edit Mode: Cutter = Selected Faces (with boundry edges)\n" \
                     "Object Mode: Cutter = Active (selected) Object (with boundry edges)"
    bl_options = {'REGISTER', 'UNDO'}

    through: bpy.props.BoolProperty(name="Cut Through", default=False)
    keep: bpy.props.BoolProperty(name="Keep Cutter Geo", default=True,
                                 description="(Edit Mode) Disable to remove cutter after operation")
    keep_selected: bpy.props.BoolProperty(name="Keep Cutter Selected", default=True,
                                          description="(Edit Mode) Or, the result will be selected"
                                                      "(Requires Keep Cutter Geo on)")
    wire: bpy.props.BoolProperty(name="Use All Edges",
                                 description="Use ALL edges in Cutter as boundary edges to cut with",
                                 default=False)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "through", toggle=True)
        if context.object.mode != "OBJECT":
            layout.prop(self, "keep", toggle=True)
            layout.prop(self, "keep_selected", toggle=True)
        layout.prop(self, "wire", toggle=True)
        row = layout.row()
        row.alignment = "CENTER"
        row.separator()
        row.label(text="Note: Redo requires unchanged viewport")
        row.separator()

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        ok_geo = {"MESH", "CURVE", "FONT", "GPENCIL", "SURFACE"}
        obj = context.object

        if context.active_object:
            if context.active_object.type in ok_geo:
                obj = context.active_object
            else:
                self.report({"INFO"}, "Invalid Selection")
                return {"CANCELLED"}

        kp_mode = "Object"
        if obj.mode != "OBJECT":
            kp_mode = "Mesh"

        if kp_mode == 'Mesh':
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            sel_faces = [f for f in bm.faces if f.select]

            if not sel_faces:
                self.report({"INFO"}, "Invalid Selection")
                return {"CANCELLED"}

            if self.keep:
                bpy.ops.mesh.duplicate(mode=2)
                for f in sel_faces:
                    f.hide_set(True)

            if self.wire and obj.type != "MESH":
                self.wire = False

            bpy.ops.mesh.separate(type="SELECTED")
            temp_obj = context.selected_objects[-1]
            obj.select_set(False)

            if self.wire:
                # Holy macro madness batman!
                temp_obj.select_set(True)
                context.view_layer.objects.active = temp_obj
                bpy.ops.object.editmode_toggle()
                t_me = temp_obj.data
                t_bm = bmesh.from_edit_mesh(t_me)
                bmesh.ops.delete(t_bm, geom=t_bm.faces, context="FACES_ONLY")
                bmesh.update_edit_mesh(t_me)
                t_bm.free()
                bpy.ops.object.editmode_toggle()
                temp_obj.select_set(False)
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                obj.select_set(False)
                temp_obj.select_set(True)

            # KNIFE!
            bpy.ops.mesh.knife_project(cut_through=self.through)
            bpy.data.objects.remove(temp_obj, do_unlink=True)
            if self.wire:
                bpy.data.meshes.remove(t_me)

            if self.keep:
                if self.keep_selected:
                    bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.reveal(select=self.keep_selected)

            bmesh.update_edit_mesh(obj.data)
            obj.select_set(True)

        elif kp_mode == "Object":
            bpy.ops.object.editmode_toggle()
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            b_edges = [e for e in bm.edges if e.is_boundary]
            bpy.ops.object.editmode_toggle()

            if not b_edges:
                self.wire = True

            if self.wire:
                # Holy multitudes of macros batman!
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.duplicate()
                obj.hide_set(True)
                temp_obj = context.selected_objects[-1]
                context.view_layer.objects.active = temp_obj
                bpy.ops.object.editmode_toggle()
                t_me = temp_obj.data
                t_bm = bmesh.from_edit_mesh(t_me)
                bmesh.ops.delete(t_bm, geom=t_bm.faces, context="FACES_ONLY")
                bmesh.update_edit_mesh(t_me)
                cutter = temp_obj
            else:
                cutter = obj

            targets = [o for o in context.scene.objects if o.type == 'MESH' and o.visible_get() and o != cutter]
            for o in targets:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action="DESELECT")
                o.select_set(True)
                context.view_layer.objects.active = o

                bpy.ops.object.mode_set(mode='EDIT')
                cutter.select_set(True)
                bpy.ops.mesh.knife_project(cut_through=self.through)

            if self.wire:
                bpy.data.objects.remove(temp_obj, do_unlink=True)
                bpy.data.meshes.remove(t_me)
                obj.hide_set(False)

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj

        else:
            self.report({"INFO"}, "Invalid Selection")
            return {"CANCELLED"}

        return {"FINISHED"}

#
# CLASS REGISTRATION
#
classes = (
    KeNiceProject,
)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
