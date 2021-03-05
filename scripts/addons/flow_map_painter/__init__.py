bl_info = {
    'name' : 'Flow Map Painter',
    'author' : 'Clemens Beute <feedback.clemensbeute@gmail.com>',
    'version' : (1, 2),
    'blender' : (2, 92, 0),
    'category' : 'Paint',
    'location' : 'Paint Brush Tool Panel',
    'description' : 'A brush tool for flow map painting. The brush gets the color of the painting direction',
    'warning' : '',
    'doc_url' : '',
}

import bpy, numpy, bmesh, mathutils
from bpy_extras import view3d_utils
from gpu_extras.presets import draw_circle_2d

# VARIABLES
circle = None
circle_pos = (0,0)
tri_obj = None
pressing = False

# FUNCTIONS
def lerp(mix, a, b):
    return (b - a) * mix + a

def remove_temp_obj():
    '''removes the temp object and data if it exists'''
    if bpy.data.meshes.get('FLOWMAP_temp_mesh'):
        bpy.data.meshes.remove(bpy.data.meshes['FLOWMAP_temp_mesh'])
    if bpy.data.objects.get('FLOWMAP_temp_obj'):
        bpy.data.objects.remove(bpy.data.objects['FLOWMAP_temp_obj'])

def triangulate_object(obj):
    '''triangulate incoming object and return it as a temporary copy'''

    template_ob = obj

    # first remove temp stuff, if it exists already
    remove_temp_obj()

    ob = template_ob.copy()
    ob.data = ob.data.copy()
    ob.modifiers.new('triangulate', 'TRIANGULATE')

    # need to be in scnene, for depsgraph to work apparently
    bpy.context.collection.objects.link(ob)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = ob.evaluated_get(depsgraph)
    mesh_from_eval = bpy.data.meshes.new_from_object(object_eval)
    ob.data = mesh_from_eval

    new_ob = bpy.data.objects.new(name='FLOWMAP_temp_obj', object_data=mesh_from_eval)
    bpy.context.collection.objects.link(new_ob)
    new_ob.matrix_world = template_ob.matrix_world

    # remove the depsgraph object    
    bpy.data.objects.remove(ob, do_unlink=True)
    
    # hide temp obj
    # new_ob.hide_viewport = True
    new_ob.hide_set(True)

    return new_ob

def get_uv_direction_three_d(context, area_pos, area_prev_pos):
    '''combine area_pos and previouse linetrace into direction color'''

    def line_trace_for_uv(context, area_pos):
        '''line trace into the scene, to find uv coordinates at the brush location at the object '''
        # get the context arguments
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = area_pos[0], area_pos[1]

        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + view_vector


        def obj_ray_cast(obj, matrix):
            '''Wrapper for ray casting that moves the ray into object space'''
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj

            # cast the ray
            success, location, normal, face_index = obj.ray_cast(origin=ray_origin_obj, direction=ray_direction_obj, distance=bpy.context.scene.trace_distance)

            if success:
                return location, normal, face_index
            else:
                return None, None, None


        def pos_to_uv_co(obj, matrix_world, world_pos, face_index):
            '''translate 3D postion on a mesh into uv coordinates'''
            face_verts = []
            uv_verts = []

            # uv's are stored in loops
            face = obj.data.polygons[face_index]
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uv_coords = obj.data.uv_layers.active.data[loop_idx].uv

                face_verts.append(matrix_world @ obj.data.vertices[vert_idx].co)
                uv_verts.append(uv_coords.to_3d())

                # print(f'face idx {face.index}, vert idx {vert_idx}, vert coords {ob.data.vertices[vert_idx].co},uv coords {uv_coords.x} {uv_coords.y}')


            # print("world_pos: ", world_pos)
            # print("face_verts: ", face_verts[0], face_verts[1], face_verts[2])
            # print("uv_verts: ", uv_verts[0], uv_verts[1], uv_verts[2])

            # point, tri_a1, tri_a2, tri_a3, tri_b1, tri_b2, tri_b3
            uv_co = mathutils.geometry.barycentric_transform(
                world_pos,
                face_verts[0],
                face_verts[1],
                face_verts[2],
                uv_verts[0],
                uv_verts[1],
                uv_verts[2])

            return uv_co
        global tri_obj
        obj = bpy.context.active_object
        matrix = obj.matrix_world.copy()
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj=tri_obj, matrix=matrix)
            if hit is not None:
                hit_world = matrix @ hit
                # scene.cursor.location = hit_world

                uv_co = pos_to_uv_co(obj=tri_obj, matrix_world=obj.matrix_world, world_pos=hit_world, face_index=face_index)
            else:
                uv_co = None

        return uv_co

    # finally get the uv coordinates
    uv_pos = line_trace_for_uv(context, area_pos)
    uv_prev_pos = line_trace_for_uv(context, area_prev_pos)

    # if uv_pos == None:
    #     uv_pos = (0,0)
    # if uv_prev_pos == None:
    #     uv_prev_pos = (0,0)
    if uv_pos == None or uv_prev_pos == None:
        return None
    else:
        # convert to numpy array for further math
        uv_pos = numpy.array([uv_pos[0],uv_pos[1]])
        uv_prev_pos = numpy.array([uv_prev_pos[0],uv_prev_pos[1]])

        # calculate direction vector and normalize it
        uv_direction_vector = uv_pos - uv_prev_pos
        norm_factor = numpy.linalg.norm(uv_direction_vector)
        if norm_factor == 0:
            return None
        else:
            norm_uv_direction_vector = uv_direction_vector / norm_factor
        
            # map the range to the color range, so 0.5 ist the middle
            color_range_vector = (norm_uv_direction_vector + 1) * 0.5
            direction_color = [color_range_vector[0], color_range_vector[1], 0]

            # return [uv_pos[0], uv_pos[1], 0]
            return direction_color

def paint_a_dot(area_type, mouse_position, event):
    '''paint one dot | works 2D, as well as 3D'''
    if bpy.context.area.type == area_type:
        area_position_x = bpy.context.area.x
        area_position_y = bpy.context.area.y

        pressure = bpy.context.scene.tool_settings.unified_paint_settings.use_unified_strength
        if bpy.data.brushes["TexDraw"].use_pressure_strength == True:
            pressure = pressure * event.pressure

        size = bpy.context.scene.tool_settings.unified_paint_settings.size
        if bpy.data.brushes["TexDraw"].use_pressure_size == True:
            size = size * event.pressure

        stroke = [
        {
            'name' : 'test',
            'is_start' : True,
            'location' : (0, 0, 0),
            'mouse' : (mouse_position[0] - area_position_x, mouse_position[1] - area_position_y),
            'mouse_event' : (mouse_position[0] - area_position_x, mouse_position[1] - area_position_y),
            'pen_flip' : False,
            'pressure' : pressure,
            'size' : size,
            'time' : 1,
            'x_tilt' : 0,
            'y_tilt' : 0,
        }
        ]

        bpy.ops.paint.image_paint(stroke=stroke, mode='NORMAL')

# OPERATORS
class FLOWMAP_OT_flow_map_paint_two_d(bpy.types.Operator):
    '''2D Paint Flowmap -> mouse movement gets translated directly to UV direction vector'''
    bl_idname = 'flowmap.flow_map_paint_two_d'
    bl_label = 'Flowmap 2D Paint Mode'

    furthest_position = numpy.array([0,0])
    mouse_prev_position = (0,0)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        context.area.tag_redraw()

        global circle
        global circle_pos
        global pressing

        # this is necessary, to find out if left mouse is pressed down (so no other keypress ist taken into account to trigger painting)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # set first position of stroke
            self.furthest_position = numpy.array([event.mouse_x, event.mouse_y])
            pressing = True
            
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            pressing = False


        if event.type == 'MOUSEMOVE' or event.type == 'LEFTMOUSE':
            # get mouse positions
            mouse_position = numpy.array([event.mouse_x, event.mouse_y])

            # if mouse has traveled enough distance and mouse is pressed, draw a dot
            distance = numpy.linalg.norm(self.furthest_position - mouse_position)
            if distance >= bpy.context.scene.brush_spacing:
                # reset threshold
                self.furthest_position = mouse_position

                # calculate direction vector and normalize it
                mouse_direction_vector = mouse_position - self.mouse_prev_position
                norm_factor = numpy.linalg.norm(mouse_direction_vector)
                if norm_factor == 0:
                    norm_mouse_direction_vector = numpy.array([0,0])
                else:
                    norm_mouse_direction_vector = mouse_direction_vector / norm_factor
                
                # map the range to the color range, so 0.5 ist the middle
                color_range_vector = (norm_mouse_direction_vector + 1) * 0.5
                direction_color = [color_range_vector[0], color_range_vector[1], 0]

                # set paint brush color, but check for nan first (fucked value, when direction didnt work)
                if any(numpy.isnan(val) for val in direction_color):
                    pass
                else:
                    bpy.context.scene.tool_settings.unified_paint_settings.color = direction_color

                if pressing:
                    # paint the actual dots with the selected brush spacing
                    # if mouse moved more than double of the brush_spacing -> draw substeps
                    substeps_float = distance / bpy.context.scene.brush_spacing
                    substeps_int = int(substeps_float)
                    if distance > 2 * bpy.context.scene.brush_spacing:
                        # substep_count = substeps_int
                        substep_count = substeps_int
                        while substep_count > 0:
                            # lerp_mix = 1 / (substeps_int + 1) * substep_count
                            lerp_mix = 1 / (substeps_int) * substep_count
                            lerp_paint_position = numpy.array([lerp(lerp_mix, self.mouse_prev_position[0], mouse_position[0]), lerp(lerp_mix, self.mouse_prev_position[1], mouse_position[1])])
                            paint_a_dot(area_type='IMAGE_EDITOR', mouse_position=lerp_paint_position, event=event)
                            substep_count = substep_count - 1
                        
                    else: 
                        paint_a_dot(area_type='IMAGE_EDITOR', mouse_position=mouse_position, event=event)
         
                self.mouse_prev_position = mouse_position
                

            # remove circle
            if circle:
                bpy.types.SpaceImageEditor.draw_handler_remove(circle, 'WINDOW')
                circle = None

            circle_pos = (event.mouse_region_x, event.mouse_region_y)

            # draw circle
            def draw():
                global circle_pos
                pos = circle_pos
                brush_col = bpy.context.scene.tool_settings.unified_paint_settings.color
                col = (brush_col[0], brush_col[1], 0, 1)

                size = bpy.context.scene.tool_settings.unified_paint_settings.size * bpy.context.space_data.zoom[0]

                draw_circle_2d(pos, col, size)

            circle = bpy.types.SpaceImageEditor.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')

            return {'RUNNING_MODAL'}

        if event.type == 'ESC':
            # print('stop')
            bpy.context.scene.tool_settings.unified_paint_settings.color = (0.5, 0.5, 0.5)
            # remove circle
            if circle:
                bpy.types.SpaceImageEditor.draw_handler_remove(circle, 'WINDOW')
                circle = None
            context.area.tag_redraw()
            return {'FINISHED'}

        # return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        # turn on unified settings (so its easier to get values for 2D and 3D paint)
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = True
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_strength = True
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_size = True
        bpy.context.window.cursor_set("PAINT_CROSS")
        return {'RUNNING_MODAL'}

class FLOWMAP_OT_flow_map_paint_three_d(bpy.types.Operator):
    '''3D Paint Flowmap -> mouse position -> 3D position on face -> UV coordinate -> UV direction vector'''
    bl_idname = 'flowmap.flow_map_paint_three_d'
    bl_label = 'Flowmap 3D Paint Mode'

    furthest_position = numpy.array([0,0])
    mouse_prev_position = (0,0)
    
    def modal(self, context: bpy.types.Context, event: bpy.types.Event):  
        context.area.tag_redraw()

        global circle
        global circle_pos
        global pressing

        # this is necessary, to find out if left mouse is pressed down (so no other keypress ist taken into account to trigger painting)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # set first position of stroke
            self.furthest_position = numpy.array([event.mouse_x, event.mouse_y])
            pressing = True
            
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            pressing = False
    

        if event.type == 'MOUSEMOVE' or event.type == 'LEFTMOUSE':
            # get mouse positions
            mouse_position = numpy.array([event.mouse_x, event.mouse_y])

            # if bpy.context.area.type == 'VIEW_3D':

            # get area position
            area_position_x = bpy.context.area.x
            area_position_y = bpy.context.area.y

            # get area mouse positions
            area_pos = (mouse_position[0] - area_position_x, mouse_position[1] - area_position_y)
            area_prev_pos = (self.mouse_prev_position[0] - area_position_x, self.mouse_prev_position[1] - area_position_y)

            # if mouse has traveled enough distance and mouse is pressed, get color, draw a dot
            distance = numpy.linalg.norm(self.furthest_position - mouse_position)               
            if distance >= bpy.context.scene.brush_spacing:
                # reset threshold
                self.furthest_position = mouse_position

                # finding the direction vector, from UV Coordinates, from 3D location
                direction_color = get_uv_direction_three_d(context, area_pos, area_prev_pos)

                # set paint brush color, but check for nan first (fucked value, when direction didnt work)
                if not direction_color == None:
                    if not any(numpy.isnan(val) for val in direction_color):
                        bpy.context.scene.tool_settings.unified_paint_settings.color = direction_color

                if pressing:
                    # paint the actual dots with the selected brush spacing
                    # if mouse moved more than double of the brush_spacing -> draw substeps
                    substeps_float = distance / bpy.context.scene.brush_spacing
                    substeps_int = int(substeps_float)
                    if distance > 2 * bpy.context.scene.brush_spacing:
                        # substep_count = substeps_int
                        substep_count = substeps_int
                        while substep_count > 0:
                            # lerp_mix = 1 / (substeps_int + 1) * substep_count
                            lerp_mix = 1 / (substeps_int) * substep_count
                            lerp_paint_position = numpy.array([lerp(lerp_mix, self.mouse_prev_position[0], mouse_position[0]), lerp(lerp_mix, self.mouse_prev_position[1], mouse_position[1])])
                            paint_a_dot(area_type='VIEW_3D', mouse_position=lerp_paint_position, event=event)
                            substep_count = substep_count - 1
                        
                    else: 
                        paint_a_dot(area_type='VIEW_3D', mouse_position=mouse_position, event=event)

                self.mouse_prev_position = mouse_position

            # remove circle
            if circle:
                bpy.types.SpaceView3D.draw_handler_remove(circle, 'WINDOW')
                circle = None

            circle_pos = (event.mouse_region_x, event.mouse_region_y)

            # draw circle
            def draw():
                global circle_pos
                pos = circle_pos
                brush_col = bpy.context.scene.tool_settings.unified_paint_settings.color
                col = (brush_col[0], brush_col[1], 0, 1)
                size = bpy.context.scene.tool_settings.unified_paint_settings.size

                draw_circle_2d(pos, col, size)

            circle = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')

            return {'RUNNING_MODAL'}


        if event.type == 'ESC':
            # clean brush color from nan shit
            bpy.context.scene.tool_settings.unified_paint_settings.color = (0.5, 0.5, 0.5)
            # remove circle
            if circle:
                bpy.types.SpaceView3D.draw_handler_remove(circle, 'WINDOW')
                context.area.tag_redraw()
                circle = None
            context.area.tag_redraw()
            remove_temp_obj()
            return {'FINISHED'}

        # return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        # turn on unified settings (so its easier to get values for 2D and 3D paint)
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = True
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_strength = True
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_size = True
        global tri_obj
        tri_obj = triangulate_object(obj=bpy.context.active_object)
        bpy.context.window.cursor_set("PAINT_CROSS")
        return {'RUNNING_MODAL'}


# UI (PANELS)
class FLOWMAP_PT_flow_map_paint_two_d(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = '2D Flowmap Paint'
    bl_context = '.imagepaint_2d'

    def draw(self, context):
        self.layout.label(text="ESC = Exit Mode")

        row = self.layout.row()
        row.label(icon='ONIONSKIN_ON')
        row.prop(bpy.context.scene, "brush_spacing")

        self.layout.operator(
            'flowmap.flow_map_paint_two_d',
            text='Flowmap 2D Paint Mode',
            icon='ANIM_DATA'
        )
        
class FLOWMAP_PT_flow_map_paint_three_d(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = '3D Flowmap Paint'
    bl_context = 'imagepaint'

    def draw(self, context):
        self.layout.label(text="ESC = Exit Mode")

        row = self.layout.row()
        row.label(icon='ONIONSKIN_ON')
        row.prop(bpy.context.scene, "brush_spacing")

        row = self.layout.row()
        row.label(icon='CON_TRACKTO')
        row.prop(bpy.context.scene, "trace_distance")

        self.layout.operator(
            'flowmap.flow_map_paint_three_d',
            text='Flowmap 3D Paint Mode',
            icon='ANIM_DATA'
        )

def register():
    # VARIABLES
    bpy.types.Scene.brush_spacing = bpy.props.FloatProperty(
        name='brush spacing',
        description='How much has the mouse to travel, bevor a new stroke is painted?',
        default=20,
        min=0.1
        )

    bpy.types.Scene.trace_distance = bpy.props.FloatProperty(
        name='trace distance',
        description='How deep reaches your object into the scene?',
        default=1000
        )

    # OPERATORS
    bpy.utils.register_class(FLOWMAP_OT_flow_map_paint_two_d)
    bpy.utils.register_class(FLOWMAP_OT_flow_map_paint_three_d)

    # PANELS
    bpy.utils.register_class(FLOWMAP_PT_flow_map_paint_two_d)
    bpy.utils.register_class(FLOWMAP_PT_flow_map_paint_three_d)

def unregister():
    # VARIABLES
    del bpy.types.Scene.brush_spacing
    del bpy.types.Scene.trace_distance

    # OPERATORS
    bpy.utils.unregister_class(FLOWMAP_OT_flow_map_paint_two_d)
    bpy.utils.unregister_class(FLOWMAP_OT_flow_map_paint_three_d)
    
    # PANELS
    bpy.utils.unregister_class(FLOWMAP_PT_flow_map_paint_two_d)
    bpy.utils.unregister_class(FLOWMAP_PT_flow_map_paint_three_d)
