import bpy
from bpy.types import Operator

import bgl
import blf

import bmesh

import gpu
from gpu_extras.batch import batch_for_shader

import mathutils
import math
from ..api.armature_utils import create_softMod_armature
from mathutils.geometry import intersect_line_plane
from  ..api.object_handlers import GpHandler, MeshHandler, LatticeHandler
from bpy_extras.view3d_utils import (
    region_2d_to_vector_3d,
    region_2d_to_origin_3d,
    location_3d_to_region_2d,
)

class OT_Create_SoftMod_operator(Operator):
    bl_idname = "object.create_softmod_op"
    bl_label = "Soft mod operator"
    bl_description = "Operator for creating softMods"
    bl_options = {'REGISTER'}
    	
    def __init__(self):
        self.mouse_origins_coordinates=None
        self.circle_3d_origins =None
        self.circle_3d_normal = None
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event  = None
        self.mouse_vert = None
        self.offset = 0.02
        self.active_object=None

        self.circle_2d_origins=None
        self.vertices = []
        self.create_batch()

        self.mesh_handler = None
        self.gp_handler = None
        self.lattice_handler = None
        self.bmesh = None
                
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and context.active_object.type in {'MESH'}
                and context.active_object.mode == 'OBJECT')

    def invoke(self, context, event):


        # checking if anything slipped out of poll
        if context.active_object.type not in {'MESH'}:
            return{"CANCELLED"}

        self.active_object = context.active_object
        args = (self, context)                   
        self.register_handlers(args, context)


        context.window_manager.modal_handler_add(self)

        if self.active_object.type == "MESH":
            self.mesh_handler = MeshHandler(context, self.active_object)

        elif self.active_object.type == "LATTICE":
            self.lattice_handler = LatticeHandler (context , self.active_object)
        else:
            self.gp_handler=GpHandler(context, self.active_object)
            self.gp_handler.turn_all_mods_off()

        return {"RUNNING_MODAL"}


    def register_handlers(self, args, context):
        self.draw_handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, "WINDOW", "POST_VIEW")

        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")

        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        
    def unregister_handlers(self, context):
        
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3d, "WINDOW")
        if self.gp_handler:
            self.gp_handler.turn_all_mods_on()
        
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event  = None
        self.mesh_handler=None
        self.gp_handler=None
        self.lattice_handler = None

    def get_origin_and_direction(self, event, context, mouse_coord=None):
        region    = context.region
        region_3d = context.space_data.region_3d
        if not mouse_coord:
            mouse_coord = (event.mouse_region_x, event.mouse_region_y)

        origin    = region_2d_to_origin_3d(region, region_3d, mouse_coord)
        direction = region_2d_to_vector_3d(region, region_3d, mouse_coord)

        return origin, direction

    def get_mouse_3d_on_mesh(self, event, context):

        if self.active_object.type =="MESH":
            origin, direction = self.get_origin_and_direction(event, context)
            hit, normal = self.mesh_handler.get_point_on_mesh(origin, direction, self.offset)

        elif self.active_object.type=="LATTICE":
            mouse_coord = (event.mouse_region_x , event.mouse_region_y, 0.0)
            hit = self.lattice_handler.find_2d(mouse_coord)
            hit =hit.co


        else:
            mouse_coord = (event.mouse_region_x , event.mouse_region_y, 0.0)
            hit = self.gp_handler.find_2d(mouse_coord)
            hit =hit.co


        print("\n###################\nHit is: {}\n###################\n".format(hit))
        return hit


    def get_mouse_circle_on_mesh(self,event, context):

        # let's get the radius
        radius_mouse_coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        radius=(radius_mouse_coord - self.mouse_origins_coordinates).magnitude
        offset= self.mouse_origins_coordinates

        circle_2d_points = self.vertex_circle(segments=300,radius=radius, offset=offset)
        #projecting points on mesh
        circle_3d_points=[]
        self.plane_origin = self.circle_3d_origins
        for point_2d in circle_2d_points:
            origin, direction = self.get_origin_and_direction(event, context, mouse_coord=(point_2d.x,point_2d.y))
            hit = self.get_point_on_plane (origin , direction)
            circle_3d_points.append(hit)

        return circle_3d_points


    def get_point_on_plane(self, origin, direction):
        hit= intersect_line_plane(origin, origin + direction,
        self.plane_origin, direction)
        #print("plane on point is:",hit)
        return hit


    def vertex_circle(self,segments,radius, offset=mathutils.Vector((0.0,0.0))):
        """ Return a ring of vertices """
        verts = []
        for i in range(segments):
            angle = (math.pi*2) * i / segments
            verts.append(mathutils.Vector((math.cos(angle)*radius, math.sin(angle)*radius))+offset)
        return verts



    def get_mouse_3d_on_plane(self, event, context):
        
        origin, direction = self.get_origin_and_direction(event, context)
               
        # get the intersection point on infinite plane
        return self.get_point_on_plane(origin, direction)
            
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
                               
        if event.type in {"ESC"}:
            self.unregister_handlers(context)
            return {'CANCELLED'}


        if event.type == "MOUSEMOVE" or event.type == "MOUSEROTATE":
            
            if len(self.vertices) > 0:
                points = self.get_mouse_circle_on_mesh(event, context)
                self.create_batch(points=points)
        
        if event.value == "PRESS":

            if event.type == "RIGHTMOUSE":
                self.unregister_handlers (context)
                return {'CANCELLED'}
            # Left mouse button pressed            
            if event.type == "LEFTMOUSE":
                if len(self.vertices) == 0:
                    vertex = self.get_mouse_3d_on_mesh(event, context)
                    self.mouse_origins_coordinates = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
                    if vertex:
                        self.circle_3d_origins = vertex
                        print("Circle origin plane is: ", self.circle_3d_origins)
                else:
                    vertex = self.get_mouse_3d_on_plane(event, context)
                    #print("second click vertex", vertex)
                    

                if vertex is not None: 
                    self.vertices.append(vertex)

                    # self.create_batch()

                if len(self.vertices)==2:
                    
                    map = self.create_soft_mod(context)
                    self.unregister_handlers(context)
                    return {'FINISHED'}


                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}


    def create_soft_mod(self, context):
        surf_falloff = context.scene.soft_mod.surf_falloff
        active= context.active_object
        selection = context.selected_objects
        start = mathutils.Vector (self.vertices[0])
        if len(selection) > 1:
            for selected in selection:
                if not selected == active:
                    #print("Getting the pivot point from :".format(selected.name))
                    pivot_matrix = selected.matrix_world
                    widget_position = pivot_matrix.decompose()[0]
                    break
        else:
            widget_position = start
        end = mathutils.Vector(self.vertices[1])
        radius = (end - start).magnitude
        print("Radius is: ", radius)



        if self.mesh_handler:
            nearest = self.mesh_handler.kdtree.find(start)
            #points_in_range = self.mesh_handler.calculate_map(start, radius, surf_falloff)
            create_softMod_armature(name=active.name,object_handler=self.mesh_handler, radius=radius,
                                    active_object=active, location=start, widget_position=widget_position )

        elif self.lattice_handler:
            nearest = self.lattice_handler.kdtree_3d.find (start)
            #points_in_range = self.lattice_handler.calculate_map (start , radius)
            create_softMod_armature(name=active.name,object_handler=self.lattice_handler, radius=radius,
                                    active_object=active, location=start,widget_position=widget_position )
        else:
            nearest = self.gp_handler.kdtree_3d.find (start)
            #points_in_range = self.gp_handler.calculate_map (start , radius, surf_falloff)
            create_softMod_armature(name=active.name,object_handler=self.gp_handler, radius=radius,
                                    active_object=active, location=start, widget_position=widget_position )

        return True

    def finish(self):
        self.unregister_handlers(context)
        return {"FINISHED"}

    def create_batch(self, points=None):

        if not points:
            points = self.vertices.copy()
        
        if self.mouse_vert is not None:
            points.append(self.mouse_vert)
                    
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        
        self.batch = batch_for_shader(self.shader, 'LINES', 
        {"pos": points})
        # self.shader.uniform_float("color", (1, 1, 1, 1))

	# Draw handler to paint in pixels
    def draw_callback_2d(self, op, context):
        # Draw text to indicate that draw mode is active
        region = context.region
        text = "- Softmod Mode-"

        xt = int(region.width / 2.0)
        
        blf.size(0, 24, 60)
        blf.position(0, xt - blf.dimensions(0, text)[0] / 2, 60 , 0)
        blf.draw(0, text) 

    # Draw handler to paint onto the screen
    def draw_callback_3d(self, op, context):
        # Draw lines
        bgl.glLineWidth(2)
        self.shader.bind()
        self.shader.uniform_float("color", (0.8, 0.8, 0.8, 1.0))
        self.batch.draw(self.shader)