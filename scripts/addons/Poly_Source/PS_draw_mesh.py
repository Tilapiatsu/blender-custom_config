import bpy
import bgl 
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, GizmoGroup, Gizmo
import bmesh

import mathutils





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

##########################################################################################################################################################
########################################################################## TEST ##########################################################################
vertex_shader = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    

    vec4 pos_view;
    
    in vec3 position;




    void main()
    {
        pos_view = view_mat * vec4(position, 1.0f);
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fragment_shader = '''
    uniform vec4 color;
    out vec4 gl_FragColor;

    void main()
    {
        gl_FragColor = vec4(color.xyz, color.w);
    }

'''
 

shader_uni = gpu.types.GPUShader(vertex_shader, fragment_shader)
##########################################################################################################################################################
##########################################################################################################################################################


from gpu.types import (
            GPUBatch,
            GPUVertBuf,
            GPUVertFormat,
            GPUIndexBuf,
        )



def mesh_draw_bgl(self, context):

    if context.active_object != None and context.active_object.select_get() and context.mode == 'EDIT_MESH':
        #start_time = time.time()
        #props = context.preferences.addons[__package__.split(".")[0]].preferences
        props = context.preferences.addons[__package__].preferences

        theme = context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size

        
        
        

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(props.edge_width)
        bgl.glPointSize(vertex_size + props.verts_size)
        bgl.glCullFace(bgl.GL_BACK)
        
        
        if props.xray_ret == False:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glEnable(bgl.GL_CULL_FACE)


        if props.line_smooth:
            bgl.glEnable(bgl.GL_LINE_SMOOTH)

        
        #bgl.glDepthRange(0, 0.99999)
        #bgl.glDepthFunc(600)
        bgl.glDepthMask(False)

        

        

        is_perspective = context.region_data.is_perspective
        if is_perspective:
            z_bias = props.z_bias / 350
        else:
            z_bias = 0.0


        shader.bind()
        



        view_mat = context.region_data.perspective_matrix
        shader.uniform_float("view_mat", view_mat)
        shader.uniform_float("Z_Bias", z_bias)
        
        

        """ shader_uni.bind()
        shader_uni.uniform_float("view_mat", view_mat)
        shader_uni.uniform_float("Z_Bias", z_bias)
        fmt = GPUVertFormat()
        pos_id = fmt.attr_add(id="position", comp_type='F32', len=3, fetch_mode='FLOAT') """
        
        
        
        #uniques = context.objects_in_mode_unique_data
        uniques = context.selected_objects
        for obj in uniques:
            """ depsgraph = context.evaluated_depsgraph_get()

            if len(obj.modifiers) > 0 : 
                depsgraph.update()


            object_eval = obj.evaluated_get(depsgraph) """
            #me = object_eval.to_mesh()


            

            


            me = obj.data
            mesh = bmesh.from_edit_mesh(me)



            if len(mesh.faces)<15000:
                # color
                g_vertex_color = props.vertex_color
                g_wire_edit_color = props.edge_color
                g_face_color = props.face_color

            
                
                vertex_co = [obj.matrix_world @ v.co for v in mesh.verts]


                select_color_i = (props.select_items_color.r, props.select_items_color.g, props.select_items_color.b, 1.0)


                loop_triangles = mesh.calc_loop_triangles()
                faces_indices = [[loop.vert.index for loop in looptris] for looptris in loop_triangles]

                face_col = [(g_face_color[0], g_face_color[1], g_face_color[2], props.opacity) for _ in range(len(mesh.verts))]
                FACES = batch_for_shader(shader, 'TRIS', {"position": vertex_co, "colorize": face_col}, indices=faces_indices)
                FACES.draw(shader)


           
        
               
                
                """ vbo = GPUVertBuf(len=len(vertex_co), format=fmt)
                vbo.attr_fill(id=pos_id, data=vertex_co)

                ind = GPUIndexBuf(type="TRIS", seq=faces_indices)
                FACES = GPUBatch(type="TRIS", buf=vbo, elem=ind)
                
                FACES.program_set(shader_uni)
                

                face_col = (g_face_color[0], g_face_color[1], g_face_color[2], props.opacity)
                shader_uni.uniform_float("color", face_col)
              
                FACES.draw() """

                








        
                edges_ind = [e.index for e in mesh.edges]
                edges_cord = [obj.matrix_world @ v.co for i in edges_ind for v in mesh.edges[i].verts]
                #print(edges_cord)

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



                """ ###  EDGES
               
                vbo = GPUVertBuf(len=len(edges_cord), format=fmt)
                vbo.attr_fill(id=pos_id, data=edges_cord)
                EDGES = GPUBatch(type="LINES", buf=vbo) 
                EDGES.program_set(shader_uni)


                edge_col = (g_wire_edit_color.r, g_wire_edit_color.g, g_wire_edit_color.b, 1.0)
                shader_uni.uniform_float("color", edge_col)
                EDGES.draw()


                ###  VERTS
                
                vbo = GPUVertBuf(len=len(vertex_co), format=fmt)
                vbo.attr_fill(id=pos_id, data=vertex_co)
                EDGES = GPUBatch(type="POINTS", buf=vbo) 
                EDGES.program_set(shader_uni)


                vert_col = (g_vertex_color.r, g_vertex_color.g, g_vertex_color.b, 1.0)
                shader_uni.uniform_float("color", edge_col)
                EDGES.draw() """

                
                EDGES = batch_for_shader(shader, 'LINES', {"position": edges_cord, "colorize": edge_col})
                VERTS = batch_for_shader(shader, 'POINTS', {"position": vertex_co, "colorize": vert_col}) 
            
                EDGES.draw(shader)
                if bpy.context.tool_settings.mesh_select_mode[0]:
                    VERTS.draw(shader)
                    
                    
                    
                    

                
            
            

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
        mesh_draw_bgl(self, context)

    def setup(self):
        self.use_draw_modal = True
        self.select = True
        self.hide_select = True
        #self.group = PS_GGT_draw_group.bl_idname """


""" def test_select(self, context, location):
    if context.area.type == 'VIEW_3D':
        context.area.tag_redraw()
    return -1 """



""" class PS_GGT_draw_group(GizmoGroup):
    
    bl_idname = "ps.draw_group"
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL'
 

    @classmethod
    def poll(cls, context):
        settings = context.scene.ps_set_
        return settings.retopo_mode == True
        

    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_draw.bl_idname)
        self.mesh = mesh 


    def draw_prepare(self, context):
        settings = context.scene.ps_set_
        #props = context.preferences.addons[__package__.split(".")[0]].preferences
        mesh = self.mesh
        if settings.retopo_mode == True:
            mesh.hide = False
        else:
            mesh.hide = True """


















class PS_OT_draw_mesh(Operator):
    bl_idname = "ps.draw_mesh"
    bl_label = "Draw Mesh Advance"


    def modal(self, context, event):
        settings = context.scene.ps_set_
        #props = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        
        
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()

               
        if settings.retopo_mode == False:
            bpy.types.SpaceView3D.draw_handler_remove(self._ps_mesh_draw, 'WINDOW')
            return {'FINISHED'}
            

    
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
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