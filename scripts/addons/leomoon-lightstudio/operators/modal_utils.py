import gpu, bgl, blf
from gpu_extras.batch import batch_for_shader
from mathutils import *
from math import pi, fmod, radians, sin, cos, atan2
from .. common import *
from . import *
import time
from copy import deepcopy

shader2Dcolor = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
shader2Dcolor.bind()

shader2Dtexture = gpu.shader.from_builtin('2D_IMAGE')
shader2Dtexture.bind()

vertex_shader = '''
    uniform mat4 ModelViewProjectionMatrix;

    /* Keep in sync with intern/opencolorio/gpu_shader_display_transform_vertex.glsl */
    in vec2 pos;
    in vec2 texCoord;
    out vec2 texCoord_interp;

    void main()
    {
        gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
        gl_Position.z = 1.0;
        texCoord_interp = texCoord;
    }
'''

fragment_shader = '''
    in vec2 texCoord_interp;
    out vec4 fragColor;

    uniform sampler2D image;

    void main()
    {
        fragColor = texture(image, texCoord_interp);
    }
'''

lightIconShader = gpu.types.GPUShader(vertex_shader, fragment_shader)
lightIconShader.bind()

class Rectangle:
    def __init__(self, start_point, width, height):
        self.point_lt = Vector((
            min(start_point.x, start_point.x+width),
            max(start_point.y, start_point.y+height),
            ))
        self.point_rb = Vector((
            max(start_point.x, start_point.x+width),
            min(start_point.y, start_point.y+height),
            ))

        self.rot = 0

    @property
    def loc(self):
        return (self.point_lt + self.point_rb)/2

    @loc.setter
    def loc(self, loc):
        d = loc - self.loc
        self.point_lt += d
        self.point_rb += d
    
    @property
    def width(self):
        return self.point_rb.x - self.point_lt.x

    @width.setter
    def width(self, width):
        d = width - self.width
        self.point_lt.x -= d/2
        self.point_rb.x = self.point_lt.x + width

    @property
    def height(self):
        return self.point_lt.y - self.point_rb.y

    @height.setter
    def height(self, height):
        d = height - self.height
        self.point_lt.y += d/2
        self.point_rb.y = self.point_lt.y - height

    def get_verts(self):
        def rotate(x1, y1, offset):
            x1 -= offset.x
            y1 -= offset.y
            x2 = cos(self.rot) * x1 - sin(self.rot) * y1
            y2 = sin(self.rot) * x1 + cos(self.rot) * y1
            x2 += offset.x
            y2 += offset.y
            return [x2, y2]
        
        loc = self.loc # prevent property from recomputing
        return (
            rotate(self.point_lt.x, self.point_lt.y, loc),
            rotate(self.point_lt.x, self.point_rb.y, loc),
            rotate(self.point_rb.x, self.point_lt.y, loc),
            rotate(self.point_rb.x, self.point_rb.y, loc),
        )

    def get_tex_coords(self):
        return ([0, 1], [0, 0], [1, 1], [1, 0])

    def move(self, loc_diff):
        rect = self.panel if hasattr(self, 'panel') else self

        new_loc = self.loc + loc_diff
        new_loc.x = clamp(rect.point_lt.x, new_loc.x, rect.point_rb.x)
        new_loc.y = clamp(rect.point_rb.y, new_loc.y, rect.point_lt.y)
        self.loc = new_loc

class Panel(Rectangle):
    def __init__(self, loc, width, height):
        super().__init__(loc, width, height)
        self.button_exit = Button(Vector((0,0)), 'X', 30)
        self.button_exit.function = lambda x: "FINISHED"

        self.button_send_to_bottom = Button(Vector((0,0)), 'Send to Bottom')
        def send_light_to_bottom(args):
            light = LightImage.selected_object
            lights = LightImage.lights
            lights.insert(0, lights.pop(lights.index(light)))
        self.button_send_to_bottom.function = send_light_to_bottom

        self._move_buttons()

    def _move_buttons(self):
        self.button_exit.loc = Vector((
            self.point_rb.x - self.button_exit.dimensions[0]/4,
            self.point_lt.y - self.button_exit.dimensions[1]/4,
        ))

        self.button_send_to_bottom.loc = Vector((
            self.point_lt.x + self.button_send_to_bottom.dimensions[0]/2,
            self.point_rb.y - self.button_exit.dimensions[1]/2,
        ))

    def draw(self):
        shader2Dcolor.uniform_float("color", (0.05, 0.05, 0.05, 1))
        batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": self.get_verts()}).draw(shader2Dcolor)

    def move(self, loc_diff):
        super().move(loc_diff)

        for l in LightImage.lights:
            l.update_visual_location()
        
        self._move_buttons()

class Button(Rectangle):
    buttons = []
    def __init__(self, loc, text, size=15):
        self.font_size = size
        self.font_color = (.25, .25, .25, 1)
        self.bg_color = (.5, .5, .5, 1)
        self.bg_color_selected = (.7, .7, .7, 1)
        self.font_id = len(Button.buttons)
        self.text = text
        blf.color(self.font_id, *self.font_color)
        blf.position(self.font_id, *loc, 0)
        blf.size(self.font_id, self.font_size, 72)
        self.dimensions = blf.dimensions(self.font_id, text)
        self.function = lambda args : None

        super().__init__(loc, self.dimensions[0]+5, self.dimensions[1]+5)
        Button.buttons.append(self)

    def draw(self, mouse_x, mouse_y):
        # draw something to refresh buffer?
        shader2Dcolor.uniform_float("color", (0, 0, 0, 0))
        batch_for_shader(shader2Dcolor, 'POINTS', {"pos": [(0,0), ]}).draw(shader2Dcolor)

        if is_in_rect(self, Vector((mouse_x, mouse_y))):
            shader2Dcolor.uniform_float("color", self.bg_color_selected)
        else:
            shader2Dcolor.uniform_float("color", self.bg_color)
        batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": self.get_verts()}).draw(shader2Dcolor)
        blf.size(self.font_id, self.font_size, 72)
        blf.position(self.font_id, self.point_lt.x + 2.5, self.point_rb.y + 2.5, 0)
        blf.draw(self.font_id, self.text)

    def click(self, args=None):
        return self.function(args)

view_layers = []

class Border(Rectangle):
    weight = 5

    def __init__(self, light_image, color):
        self.color = color
        self.light_image = light_image
        super().__init__(Vector((0, 0)), 100, 100)

    def draw(self):
        bleft = self.light_image.panel.point_lt[0]
        bright = self.light_image.panel.point_rb[0]
        lleft = self.light_image.point_lt[0]
        lright = self.light_image.point_rb[0]

        off = 0
        # is left overextending
        if lleft < bleft:
            off = lleft - bleft
        
        # is right overextending
        elif lright > bright:
            off = lright - bright

        verts = self.get_verts()
        if off < 0:
            verts2 = deepcopy(verts)
            verts[0][0] -= off - self.weight
            verts[1][0] = verts[0][0]

            verts2[0][0] = verts2[1][0] = self.light_image.panel.point_rb[0] + off - self.weight
            verts2[2][0] = verts2[3][0] = self.light_image.panel.point_rb[0]

            shader2Dcolor.uniform_float("color", self.color)
            batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": verts}).draw(shader2Dcolor)

            shader2Dcolor.uniform_float("color", self.color)
            batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": verts2}).draw(shader2Dcolor)
        elif off > 0:
            verts2 = deepcopy(verts)
            verts[2][0] -= off + self.weight
            verts[3][0] = verts[2][0]

            verts2[0][0] = verts2[1][0] = self.light_image.panel.point_lt[0]
            verts2[2][0] = verts2[3][0] = self.light_image.panel.point_lt[0] + off + self.weight

            shader2Dcolor.uniform_float("color", self.color)
            batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": verts}).draw(shader2Dcolor)

            shader2Dcolor.uniform_float("color", self.color)
            batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": verts2}).draw(shader2Dcolor)
        else:
            shader2Dcolor.uniform_float("color", self.color)
            batch_for_shader(shader2Dcolor, 'TRI_STRIP', {"pos": verts}).draw(shader2Dcolor)

    def get_verts(self):
        self.point_lt = self.light_image.point_lt.copy()
        self.point_rb = self.light_image.point_rb.copy()

        self.point_lt.x -= self.weight
        self.point_lt.y += self.weight

        self.point_rb.x += self.weight
        self.point_rb.y -= self.weight
        
        self.rot = self.light_image.rot

        return super().get_verts()


class LightImage(Rectangle):
    selected_object = None
    lights = []
    @classmethod
    def find_idx(cls, bls_light_collection):
        for idx, l in enumerate(cls.lights):
            if l._collection == bls_light_collection:
                return idx
        return -1
    @classmethod
    def remove(cls, bls_light_collection):
        del cls.lights[cls.find_idx(bls_light_collection)]

    def delete(self):
        del LightImage.lights[LightImage.lights.index(self)]
    
    @classmethod
    def refresh(cls):
        cls.selected_object = None
        for l in cls.lights:
            try:
                if l.update_from_bls():
                    l.update_visual_location()
            except ReferenceError:
                l.delete()
            
    
    default_size = 100
    @classmethod
    def change_default_size(cls, value):
        cls.default_size = value
        for l in cls.lights:
            l.width = value
            l.height = value
        
    def panel_loc_to_area_px_lt(self):
        panel_px_loc = Vector((self.panel.width * self.panel_loc.x, -self.panel.height * (1-self.panel_loc.y)))
        return panel_px_loc + self.panel.point_lt - Vector((LightImage.default_size*self._scale.y/2, LightImage.default_size*self._scale.z/2))
    
    def _update_panel_loc(self):
        self.panel_loc.x = (self._bls_rot.x + pi) % (2*pi) / (2*pi)
        self.panel_loc.y = fmod(self._bls_rot.y + pi/2, pi) / (pi)

    def update_from_bls(self):
        if self._bls_mesh.select_get():
            LightImage.selected_object = self

        updated = False
        if self._bls_rot != self._bls_actuator.rotation_euler:
            updated |= True
            self._bls_rot = self._bls_actuator.rotation_euler.copy()
        if self.rot != self._bls_mesh.rotation_euler.x:
            updated |= True
            self.rot = self._bls_mesh.rotation_euler.x
        if self._scale != self._bls_mesh.scale:
            updated |= True
            self._scale = self._bls_mesh.scale.copy()
            self.width = LightImage.default_size * self._scale.y
            self.height = LightImage.default_size * self._scale.z
        
        if updated:
            self._update_panel_loc()

        if self._image_path != self._bls_mesh.active_material.node_tree.nodes["Light Texture"].image.filepath:
            updated |= True
            self.image = self._bls_mesh.active_material.node_tree.nodes["Light Texture"].image
            self._image_path = self._bls_mesh.active_material.node_tree.nodes["Light Texture"].image.filepath
        # this should run when image changes but sometimes Blender looses images... so it's run every time to be safe
        if self.image.gl_load():
            raise Exception
        

        return updated

    def update_bls(self):
        self._bls_actuator.rotation_euler = self._bls_rot
        self._bls_mesh.rotation_euler.x = self.rot

    def __init__(self, context, panel, bls_light_collection):
        self.panel = panel
        self.__panel_loc = Vector((.5, .5))

        self._collection = bls_light_collection
        self._bls_mesh = [m for m in bls_light_collection.objects if m.name.startswith("BLS_LIGHT_MESH")][0]
        self._bls_actuator = self._bls_mesh.parent
        self._view_layer = find_view_layer(self._collection, context.view_layer.layer_collection)
        
        self._image_path = ""
        self._bls_rot = None
        self._scale = None

        super().__init__(Vector((0,0)), LightImage.default_size, LightImage.default_size)
        self.update_from_bls()
        self.update_visual_location()
        
        LightImage.lights.append(self)

        self.mute_border = Border(self, (.7, 0, 0, 1))
        self.select_border = Border(self, (.2, .9, .2, 1))
        self.select_border.weight = 2
    
    @property
    def mute(self):
        return self._view_layer.exclude
    
    @mute.setter
    def mute(self, value):
        self._view_layer.exclude = value

    @property
    def panel_loc(self):
        return self.__panel_loc
    
    @panel_loc.setter
    def panel_loc(self, pos):
        self.__panel_loc = pos
        self._bls_rot = Vector((
            (self.panel_loc.x -.5) * (2*pi),
            (self.panel_loc.y -.5) * (pi),
            self._bls_rot.z
        ))
        self.update_visual_location() # update self.loc

    def select(self):
        if self.mute:
            return
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self._bls_mesh
        self._bls_mesh.select_set(True)

    def is_mouse_over(self, mouse_x, mouse_y):
        if not (mouse_y <= self.point_lt[1] and mouse_y >= self.point_rb[1]):
            return False
        if not (mouse_x >= self.panel.point_lt[0] and mouse_x <= self.panel.point_rb[0]):
            return False
        if mouse_x >= self.point_lt[0] and mouse_x <= self.point_rb[0]:
            return True

        bleft = self.panel.point_lt[0]
        bright = self.panel.point_rb[0]
        lleft = self.point_lt[0]
        lright = self.point_rb[0]

        off = 0
        # is left overextending
        if lleft < bleft:
            off = lleft - bleft
            if mouse_x >= bright + off:
                return True
        
        # is right overextending
        elif lright > bright:
            off = lright - bright
            if mouse_x <= bleft + off:
                return True

        return False

    def draw(self):
        try:
            select = self._bls_mesh.select_get()
        except ReferenceError:
            return
        
        # draw something to refresh buffer?
        shader2Dcolor.uniform_float("color", (0, 0, 0, 0))
        batch_for_shader(shader2Dcolor, 'POINTS', {"pos": [(0,0), ]}).draw(shader2Dcolor)

        bleft = self.panel.point_lt[0]
        bright = self.panel.point_rb[0]
        lleft = self.point_lt[0]
        lright = self.point_rb[0]

        off = 0
        # is left overextending
        if lleft < bleft:
            off = lleft - bleft
        
        # is right overextending
        elif lright > bright:
            off = lright - bright

        uv_factor = abs(off / self.width)

        verts = self.get_verts()
        uv_coords = self.get_tex_coords()

        if self.mute:
            self.mute_border.draw()
        if select:
            self.select_border.draw()

        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.image.bindcode)
        lightIconShader.uniform_int("image", 0)

        if off < 0:
            verts2 = deepcopy(verts)
            verts[0][0] -= off
            verts[1][0] = verts[0][0]

            verts2[0][0] = verts2[1][0] = self.panel.point_rb[0] + off
            verts2[2][0] = verts2[3][0] = self.panel.point_rb[0]

            uv_coords2 = deepcopy(uv_coords)
            uv_coords[0][0] = uv_coords[1][0] = uv_factor
            uv_coords2[2][0] = uv_coords2[3][0] = uv_factor

            batch_for_shader(
                lightIconShader, 'TRI_STRIP',
                {
                    "pos": verts,
                    "texCoord": uv_coords,
                }
            ).draw(lightIconShader)

            batch_for_shader(
                lightIconShader, 'TRI_STRIP',
                {
                    "pos": verts2,
                    "texCoord": uv_coords2,
                }
            ).draw(lightIconShader)
        elif off > 0:
            verts2 = deepcopy(verts)
            verts[2][0] -= off
            verts[3][0] = verts[2][0]

            verts2[0][0] = verts2[1][0] = self.panel.point_lt[0]
            verts2[2][0] = verts2[3][0] = self.panel.point_lt[0] + off

            uv_coords2 = deepcopy(uv_coords)
            uv_coords[2][0] = uv_coords[3][0] = 1-uv_factor
            uv_coords2[0][0] = uv_coords2[1][0] = 1-uv_factor

            batch_for_shader(
                lightIconShader, 'TRI_STRIP',
                {
                    "pos": verts,
                    "texCoord": uv_coords,
                }
            ).draw(lightIconShader)

            batch_for_shader(
                lightIconShader, 'TRI_STRIP',
                {
                    "pos": verts2,
                    "texCoord": uv_coords2,
                }
            ).draw(lightIconShader)
        else:
            batch_for_shader(
                lightIconShader, 'TRI_STRIP',
                {
                    "pos": verts,
                    "texCoord": self.get_tex_coords(),
                }
            ).draw(lightIconShader)

    def update_visual_location(self):
        self.loc = self.panel_loc_to_area_px_lt() + Vector((self.width/2, self.height/2))

    def move(self, loc_diff):
        super().move(loc_diff)

        self.panel_loc = Vector((
            (self.loc.x-self.panel.loc.x) / self.panel.width +.5,
            clamp(0.0001, (self.loc.y-self.panel.loc.y) / self.panel.height +.5, 0.9999),
        ))

        self.update_bls()

def is_in_rect(rect, loc):
    return (loc.x >= rect.point_lt.x and loc.x <= rect.point_rb.x) and (loc.y >= rect.point_rb.y and loc.y <= rect.point_lt.y)

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

class ClickManager:
    def __init__(self):
        self.times = [0, 0, 0]
        self.objects = [None, None, None]
    
    def click(self, object):
        self.times.append(time.time())
        self.objects.append(object)
        if len(self.times) > 3:
            del self.times[0]
            del self.objects[0]
        
        if self.objects[0] == self.objects[1] == self.objects[2]:
            if self.times[2] - self.times[0] <= .5:
                return "TRIPLE"
        if self.objects[1] == self.objects[2]:
            if self.times[2] - self.times[1] <= .5:
                return "DOUBLE"

class MouseWidget:
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()
    
    def __init__(self):
        self._start_position = Vector((0, 0))
        self._end_position = Vector((0, 0))
        self._reference_end_position = Vector((0, 0))
        self._base_rotation = 0
        self.handler = None

        self.draw_guide = True

        self.allow_xy_keys = False
        self.x_key = False
        self.y_key = False

        self.continous = False

        self.allow_precision_mode = False
        self.precision_mode = False
        self.precision_offset = Vector((0,0))

    def invoke(self, context, event):
        mouse_x = event.mouse_x - context.area.x
        mouse_y = event.mouse_y - context.area.y

        self._start_position = Vector((self.mouse_x, self.mouse_y))
        self._end_position = Vector((mouse_x, mouse_y))
        self._reference_end_position = self._end_position
        vec = self._end_position - self._start_position
        self._base_rotation = atan2(vec.y, vec.x)

        self.handler = bpy.types.SpaceView3D.draw_handler_add(self._draw, (context, event,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

    def _cancel(self, context, event): pass
    def _finish(self, context, event): pass

    def modal(self, context, event):
        # print(event.type, event.value)
        if not context.area:
            self._unregister_handler()
            self._cancel(context, event)
            return {"CANCELLED"}

        if event.type in {"ESC", "RIGHTMOUSE"}:
            self._unregister_handler()
            self._cancel(context, event)
            return {'CANCELLED'}

        if event.type == "RET" or (not self.continous and event.type == "LEFTMOUSE"):
            self._unregister_handler()
            self._finish(context, event)
            return {'FINISHED'}

        if self.continous and event.value == "RELEASE" and event.type == "LEFTMOUSE":
            self._unregister_handler()
            self._finish(context, event)
            return {'FINISHED'}

        self.mouse_x = event.mouse_x - context.area.x
        self.mouse_y = event.mouse_y - context.area.y
        self._end_position = Vector((self.mouse_x, self.mouse_y))
        
        if self.allow_xy_keys:
            if event.value == "PRESS":
                if event.type == "X":
                    self.x_key = not self.x_key
                    self.y_key = False
                if event.type == "Y":
                    self.y_key = not self.y_key
                    self.x_key = False

        if self.allow_precision_mode and event.value == "PRESS" and event.type == "LEFT_SHIFT":
            self.precision_mode = True
            self._precision_mode_mid_stop = self._end_position.copy()
        elif self.allow_precision_mode and event.value == "RELEASE" and event.type == "LEFT_SHIFT" and self.precision_mode: #last condition in case when operator invoked with shift already pressed
            self.precision_mode = False
            self.precision_offset += self._end_position - self._precision_mode_mid_stop

        return self._modal(context, event)

    def __del__(self):
        self._unregister_handler()

    def _unregister_handler(self):
        try:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
        except ValueError:
            pass
    
    def length(self):
        return (self._start_position - self._reference_end_position - self.delta_vector()).length
    
    def delta_vector(self):
        if self.precision_mode:
            return self._precision_mode_mid_stop - self._reference_end_position - self.precision_offset*.9 + (self._end_position - self._precision_mode_mid_stop) * .1
        return self._end_position - self._reference_end_position - self.precision_offset*.9
    
    def delta_length_factor(self):
        return self.length() / ((self._start_position - self._reference_end_position).length)

    def angle(self):
        vec = self._reference_end_position - self._start_position + self.delta_vector() + self.precision_offset*.9
        return atan2(vec.y, vec.x) - self._base_rotation

    def _draw(self, context, event):
        # first draw to reset buffer
        shader2Dcolor.uniform_float("color", (.5, .5, .5, .5))
        batch_for_shader(shader2Dcolor, 'LINES', {"pos": ((0,0), (0,0))}).draw(shader2Dcolor)
        
        if self.draw_guide:
            shader2Dcolor.uniform_float("color", (.5, .5, .5, .5))
            batch_for_shader(shader2Dcolor, 'LINES', {"pos": ((self._start_position[:]), (self._end_position[:]))}).draw(shader2Dcolor)

        if self.allow_xy_keys:
            if self.x_key:
                shader2Dcolor.uniform_float("color", (1, 0, 0, .5))
                batch_for_shader(shader2Dcolor, 'LINES', {"pos": ((0, self._start_position.y), (context.area.width, self._start_position.y))}).draw(shader2Dcolor)
            elif self.y_key:
                shader2Dcolor.uniform_float("color", (0, 1, 0, .5))
                batch_for_shader(shader2Dcolor, 'LINES', {"pos": ((self._start_position.x, 0), (self._start_position.x, context.area.height))}).draw(shader2Dcolor)