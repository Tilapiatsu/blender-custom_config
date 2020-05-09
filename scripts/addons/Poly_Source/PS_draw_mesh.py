import bpy
import bgl 
import gpu
from gpu_extras.batch import batch_for_shader

from bpy.types import Operator, Panel, Gizmo, GizmoGroup


import numpy as np
import bmesh
from mathutils import Vector

#import time
from bpy.app.handlers import load_pre




vertex_shader = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    

    vec4 pos_view;
    
    in vec3 position;
    in vec4 colorize;

    out vec4 color;

    void main()
    {
        pos_view = view_mat * vec4(position, 1.0f);
        color = colorize;
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fragment_shader = '''
    in vec4 color;
    out vec4 gl_FragColor;

    void main()
    {
        gl_FragColor = vec4(color.xyz, color.w);
    }
'''

shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
#shader2 = gpu.shader.from_builtin('3D_SMOOTH_COLOR')



def mesh_draw_bgl():
    if bpy.context.active_object != None:
        if bpy.context.active_object.select_get():
            if bpy.context.object.type == 'MESH':
                #start_time = time.time()


                props = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
                #settings = bpy.context.scene.polySource_set

                theme = bpy.context.preferences.themes['Default']
                vertex_size = theme.view_3d.vertex_size

                
                
                

                bgl.glEnable(bgl.GL_BLEND)
                bgl.glLineWidth(props.edge_width)
                bgl.glPointSize(vertex_size + 5)
                bgl.glCullFace(bgl.GL_BACK)
                
                
                if props.xray == False:
                    bgl.glEnable(bgl.GL_DEPTH_TEST)
                    bgl.glEnable(bgl.GL_CULL_FACE)


                if props.line_smooth:
                    bgl.glEnable(bgl.GL_LINE_SMOOTH)

                
                #bgl.glDepthRange(0, 0.99999)
                #bgl.glDepthFunc(600)
                bgl.glDepthMask(False)

                

                

                
                z_bias = (0.2 + props.z_bias) / 200
                


                shader.bind()
                

                matrix = bpy.context.region_data.perspective_matrix
                shader.uniform_float("view_mat", matrix)
                shader.uniform_float("Z_Bias", z_bias)
                
                
                
                
                
                #uniques = bpy.context.objects_in_mode_unique_data
                uniques = bpy.context.selected_objects
                for obj in uniques:
                    
                    me = obj.data
                    if bpy.context.mode != 'EDIT_MESH':
                        mesh = bmesh.new()
                        mesh.from_mesh(me)
                        mesh.verts.ensure_lookup_table()
                        mesh.edges.ensure_lookup_table()
                        mesh.faces.ensure_lookup_table()

                    elif bpy.context.mode == 'EDIT_MESH':
                        mesh = bmesh.from_edit_mesh(me)

                   



                    if len(mesh.verts)>1:
                        
                        #retopology mode
                        if props.retopo_mode:
                            # color
                            g_vertex_color = props.vertex_color
                            g_wire_edit_color = props.edge_color
                            g_face_color = props.face_color

                        
                            #faces_ind = [f.index for f in mesh.faces]
                            #faces_cord = [obj.matrix_world @ v.co for i in faces_ind for v in mesh.faces[i].verts]
                            #faces_cord = [obj.matrix_world @ mesh.verts[v].co for i in faces_indices for v in i ] #rab



                            
                            """ face_ind_ngone = []
                            for face in mesh.faces:
                                if len(face.verts) > 4:
                                    face_ind_ngone.append(face.index) """
                                    


                            """ ngone_cord = []
                            for f in faces_indices:
                                for n_i in face_ind_ngone:
                                    if n_i == f.index:
                                        for v in f:
                                            ngone_cord.append(obj.matrix_world @ mesh.verts[v].co) """


                            """ edges_indices = []
                            for i in edges_ind:
                                verts = []
                                for v in mesh.edges[i].verts:
                                    verts.append(v.index)
                                edges_indices.append(verts) """

                    

                            """ for face in mesh.faces:
                                if face.select:
                                    for i, looptris in enumerate(loop_triangles):
                                        for loop in looptris:
                                            if loop.face == face:
                                                ind = i * 3
                                                ind2 = i * 3 + 1
                                                ind3 = ind2 + 1
                                                face_col[ind] = select_color_f
                                                #face_col[ind2] = select_color_f
                                                #face_col[ind3] = select_color_f  """
                            ##################################################################################################################
                            vertex_co = [obj.matrix_world @ v.co for v in mesh.verts]


                            select_color_i = (props.select_items_color.r, props.select_items_color.g, props.select_items_color.b, 1.0)


                            loop_triangles = mesh.calc_loop_triangles()
                            faces_indices = [[loop.vert.index for loop in looptris] for looptris in loop_triangles]

                            face_col = [(g_face_color[0], g_face_color[1], g_face_color[2], props.opacity) for _ in range(len(mesh.verts))]

                            FACES = batch_for_shader(shader, 'TRIS', {"position": vertex_co, "colorize": face_col}, indices=faces_indices)
                            FACES.draw(shader)


                            if bpy.context.mode == 'EDIT_MESH':
                                edges_ind = [e.index for e in mesh.edges]
                                edges_cord = [obj.matrix_world @ v.co for i in edges_ind for v in mesh.edges[i].verts]


                                edge_col = [(g_wire_edit_color.r, g_wire_edit_color.g, g_wire_edit_color.b, 1.0) for _ in range(len(edges_cord))]
                                vert_col = [(g_vertex_color.r, g_vertex_color.g, g_vertex_color.b, 1.0) for _ in range(len(mesh.verts))]

                                for i, vert in enumerate(mesh.verts):
                                    if vert.select:
                                        #face_col[i] = select_color_f
                                        vert_col[i] = select_color_i
                                        
                                for i, edge in enumerate(mesh.edges):
                                    if edge.select:
                                        ind = i*2
                                        ind2 = ind + 1
                                        edge_col[ind] = select_color_i
                                        edge_col[ind2] = select_color_i


                                EDGES = batch_for_shader(shader, 'LINES', {"position": edges_cord, "colorize": edge_col})
                                VERTS = batch_for_shader(shader, 'POINTS', {"position": vertex_co, "colorize": vert_col}) 
                            
                                EDGES.draw(shader)
                                if bpy.context.tool_settings.mesh_select_mode[0]:
                                    VERTS.draw(shader)
                            
                            
                            
                            

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

                            ngone_col = [(props.ngone_col.r, props.ngone_col.g, props.ngone_col.b, opacity_second) for _ in range(len(ngone_co))]

                            NGONE = batch_for_shader(shader, 'TRIS', {"position": ngone_co, "colorize": ngone_col}, indices=ngons_indices)
                            NGONE.draw(shader)
                        

                        if props.tris:
                            tris_co = [obj.matrix_world @ v.co for f in mesh.faces for v in f.verts if len(f.verts)==3]
                            tris_col = [(props.tris_col.r, props.tris_col.g, props.tris_col.b, opacity_second) for _ in range(len(tris_co))]
                            TRIS = batch_for_shader(shader, 'TRIS', {"position": tris_co, "colorize": tris_col})
                            TRIS.draw(shader)

                        
                        if props.non_manifold_check:
                            e_non_i = [e.index for e in mesh.edges if not e.is_manifold]
                            e_non_co = [obj.matrix_world @ v.co for i in e_non_i for v in mesh.edges[i].verts]
                            e_non_col = [(props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second) for _ in range(len(e_non_co))]
                            EDGES_NON = batch_for_shader(shader, 'LINES', {"position": e_non_co, "colorize": e_non_col})
                            EDGES_NON.draw(shader)


                        if props.e_pole: 
                            e_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)==5]
                            e_pole_col = [(props.e_pole_col.r, props.e_pole_col.g, props.e_pole_col.b, opacity_second) for _ in range(len(e_pole_co))]
                            E_POLE = batch_for_shader(shader, 'POINTS', {"position": e_pole_co, "colorize": e_pole_col}) 
                            E_POLE.draw(shader)


                        if props.n_pole:
                            n_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)==3]
                            n_pole_col = [(props.n_pole_col.r, props.n_pole_col.g, props.n_pole_col.b, opacity_second) for _ in range(len(n_pole_co))]
                            N_POLE = batch_for_shader(shader, 'POINTS', {"position": n_pole_co, "colorize": n_pole_col}) 
                            N_POLE.draw(shader)


                        if props.f_pole: 
                            f_pole_co = [obj.matrix_world @ v.co for v in mesh.verts if len(v.link_edges)>5]
                            f_pole_col = [(props.f_pole_col.r, props.f_pole_col.g, props.f_pole_col.b, opacity_second) for _ in range(len(f_pole_co))]
                            F_POLE = batch_for_shader(shader, 'POINTS', {"position": f_pole_co, "colorize": f_pole_col})
                            F_POLE.draw(shader)


                        if props.v_bound:
                            v_bound_co = [obj.matrix_world @ v.co for v in mesh.verts if v.is_boundary and v.is_manifold] 
                            v_bound_col = [(props.bound_col.r, props.bound_col.g, props.bound_col.b, opacity_second) for _ in range(len(v_bound_co))]
                            V_BOUND = batch_for_shader(shader, 'POINTS', {"position": v_bound_co, "colorize": v_bound_col}) 
                            V_BOUND.draw(shader)
                        

                        if props.v_alone:
                            v_alone_co = [obj.matrix_world @ v.co for v in mesh.verts if not v.is_manifold]
                            v_alone_col = [(props.non_manifold_color.r, props.non_manifold_color.g, props.non_manifold_color.b, opacity_second) for _ in range(len(v_alone_co))]
                            V_ALONE = batch_for_shader(shader, 'POINTS', {"position": v_alone_co, "colorize": v_alone_col}) 
                            V_ALONE.draw(shader)
                    
                    

                if props.line_smooth:
                    bgl.glDisable(bgl.GL_LINE_SMOOTH)
                
                bgl.glDisable(bgl.GL_DEPTH_TEST)
                bgl.glDisable(bgl.GL_CULL_FACE)
                bgl.glLineWidth(2)
                bgl.glPointSize(vertex_size)
                
                bgl.glDisable(bgl.GL_BLEND)  

                #print(time.time() - start_time)



""" class PS_GT_draw(Gizmo):
    bl_idname = "ps.draw"

    def draw(self, context):
        mesh_draw_bgl()



class PS_GGT_draw_group(GizmoGroup):
    
    bl_idname = "ps.draw_group"
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE'


    @classmethod
    def poll(cls, context):
        props = context.preferences.addons[__package__.split(".")[0]].preferences
        return props.draw == True
        
  
    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_draw.bl_idname)

        self.mesh = mesh 

  
    def draw_prepare(self, context):
        props = context.preferences.addons[__package__.split(".")[0]].preferences

        mesh = self.mesh
        if props.draw == True:
            mesh.hide = False
        else:
            mesh.hide = True """



class PS_OT_draw_mesh(Operator):
    bl_idname = "ps.draw_mesh"
    bl_label = "Draw Mesh Advance"


    def modal(self, context, event):
        settings = context.scene.polySource_set
        #props = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        
        if context.area:
            if context.area.type == 'VIEW_3D':
                context.area.tag_redraw()

               
                if settings.draw_advance == False:
                    bpy.types.SpaceView3D.draw_handler_remove(self._ps_mesh_draw, 'WINDOW')
                    return {'FINISHED'}
            

        else:
            settings.draw_advance = False
            bpy.types.SpaceView3D.draw_handler_remove(self._ps_mesh_draw, 'WINDOW')
            return {'FINISHED'}

        

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = ()
            self._ps_mesh_draw= bpy.types.SpaceView3D.draw_handler_add(mesh_draw_bgl, args, 'WINDOW', 'POST_VIEW')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Area Type Not 'VIEW_3D'")
            return {'CANCELLED'} 







classes = [
    PS_OT_draw_mesh,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)