import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from .._utils import average_vector, vertloops, correct_normal, tri_points_order


class KeExtractAndEdit(Operator):
    bl_idname = "mesh.ke_extract_and_edit"
    bl_label = "Extract & Edit"
    bl_description = "Separate element selection into a New Object & set as Active Object in Edit Mode\n" \
                     "Customize shortcut(s) with ADDITIONAL OPTIONS (not in redo-panel) in PREFS/KEYMAP"
    bl_options = {'REGISTER', 'UNDO'}

    expand: BoolProperty(
        default=False,
        name="Select Connected",
        description="Auto-selects all connected geo"
    )
    dupe: BoolProperty(
        default=False,
        name="Duplicate",
        description="Duplicate selection before extraction"
    )
    origin: EnumProperty(
        items=[("COPY", "Copy", "Extracted obj uses same origin (loc/rot) as source obj", 1),
               ("ACTIVE", "Active", "Active Face or Edge(+2 connected edges) used for loc/rot origin placement", 2),
               ("APPLY", "Apply", "Apply loc/rot (0,0,0) to extracted geo obj", 3)],
        name="Origin", default="COPY"
    )
    datacopy: BoolProperty(
        default=True,
        name="Mesh Data Copy",
        description="Copy original object's mesh data: Normal settings & other attributes"
    )
    objcopy: BoolProperty(
        default=True,
        name="Object Properties Copy",
        description="Copy original object's properties: Viewport visibility settings etc."
    )
    objmode: BoolProperty(
        default=False, name="Set Object Mode",
        description="Set Object Mode after operation\n"
                    "Note: Will disable redo-panel"
    )

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "expand", toggle=True)
        layout.prop(self, "dupe", toggle=True)

    def execute(self, context):
        obj = context.object
        obj.update_from_editmode()
        sel_verts = [v for v in obj.data.vertices if v.select]
        if not sel_verts:
            self.report({"INFO"}, "Nothing Selected?")
            return {"CANCELLED"}

        ouc = obj.users_collection
        if len(ouc) > 0:
            coll = ouc[0]
        else:
            coll = context.scene.collection

        # Expand Linked
        if self.expand:
            bpy.ops.mesh.select_linked()

        # Default + self.origin == "APPLY":
        rot = loc = Vector()

        # Check selections
        bm = bmesh.from_edit_mesh(obj.data)
        obj_mtx = obj.matrix_world.copy()
        sel_mode = context.tool_settings.mesh_select_mode[:]

        sel_poly = [p for p in bm.faces if p.select]
        active_face = bm.faces.active

        if self.origin == "ACTIVE":
            n_v, pos, vec_poslist = [], [], []

            if sel_mode[1]:
                # EDGE MODE
                bm.edges.ensure_lookup_table()

                sel_edges = [e for e in bm.edges if e.select]
                active_edge = bm.select_history.active

                if len(sel_edges) >= 2 and active_edge:
                    # Find the active edges loop selection
                    vert_pairs = []
                    for e in sel_edges:
                        vp = [v for v in e.verts]
                        vert_pairs.append(vp)

                    active_loop_verts = 0
                    loops = vertloops(vert_pairs)

                    if loops:
                        # print("loop found")
                        sel_verts = []
                        for loop in loops:
                            if active_edge.verts[0] in loop and active_edge.verts[1] in loop:
                                sel_verts.extend(loop)
                                active_loop_verts = len(loop)
                                break
                        sel_verts = list(set(sel_verts))

                        if active_loop_verts >= 3:
                            # Trimming selection
                            if len(sel_verts) > 4:
                                vec_poslist.append(obj_mtx @ sel_verts[0].co)
                                vec_poslist.append(obj_mtx @ sel_verts[int(len(sel_verts) * 0.33)].co)
                                vec_poslist.append(obj_mtx @ sel_verts[int(len(sel_verts) * 0.66)].co)
                            else:
                                vec_poslist = obj_mtx @ sel_verts[0].co, \
                                              obj_mtx @ sel_verts[1].co, \
                                              obj_mtx @ sel_verts[2].co

                        if active_loop_verts > 2:
                            sel_pos_co = [obj_mtx @ v.co for v in sel_verts]
                            pos = Vector(average_vector(sel_pos_co))

            elif sel_mode[2] and sel_poly and active_face:
                # FACE mode
                if active_face in sel_poly:
                    n_v = correct_normal(obj_mtx, active_face.normal * -1)
                    vec_poslist = [obj_mtx @ v.co for v in active_face.verts]
                    pos = obj_mtx @ active_face.calc_center_median()

            # Get settings & Make new item
            if pos and vec_poslist:
                h = tri_points_order(vec_poslist)
                vec_poslist = vec_poslist[h[0]], vec_poslist[h[1]], vec_poslist[h[2]]

                p1, p2, p3 = vec_poslist[0], vec_poslist[1], vec_poslist[2]
                v_1 = p2 - p1
                v_2 = p3 - p1
                if not n_v:
                    n_v = v_1.cross(v_2).normalized()
                    n_v *= -1
                # find the better rot
                c1 = n_v.cross(v_1).normalized()
                c2 = n_v.cross(v_2).normalized()
                if c1.dot(n_v) < c2.dot(n_v):
                    u_v = c2
                else:
                    u_v = c1
                t_v = u_v.cross(n_v).normalized()

                nrot = Matrix((t_v, u_v, n_v)).to_4x4().inverted()
                loc = pos
                rot = nrot.to_euler()
                rot.x = round(rot.x, 4)
                rot.y = round(rot.y, 4)
                rot.z = round(rot.z, 4)

        # Create new mesh and apply settings
        if self.datacopy:
            new_mesh = obj.data.copy()
            new_mesh.clear_geometry()
        else:
            new_mesh = bpy.data.meshes.new(obj.name + '_extracted_mesh')

        if self.objcopy:
            new_obj = obj.copy()
            new_obj.name = obj.name + '_extracted'
            new_obj.data = new_mesh
        else:
            new_obj = bpy.data.objects.new(obj.name + '_extracted', new_mesh)

        if self.origin == "COPY":
            rot = obj.rotation_euler
            loc = obj.location

        new_obj.location = loc
        new_obj.rotation_euler = rot

        coll.objects.link(new_obj)

        if bpy.app.version < (4, 1):
            new_obj.data.use_auto_smooth = True

        if self.dupe:
            bpy.ops.mesh.duplicate()

        bpy.ops.mesh.separate(type='SELECTED')
        temp_dupe = context.selected_objects[-1]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="DESELECT")

        temp_dupe.select_set(True)
        new_obj.select_set(True)

        context.view_layer.objects.active = temp_dupe
        context.view_layer.objects.active = new_obj
        bpy.ops.object.join('INVOKE_DEFAULT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action="SELECT")
        # bm = bmesh.from_edit_mesh(context.object.data)
        # bm.faces.ensure_lookup_table()
        # bm.faces.active = None
        # bmesh.update_edit_mesh(context.object.data)

        if self.objmode:
            bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.transform.select_orientation(orientation='LOCAL')
        # bpy.context.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        return {'FINISHED'}
