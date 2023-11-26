import bpy
import bmesh
from bpy.types import Operator
from bpy.props import EnumProperty


class KeTripleConnectSpin(Operator):
    bl_idname = "mesh.ke_triple_connect_spin"
    bl_label = "Triple-Connect-Spin"
    bl_description = "VERTS: Connect Verts, EDGE(s): Spin, FACE(s): Triangulate"
    bl_options = {'REGISTER', 'UNDO'}

    connect_mode: EnumProperty(
        items=[("PATH", "Vertex Path", "", 1),
               ("PAIR", "Vertex Pair", "", 2),
               ("ACTIVE", "Selected To Active", "", 3)],
        name="Vertex Connect",
        default="PATH")

    spin_mode: EnumProperty(
        items=[("CW", "Clockwise", "", 1),
               ("CCW", "Counter Clockwise", "", 2)],
        name="Edge Spin",
        default="CW")

    triple_mode: EnumProperty(
        items=[("BEAUTY", "Beauty Method", "", 1),
               ("FIXED", "Fixed/Clip Method", "", 2)],
        name="Face Triangulation",
        default="BEAUTY")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        selection = False

        bpy.ops.object.mode_set(mode='OBJECT')
        for v in context.object.data.vertices:
            if v.select:
                selection = True
                break
        bpy.ops.object.mode_set(mode='EDIT')

        if selection:
            sel_mode = context.tool_settings.mesh_select_mode[:]

            if sel_mode[0]:
                if self.connect_mode == 'PATH':
                    try:
                        bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
                    except Exception as e:
                        print("Connect Path fail: Using Vert Connect instead", e)
                        bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

                elif self.connect_mode == 'PAIR':
                    bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

                elif self.connect_mode == 'ACTIVE':
                    # (Modified) contribution by: Wahyu Nugraha
                    obj = context.object
                    me = obj.data
                    bm = bmesh.from_edit_mesh(me)
                    sel_verts = [v for v in bm.verts if v.select]
                    active = bm.select_history.active

                    if len(sel_verts) < 2 or not active:
                        self.report({"INFO"}, "Invalid selection")
                        return {'CANCELLED'}

                    for v in sel_verts:
                        v.select_set(False)

                    sel_verts = [v for v in sel_verts if v != active]
                    for v in sel_verts:
                        pair = [v, active]
                        bmesh.ops.connect_verts(bm, verts=pair)

                    bmesh.update_edit_mesh(me)

            elif sel_mode[1]:
                try:
                    if self.spin_mode == 'CW':
                        bpy.ops.mesh.edge_rotate(use_ccw=False)
                    elif self.spin_mode == 'CCW':
                        bpy.ops.mesh.edge_rotate(use_ccw=True)
                except Exception as e:
                    self.report({"INFO"}, "TripleConnectSpin: Invalid Edge Selection?")
                    print(e)
                    return {'CANCELLED'}

            elif sel_mode[2]:
                if self.triple_mode == 'BEAUTY':
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                elif self.triple_mode == 'FIXED':
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED', ngon_method='CLIP')
        else:
            return {'CANCELLED'}

        return {'FINISHED'}
