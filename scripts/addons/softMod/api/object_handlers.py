import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from bpy_extras.view3d_utils import (
    region_2d_to_vector_3d,
    region_2d_to_origin_3d,
    location_3d_to_region_2d,
)

class LatticeHandler():
    def __init__(self,context , lattice):

        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.context = context
        self.obj = lattice
        self.mesh = None
        self.kdtree_3d = None
        self.kdtree_2d = None
        self.generate_trees()

    @property
    def type(self):
        return self.obj.type

    @property
    def name(self):
        return self.obj.name

    @property
    def modifiers(self):
        return self.obj.modifiers

    @property
    def volume(self):

        dimensions = [x for x in self.dimensions if x != 0.0]
        volume = dimensions[0]
        for i in range (1 , len (dimensions)):
            volume = volume * dimensions[i]

        root_size = len (dimensions)
        # gettign the cubic root of the volume
        volume = (abs (volume) ** (1. / root_size))

        return volume


    @property
    def dimensions(self):
        return self.obj.dimensions

    def add_armature(self , name):
        armature = self.obj.modifiers.new (name=name , type='ARMATURE')
        armature.use_bone_envelopes = True
        armature.use_deform_preserve_volume = True
        return armature

    def add_vertex_group(self , name):
        group = self.obj.vertex_groups.new (name=name)
        return group

    def convert_3d_point_to_screen(self , point):

        point_2d = location_3d_to_region_2d (self.region , self.region_3d , point)
        if point_2d:
            point_2d = Vector ((point_2d[0] , point_2d[1] , 0.0))
        else:
            point_2d = Vector ((0.0 , 0.0 , 0.0))
        return point_2d

    @property
    def points(self):
        return self.obj.data.points

    def generate_bmesh(self , deformed=True , transformed=True):
        """
        Create a bmesh from the object.
        This will capture the deformers too.
        :param object:
        :return:
        """
        if not self.mesh:
            self.convert_to_mesh()
        bm = bmesh.new ()
        if deformed:
            depsgraph = self.context.evaluated_depsgraph_get ()
            ob_eval = self.mesh.evaluated_get (depsgraph)
            mesh = ob_eval.to_mesh ()
            bm.from_mesh (mesh)
            ob_eval.to_mesh_clear ()
        else:
            mesh = self.mesh.to_mesh ()
            bm.from_mesh (mesh)
        if transformed:
            bm.transform(self.mesh.matrix_world)
        bpy.data.objects.remove(self.mesh)
        self.mesh = None
        return bm

    def generate_trees(self , deformed=True , transformed=True):
        bm = self.generate_bmesh (deformed , transformed)

        size = len (bm.verts)
        self.kdtree_3d = KDTree (size)
        self.kdtree_2d = KDTree (size)

        for i , v in enumerate (bm.verts):

            point_2d = self.convert_3d_point_to_screen (v.co)
            self.kdtree_2d.insert ((point_2d) , i)
            self.kdtree_3d.insert ((v.co) , i)
        self.kdtree_3d.balance ()
        self.kdtree_2d.balance ()

    def build_kd_tree_3d(self):

        size = len (self.points)
        self.kdtree_3d = KDTree (size)
        for i in range (size):
            v = self.points[i]
            print(v.co)
            print (v.co_deform)
            self.kdtree_3d.insert ((v.co_deform) , i)
        self.kdtree_3d.balance ()

    def build_kd_tree_2d(self):
        size = len (self.points)
        self.kdtree_2d = KDTree (size)

        for i in range (size):
            v = self.points[i]
            point_2d = self.convert_3d_point_to_screen (v.co)
            self.kdtree_2d.insert ((point_2d) , i)

        self.kdtree_2d.balance ()
        return self.kdtree_2d

    def find_2d(self , co):
        point = self.kdtree_2d.find (co)
        return self.points[point[1]]

    @property
    def vertex_groups(self):
        return self.obj.vertex_groups

    def set_vertex_group_value(self , v_group , value):
        for i, v in enumerate(self.points):
            v_group.add ((i ,) , value , "REPLACE")

    def set_vertex_group_values(self , v_group , points):
        for weight_id in points:
            v_group.add ((weight_id ,) , points[weight_id] , "REPLACE")

    def calculate_map(self , center , radius, surf_falloff=False):
        # find the closest vertex first
        points_in_range_list = self.kdtree_3d.find_range (center , radius)
        points_in_range = {}

        for position , index , distance in points_in_range_list:
            points_in_range[index] = (
                ((abs ((distance ** 2) - (1.0 ** 2))) ** (1. / 2)) * ((1.0 - distance) ** (1. / 2)))
        return points_in_range

    def convert_to_mesh(self):
        u = self.obj.data.points_u
        v = self.obj.data.points_v
        w = self.obj.data.points_w

        w_cap = u * v * (w - 1)
        v_cap = v * u
        verts = []
        edges = []
        faces = []

        for point in self.obj.data.points:
            verts.append (point.co_deform)

        x = 0

        for i in range (0 , len (verts)):
            if i % u:
                edges.append ((i - 1 , i))  # creating u edges

            if (i - x) % (v_cap):
                edges.append ((i , i - u))  # creating v edges
            if (x + 1) % u:
                x += 1
            else:
                x = 0
            if i < w_cap:
                edges.append ((i , i + v_cap))  # creating w edges

        mesh = bpy.data.meshes.new('{}PolyMesh'.format(self.name))
        self.mesh = bpy.data.objects.new('{}Poly'.format(self.name) , mesh)
        mesh.from_pydata (verts , edges , faces)

        #bpy.context.scene.collection.objects.link (obj)
        self.mesh.matrix_world = self.obj.matrix_world
        self.transfer_vertex_groups(self.mesh)
        self.transfer_modifiers(self.mesh)

        return self.mesh

    def transfer_vertex_groups(self , target):

        lattice_groups = self.obj.vertex_groups
        target_vertex_groups = target.vertex_groups
        # create all the vertex groups
        vertex_values = self.get_vertex_groups_values (self.obj)

        for group in lattice_groups:
            target_group = target_vertex_groups.get(group.name)
            if not target_group:
                target_group = target_vertex_groups.new(name=group.name)

        for group in vertex_values:
            values = vertex_values[group]
            v_group = target_vertex_groups.get (group)
            for v , value in values:
                v_group.add((v,), value, "REPLACE")

    def transfer_modifiers(self , target):
        lat_modifiers = self.obj.modifiers
        for mod in lat_modifiers:
            mod_type = mod.type
            mod_name = mod.name
            try:
                target_mod = target.modifiers.new (mod_name , mod_type)
            except TypeError:
                continue
            properties = [p.identifier for p in mod.bl_rna.properties if not p.is_readonly]

            for prop in properties:
                setattr(target_mod, prop, getattr(mod, prop))

    @property
    def vertex_groups_values(self):
        return self.get_vertex_groups_values(self.obj)

    @vertex_groups_values.setter
    def vertex_groups_values(self, vertex_values):

        for group in vertex_values:
            values = vertex_values[group]
            v_group = self.vertex_groups.get(group)
            if not v_group:
                v_group = self.vertex_groups.new(group)
            for v, value in values:
                v_group.add((v,), value, "REPLACE")

    @staticmethod
    def get_vertex_groups_values(obj):

        points = None
        if obj.type == "LATTICE":
            points = obj.data.points
        if obj.type == "MESH":
            points = obj.data.vertices
        group_lookup = {g.index: g.name for g in obj.vertex_groups}
        verts = {name: [] for name in group_lookup.values ()}
        for i , v in enumerate (points):
            for g in v.groups:
                verts[group_lookup[g.group]].append ((i , g.weight))
        return verts


class MeshHandler (object):
    def __init__(self , contex , mesh):
        self.context = contex
        self.obj = mesh
        self.kdtree = None
        self.bhvtree = None
        self.generate_trees ()

    @property
    def type(self):
        return self.obj.type

    @property
    def name(self):
        return self.obj.name

    @property
    def dimensions(self):
        bm = self.generate_bmesh (deformed=False)
        # bm.from_object (self.obj , self.context.evaluated_depsgraph_get ())
        tmp_object_data = bpy.data.meshes.new (name='Mesh')
        # bm.transform (self.obj.matrix_world)
        bm.to_mesh (tmp_object_data)
        tmp_object = bpy.data.objects.new (name='tmp_object' , object_data=tmp_object_data)
        bm.clear ()
        bm.free ()
        return tmp_object.dimensions

    @property
    def volume(self):

        dimensions = [x for x in self.dimensions if x != 0.0]
        volume = dimensions[0]
        for i in range (1 , len (dimensions)):
            volume = volume * dimensions[i]

        root_size = len (dimensions)
        # gettign the cubic root of the volume
        volume = (abs (volume) ** (1. / root_size))

        return volume

    @property
    def modifiers(self):
        return self.obj.modfiers

    def add_armature(self , name):
        armature = self.obj.modifiers.new (name=name , type='ARMATURE')
        armature.use_bone_envelopes = True
        armature.use_deform_preserve_volume = True
        return armature

    def generate_bmesh(self , deformed=True , transformed=True):
        """
        Create a bmesh from the object.
        This will capture the deformers too.
        :param object:
        :return:
        """
        bm = bmesh.new ()
        if deformed:
            depsgraph = self.context.evaluated_depsgraph_get ()
            ob_eval = self.obj.evaluated_get (depsgraph)
            mesh = ob_eval.to_mesh ()
            bm.from_mesh (mesh)
            ob_eval.to_mesh_clear ()
        else:
            mesh = self.obj.to_mesh ()
            bm.from_mesh (mesh)
        if transformed:
            bm.transform (self.obj.matrix_world)

        return bm

    def generate_trees(self , deformed=True , transformed=True):

        bm = self.generate_bmesh (deformed , transformed)
        self.bvhtree = BVHTree.FromBMesh (bm)

        size = len (bm.verts)
        self.kdtree = KDTree (size)
        for i , v in enumerate (bm.verts):
            self.kdtree.insert ((v.co) , i)
        self.kdtree.balance ()

    def add_vertex_group(self , name):
        group = self.obj.vertex_groups.new (name=name)
        return group

    def get_point_on_mesh(self , origin , direction , offset):
        hit , normal , vid , *_ = self.bvhtree.ray_cast (origin , direction)
        if hit is not None:
            hit = hit + (normal * offset)
        return (hit , normal)

    @property
    def vertex_groups(self):
        return self.obj.vertex_groups

    def calculate_map(self , origin , radius , surf_falloff=False):

        nearest = self.kdtree.find (origin)
        starting_vert_index = nearest[1]

        # find all the vertices in the radius range
        points_in_range_list = self.kdtree.find_range (origin , radius)
        points_in_range = {}
        for position , index , distance in points_in_range_list:
            distance = distance / radius
            # points_in_range[index] = (
            # ((abs ((distance ** 2) - (1.0 ** 2))) ** (1. / 2)) * ((1.0 - distance) ** (1. / 3)))

            points_in_range[index] = (
                    ((abs ((distance ** 2) - (1.0 ** 2))) ** (1. / 2)) * ((1.0 - distance)))
            # print(points_in_range[index] )
        # here we gonna append the id of the connected edges in the range
        points_in_surf_range = {}

        bm = self.generate_bmesh ()
        if surf_falloff:
            # get the bmvert
            bm.verts.ensure_lookup_table ()
            starting_vert = bm.verts[starting_vert_index]

            # this is going to be the connected iterator
            next_in_surface_radius = [starting_vert]
            while next_in_surface_radius:
                # cleaning the ones who have already done
                extended_in_radius = []
                for v in next_in_surface_radius:
                    points_in_surf_range[v.index] = points_in_range[v.index]
                    for e in v.link_edges:
                        connected = e.other_vert (v)
                        # check if the connected is in range
                        if connected.index in points_in_range.keys () \
                                and connected.index not in points_in_surf_range.keys () \
                                and connected not in next_in_surface_radius \
                                and connected not in extended_in_radius:
                            extended_in_radius.append (connected)
                next_in_surface_radius = extended_in_radius
            points_in_range = points_in_surf_range

        return points_in_range

    def set_vertex_group_value(self , v_group , value):
        for v in self.obj.data.vertices:
            v_group.add ((v.index ,) , value , "REPLACE")

    def set_vertex_group_values(self , v_group , points):
        for weight_id in points:
            v_group.add ((weight_id ,) , points[weight_id] , "REPLACE")

class GpHandler (object):
    def __init__(self , context , gpencil):
        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.context = context
        self.obj = gpencil
        self.kdtree_3d = None
        self.kdtree_2d = None
        self.data = []
        self.initialize_gp_data ()
        self.build_kd_tree_2d ()
        self.build_kd_tree_3d ()

        self.muted_modifiers = {}

    @property
    def name(self):
        return self.obj.name

    @property
    def type(self):
        return self.obj.type

    @property
    def modifiers(self):
        return self.obj.grease_pencil_modifiers

    def turn_all_mods_off(self):
        self.muted_modifiers = {}
        for mod in self.modifiers:
            self.muted_modifiers[mod] = mod.show_viewport
            mod.show_viewport = False

    def turn_all_mods_on(self):
        if not self.muted_modifiers:
            return
        for mod in self.muted_modifiers:
            mod.show_viewport = self.muted_modifiers[mod]

    def add_armature(self , name):
        armature = self.obj.grease_pencil_modifiers.new (name=name , type='GP_ARMATURE')
        armature.use_bone_envelopes = True
        return armature

    def initialize_gp_data(self):
        """
        storing all the datas
        :return:
        """
        if not self.obj.type == "GPENCIL":
            print ("{} not a GPENCIL, it is a {}".format (self.obj.name , self.obj.type))
            return
        wm = self.obj.matrix_world
        gp_obj = self.obj.data

        index = 0
        for i , layer in enumerate (gp_obj.layers):

            current_layer = layer
            frame = layer.active_frame
            current_frame = frame
            for x , stroke in enumerate (frame.strokes):
                current_stroke = stroke
                for point in stroke.points:
                    v = GpVert (index)
                    v.layer = current_layer
                    v.frame = current_frame
                    v.stroke = current_stroke
                    v.gp_point = point
                    v.co = wm @ point.co
                    index += 1
                    self.data.append (v)

    @property
    def dimensions(self):

        dimensions = []
        x = []
        y = []
        z = []
        for v in self.data:
            # print(v.co)
            # print(v.index)
            x.append (v.co[0])
            y.append (v.co[1])
            z.append (v.co[2])

        x = sorted (x)
        y = sorted (y)
        z = sorted (z)
        print ("min is: {} max is: {}".format (x[0] , x[-1]))

        return ((x[-1] - x[0]) , (y[-1] - y[0]) , (z[-1] - z[0]))

    @property
    def volume(self):
        print ("\n##############\nDIMENSIONS ARE: {}\n##############\n".format (self.dimensions))
        dimensions = [x for x in self.dimensions if x != 0.0]
        volume = dimensions[0]
        for i in range (1 , len (dimensions)):
            volume = dimensions[i]

        return volume

    def convert_3d_point_to_screen(self , point):

        point_2d = location_3d_to_region_2d (self.region , self.region_3d , point)
        if point_2d:
            point_2d = Vector ((point_2d[0] , point_2d[1] , 0.0))
        else:
            point_2d = Vector ((0.0 , 0.0 , 0.0))
        return point_2d

    def build_kd_tree_3d(self):
        size = len (self.data)
        self.kdtree_3d = KDTree (size)
        for i in range (size):
            v = self.data[i]
            self.kdtree_3d.insert ((v.co) , i)
        self.kdtree_3d.balance ()

    def build_kd_tree_2d(self):
        size = len (self.data)
        self.kdtree_2d = KDTree (size)

        for i in range (size):
            v = self.data[i]
            point_2d = self.convert_3d_point_to_screen (v.co)
            self.kdtree_2d.insert ((point_2d) , i)

        self.kdtree_2d.balance ()
        return self.kdtree_2d

    def find_2d(self , co):
        point = self.kdtree_2d.find (co)
        return self.data[point[1]]

    @property
    def vertex_groups(self):
        return self.obj.vertex_groups

    def calculate_map(self , center , radius , active_layer_only=False):
        # find the closest vertex first
        active_layer = self.obj.data.layers.active
        points_in_range_list = self.kdtree_3d.find_range (center , radius)
        points_in_range = {}

        for position , index , distance in points_in_range_list:

            point = self.data[index]
            if active_layer_only:
                if point.layer == active_layer:
                    points_in_range[index] = (
                        ((abs ((distance ** 2) - (1.0 ** 2))) ** (1. / 2)) * ((1.0 - distance) ** (1. / 2)))
            else:
                points_in_range[index] = (
                    ((abs ((distance ** 2) - (1.0 ** 2))) ** (1. / 2)) * ((1.0 - distance) ** (1. / 2)))
        return points_in_range

    @property
    def weight_value(self):
        return self.context.scene.tool_settings.vertex_group_weight

    @weight_value.setter
    def weight_value(self , value):
        self.context.scene.tool_settings.vertex_group_weight = value

    def add_vertex_group(self , name):
        group = self.obj.vertex_groups.new (name=name)
        return group

    def set_vertex_group_value(self , v_group , value):

        self.obj.vertex_groups.active_index = v_group.index

        original_value = self.weight_value

        if bpy.ops.object.mode_set.poll ():
            current_mode = bpy.context.object.mode

        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='EDIT_GPENCIL')

        bpy.ops.gpencil.select_all (action="SELECT")
        self.weight_value = value
        bpy.ops.gpencil.vertex_group_assign ()

        self.weight_value = original_value
        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode=current_mode)

    def set_vertex_group_values(self , v_group , points):

        self.obj.vertex_groups.active_index = v_group.index
        # switch to edit mode
        original_value = self.weight_value

        if bpy.ops.object.mode_set.poll ():
            current_mode = bpy.context.object.mode

        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='EDIT_GPENCIL')
        bpy.ops.gpencil.select_all (action="DESELECT")
        for point in points:
            value = points[point]
            gp_point = self.data[point].gp_point
            gp_point.select = True
            if type (value) == complex:
                value = value.real

            self.weight_value = float (value)

            bpy.ops.gpencil.vertex_group_assign ()
            gp_point.select = False

        self.weight_value = original_value

        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='WEIGHT_GPENCIL')

        for i in range (3):
            bpy.ops.gpencil.vertex_group_smooth ()

        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode=current_mode)


class GpVert (object):
    def __init__(self , index):
        self.index = index
        self.layer = None
        self.stroke = None
        self.frame = None
        self.co = None
        self.gp_point = None

################################################## WIDGETS AND ARMATURES################################################

class SoftWidgetHandler():
    def __init__(self, widget):
        self.widget= widget
        self.scene = bpy.context.scene
        self.armature = None
        self.deformed = None
        self.v_group = None
        self.mirror_v_group = None
        self.modifier = None
        self.get_armature ()

    def __repr__(self):
        return self.widget.name

    def __str__(self):
        return self.name

    def rename(self, name):
        if not name:
            return

        self.widget.name = "{}_widget".format(name)
        self.base_widget.name = str(self.widget.name).replace("_widget", "_widget_base")
        self.get_armature()
        if self.armature:

            bone = self.armature.deform_bone
            bone_name = bone.name
            bone = self.armature.armature.data.bones[bone_name]

            deformed = self.armature.deformed
            v_group = deformed.vertex_groups.get(bone_name)
            self.armature.modifier.name = str(self.widget.name).replace("_widget", "_deformer")
            bone_new_name = str(self.widget.name).replace("_widget", "_deform")
            bone.name = bone_new_name

            #updating the drivers
            for d in self.armature.armature.data.animation_data.drivers:
                if bone_name in d.data_path:
                    d.data_path = str(d.data_path).replace(bone_name, bone_new_name)
                    dr = d.driver
                    dr.expression += " "
                    dr.expression = dr.expression[:-1]



            anchor_bone = bone.parent
            if anchor_bone:
                anchor_bone.name = str(self.widget.name).replace("_widget", "_anchor")
            if v_group:
                v_group.name = bone.name

    @property
    def symmetry(self):
        if self.armature:
            bone = self.armature.mirror_deform_bone
            if bone:
                return bone.bone.use_deform

    @symmetry.setter
    def symmetry(self, value):
        if self.armature:
            bone = self.armature.mirror_deform_bone
            if bone:
                bone.bone.use_deform = value


    @property
    def name(self):
        """
        return the widget name
        :return:
        """
        if self.widget:
            return self.widget.name

    def get_armature(self):
        widget_name = self.widget.name
        objects = self.scene.objects
        armatures = list ()
        for obj in objects:
            if obj.type in {"ARMATURE", "GP_ARMATURE"}:
                armatures.append (obj)
        for armature in armatures:
            armature_handler = SoftArmatureHandler.from_armature(armature)
            if armature_handler:
                if armature_handler.widget.name == widget_name:
                    self.armature = armature_handler
                    self.deformed = self.armature.deformed
                    self.v_group = self.deformed.vertex_groups.get(self.armature.deform_bone.name)
                    self.mirror_v_group = self.deformed.vertex_groups.get(self.armature.mirror_deform_bone.name)
                    self.modifier = self.armature.modifier

    @property
    def show_viewport(self):
        if self.modifier:
            return self.modifier.show_viewport

    @show_viewport.setter
    def show_viewport(self, state):
        if self.modifier:
            self.modifier.show_viewport = state

    @staticmethod
    def from_widget(obj):
        if "soft_mod_type" in obj.keys ():
            if obj["soft_mod_type"] == "widget":
                return SoftWidgetHandler(obj)

    @staticmethod
    def create(name, location=Vector((0.0,0.0,0.0)), widget_size=1.0, base_scale=(1.0,1.0,1.0), collection=None):
        """
        Create the widget and return the handler
        :param name: Name of the softMod widget
        :param location: position
        :return: SoftWidgetHandler
        """

        # generating the name of the handler
        i = 1
        widget_base_name = "{}_widget_base".format (name)
        objects_names = [ob.name for ob in bpy.context.scene.objects]
        while widget_base_name in objects_names:
            widget_base_name = "{}_widget_base{}".format (name , str (i).zfill (3))
            i += 1


        # creating the base for the widget and locking it
        widget_base = bpy.data.objects.new (widget_base_name , None)
        widget_base.empty_display_size = widget_size * 1.3
        widget_base.empty_display_type = 'CIRCLE' #give it a circle shape
        widget_base.scale = base_scale
        widget_base.show_in_front = True
        for i in range (len (widget_base.lock_location)):
            widget_base.lock_location[i] = True
        for i in range (len (widget_base.lock_rotation)):
            widget_base.lock_rotation[i] = True
        for i in range (len (widget_base.lock_scale)):
            widget_base.lock_scale[i] = True

        # adding size driver
        widget_base_size_dr = widget_base.driver_add("empty_display_size").driver
        widget_base_size_var = widget_base_size_dr.variables.new ()
        widget_base_size_var.targets[0].id_type = "SCENE"
        widget_base_size_var.targets[0].id = bpy.context.scene
        widget_base_size_var.targets[0].data_path = 'soft_mod.widget_global_size'
        widget_base_size_dr.expression = "{}*0.9".format(widget_base_size_var.name)




        # adding a custom property
        widget_base["soft_mod_type"] = "widget_base"

        # creating the softmod widget
        widget_name = widget_base.name.replace("_base", "")
        widget = bpy.data.objects.new(widget_name, None)

        # adding size driver
        widget_size_dr = widget.driver_add("empty_display_size").driver
        widget_size_var = widget_size_dr.variables.new ()
        widget_size_var.targets[0].id_type = "SCENE"
        widget_size_var.targets[0].id = bpy.context.scene
        widget_size_var.targets[0].data_path = 'soft_mod.widget_global_size'

        # adding second variable
        widget_rel_size_var = widget_size_dr.variables.new ()
        widget_rel_size_var.targets[0].id_type = "OBJECT"
        widget_rel_size_var.targets[0].id = widget
        widget_rel_size_var.targets[0].data_path = 'soft_widget.widget_relative_size'


        widget_size_dr.expression = "{}+{}".format(widget_size_var.name,widget_rel_size_var.name)



        widget.show_in_front = True
        # empty_draw was replaced by empty_display
        widget.empty_display_size = widget_size



        widget.empty_display_type = 'CUBE'

        widget.parent = widget_base
        widget_base.location = location

        widget["soft_mod_type"] = "widget"

        widget["influence"] = 1.0
        widget["radius"] = 1.0
        widget["_RNA_UI"] = {}
        widget["_RNA_UI"]["influence"] = {"min": 0.0 , "max": 1.0 , "soft_min": 0.0 , "soft_max": 1.0}
        widget["_RNA_UI"]["radius"] = {"min": 0.0 , "max": 1.0 , "soft_min": 0.0 , "soft_max": 1.0}





        if collection:
            collection.objects.link (widget_base)
            collection.objects.link (widget)
        else:
            bpy.context.scene.collection.objects.link (widget_base)
            bpy.context.scene.collection.objects.link (widget_base)

        return SoftWidgetHandler.from_widget(widget)


    def unparent(self):
        constraints = self.base_widget.constraints
        if constraints:
            for c in constraints:
                if c.type == "CHILD_OF":
                    self.base_widget.constraints.remove(c)

        bone_parent = self.armature.deform_bone.parent
        if not bone_parent:
            return
        constraints = bone_parent.constraints
        if constraints:
            for c in constraints:
                if c.type == "CHILD_OF":
                    bone_parent.constraints.remove(c)


    def parent_to(self, parent):

        self.unparent()
        const  = self.base_widget.constraints.new ('CHILD_OF')
        const.target = parent
        const.inverse_matrix = parent.matrix_world.inverted()


        #adding the driver
        # adding a driver to the contraint to the widget influence property
        inf_driver = const.driver_add ("influence").driver
        inf_driver.type = "SUM"
        inf_driver_var = inf_driver.variables.new ()
        inf_driver_var.targets[0].id_type = "OBJECT"
        inf_driver_var.targets[0].id = self.widget
        inf_driver_var.targets[0].data_path = '["influence"]'
        inf_driver_var.name = "widget_link"

        bone_parent = self.armature.deform_bone.parent
        bone_const = bone_parent.constraints.new ('CHILD_OF')
        bone_const.target = parent
        bone_const.inverse_matrix = parent.matrix_world.inverted()

        inf_driver = bone_const.driver_add ("influence").driver
        inf_driver.type = "SUM"
        inf_driver_var = inf_driver.variables.new ()
        inf_driver_var.targets[0].id_type = "OBJECT"
        inf_driver_var.targets[0].id = self.widget
        inf_driver_var.targets[0].data_path = '["influence"]'
        inf_driver_var.name = "par_bone_link"

    def mirror_weights(self, mirror=False):
        if self.deformed:
            topology =self.widget.soft_widget.topologycal_sym
            group = self.v_group
            if mirror:
                group = self.mirror_v_group
            self.deformed.mirror_vertex_group(group, topology)

    def set_radius_max(self, max):

        self.widget["_RNA_UI"]["radius"] = {"min": 0.0 , "max": max , "soft_min": 0.0 , "soft_max": max}

    def paint_mode(self, mirror=False):
        if not self.widget:
            return
        if not self.armature:
            return

        if not self.deformed:
            return

        bone = self.armature.deform_bone
        if mirror:
            bone = self.armature.mirror_deform_bone
        self.deformed.paint_mode(bone.name)

    def set_active(self):
        bpy.context.view_layer.objects.active = self.widget

    def activete_symmetry(self):
        pass

    def smooth_weights(self, mirror=False, iter=None, factor=None, expand=None):
        bone = self.armature.deform_bone
        if mirror:
            bone = self.armature.mirror_deform_bone
        self.deformed.smooth_weights(bone.name, iter, factor, expand)
        self.set_active()

    @property
    def base_widget(self):
        return self.widget.parent

    @property
    def collection(self):
        return self.widget.users_collection

    def delete(self):
        siblings = self.siblings
        v_groups = []
        if self.v_group:
            v_groups.append(self.v_group)
        if self.mirror_v_group:
            v_groups.append(self.mirror_v_group)

        collection = None
        if not siblings:
            collection = self.collection[0]
            base_v_group = self.deformed.vertex_groups.get("softMod_base")
            if base_v_group:
                v_groups.append(base_v_group)
        to_delete=[self.widget]
        if self.base_widget:
            to_delete.append(self.base_widget)
        obj = self.deformed
        obj.remove_modifier(self.modifier)
        for group in v_groups:
            self.deformed.vertex_groups.remove(group)

        self.armature.delete()

        for item in to_delete:
            # print ("deleting " , item.name)
            bpy.data.objects.remove (item)
        if collection:
            bpy.data.collections.remove (collection)

    @property
    def siblings(self):
        #siblings=list()
        if self.armature:
            if self.deformed:
                deformed = self.deformed
                widgets= deformed.widgets
                return [widget for widget in widgets if not widget.name == self.name]



class SoftDeformedHandler(object):
    def __init__(self, obj):
        self.obj = obj
        self.keys_status = None
        self.mods_status = None

    @property
    def name(self):
        if self.obj:
            return self.obj.name

    @property
    def type(self):
        if self.obj:
            return self.obj.type

    @property
    def modifiers(self):
        if self.type == "GPENCIL":
            return self.obj.grease_pencil_modifiers
        else:
            return self.obj.modifiers

    @property
    def armatures(self):
        armatures = list()
        for mod in self.modifiers:
            if mod.type in {"GP_ARMATURE","ARMATURE"}:
                if mod.object:
                    armature =SoftArmatureHandler(mod.object)
                    if armature:
                        armatures.append(armature)
        return armatures

    @property
    def vertex_groups(self):
        if self.obj:
            return self.obj.vertex_groups

    @property
    def widgets(self):
        widgets=list()
        for armature in self.armatures:
            if armature.widget:
                widgets.append(armature.widget)
        return widgets

    def widget_from_active_v_group(self):
        active_v_group = self.vertex_groups.active
        if active_v_group:
            active_v_group = active_v_group.name
        for widget in self.widgets:
            widget = SoftWidgetHandler.from_widget(widget)
            if not widget:
                continue
            if active_v_group == widget.armature.deform_bone.name or \
                    active_v_group == widget.armature.mirror_deform_bone.name:
                return widget

    def remove_modifier(self, mod):
        if self.type == "GPENCIL":
            self.obj.grease_pencil_modifiers.remove(mod)
        else:
            self.obj.modifiers.remove(mod)

    def paint_mode(self, v_group_name):

        bpy.context.view_layer.objects.active = self.obj
        if self.obj.type == "LATTICE":
            print("Can't go in paint mode on a Lattice")
            if bpy.ops.object.mode_set.poll ():
                bpy.ops.object.mode_set (mode='EDIT')
        if self.obj.type == "MESH":
            if bpy.ops.object.mode_set.poll ():
                bpy.ops.object.mode_set (mode='WEIGHT_PAINT')
        elif self.obj.type == "GPENCIL":
            if bpy.ops.object.mode_set.poll ():
                bpy.ops.object.mode_set (mode='WEIGHT_GPENCIL')

        v_map = self.obj.vertex_groups.get (v_group_name)
        self.obj.vertex_groups.active_index = v_map.index

    def smooth_opposite_weight(self, v_group):
        opposite_group = self.get_opposite_vertex_group(v_group)
        if opposite_group:
            self.smooth_weights(opposite_group.name)
        self.obj.vertex_groups.active_index = v_group.index

    def smooth_weights(self,v_group_name=None, iter = None, factor = None, expand=None ):
        current_mode = None
        if not iter:
            iter = bpy.context.scene.soft_mod.smooth_iterations
        if not factor:
            factor = bpy.context.scene.soft_mod.smooth_factor
        if not expand:
            expand = bpy.context.scene.soft_mod.smooth_expand
        if bpy.ops.object.mode_set.poll ():
            current_mode = bpy.context.object.mode
        self.paint_mode(v_group_name)
        if bpy.context.object.mode == "WEIGHT_GPENCIL":
            bpy.ops.gpencil.vertex_group_smooth(factor=factor, repeat=iter, expand=expand)

        else:
            bpy.ops.object.vertex_group_smooth(factor=factor, repeat=iter, expand=expand)
        bpy.ops.object.mode_set (mode=current_mode)

    def mute_shape_keys(self):
        if not self.obj.data.shape_keys:
            return
        self.keys_status = {}
        for key_block in self.obj.data.shape_keys.key_blocks:
            self.keys_status[key_block.name] = key_block.mute
            key_block.mute = True

    def unmute_shape_keys(self):
        if not self.obj.data.shape_keys:
            return
        for key_block in self.obj.data.shape_keys.key_blocks:
            if self.keys_status:
                if key_block.name in self.keys_status.keys():
                    key_block.mute = self.keys_status[key_block.name]
            else:
                key_block.mute = False
        self.keys_status = None

    def duplicate_vertex_group(self, v_group, group_name):
        if not self.obj.type =="MESH":
            return

        dup = self.vertex_groups.new(name = group_name)
        gi = v_group.index
        for v in self.obj.data.vertices:
            for g in v.groups:
                if g.group == gi:
                    weight = v_group.weight(v.index)
                    dup.add((v.index,),weight, "REPLACE")

        return dup

    def get_opposite_vertex_group(self, v_group):
        source = "_deform"
        dest = "_mirror_deform"
        if "mirror_" in v_group.name:
            source, dest = dest, source
        opposite_group_name = str(v_group.name).replace(source, dest)
        opposite_group = self.vertex_groups.get(opposite_group_name)
        if opposite_group:
            return opposite_group

    def mirror_vertex_group(self, v_group, topology=False):
        active = bpy.context.active_object
        source = "_deform"
        dest = "_mirror_deform"
        if "mirror_" in v_group.name:
            source, dest = dest, source
        dup_name = str(v_group.name).replace(source, dest)
        old_group = self.vertex_groups.get(dup_name)
        if old_group:
            self.vertex_groups.remove(old_group)
        bpy.context.view_layer.objects.active = self.obj
        dup = self.duplicate_vertex_group(v_group, dup_name)
        # making it active
        self.obj.vertex_groups.active_index = dup.index
        bpy.ops.object.vertex_group_mirror (use_topology=topology)

        bpy.context.view_layer.objects.active = active


    def bake_to_shape_key(self, name):

        bm = self.generate_bmesh(transformed=False)

        if not self.obj.data.shape_keys:
            self.obj.shape_key_add(name="Basis")

        sk =self.obj.shape_key_add(name=name)
        for i in range(len(bm.verts)):
            sk.data[i].co = bm.verts[i].co

    def mods_to_shape_keys(self, modifiers):
        #disabling all the modifiers
        mod_status = {}
        for mod in self.modifiers:
            if mod not in modifiers:
                mod_status[mod] = mod.show_viewport
                mod.show_viewport = False

        self.mute_shape_keys()
        shape_key_name = str (modifiers[0].name).replace ("_deformer" , "")
        self.bake_to_shape_key(shape_key_name)

        for mod in mod_status:
            mod.show_viewport = mod_status[mod]
        self.unmute_shape_keys()



    def generate_bmesh(self , deformed=True , transformed=True):
        """
        Create a bmesh from the object.
        This will capture the deformers too.
        :param object:
        :return:
        """
        bm = bmesh.new ()
        if deformed:
            depsgraph = bpy.context.evaluated_depsgraph_get ()
            ob_eval = self.obj.evaluated_get (depsgraph)
            mesh = ob_eval.to_mesh ()
            bm.from_mesh (mesh)
            ob_eval.to_mesh_clear ()
        else:
            mesh = self.obj.to_mesh ()
            bm.from_mesh (mesh)
        if transformed:
            bm.transform (self.obj.matrix_world)
        bm.verts.ensure_lookup_table()
        return bm








class SoftArmatureHandler(object):
    def __init__(self , armature):
        self.scene = bpy.context.scene
        self.armature = armature

        self.widget = None
        self.deformed = None
        self.modifier = None
        #bones
        self.base_bone = None
        self.deform_bone = None
        self.anchor_bone = None
        self.mirror_origin_bone = None
        self.mirror_deform_bone = None
        self.mirror_driver_bone = None

        self.get_elements()


    def delete(self):
        bpy.data.objects.remove(self.armature)

    @property
    def name(self):
        if self.armature:
            return self.armature.name

    @property
    def type(self):
        if self.armature:
            return self.armature.type

    @staticmethod
    def from_armature(obj):
        if "soft_mod_type" in obj.keys ():
            if obj["soft_mod_type"] == "armature":
                return SoftArmatureHandler(obj)

    @staticmethod
    def is_widget(obj):
        if "soft_mod_type" in obj.keys ():
            if obj["soft_mod_type"] == "widget":
                return True

    def get_elements(self):
        bones = self.armature.pose.bones
        for bone in bones:
            if "soft_mod_type" in bone.keys ():
                bone_type = bone["soft_mod_type"]
                setattr(self, bone_type, bone)

        objects = self.scene.objects

        if self.deform_bone:
            for c in self.deform_bone.constraints:
                target = c.target
                if target:
                    if self.is_widget(target):
                        self.widget = target

        for obj in objects:
            if obj.type in {"MESH","LATTICE"}:
                modifiers = obj.modifiers

            elif obj.type == "GPENCIL":
                modifiers = obj.grease_pencil_modifiers
            else:
                continue

            for modifier in modifiers:
                if modifier.type in {"ARMATURE", "GP_ARMATURE"}:
                    if modifier.object:
                        if modifier.object.name == self.armature.name:
                            deformed_handler= SoftDeformedHandler(obj)
                            if deformed_handler:
                                self.deformed = deformed_handler
                                self.modifier = modifier

    @property
    def edit_base_bone(self):
        return self.armature.data.bones["softMod_base"]

    @property
    def edit_deform_bone(self):
        return  self.armature.data.bones[self.deform_bone.name]

    @staticmethod
    def create(deform_bone_name,widget,mod, location=Vector((0.0, 0.0, 0.0)),
               mirror_origin = Vector((0.0,0.0,0.0)), collection=None):

        active = bpy.context.active_object
        # Create the armature
        armature = bpy.data.armatures.new ('soft_mod_armature')
        soft_mod_armature = bpy.data.objects.new ("SoftMod_Armature" , armature)
        # adding a custom string attribute
        soft_mod_armature["soft_mod_type"] = "armature"
        # bringing it in front
        soft_mod_armature.show_in_front = True

        bpy.context.scene.collection.objects.link (soft_mod_armature)
        # hiding the armature
        bpy.context.view_layer.objects.active = soft_mod_armature
        soft_mod_armature.select_set (True)

        # edit mode
        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='EDIT')

        # create_base bone
        base_bone_name = 'softMod_base'
        base_bone = armature.edit_bones.new (base_bone_name)

        base_bone.head.x = 0
        base_bone.head.y = 0
        base_bone.head.z = 0

        base_bone.tail.x = 0
        base_bone.tail.y = 1.0
        base_bone.tail.z = 0.0

        base_bone.roll = 0

        deform_bone = armature.edit_bones.new (deform_bone_name)
        deform_bone.head.x = location.x
        deform_bone.head.y = location.y
        deform_bone.head.z = location.z

        deform_bone.tail.x , deform_bone.tail.z = deform_bone.head.x , deform_bone.head.z

        deform_bone.tail.y = deform_bone.head.y + 0.05



        anchor_bone_name = deform_bone.name.replace("deform", "anchor")
        anchor_bone = armature.edit_bones.new(anchor_bone_name)
        anchor_bone.head = deform_bone.head
        anchor_bone.tail = deform_bone.tail
        anchor_bone.matrix = deform_bone.matrix

        anchor_bone.use_deform = False
        deform_bone.parent = anchor_bone

        mirror_origin_bone_name = deform_bone.name.replace("deform", "mirror_base")
        mirror_origin_bone = armature.edit_bones.new(mirror_origin_bone_name)
        mirror_origin_bone.head = mirror_origin
        mirror_origin_bone.tail = mirror_origin
        mirror_origin_bone.tail.y = mirror_origin_bone.head.y + 0.5

        mirror_origin_bone.use_deform = False

        mirror_deform_bone_position = Vector(((((location[0] - mirror_origin[0])*-1)+mirror_origin[0])
                                              , location[1], location[2]))

        mirror_deform_bone_name = deform_bone.name.replace("deform", "mirror_deform")
        mirror_deform_bone = armature.edit_bones.new(mirror_deform_bone_name)
        mirror_deform_bone.head = mirror_deform_bone_position
        mirror_deform_bone.tail = mirror_deform_bone_position
        mirror_deform_bone.tail.y = mirror_deform_bone.head.y + 0.05



        mirror_driver_bone_name = deform_bone.name.replace("deform", "mirror_driver")
        mirror_driver_bone = armature.edit_bones.new(mirror_driver_bone_name)
        mirror_driver_bone.head = deform_bone.head
        mirror_driver_bone.tail = deform_bone.tail

        mirror_driver_bone.use_deform = False

        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='POSE')

        deform_bone = soft_mod_armature.pose.bones.get(deform_bone_name)
        base_bone = soft_mod_armature.pose.bones.get(base_bone_name)
        mirror_deform_bone = soft_mod_armature.pose.bones.get(mirror_deform_bone_name)
        mirror_driver_bone = soft_mod_armature.pose.bones.get(mirror_driver_bone_name)
        mirror_origin_bone = soft_mod_armature.pose.bones.get(mirror_origin_bone_name)

        deform_bone["soft_mod_type"] = "deform_bone"
        base_bone["soft_mod_type"] = "base_bone"
        mirror_deform_bone["soft_mod_type"] = "mirror_deform_bone"
        mirror_driver_bone["soft_mod_type"] = "mirror_driver_bone"
        mirror_origin_bone["soft_mod_type"] = "mirror_origin_bone"
        mirror_origin_bone.scale[0] = -1.0


        #adding constraint
        main_const = deform_bone.constraints.new ('COPY_TRANSFORMS')
        main_const.target = bpy.data.objects[widget.name]
        main_const.target_space = "LOCAL"
        main_const.owner_space = "LOCAL"




        #adding mirror contraints
        mirror_driver_copy_const = mirror_driver_bone.constraints.new('COPY_TRANSFORMS')
        mirror_driver_copy_const.target = bpy.data.objects[soft_mod_armature.name]
        mirror_driver_copy_const.subtarget = deform_bone.name

        mirror_driver_child_of_const = mirror_driver_bone.constraints.new("CHILD_OF")
        mirror_driver_child_of_const.target = bpy.data.objects[soft_mod_armature.name]
        mirror_driver_child_of_const.subtarget = mirror_origin_bone.name
        mirror_driver_child_of_const.inverse_matrix = Matrix.Identity (4)
        wm = soft_mod_armature.matrix_world @ mirror_origin_bone.matrix.inverted()
        mirror_driver_child_of_const.inverse_matrix = wm


        mirror_deform_child_of_const = mirror_deform_bone.constraints.new('CHILD_OF')
        mirror_deform_child_of_const.target = bpy.data.objects[soft_mod_armature.name]
        mirror_deform_child_of_const.subtarget = mirror_driver_bone.name
        # print (const)
        # setting invers. This will give an error if the version of blender is higher than 2.8.3
        version = bpy.app.version
        if version <=(2, 82, 99):

            context_py = bpy.context.copy ()
            context_py["constraint"] = mirror_deform_child_of_const
            armature.bones.active = mirror_deform_bone.bone
            bpy.ops.constraint.childof_set_inverse (context_py , constraint="Child Of", owner='BONE')

        else:
            mirror_deform_child_of_const.set_inverse_pending = True

        #adding the driver
        if bpy.ops.object.mode_set.poll ():
            bpy.ops.object.mode_set (mode='OBJECT')
        # adding a driver to the contraint to the widget influence property
        inf_driver = main_const.driver_add ("influence").driver
        inf_driver.type = "SUM"
        inf_driver_var = inf_driver.variables.new ()
        inf_driver_var.targets[0].id_type = "OBJECT"
        inf_driver_var.targets[0].id = widget
        inf_driver_var.targets[0].data_path = '["influence"]'
        inf_driver_var.name = "Influence"

        #adding drivers for radius
        edit_bones = []
        edit_bones.append(armature.bones[deform_bone_name])
        edit_bones.append (armature.bones[mirror_deform_bone_name])

        for edit_bone in edit_bones:
            rad_driver = edit_bone.driver_add ("head_radius").driver
            rad_driver.type = "SCRIPTED"

            rad_driver_var = rad_driver.variables.new ()
            rad_driver_var.targets[0].id_type = "OBJECT"
            rad_driver_var.targets[0].id = widget
            rad_driver_var.targets[0].data_path = '["radius"]'

            rad_driver.expression = "{} /5".format (rad_driver_var.name)

            rad_driver = edit_bone.driver_add ("tail_radius").driver
            rad_driver.type = "SCRIPTED"

            rad_driver_var = rad_driver.variables.new ()
            rad_driver_var.targets[0].id_type = "OBJECT"
            rad_driver_var.targets[0].id = widget
            rad_driver_var.targets[0].data_path = '["radius"]'

            rad_driver.expression = "{} /5".format (rad_driver_var.name)

            rad_driver = edit_bone.driver_add ("envelope_distance").driver
            rad_driver.type = "SCRIPTED"

            rad_driver_var = rad_driver.variables.new ()
            rad_driver_var.targets[0].id_type = "OBJECT"
            rad_driver_var.targets[0].id = widget
            rad_driver_var.targets[0].data_path = '["radius"]'

            rad_driver.expression = "{}".format (rad_driver_var.name)



        soft_mod_armature.hide_viewport = True

        # adding softmods to the collection
        if collection:
            collection.objects.link(soft_mod_armature)
            bpy.context.scene.collection.objects.unlink (soft_mod_armature)
        else:
            bpy.context.scene.collection.objects.link(soft_mod_armature)

        # setting the modifier
        mod.object = soft_mod_armature
        mod.show_in_editmode = True

        return SoftArmatureHandler.from_armature(soft_mod_armature)

