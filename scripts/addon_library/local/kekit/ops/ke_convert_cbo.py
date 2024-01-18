import bmesh
import bpy
from mathutils import Matrix
from bpy.props import BoolProperty
from bpy.types import Operator
from .._utils import vertloops, get_distance, flattened, average_vector


class KeCBO(Operator):
    bl_idname = "view3d.ke_cbo"
    bl_label = "Convert to CBO"
    bl_description = "Curve Bevel Object - Automated setup: \n" \
                     "MESH EDGE MODE: Select one CBO edge loop. MUST lie flat on Global Z. Global X is front.\n" \
                     "& select one PATH edge loop to extrude along. Must have the Active Element. (More in wiki)\n" \
                     "CURVE MODE: Select 2 (already existing) Curve Objects, Active Object is Path, other is CBO."
    bl_options = {'REGISTER', 'UNDO'}

    invert: BoolProperty(name="Flip Shape Direction", default=False)
    invert_path: BoolProperty(name="Flip Path Direction", default=False)
    caps: BoolProperty(name="Cap Ends", default=True)
    keep: BoolProperty(name="Keep Mesh Shape", default=True)
    bezier: BoolProperty(name="Bezier", description="Bezier or polyline curve", default=True)
    closed: BoolProperty(name="Closed Loop", default=False, options={"HIDDEN"})

    mtx = None
    coll = None
    ctx = None

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "invert", toggle=True)
        layout.prop(self, "invert_path", toggle=True)
        layout.prop(self, "caps", toggle=True)
        layout.prop(self, "keep", toggle=True)
        layout.prop(self, "bezier", toggle=True)
        layout.separator()

    def make_curve(self, loops, name):
        # Create curve data
        cdata = bpy.data.curves.new(name, type='CURVE')
        cdata.dimensions = '3D'
        cdata.resolution_u = 2
        if not self.closed and self.caps:
            cdata.use_fill_caps = True
        curve = bpy.data.objects.new(name, cdata)
        # Convert coords to polylines & add to curve data block
        plines = []
        for loop in loops:
            coords = [self.mtx @ v.co for v in loop]
            polyline = cdata.splines.new('POLY')
            polyline.points.add(len(coords) - 1)
            for i, coord in enumerate(coords):
                x, y, z = coord
                polyline.points[i].co = (x, y, z, 1)
            if self.bezier:
                polyline.type = 'BEZIER'
            plines.append(polyline)
        # Auto-close continuous pathloops
        if self.closed:
            for pline in plines:
                pline.use_cyclic_u = True
        self.coll.objects.link(curve)
        return curve

    def execute(self, context):
        #
        # Object selection
        #
        src_obj = context.object
        self.mtx = src_obj.matrix_world
        ouc = src_obj.users_collection
        if len(ouc) > 0:
            self.coll = ouc[0]
        else:
            self.coll = context.scene.collection

        #
        # Edge Extrude or Curve Setup
        #
        sel_obj = []
        for o in context.selected_objects:
            if o.type == "CURVE":
                sel_obj.append(o)

        # Curve Setup Mode
        if len(sel_obj) == 2 and context.active_object in sel_obj:
            path_obj = context.active_object
            shape_obj = [o for o in sel_obj if o != path_obj][0]
            path_obj.data.bevel_mode = 'OBJECT'
            path_obj.data.bevel_object = shape_obj
            if self.caps:
                path_obj.data.use_fill_caps = True
            if self.bezier:
                for s in shape_obj.data.splines:
                    s.type = 'BEZIER'
            shape_obj.select_set(True)
            path_obj.select_set(False)
            context.view_layer.objects.active = shape_obj
            if self.invert:
                bpy.ops.curve.switch_direction()
            # bpy.ops.object.mode_set(mode="OBJECT")
            return {"FINISHED"}

        # Else, Mesh Convert Mode
        if src_obj.type == "MESH" and src_obj.data.is_editmode:
            pass
        else:
            self.report({"INFO"}, "Invalid Selection: Mesh object in edit mode expected")
            return {"CANCELLED"}

        src_obj.select_set(True)
        context.view_layer.objects.active = src_obj

        #
        # Mesh Selections
        #
        bm = bmesh.from_edit_mesh(src_obj.data)
        sel_edges = [e for e in bm.edges if e.select]

        if not sel_edges:
            self.report({"INFO"}, "Invalid Selection: No edges selected?")
            return {"CANCELLED"}
        else:
            sel_verts = [v for v in bm.verts if v.select]

        active = bm.select_history.active
        if active:
            if type(active).__name__ != "BMVert":
                active = [v for v in active.verts][0]

        if active not in sel_verts:
            self.report({"INFO"}, "Invalid Selection: No active element")
            return {"CANCELLED"}

        vps = [e.verts for e in sel_edges]
        islands = vertloops(vps)
        if len(islands) < 2:
            self.report({"INFO"}, "Invalid Selection: Minimum 2 edge loops expected")
            return {"CANCELLED"}

        shapeloops = []
        # Path also list-append, to re-use make_curve func
        pathloop = []
        self.closed = False

        for island in islands:
            if active in island:
                if island[0] == island[-1] :
                    self.closed = True
                if self.invert_path:
                    island.reverse()
                pathloop.append(island)
            else:
                # cheap winding adjustment
                island.reverse()
                if self.invert:
                    island.reverse()
                shapeloops.append(island)

        # Origin positions
        shape_verts = list(set(flattened(shapeloops)))
        shape_co = average_vector([v.co for v in shape_verts])

        origin_point = pathloop[0][0].co
        nearest = 999999
        for v in pathloop[0]:
            d = get_distance(v.co, shape_co)
            if d < nearest:
                origin_point = v.co
                nearest = d

        origin_point = self.mtx @ origin_point
        path_co = average_vector([v.co for v in pathloop[0]])
        path_co = self.mtx @ path_co

        #
        # Make Curves # IDK/IDC about automatic winding detection. tbd.
        #
        shape_obj = self.make_curve(shapeloops, src_obj.name + "_CBO")
        loop_obj = self.make_curve(pathloop, src_obj.name + "_path")

        if not self.keep:
            for v in shape_verts:
                if v.is_valid:
                    bm.verts.remove(v)
            bmesh.update_edit_mesh(src_obj.data)

        # Set origin
        shape_obj.data.transform(Matrix.Translation(-origin_point))
        shape_obj.location += origin_point
        loop_obj.data.transform(Matrix.Translation(-path_co))
        loop_obj.location += path_co

        # Set up shape curve as bevel object for loop object
        loop_obj.data.bevel_mode = 'OBJECT'
        loop_obj.data.bevel_object = shape_obj

        # Finish & Select
        shape_obj.select_set(True)
        src_obj.select_set(False)
        context.view_layer.objects.active = shape_obj
        bpy.ops.object.mode_set(mode="OBJECT")

        return {"FINISHED"}
