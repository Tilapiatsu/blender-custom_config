import blf
import bpy

'''

    Copyright (c) 2019

    Jorge Hernández - Meléndez Saiz
    zebus3dream@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.


'''

bl_info = {
    "name": "ExtraInfo",
    "description": "Show Extra Information in Viewport",
    "author": "zebus3d",
    "version": (0, 0, 8),
    "blender": (2, 81, 0),
    "location": "View3D",
    "wiki_url": "https://github.com/zebus3d/ExtraInfo",
    "category": "3D View" 
}


font_info = {
    "font_id": 0,
    "handler": None,
}


def keep_proportions(new_min, new_max, ui_scale):
    # los valores en los que pondre el size del ui
    # para ir probando los new_min y new_max que funcionen bien con estos
    # valor de partida minimo
    old_min = 0.5
    # valor de partida maximo
    old_max = 2

    old_range = (old_max - old_min)
    old_value = ui_scale

    if old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)
        result = (((old_value - old_min) * new_range) / old_range) + new_min

    return result


# this is calculated every drawing pass of the viewport:
def draw_callback_px(self, context):

    display = []
    font_id = font_info["font_id"]
    
    ui_scale = bpy.context.preferences.view.ui_scale

    areas = list(bpy.context.window.screen.areas)
    regions = {}

    for a in areas:
        if a.type == "VIEW_3D":
            for r in a.regions:
                regions[r.type] = r

    active_tools_panel = regions["TOOLS"]
    n_panel = regions["UI"]

    left_margin = 20

    # horizonatl:
    # si esta colapsado el active tool es = 1:
    if active_tools_panel.width == 1:
        x_offset = left_margin * ui_scale
    else:
        # si las active tools esta a la izquierda y el panel n a la derecha:
        if active_tools_panel.alignment == "LEFT" and n_panel.alignment == "RIGHT":
            # x_offset = left_margin + active_tools_panel.width * ui_scale
            new_min = active_tools_panel.width + 12
            new_max = active_tools_panel.width + 40
            x_offset = keep_proportions(new_min, new_max, ui_scale)

        # si las active tools esta a la derecha y el panel n a la derecha:
        elif active_tools_panel.alignment == "RIGHT" and n_panel.alignment == "RIGHT":
            x_offset = left_margin * ui_scale

        # si el panel n esta a la izquierda y las active tools a la derecha:
        elif n_panel.alignment == "LEFT" and active_tools_panel.alignment == "RIGHT":
            # x_offset = left_margin + n_panel.width * ui_scale
            new_min = n_panel.width + 12
            new_max = n_panel.width + 40
            x_offset = keep_proportions(new_min, new_max, ui_scale)

        # si estan todas a la izquierda:
        elif n_panel.alignment == "LEFT" and active_tools_panel.alignment == "LEFT":
            # x_offset = left_margin + n_panel.width + active_tools_panel.width * ui_scale
            new_min = (n_panel.width + active_tools_panel.width) + 12
            new_max = (n_panel.width + active_tools_panel.width) + 40
            x_offset = keep_proportions(new_min, new_max, ui_scale)

    header_height = getattr(regions["HEADER"], 'height')
    window_height = getattr(regions["WINDOW"], 'height')

    # por si esta colapsado el header o no:
    # vertical:
    if header_height == 1:
        new_min = 35
        new_max = 130
        y_static_offest = keep_proportions(new_min, new_max, ui_scale)
    else:
        new_min = 50
        new_max = 180
        y_static_offest = keep_proportions(new_min, new_max, ui_scale)

    y_offset = window_height - y_static_offest



    font_size = int(12 * ui_scale)
    blf.size(font_id, font_size, 72)
    
    # shadows:
    # the level has to be 3, 5 o 0
    level = 5
    r = 0.0
    g = 0.0
    b = 0.0
    a = 0.9
    
    blf.enable(font_id , blf.SHADOW )
    blf.shadow(font_id, level, r, g, b, a)
    blf.shadow_offset(font_id, 1, -1)
    
    engines = {
        'BLENDER_EEVEE' : 'Eevee',
        'BLENDER_WORKBENCH' : 'Workbench',
        'CYCLES' : 'Cycles'
    }

    re = 'Engine: ' + engines.get(bpy.context.scene.render.engine)
    display.append(re)

    view_layer = bpy.context.view_layer
    stats = bpy.context.scene.statistics(view_layer).split("|")

    if bpy.context.mode == 'OBJECT':
        ss = stats[2:5]
        ss.append(stats[-2])
        stats = ss
    elif bpy.context.mode == 'EDIT_MESH':
        ss = stats[1:6]
        stats = ss
    elif bpy.context.mode == 'SCULPT':
        ss = stats[1:4]
        ss.append(stats[-2])
        stats = ss
    else:
        stats = []

    if len(stats) > 0:
        display = display + stats

    if engines.get(bpy.context.scene.render.engine) == 'Cycles':
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        if space.shading.type == 'RENDERED': 
            rendered = 20
        else:
            rendered = 0
    else:
        rendered = 0

    if bpy.context.space_data.overlay.show_overlays:
        if bpy.context.space_data.overlay.show_text:
            for counter, value in enumerate(display):
                # print(value)
                value = value.replace(" ","")
                value = value.replace(":",": ")
                # print(value)
                increment = (20*counter*ui_scale)
                blf.position(font_id, x_offset, y_offset - increment - rendered * ui_scale, 0)
                blf.draw(font_id, value)
    
    # fix de la sombra en el navigation simple y en los botones de preferencias de la izquierda.
    blf.disable(font_id, blf.SHADOW)

def init():
    font_info["font_id"] = 0
    # run every frame
    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


def register():
    init()


def unregister():
    pass


if __name__ == "__main__":
    register()
