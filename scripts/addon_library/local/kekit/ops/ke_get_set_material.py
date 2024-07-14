import bpy
from bpy.types import Operator
from bpy.props import IntVectorProperty
from mathutils import Vector
from .._utils import mouse_raycast, get_prefs


class KeGetSetMaterial(Operator):
    bl_idname = "view3d.ke_get_set_material"
    bl_label = "Get & Set Material"
    bl_description = "Samples material under mouse pointer and applies it to the selection"
    bl_options = {'REGISTER', 'UNDO'}

    offset: IntVectorProperty(name="Offset", default=(0, 0), size=2, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))
    nonmesh_target = False
    image_target = None
    target_index = None
    cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR'}

    def raycast(self, context):
        obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos, evaluated=True)
        # Double-check with viewpicker since raycasting is only good for "real mesh" ?
        if face_index is None:
            bpy.ops.view3d.select(extend=False, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))
            obj = context.object
            if obj.type in self.cat and obj.type != 'MESH':
                self.nonmesh_target = True
                self.target_index = 0
            elif obj.type == "EMPTY":
                if obj.empty_display_type == "IMAGE" and obj.data is not None:
                    self.image_target = obj.data
        return obj, hit_wloc, hit_normal, face_index

    def mat_from_image(self):
        mat = None
        for m in bpy.data.materials:
            if m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE":
                        if n.image == self.image_target:
                            return m
        if mat is None:
            # Create new
            m = bpy.data.materials.new(name=self.image_target.name.split(".")[0])
            m.use_nodes = True
            shader = m.node_tree.nodes["Material Output"].inputs[0].links[0].from_node
            n_color = m.node_tree.nodes.new("ShaderNodeTexImage")
            m.node_tree.links.new(shader.inputs["Base Color"], n_color.outputs[0])
            n_color.image = self.image_target
            n_color.location = (-300, 300)
            m.node_tree.links.new(shader.inputs["Alpha"], n_color.outputs[1])
            return m

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x - self.offset[0]
        self.mouse_pos[1] = event.mouse_region_y - self.offset[1]
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        hidden = []
        og_active_obj = context.active_object
        og_active_obj.select_set(True)
        sel_obj = context.selected_objects[:]
        sel_mode = context.mode[:]

        bpy.ops.object.mode_set(mode='OBJECT')

        for o in sel_obj:
            if o.type not in self.cat:
                self.report({"INFO"}, "GetSetMaterial: Invalid Object Type Selected")
                return {"CANCELLED"}

        # hide blocking wireframe objects
        for o in context.scene.objects:
            if o.display_type in {'WIRE', 'BOUNDS'} and not o.hide_viewport:
                o.hide_viewport = True
                hidden.append(o)

        target_material = None
        obj, hit_wloc, hit_normal, face_index = self.raycast(context)

        if self.image_target is not None:
            target_material = self.mat_from_image()
            obj.select_set(False)
            # QoL (& user error countermeasure):
            context.space_data.shading.color_type = 'TEXTURE'

        elif face_index is not None or self.nonmesh_target:
            if self.target_index is None:
                self.target_index = obj.data.polygons[face_index].material_index
            slots = obj.material_slots[:]
            if slots:
                target_material = obj.material_slots[self.target_index].material

        if target_material is not None:
            for o in sel_obj:
                o.select_set(False)
            if self.nonmesh_target:
                obj.select_set(False)

            for o in sel_obj:
                o.select_set(True)
                context.view_layer.objects.active = o
                og_mat = None
                screw_type = None
                for slot_index, slot in enumerate(o.material_slots):
                    if slot.name:
                        if slot.material.name == target_material.name:
                            og_mat = slot_index

                if o.type == "MESH":
                    if sel_mode == "OBJECT":
                        screw_type = [m for m in o.modifiers if m.type == "SCREW"]
                        if not screw_type:
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')
                    else:
                        bpy.ops.object.mode_set(mode='EDIT')

                if og_mat is not None:
                    # print("Found & Assigned Existing Material Slot")
                    o.active_material_index = og_mat
                    bpy.ops.object.material_slot_assign()
                else:
                    # print("creating new material slot and linking material")
                    bpy.ops.object.material_slot_add()
                    o.active_material = bpy.data.materials[target_material.name]
                    bpy.ops.object.material_slot_assign()

                # Cleanup
                if k.getmat_clear_unused:
                    # 'Remove_unused' does not work on 'screw-mesh' (it's checking non-existant geo?)
                    if o.type != "MESH" or screw_type:
                        # print("'Non-mesh' just use the top slot")
                        for s in range(len(o.material_slots)):
                            bpy.ops.object.material_slot_move(direction='UP')
                    else:
                        if sel_mode == "OBJECT":
                            bpy.ops.object.mode_set(mode='OBJECT')
                            o.data.update()
                            bpy.ops.object.material_slot_remove_unused()
                        else:
                            bpy.ops.object.mode_set(mode='OBJECT')
                            o.data.update()
                            bpy.ops.object.material_slot_remove_unused()
                            bpy.ops.object.mode_set(mode='EDIT')

                        o.select_set(False)

            for o in sel_obj:
                o.select_set(True)

            if sel_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')

            if hidden:
                for o in hidden:
                    o.hide_viewport = False
            return {'FINISHED'}

        else:
            # Restore sel
            if hidden:
                for o in hidden:
                    o.hide_viewport = False
            if obj:
                obj.select_set(False)
            for o in sel_obj:
                o.select_set(True)
            if og_active_obj:
                context.view_layer.objects.active = og_active_obj
            self.report({"INFO"}, "GetSetMaterial: No Material found")

            return {'CANCELLED'}
