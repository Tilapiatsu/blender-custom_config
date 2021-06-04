bl_info = {
    "name": "CopyPlus",
    "author": "Kjell Emanuelsson 2020",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 3, 2),
    "blender": (2, 80, 0),
}

import bpy


class VIEW3D_OT_ke_copyplus(bpy.types.Operator):
    bl_idname = "view3d.ke_copyplus"
    bl_label = "CopyPlus"
    bl_description = "Cut+ or Copy+ face selection (to temporary cache) then Paste+ into another object."
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("COPY", "Copy", "", 1),
               ("PASTE", "Paste", "", 2),
               ("CUT", "Cut", "", 3),
               ],
        options={'HIDDEN'},
        default="COPY")

    def execute(self, context):
        # -----------------------------------------------------------------------------------------
        # OBJECT SELECTION CHECK
        # -----------------------------------------------------------------------------------------
        cut_obj = False
        obj_merge = bool(bpy.context.scene.kekit.paste_merge)
        co = bpy.data.collections[:]

        sel_mode = bpy.context.mode[:]
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]

        active_obj = context.active_object
        if active_obj:
            if active_obj.type != "MESH":
                active_obj = []
        if not active_obj and sel_obj:
            active_obj = sel_obj[0]

        # -----------------------------------------------------------------------------------------
        # COPY/PASTE BUFFER (without copy+ cache)
        # -----------------------------------------------------------------------------------------
        check_cache = [o.name for o in co if o.name == "_kc_cache_temp"]

        if sel_obj:
            if sel_mode == "OBJECT" and self.mode == "COPY" and not check_cache:
                bpy.ops.view3d.copybuffer("INVOKE_DEFAULT")
                return {'FINISHED'}

            elif sel_mode == "OBJECT" and self.mode == "PASTE" and not check_cache:
                bpy.ops.view3d.pastebuffer("INVOKE_DEFAULT")
                context.view_layer.objects.active = context.selected_objects[-1]
                return {'FINISHED'}

            elif sel_mode == "OBJECT" and self.mode == "CUT" and not check_cache:
                bpy.ops.object.mode_set(mode="EDIT")
                # bpy.ops.mesh.select_mode(type="FACE")
                bpy.context.tool_settings.mesh_select_mode = (False, False, True)
                bpy.ops.mesh.select_all(action='SELECT')
                sel_mode = "EDIT_MESH"
                cut_obj = True

        elif sel_mode == "OBJECT" and self.mode == "PASTE" and check_cache:
            if not active_obj:
                obj_merge = False

        # NON MESH COPY
        elif sel_mode == "OBJECT":
            if self.mode == "COPY":
                bpy.ops.view3d.copybuffer("INVOKE_DEFAULT")
                return {'FINISHED'}
            elif self.mode == "PASTE":
                bpy.ops.view3d.pastebuffer("INVOKE_DEFAULT")
                context.view_layer.objects.active = context.selected_objects[-1]
                return {'FINISHED'}
            else:
                return {'CANCELLED'}

        # -----------------------------------------------------------------------------------------
        # CACHE CHECK
        # -----------------------------------------------------------------------------------------
        active_coll = []
        cache = []
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
            # print("Copy+ Aborted: Nothing to Paste.")
            self.report({"INFO"}, "Cache Empty: Nothing to Paste")
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
                # print("Copy+ Aborted: No polygons selected.")
                self.report({"INFO"}, "Aborted: No polygons selected")
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

            if cut_obj:
                sel_obj = [o for o in sel_obj if o != active_obj]


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
            if cut_obj:
                for o in sel_obj:
                    o.select_set(False)
                active_obj.select_set(True)
                bpy.ops.object.delete()
            else:
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

            if sel_mode != "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')

            if sel_mode == "OBJECT" and not obj_merge:
                cache.select_set(True)
                context.view_layer.objects.active = context.selected_objects[-1]

            elif sel_mode == "OBJECT" and obj_merge and active_obj:
                active_obj.select_set(True)
                context.view_layer.objects.active = active_obj
                cache.select_set(True)
                bpy.ops.object.join()

            elif sel_mode == "OBJECT" and obj_merge and not active_obj:
                cache.select_set(True)
                context.view_layer.objects.active = context.selected_objects[-1]

            else:
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

        if self.mode != "PASTE":
            self.report({"INFO"}, "Copy+: %s Polygons Cached" %len(sel_poly))

        return {"FINISHED"}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_copyplus)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_copyplus)

if __name__ == "__main__":
    register()
