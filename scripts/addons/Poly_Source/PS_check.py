import bpy
import bgl 
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Gizmo, GizmoGroup
import bmesh



shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')



def check_draw_bgl(self, context):

    if context.active_object != None and context.active_object.select_get():
        props = context.preferences.addons[__package__].preferences

        theme = context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size

 
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(props.edge_width + 1)
        bgl.glPointSize(vertex_size + 5)
        bgl.glCullFace(bgl.GL_BACK)
        
        
        if props.xray_che == False:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glEnable(bgl.GL_CULL_FACE)


        if props.line_smooth:
            bgl.glEnable(bgl.GL_LINE_SMOOTH)

        
        bgl.glDepthRange(0, 0.9999)
        #bgl.glDepthFunc(600)
        bgl.glDepthMask(False)

        

       
        shader.bind()
        


        #uniques = context.objects_in_mode_unique_data
        uniques = context.selected_objects
        for obj in uniques:
            if obj.type == 'MESH':
                me = obj.data
                if len(me.polygons) < 15000:
                    if context.mode == 'EDIT_MESH':
                        mesh = bmesh.from_edit_mesh(me)
                    
                    else:
                        mesh = bmesh.new()
                        mesh.from_mesh(me)
                        mesh.verts.ensure_lookup_table()
                        mesh.edges.ensure_lookup_table()
                        mesh.faces.ensure_lookup_table()


                
                    


                
                    
                    opacity_second = props.opacity + 0.1
                    # check
                    if props.ngone:
                        ngone = []
                        for n in mesh.faces:
                            if len(n.verts)>4:
                                ngone.append(n.index)
                        #print("ngone",ngone)
                                
                        copy = mesh.copy()
                        copy.faces.ensure_lookup_table()
                        edge_n = [e for i in ngone for e in copy.faces[i].edges]

                        for e in copy.edges:
                            if not e in edge_n:
                                e.hide_set(True)

                        bmesh.ops.triangulate(copy, faces=copy.faces[:])

                        v_index = []
                        ngone_co = []
                        for f in copy.faces:
                            v_index.extend([v.index for v in f.verts if not f.hide])
                            ngone_co.extend([obj.matrix_world @ v.co for v in f.verts if not f.hide]) 

                        copy.free() #maybe delete

                        ngons_indices = []
                        ngons_indices.extend(list(range(0, len(v_index)))[v_i:v_i+3] for v_i in range(0, len(v_index), 3))
                        #print("ngons_indices",ngons_indices)

                        #ngone_col = [(props.ngone_col.r, props.ngone_col.g, props.ngone_col.b, opacity_second) for _ in range(len(ngone_co))]
                        ngone_col = (props.ngone_col.r, props.ngone_col.g, props.ngone_col.b, opacity_second)

                        NGONE = batch_for_shader(shader, 'TRIS', {"pos": ngone_co}, indices=ngons_indices)
                        shader.uniform_float("color", ngone_col)
                        NGONE.draw(shader)
                    

                    if props.tris:
                        tris_co = [obj.matrix_world @ v.co for f in mesh.faces for v in f.verts if len(f.verts)==3]
                        #tris_col = [(props.tris_col.r, props.tris_col.g, props.tris_col.b, opacity_second) for _ in range(len(tris_co))]
                        tris_col = (props.tris_col.r, props.tris_col.g, props.tris_col.b, opacity_second)
                        TRIS = batch_for_shader(shader, 'TRIS', {"pos": tris_co})
                        shader.uniform_float("color", tris_col)
                        TRIS.draw(shader)

                    
                    if props.non_manifold_check:
                        e_non_i = [e.index for e in mesh.edges if not e.is_manifold]
                        e_non_co = [obj.matrix_world @ v.co for i in e_non_i for v in mesh.edges[i].verts]
                        #e_non_col = [(props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second) for _ in range(len(e_non_co))]
                        e_non_col = (props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second)
                        EDGES_NON = batch_for_shader(shader, 'LINES', {"pos": e_non_co})
                        shader.uniform_float("color", e_non_col)
                        EDGES_NON.draw(shader)


                    if props.e_pole: 
                        e_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)==5]
                        #e_pole_col = [(props.e_pole_col.r, props.e_pole_col.g, props.e_pole_col.b, opacity_second) for _ in range(len(e_pole_co))]
                        e_pole_col = (props.e_pole_col.r, props.e_pole_col.g, props.e_pole_col.b, opacity_second)
                        E_POLE = batch_for_shader(shader, 'POINTS', {"pos": e_pole_co})
                        shader.uniform_float("color", e_pole_col) 
                        E_POLE.draw(shader)


                    if props.n_pole:
                        n_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)==3]
                        #n_pole_col = [(props.n_pole_col.r, props.n_pole_col.g, props.n_pole_col.b, opacity_second) for _ in range(len(n_pole_co))]
                        n_pole_col = (props.n_pole_col.r, props.n_pole_col.g, props.n_pole_col.b, opacity_second)
                        N_POLE = batch_for_shader(shader, 'POINTS', {"pos": n_pole_co}) 
                        shader.uniform_float("color", n_pole_col) 
                        N_POLE.draw(shader)


                    if props.f_pole: 
                        f_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)>5]
                        #f_pole_col = [(props.f_pole_col.r, props.f_pole_col.g, props.f_pole_col.b, opacity_second) for _ in range(len(f_pole_co))]
                        f_pole_col = (props.f_pole_col.r, props.f_pole_col.g, props.f_pole_col.b, opacity_second)
                        F_POLE = batch_for_shader(shader, 'POINTS', {"pos": f_pole_co})
                        shader.uniform_float("color", f_pole_col) 
                        F_POLE.draw(shader)


                    if props.v_bound:
                        v_bound_co = [obj.matrix_world @ v.co for v in mesh.verts if v.is_boundary and v.is_manifold] 
                        #v_bound_col = [(props.bound_col.r, props.bound_col.g, props.bound_col.b, opacity_second) for _ in range(len(v_bound_co))]
                        v_bound_col = (props.bound_col.r, props.bound_col.g, props.bound_col.b, opacity_second)
                        V_BOUND = batch_for_shader(shader, 'POINTS', {"pos": v_bound_co,})
                        shader.uniform_float("color", v_bound_col) 
                        V_BOUND.draw(shader)
                    

                    if props.v_alone:
                        v_alone_co = [obj.matrix_world @ v.co for v in mesh.verts if not v.is_manifold]
                        #v_alone_col = [(props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second) for _ in range(len(v_alone_co))]
                        v_alone_col = (props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second)
                        V_ALONE = batch_for_shader(shader, 'POINTS', {"pos": v_alone_co})
                        shader.uniform_float("color", v_alone_col)
                        V_ALONE.draw(shader)
            
            

        if props.line_smooth:
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
        
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_CULL_FACE)
        bgl.glLineWidth(2)
        bgl.glPointSize(vertex_size)
        
        bgl.glDisable(bgl.GL_BLEND)  

  



class PS_GT_check(Gizmo):
    bl_idname = "ps.check"

    def draw(self, context):
        check_draw_bgl(self, context)

    """ def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1 """



class PS_GGT_check_group(GizmoGroup):
    
    bl_idname = "ps.check_group"
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL'
 

    @classmethod
    def poll(cls, context):
        settings = context.scene.ps_set_
        #props = context.preferences.addons[__package__.split(".")[0]].preferences
        return settings.mesh_check == True
        

    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_check.bl_idname)
        mesh.use_draw_modal = True
        self.mesh = mesh 


    def draw_prepare(self, context):
        settings = context.scene.ps_set_
        #props = context.preferences.addons[__package__.split(".")[0]].preferences
        mesh = self.mesh
        if settings.mesh_check == True:
            mesh.hide = False
        else:
            mesh.hide = True






















classes = [
    PS_GT_check,
    PS_GGT_check_group,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)