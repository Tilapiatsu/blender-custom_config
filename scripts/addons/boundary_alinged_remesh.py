# This is a remeshing algorithm that only uses blender-native operations.
# It Works in a similar fashion to Toporake feature of dyntopo.

bl_info = {
	"name": "Boundary Aligned Remesh",
	"author": "Jean Da Costa, Bookyakuno(ver1.1.0-)",
	"version": (1, 1, 0),
	"blender": (2, 83, 0),
	"location": "Property > Mesh Data > Remesh > Boundary Aligned Remesh",
	"description": "Rebuilds mesh out of isotropic polygons.",
	"warning": "",
	"wiki_url": "",
	"category": "Remesh",
}

import bpy, bmesh, math,itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from bpy.types import Operator, AddonPreferences, Panel, PropertyGroup
from bpy.props import *

# Main Remesher class, this stores all the needed data
class BoundaryAlignedRemesher:


	def get_hold_edges(self, obj):
		sc = bpy.context.scene
		props = sc.ba_remesh

		split_edge_l = []

		# create layer
		if props.use_edge_bevel_weight:
			if self.bm.edges.layers.bevel_weight:
				bevelweight_Layer = self.bm.edges.layers.bevel_weight.verify()

		if props.use_edge_crease:
			if self.bm.edges.layers.crease:
				crease_Layer = self.bm.edges.layers.crease.verify()

		if props.use_edge_freestyle:
			if self.bm.edges.layers.freestyle:
				freestyle_Layer = self.bm.edges.layers.freestyle.verify()


		# find edge
		for edge in self.bm.edges:
			# 選択
			if props.use_edge_select:
				if edge.select:
					split_edge_l.append(edge)

			# 角度
			if props.use_edge_angle:
				try:
					if math.degrees(edge.calc_face_angle()) >= props.edge_angle:
						split_edge_l.append(edge)
				except: pass

			# シーム
			if props.use_edge_seam:
				if edge.seam:
					split_edge_l.append(edge)

			# シャープ
			if props.use_edge_sharp:
				if not edge.smooth: # sharp
					split_edge_l.append(edge)

			# ベベルウェイト
			if props.use_edge_bevel_weight:
				if self.bm.edges.layers.bevel_weight:
					if edge[bevelweight_Layer]:
						split_edge_l.append(edge)

			# クリース
			if props.use_edge_crease:
				if self.bm.edges.layers.crease:
					if edge[crease_Layer]:
						split_edge_l.append(edge)

			# Freestyle
			if props.use_edge_freestyle:
				if self.bm.edges.layers.freestyle:
					if edge[freestyle_Layer]:
						split_edge_l.append(edge)


		# 重複を削除
		new_split_edge_l = []
		for i in split_edge_l:
			if not i in new_split_edge_l:
				new_split_edge_l.append(i)

		return new_split_edge_l


	def split_feature_edges(self, obj):
		new_split_edge_l = self.get_hold_edges(obj)

		if new_split_edge_l:
			bmesh.ops.split_edges(self.bm, edges=new_split_edge_l)


	def __init__(self, obj):
		self.obj = object

		self.bm = bmesh.new()
		self.bm.from_mesh(obj.data)
		self.bvh = BVHTree.FromBMesh(self.bm)

		# ホールドエッジ
		self.split_feature_edges(obj)

		# 開いたエッジのガイド
		# Boundary_data is a list of directions and locations of boundaries.
		# This data will serve as guidance for the alignment
		self.boundary_data = []


		# Fill the data using boundary edges as source of directional data.
		for edge in self.bm.edges:
			if edge.is_boundary:
				vec = (edge.verts[0].co - edge.verts[1].co).normalized()
				center = (edge.verts[0].co + edge.verts[1].co) / 2

				self.boundary_data.append((center, vec))




		# Create a Kd Tree to easily locate the nearest boundary point
		self.boundary_kd_tree = KDTree(len(self.boundary_data))

		for index, (center, vec) in enumerate(self.boundary_data):
			self.boundary_kd_tree.insert(center, index)

		self.boundary_kd_tree.balance()


	def nearest_boundary_vector(self, location):
		""" Gets the nearest boundary direction """
		location, index, dist = self.boundary_kd_tree.find(location)
		location, vec = self.boundary_data[index]
		return vec


	def enforce_edge_length(self, edge_length=0.05, bias=0.333):
		""" Replicates dyntopo behaviour """
		upper_length = edge_length + edge_length * bias
		lower_length = edge_length - edge_length * bias

		# Subdivide Long edges
		subdivide = []
		for edge in self.bm.edges:
			if edge.calc_length() > upper_length:
				subdivide.append(edge)

		bmesh.ops.subdivide_edges(self.bm, edges=subdivide, cuts=1)
		bmesh.ops.triangulate(self.bm, faces=self.bm.faces)

		# Remove verts with less than 5 edges, this helps inprove mesh quality
		dissolve_verts = []
		for vert in self.bm.verts:
			if len(vert.link_edges) < 5:
				if not vert.is_boundary:
					dissolve_verts.append(vert)

		bmesh.ops.dissolve_verts(self.bm, verts=dissolve_verts)
		bmesh.ops.triangulate(self.bm, faces=self.bm.faces)

		# 外側エッジを固定
		# Collapse short edges but ignore boundaries and never collapse two chained edges
		lock_verts = set(vert for vert in self.bm.verts if vert.is_boundary)
		collapse = []

		for edge in self.bm.edges:
			if edge.calc_length() < lower_length and not edge.is_boundary:
				verts = set(edge.verts)
				if verts & lock_verts:
					continue
				collapse.append(edge)
				lock_verts |= verts

		bmesh.ops.collapse(self.bm, edges=collapse)
		bmesh.ops.beautify_fill(self.bm, faces=self.bm.faces, method="ANGLE")


	def align_verts(self, rule=(-1, -2, -3, -4)):
		# Align verts to the nearest boundary by averaging neigbor vert locations selected
		# by a specific rule,

		# Rules work by sorting edges by angle relative to the boundary.
		# Eg1. (0, 1) stands for averagiing the biggest angle and the 2nd biggest angle edges.
		# Eg2. (-1, -2, -3, -4), averages the four smallest angle edges
		for vert in self.bm.verts:
			if not vert.is_boundary:
				vec = self.nearest_boundary_vector(vert.co)
				neighbor_locations = [edge.other_vert(vert).co for edge in vert.link_edges]
				best_locations = sorted(neighbor_locations,
										key = lambda n_loc: abs((n_loc - vert.co).normalized().dot(vec)))
				co = vert.co.copy()
				le = len(vert.link_edges)
				for i in   rule:
					co += best_locations[i % le]
				co /= len(rule) + 1
				co -= vert.co
				co -= co.dot(vert.normal) * vert.normal
				vert.co += co


	def reproject(self):
		""" Recovers original shape """
		for vert in self.bm.verts:
			location, normal, index, dist = self.bvh.find_nearest(vert.co)
			if location:
				vert.co = location


	def remesh(self,edge_length=0.05, iterations=30, quads=True):
		""" Coordenates remeshing """
		if quads:
			rule = (-1,-2, 0, 1)
		else:
			rule = (0, 1, 2, 3)

		for _ in range(iterations):
			self.enforce_edge_length(edge_length=edge_length)
			try:
				self.align_verts(rule=rule)
			except: pass
			self.reproject()



		if quads:
			bmesh.ops.join_triangles(self.bm, faces=self.bm.faces,
									 angle_face_threshold=3.14,
									 angle_shape_threshold=3.14)

		bmesh.ops.remove_doubles(self.bm,verts=self.bm.verts, dist=0.001)

		return self.bm


class BAREMESH_PT_Remesher(Operator):
	bl_idname = "ba_remesh.boundary_aligned_remesh"
	bl_label = "Boundary Aligned Remesh"
	bl_options = {"REGISTER", "UNDO"}

	edge_length                : FloatProperty(name="Edge Length", min=0, default = 0.1)
	iterations                 : IntProperty(name="Iterations", min=1, default=30)
	quads                      : BoolProperty(name="Quad", default=True)


	def invoke(self, context,event):
		sc = bpy.context.scene
		props = sc.ba_remesh

		self.edge_length = props.edge_length
		self.iterations = props.iterations
		self.quads = props.quads

		return self.execute(context)


	def execute(self, context):
		obj = bpy.context.active_object
		sc = bpy.context.scene
		props = sc.ba_remesh

		if props.use_uv_transfer:
			backup_obj = obj.copy()
			backup_obj.data = obj.data.copy()

		# モードを切り替え
		is_edit = False
		if obj.mode == "EDIT":
			is_edit = True
			bpy.ops.object.mode_set(mode="OBJECT")


		# リメッシュ
		# print(f"Remeshing {obj.name}")
		remesher = BoundaryAlignedRemesher(obj)
		bm = remesher.remesh(self.edge_length, self.iterations, self.quads)


		# # 2辺頂点を除去
		if props.remove_verts_link_2_edges:
			vert_l = [v for v in bm.verts
				if len(v.link_edges) == 2
				if math.degrees(v.calc_edge_angle()) <= 45
				]

			if vert_l:
				bmesh.ops.dissolve_verts(bm, verts=vert_l)



		# アウトラインのポリゴンを減らす
		if props.boundary_reduce_verts:
			# アウトラインの頂点
			outline_vert_l = [v for e in bm.edges if e.is_boundary for v in e.verts]
			outline_vert_l = list(set(outline_vert_l))

			# ホールドエッジの頂点
			hold_edge_l = remesher.get_hold_edges(obj)
			hold_verts_l = [v for e in hold_edge_l for v in e.verts]
			hold_verts_l = list(set(hold_verts_l))

			# ホールドエッジ以外を近接頂点結合
			outline_vert_l = [v for v in outline_vert_l if not v in hold_verts_l]

			if outline_vert_l:
				bmesh.ops.remove_doubles(bm, verts=outline_vert_l, dist=0.1)
				# bmesh.ops.triangulate(bm, faces=bm.faces)




			# ホールドエッジの頂点
			hold_edge_l = remesher.get_hold_edges(obj)
			hold_faces_l = [f for e in hold_edge_l for f in e.link_faces]
			# hold_faces_l = [f for e in hold_edge_l for v in e.verts for f in v.link_faces]

			hold_faces_l = list(set(hold_faces_l))
			do_quad_face_l = [f for f in bm.faces if not f in hold_faces_l]

			# ホールドエッジ面以外の前メッシュの面の、三角形を除去
			if self.quads:
				bmesh.ops.join_triangles(bm, faces=do_quad_face_l,
										 angle_face_threshold=3.14,
										 angle_shape_threshold=3.14)


		# インセット
		if props.boundary_loop_add:
			face_l = [f for f in bm.faces]
			bmesh.ops.inset_region(bm, faces = face_l,
									thickness=props.boundary_loop_offset,
									use_boundary=True,
									use_interpolate=True,
									)
		# bmesh.ops.inset_region(bm, faces,
		# 						faces_exclude,
		# 						use_boundary,
		# 						use_even_offset,
		# 						use_interpolate,
		# 						use_relative_offset,
		# 						use_edge_rail,
		# 						thickness,
		# 						depth,
		# 						use_outset)


		# メッシュ編集を完了
		bm.to_mesh(obj.data)

		if True in {props.use_mirror_x,props.use_mirror_y,props.use_mirror_z}:
			self.mod_mirror(context,obj)

		# UVを転送
		if props.use_uv_transfer:
			if obj.data.uv_layers:
				self.mod_uv_transfer(context,obj,backup_obj)


		# モードを戻す
		if is_edit:
			bpy.ops.object.mode_set(mode="EDIT")


		# バックアップオブジェクトを削除
		if props.use_uv_transfer:
			if backup_obj:
				bpy.data.objects.remove(backup_obj)


		# ビューポートを更新
		for area in context.screen.areas:
			area.tag_redraw()

		return {"FINISHED"}


	def mod_mirror(self,context,obj):
		sc = bpy.context.scene
		props = sc.ba_remesh

		mod = obj.modifiers.new(name="Mirror" , type="MIRROR")

		if props.use_mirror_x:
			mod.use_axis[0] = True
			mod.use_bisect_axis[0] = True

		if props.use_mirror_y:
			mod.use_axis[1] = True
			mod.use_bisect_axis[1] = True

		if props.use_mirror_z:
			mod.use_axis[2] = True
			mod.use_bisect_axis[2] = True

		bpy.ops.object.modifier_apply(modifier=mod.name)


	def mod_uv_transfer(self,context,obj,tgt_obj):
		mod = obj.modifiers.new(name="Data Transfer" , type="DATA_TRANSFER")
		mod.object = tgt_obj
		mod.use_object_transform = False
		mod.use_loop_data = True
		mod.data_types_loops = {'UV'}
		bpy.ops.object.modifier_apply(modifier=mod.name)


class BAREMESH_OT_remesh_size_up_down(Operator):
	bl_idname = "ba_remesh.remesh_size_up_down"
	bl_label = "Remesh Size Up/Down"
	bl_description = ""
	bl_options = {'REGISTER','UNDO'}

	up : BoolProperty(default=False)

	def execute(self, context):
		sc = bpy.context.scene
		props = sc.ba_remesh
		if self.up:
			props.edge_length /= 2

		else:
			props.edge_length *= 2
		return {'FINISHED'}



def draw_context_menu(self, context):
	layout = self.layout
	layout.operator("ba_remesh.boundary_aligned_remesh")

def draw_panel(self, context):
	layout = self.layout
	sc = bpy.context.scene
	props = sc.ba_remesh

	layout.separator()
	box = layout.box()
	row = box.row(align=True)
	row.scale_y = 1.2
	row.operator("ba_remesh.boundary_aligned_remesh")
	col = box.column(align=True)
	row = col.row(align=True)
	row.prop(props,"edge_length")
	row.operator("ba_remesh.remesh_size_up_down",text="",icon="SORT_ASC").up = True
	row.operator("ba_remesh.remesh_size_up_down",text="",icon="SORT_DESC").up = False
	col.prop(props,"iterations")
	col.prop(props,"quads")
	col.prop(props,"boundary_reduce_verts")
	col.prop(props,"remove_verts_link_2_edges")
	col.prop(props,"use_uv_transfer")
	sp = col.split(align=True,factor=0.5)
	sp.use_property_split = False
	row = sp.row(align=True)
	row.alignment ="RIGHT"
	row.label(text="Mirror",icon="NONE")
	row = sp.row(align=True)
	row.prop(props,"use_mirror_x",text="X",icon="BLANK1")
	row.prop(props,"use_mirror_y",text="Y",icon="BLANK1")
	row.prop(props,"use_mirror_z",text="Z",icon="BLANK1")

	col.prop(props,"boundary_loop_add")


	row = col.row(align=True)
	row.active = props.boundary_loop_add
	row.prop(props,"boundary_loop_offset")

	boxs = box.box()
	boxs.label(text="Hold Edge Type",icon="NONE")
	col = boxs.column(align=True)
	col.prop(props,"use_edge_angle")
	row = col.row(align=True)
	row.active = props.use_edge_angle
	row.prop(props,"edge_angle")

	col.separator()

	col.prop(props,"use_edge_select")
	col.prop(props,"use_edge_seam")
	col.prop(props,"use_edge_sharp")
	col.prop(props,"use_edge_bevel_weight")
	col.prop(props,"use_edge_crease")
	col.prop(props,"use_edge_freestyle")



class BAREMESH_PR_main(PropertyGroup):
	edge_length                : FloatProperty(name="Edge Length", min=0, default = 0.1)
	iterations                 : IntProperty(name="Iterations", min=1, default=30)
	quads                      : BoolProperty(name="Quad", default=True)
	boundary_reduce_verts       : BoolProperty(name="Reduce boundary vertex", default=False)
	remove_verts_link_2_edges  : BoolProperty(name="Remove vertices 2 link edges", default=True)
	use_uv_transfer            : BoolProperty(name="UV Transfer", default=True)
	use_mirror_x            : BoolProperty(name="Mirror X")
	use_mirror_y            : BoolProperty(name="Mirror Y")
	use_mirror_z            : BoolProperty(name="Mirror Z")

	use_edge_select            : BoolProperty(name="Select")
	use_edge_seam              : BoolProperty(name="Seam", default=True)
	use_edge_sharp             : BoolProperty(name="Sharp", default=True)
	use_edge_bevel_weight      : BoolProperty(name="Bevel Weight")
	use_edge_crease            : BoolProperty(name="Crease")
	use_edge_freestyle         : BoolProperty(name="Freestyle Edge Mark")
	use_edge_angle             : BoolProperty(name="Edge Angle")

	boundary_loop_add             : BoolProperty(name="Add Boundary Loop")
	boundary_loop_offset             : FloatProperty(name="Offset",min=0.0001,default=0.02)
	edge_angle                 : FloatProperty(name="Edge Angle", description = "", default = 1.0466667, min = 0, max = 3.14,subtype = 'ANGLE')
	edge_angle                 : FloatProperty(name="Edge Angle", description = "", default = 1.0466667, min = 0, max = 3.14,subtype = 'ANGLE')


classes = (
BAREMESH_OT_remesh_size_up_down,
BAREMESH_PT_Remesher,
BAREMESH_PR_main,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.ba_remesh = PointerProperty(type=BAREMESH_PR_main)

	bpy.types.DATA_PT_remesh.append(draw_panel)
	bpy.types.VIEW3D_PT_sculpt_voxel_remesh.append(draw_panel)
	bpy.types.VIEW3D_MT_object_context_menu.append(draw_context_menu)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	bpy.types.DATA_PT_remesh.remove(draw_panel)
	bpy.types.VIEW3D_PT_sculpt_voxel_remesh.remove(draw_panel)
	bpy.types.VIEW3D_MT_object_context_menu.append(draw_panel)

	del bpy.types.Scene.ba_remesh

if __name__ == "__main__":
	register()
