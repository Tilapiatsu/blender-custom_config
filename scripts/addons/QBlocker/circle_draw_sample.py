import bpy
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader


####### Functions to draw circles ########

# get circle vertices on pos 2D by segments
def GenerateCircleVerts(position, radius, segments):
    from math import sin, cos, pi
    coords = [position]
    mul = (1.0 / segments) * (pi * 2)
    for i in range(1, segments + 1):
        coord = (sin(i * mul) * radius + position[0], cos(i * mul) * radius + position[1])
        coords.append(coord)
    return coords


# get circle triangles by segments
def GenerateCircleTris(segments, startID):
    triangles = []
    tri = startID
    for i in range(segments-1):
        tricomp = (startID, tri + 1, tri + 2)
        triangles.append(tricomp)
        tri += 1
    triangles.append((startID, tri+1, startID+1))
    return triangles


# draw a circle on scene
def draw_circle_fill_2d(position, color, radius, segments=8, alpha=False):
    import gpu
    import bgl

    if alpha:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    # create vertices
    coords = GenerateCircleVerts(position, radius, segments)
    # create triangles
    triangles = GenerateCircleTris(segments, 0)
    # set shader and draw
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


# draw multiple circle in one batch on screen
def draw_multicircles_fill_2d(positions, color, radius, segments=8, alpha=False):
    import gpu
    import bgl

    if alpha:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    coords = []
    triangles = []
    # create vertices
    for center in positions:
        actCoords = GenerateCircleVerts(center, radius, segments)
        coords.extend(actCoords)
    # create triangles
    for tris in range(len(positions)):
        actTris = GenerateCircleTris(segments, tris*(segments+1))
        triangles.extend(actTris)
    # set shader and draw
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


####### The draw handler for the class ########

def PointsDrawHandler(_op, _context):
    region = _context.region
    rv3d = _context.region_data

    pointColor = (1.0, 1.0, 1.0, 0.5)
    multipColor = (0.12, 0.56, 1.0, 0.7)
    # transform points to screen
    posBatch = []
    for pos in _op.worldPosList:
        pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
        posBatch.append(pos2D)

    # draw multiple circles in one batch
    draw_multicircles_fill_2d(positions=posBatch, color=multipColor, radius=5, segments=8, alpha=True)

    # draw one point
    pos2D = location_3d_to_region_2d(region, rv3d, _op.singlePointPos, default=None)
    draw_circle_fill_2d(position=pos2D, color=pointColor, radius=8, segments=16, alpha=False)




class ModalCircleDrawOperator(bpy.types.Operator):
    """Draw circles with the mouse"""
    bl_idname = "view3d.modal_circles_operator"
    bl_label = "Draw Circles"

    worldPosList = [(-1.0,-1.0,0.0),(1.0,-1.0,0.0),(-1.0,1.0,0.0),(1.0,1.0,0.0)]
    singlePointPos =  (0.0,0.0,1.0)

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(PointsDrawHandler, args, 'WINDOW', 'POST_PIXEL')

            self.mouse_path = []

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalCircleDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalCircleDrawOperator)


if __name__ == "__main__":
    register()