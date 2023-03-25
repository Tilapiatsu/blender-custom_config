import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
# from bpy_extras.view3d_utils import location_3d_to_region_2d
from .help_text import helpstring_common, helpstring_box, helpstring_cylinder, helpstring_sphere, helpstring_torus


mouseXoffset = 40


def draw_callback_transform(self, op, context, _uidpi, _uifactor, _addon_prefs):
    pass


def draw_callback_cube(self, op, context, _uidpi, _uifactor, _addon_prefs):
    blf.size(0, _addon_prefs.text_size_int, _uidpi)
    DrawHelp(helpstring_box, _uifactor, _addon_prefs, op)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    else:
        BoolDraw(op.mouse_pos, -60, op.isOriented, "Align", "Oriented", "Axis", _uifactor, _addon_prefs)
        HitFilterDraw(op.object_ignorebehind, op.mouse_pos, -40, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, -20, op.qObject.isFlat, "Mesh", "Plane", "Cube", _uifactor, _addon_prefs)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor, _addon_prefs)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 40, _uifactor, _addon_prefs)


def draw_callback_cylinder(self, op, context, _uidpi, _uifactor, _addon_prefs):
    blf.size(0, _addon_prefs.text_size_int, _uidpi)
    DrawHelp(helpstring_cylinder, _uifactor, _addon_prefs, op)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    elif op.segkeyHold:
        SliderDraw(op, context, op.qObject.meshSegments)

    else:
        BoolDraw(op.mouse_pos, -60, op.isOriented, "Align", "Oriented", "Axis", _uifactor, _addon_prefs)
        HitFilterDraw(op.object_ignorebehind, op.mouse_pos, -40, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, -20, op.qObject.isFlat, "Mesh", "Circle", "Cylinder", _uifactor, _addon_prefs)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor, _addon_prefs)
        NumberDraw(op.meshSegments, op.mouse_pos, "Segments", 40, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 60, op.qObject.isSmooth, "Shading", "Smooth", "Flat", _uifactor, _addon_prefs)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 80, _uifactor, _addon_prefs)


def draw_callback_torus(self, op, context, _uidpi, _uifactor, _addon_prefs):
    blf.size(0, _addon_prefs.text_size_int, _uidpi)
    DrawHelp(helpstring_torus, _uifactor, _addon_prefs, op)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    elif op.segkeyHold:
        SliderDraw(op, context, op.qObject.meshSegments)

    else:
        BoolDraw(op.mouse_pos, -40, op.isOriented, "Align", "Oriented", "Axis", _uifactor, _addon_prefs)
        HitFilterDraw(op.object_ignorebehind, op.mouse_pos, -20, True, _uifactor, _addon_prefs)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor, _addon_prefs)
        NumberDraw(op.meshSegments, op.mouse_pos, "Segments", 40, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 60, op.qObject.isSmooth, "Shading", "Smooth", "Flat", _uifactor, _addon_prefs)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 80, _uifactor, _addon_prefs)


def draw_callback_sphere(self, op, context, _uidpi, _uifactor, _addon_prefs):
    blf.size(0, _addon_prefs.text_size_int, _uidpi)
    DrawHelp(helpstring_sphere, _uifactor, _addon_prefs, op)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    elif op.segkeyHold:
        SliderDraw(op, context, op.qObject.meshSegments)

    else:
        BoolDraw(op.mouse_pos, -40, op.isOriented, "Align", "Oriented", "Axis", _uifactor, _addon_prefs)
        HitFilterDraw(op.object_ignorebehind, op.mouse_pos, -20, True, _uifactor, _addon_prefs)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor, _addon_prefs)
        NumberDraw(op.meshSegments, op.mouse_pos, "Segments", 40, _uifactor, _addon_prefs)
        BoolDraw(op.mouse_pos, 60, op.qObject.isSmooth, "Shading", "Smooth", "Flat", _uifactor, _addon_prefs)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 80, _uifactor, _addon_prefs)


def DrawHelp(htext, _uifactor, _addon_prefs, _op):
    textsize = 14
    # get leftbottom corner
    offset = textsize + 40
    columnoffs = 320 * _uifactor
    col_header = _addon_prefs.header_color
    col_text = _addon_prefs.text_color
    col_hk = _addon_prefs.hotkey_color

    if _op.isHelpDraw:
        # draw common help
        for line in reversed(helpstring_common):
            if line[1] == "SEP":
                offset += 20 * _uifactor
            elif line[1] == "HEADER":
                # draw header
                blf.color(0, col_header[0], col_header[1], col_header[2], col_header[3])
                blf.position(0, 60 * _uifactor, offset, 0)
                blf.draw(0, line[0])
                offset += 30 * _uifactor
            else:
                # draw left col
                blf.color(0, col_text[0], col_text[1], col_text[2], col_text[3])
                blf.position(0, 60 * _uifactor, offset, 0)
                blf.draw(0, line[0])
                # draw right col
                blf.color(0, col_hk[0], col_hk[1], col_hk[2], col_hk[3])
                textdim = blf.dimensions(0, line[1])
                coloffset = columnoffs - textdim[0]
                blf.position(0, coloffset, offset, 0)
                blf.draw(0, line[1])
                offset += 20 * _uifactor
        # draw operator specific help
        for line in reversed(htext):
            if line[1] == "SEP":
                offset += 20 * _uifactor
            elif line[1] == "HEADER":
                # draw header
                blf.color(0, col_header[0], col_header[1], col_header[2], col_header[3])
                blf.position(0, 60 * _uifactor, offset, 0)
                blf.draw(0, line[0])
                offset += 30 * _uifactor
            else:
                # draw left col
                blf.color(0, col_text[0], col_text[1], col_text[2], col_text[3])
                blf.position(0, 60 * _uifactor, offset, 0)
                blf.draw(0, line[0])
                # draw right col
                blf.color(0, col_hk[0], col_hk[1], col_hk[2], col_hk[3])
                textdim = blf.dimensions(0, line[1])
                coloffset = columnoffs - textdim[0]
                blf.position(0, coloffset, offset, 0)
                blf.draw(0, line[1])
                offset += 20 * _uifactor
    else:
        # draw left col
        blf.color(0, col_text[0], col_text[1], col_text[2], col_text[3])
        blf.position(0, 60 * _uifactor, offset, 0)
        blf.draw(0, "Show Help")
        # draw right col
        blf.color(0, col_hk[0], col_hk[1], col_hk[2], col_hk[3])
        textdim = blf.dimensions(0, "F1")
        coloffset = columnoffs - textdim[0]
        blf.position(0, coloffset, offset, 0)
        blf.draw(0, "F1")


def BoolDraw(pos, offset, value, textname, text1, text2, _uifactor, _addon_prefs):
    # left
    col = _addon_prefs.text_color
    blf.color(0, col[0], col[1], col[2], col[3])
    offsetfac = offset * _uifactor
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, textname)
    # right
    col = _addon_prefs.hotkey_color
    blf.color(0, col[0], col[1], col[2], col[3])
    textToDraw = text1 if value else text2
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


def NumberDraw(value, pos, text, offset, _uifactor, _addon_prefs):
    # left
    col = _addon_prefs.text_color
    blf.color(0, col[0], col[1], col[2], col[3])
    offsetfac = offset * _uifactor
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, text)
    # right
    col = _addon_prefs.hotkey_color
    blf.color(0, col[0], col[1], col[2], col[3])
    textToDraw = str(value)
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


def HitFilterDraw(basetype, pos, offset, active, _uifactor, _addon_prefs):
    # left
    offsetfac = offset * _uifactor
    if active:
        col = _addon_prefs.text_color
        blf.color(0, col[0], col[1], col[2], col[3])
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, "Hit Filter")
    # right
    if active:
        col = _addon_prefs.hotkey_color
        blf.color(0, col[0], col[1], col[2], col[3])
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    # set matching text
    if basetype == 'ALL':
        textToDraw = "All"
    elif basetype == 'FRONT':
        textToDraw = "Front Grid"
    elif basetype == 'GRID':
        textToDraw = "Grid Only"
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


def GroundTypeDraw(basetype, pos, offset, active, _uifactor, _addon_prefs):
    # left
    offsetfac = offset * _uifactor
    if active:
        col = _addon_prefs.text_color
        blf.color(0, col[0],col[1],col[2],col[3])
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, "BaseType")
    # right
    if active:
        col = _addon_prefs.hotkey_color
        blf.color(0, col[0],col[1],col[2],col[3])
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    # set matching text
    if basetype == 1:
        textToDraw = "Corners"
    elif basetype == 2:
        textToDraw = "Midpoint"
    elif basetype == 3:
        textToDraw = "Uniform"
    elif basetype == 4:
        textToDraw = "Uniform all"
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


# draw Slider
def SliderDraw(op, context, value):
    bgl.glLineWidth(2)

    x = op.mouseStart[0]
    x2 = op.mouseEnd_x
    y = op.mouseStart[1]
    ytop = op.mouseStart[1] + 15

    with gpu.matrix.push_pop():
        coords = [(x, ytop), (x, y), (x, y), (x2, y), (x2, y), (x2, ytop)]
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch.draw(shader)

    # draw segments text
    textToDraw = str(value)
    blf.position(0, x + 3, y + 5, 0)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.draw(0, textToDraw)
