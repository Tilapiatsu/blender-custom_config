bl_info = {
    "name": "CopyPastePlus",
    "author": "Kjell Emanuelsson 2019",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}
# -------------------------------------------------------------------------------------------------
# Note: Yeah. A wonky macro script to solve a silly workflow problem... TODO: A better way
# -------------------------------------------------------------------------------------------------
import bpy
import bmesh
import re

from bpy.types import (
        Operator,
        PropertyGroup,
        )
from bpy.props import (
        PointerProperty,
        StringProperty,
        )


class MESH_OT_copyplus(Operator):
    bl_idname = "mesh.copyplus"
    bl_label = "Copy+"
    bl_description = "Macro-hack Copy replacement that can copy faces object-to-object (with Paste+)" \
                     "--- Note: You cant delete the original geo before paste+ ---"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        obj = bpy.context.active_object

        if obj.type == "MESH" and bpy.context.mode == "EDIT_MESH":
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            sel_polys = [p.index for p in bm.faces if p.select]

            wm = bpy.context.scene.copypasteplus
            if sel_polys:
                wm.stored_object = str(obj.name)
                wm.stored_elements = str(sel_polys)
            else:
                wm.stored_object = "None"
                wm.stored_elements = "None"

        return {'FINISHED'}


class MESH_OT_pasteplus(Operator):
    bl_idname = "mesh.pasteplus"
    bl_label = "Paste+"
    bl_description = "Macro-hack Paste replacement that can paste faces object-to-object (after using Copy+). Duplicate if in same object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        return self.execute(context="VIEW_3D")

    def execute(self, context):
        wm = bpy.context.scene.copypasteplus
        source_obj = wm.stored_object
        target_obj = bpy.context.active_object

        if target_obj.type == "MESH" and bpy.context.mode == "EDIT_MESH" and target_obj.name != source_obj:

            all_objects = [o.name for o in bpy.context.scene.objects]
            sel_poly = wm.stored_elements

            indexlist = []
            if source_obj != "None" and sel_poly != "None":

                indices = re.findall('[0-9]+', sel_poly)
                for index in indices:
                    try:
                        indexlist.append(int(index))
                    except:
                        pass

            if indexlist:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')

                src_obj = bpy.context.scene.objects[source_obj]
                bpy.context.view_layer.objects.active = src_obj
                src_obj.select_set(True)

                bpy.ops.object.mode_set(mode='EDIT')
                mesh = src_obj.data
                bm = bmesh.from_edit_mesh(mesh)
                bm.faces.ensure_lookup_table()
                for p in indexlist:
                    bm.faces[p].select = True

                bpy.ops.mesh.duplicate_move()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')

                recheck_objects = [o.name for o in bpy.context.scene.objects]
                new_obj = [o for o in recheck_objects if o not in all_objects]

                bpy.ops.object.select_all(action='DESELECT')
                new_sel_obj = bpy.context.scene.objects[new_obj[0]]
                bpy.context.view_layer.objects.active = target_obj
                new_sel_obj.select_set(True)
                target_obj.select_set(True)

                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode='EDIT')

                wm.stored_object = "None"
                wm.stored_elements = "None"

        elif target_obj.name == source_obj:
            print("Paste+: Source and Target Mesh is the same - running Duplicate and clearing buffer.")
            bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT')
            wm.stored_object = "None"
            wm.stored_elements = "None"

        return {'FINISHED'}


class copypaste_props(PropertyGroup):
    stored_object: StringProperty(
        default="None"
        )
    stored_elements: StringProperty(
        default="None"
    )


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    copypaste_props,
    MESH_OT_copyplus,
    MESH_OT_pasteplus,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.copypasteplus = PointerProperty(type=copypaste_props)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    try:
        del bpy.types.Scene.copypasteplus
    except Exception as e:
        print('unregister fail:\n', e)
        pass


if __name__ == "__main__":
    register()
