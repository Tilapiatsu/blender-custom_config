bl_info = {
    "name": "CopyPlus",
    "author": "Kjell Emanuelsson 2020",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
}

import bpy


class MESH_OT_ke_copyplus(bpy.types.Operator):
    bl_idname = "mesh.ke_copyplus"
    bl_label = "CopyPlus"
    bl_description = "Cut+ or Copy+ face selection (to temporary cache) then Paste+ into another object."
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("COPY", "Copy", "", "COPY", 1),
               ("PASTE", "Paste", "", "PASTE", 2),
               ("CUT", "Cut", "", "CUT", 3),
               ],
        name="Copy+ Mode",
        options={'HIDDEN'},
        default="COPY")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        # -----------------------------------------------------------------------------------------
        # OBJECT SELECTION CHECK
        # -----------------------------------------------------------------------------------------
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        active_obj = context.active_object
        if not active_obj:
            active_obj = sel_obj[0]

        active_coll = []
        cache = []

        # -----------------------------------------------------------------------------------------
        # CACHE CHECK
        # -----------------------------------------------------------------------------------------
        co = bpy.data.collections[:]
        cache_coll_set = False

        for c in co:
            # CHECK CACHE
            if c.name == "_kc_cache_temp":
                cache_coll_set = True
                cobj = c.objects[:]
                if cobj:
                    if self.mode == "COPY":
                        bpy.data.collections.remove(bpy.data.collections["_kc_cache_temp"], do_unlink=True)
                    else:
                        cache = cobj[0]
            else:
                # GET SELECTED OBJECT(s) SCENE COLLECTION (FOR PASTE OP)
                cobj = [o for o in c.objects if o.type == "MESH"]
                for o in cobj:
                    if o == active_obj:
                        active_coll.insert(0, c)
                        break
                    else:
                        if o in sel_obj:
                            active_coll.append(c)

        if self.mode == "PASTE" and not cache_coll_set:
            print("Copy+ Aborted: Nothing to Paste.")
            return {'CANCELLED'}

        if not active_coll:
            active_coll = context.scene.collection
        else:
            active_coll = active_coll[0]

        # -----------------------------------------------------------------------------------------
        # ELEMENT SELECTION CHECK
        # -----------------------------------------------------------------------------------------
        if self.mode == "COPY" or self.mode == "CUT":
            sel_poly = []

            for o in sel_obj:
                o.update_from_editmode()
                p = [v for v in o.data.polygons if v.select]
                sel_poly.extend(p)

            if not sel_poly:
                print("Copy+ Aborted: No polygons selected.")
                return {'CANCELLED'}

        # -----------------------------------------------------------------------------------------
        # COPY/CUT (SEPARATE SELECTION INTO NEW OBJECT & TEMP COLL MACRO)
        # -----------------------------------------------------------------------------------------
        if self.mode == "COPY" or self.mode == "CUT":

            # COPY/CUT
            if self.mode == "COPY":
                bpy.ops.mesh.duplicate()

            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode="OBJECT")

            for o in sel_obj:
                o.select_set(False)

            # CREATE CACHE OBJECT
            new_obj = [o for o in context.selected_objects if o.type == "MESH" and o not in sel_obj]
            obj_to_cache = new_obj[0]

            if len(new_obj) > 1:
                context.view_layer.objects.active = obj_to_cache
                bpy.ops.object.join()

            # CREATE TEMP COLL, CLEAR LINKS & ADD CACHE OBJECT
            if not cache_coll_set:
                bpy.data.collections.new("_kc_cache_temp")

            current_collections = obj_to_cache.users_collection

            for cc in current_collections:
                cc.objects.unlink(obj_to_cache)

            bpy.data.collections['_kc_cache_temp'].objects.link(obj_to_cache)

            # RESTORE MODE
            for o in sel_obj:
                o.select_set(True)
            context.view_layer.objects.active = active_obj
            bpy.ops.object.mode_set(mode="EDIT")

        # -----------------------------------------------------------------------------------------
        # PASTE OPs
        # -----------------------------------------------------------------------------------------
        elif self.mode == "PASTE" and cache and active_coll:
            # PASTE
            active_coll.objects.link(cache)
            bpy.data.collections.remove(bpy.data.collections["_kc_cache_temp"], do_unlink=True)

            # MERGE CACHE TO ACTIVE & SELECT RESULT MACRO
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action='DESELECT')

            active_obj.select_set(True)
            context.view_layer.objects.active = active_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            cache.select_set(True)

            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action='INVERT')

        # SCENE CLEANUP - YOU´RE WELCOME (blendfiles store useless data until restart)
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)

        return {"FINISHED"}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

classes = (MESH_OT_ke_copyplus,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
