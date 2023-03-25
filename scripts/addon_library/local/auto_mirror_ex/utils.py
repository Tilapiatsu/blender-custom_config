import bpy
import os, csv, codecs #辞書


def preference():
	preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

	return preference


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			for context in bpy.app.translations.contexts:
				dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict


# モディファイアをソート
def sort_top_mod(self,context,obj,mod,move_count):
	old_act = bpy.context.view_layer.objects.active

	bpy.context.view_layer.objects.active = obj

	if not self.sort_top_mod:
		return

	if not len(obj.modifiers) > 1:
		return

	modindex = len(obj.modifiers) - move_count
	for i in range(modindex):
		bpy.ops.object.modifier_move_up(modifier=mod.name)


	bpy.context.view_layer.objects.active = old_act



# メッシュ モディファイア
mesh_mod_items = [
	('', 'Modify', 'description', 'None', 0) ,
	("DATA_TRANSFER", "Data Transfer","","MOD_DATA_TRANSFER",0),
	("MESH_CACHE", "Mesh Cache","","MOD_MESHDEFORM",1),
	("MESH_SEQUENCE_CACHE", "Mesh Sequence Cache","","MOD_MESHDEFORM",2),
	("NORMAL_EDIT", "Normal Edit","","MOD_NORMALEDIT",3),
	("WEIGHTED_NORMAL", "Weighted Normal","","MOD_NORMALEDIT",4),
	("UV_PROJECT", "UV Project","","MOD_UVPROJECT",5),
	("UV_WARP", "UV Warp","","MOD_UVPROJECT",6),
	("VERTEX_WEIGHT_EDIT", "Vertex Weight Edit","","MOD_VERTEX_WEIGHT",7),
	("VERTEX_WEIGHT_MIX", "Vertex Weight Mix","","MOD_VERTEX_WEIGHT",8),
	("VERTEX_WEIGHT_PROXIMITY", "Vertex Weight Proximity","","MOD_VERTEX_WEIGHT",9),
	('', 'Generate', 'description', 'None', 0) ,
	("ARRAY", "Array","","MOD_ARRAY",11),
	("BEVEL", "Bevel","","MOD_BEVEL",12),
	("BOOLEAN", "Boolean","","MOD_BOOLEAN",13),
	("BUILD", "Build","","MOD_BUILD",14),
	("DECIMATE", "Decimate","","MOD_DECIM",15),
	("NODES", "Geometry Node","","NODETREE",16),
	("EDGE_SPLIT", "Edge Split","","MOD_EDGESPLIT",17),
	("MASK", "Mask","","MOD_MASK",18),
	("MIRROR", "Mirror","","MOD_MIRROR",19),
	("MULTIRES", "Multiresolution","","MOD_MULTIRES",20),
	("REMESH", "Remesh","","MOD_REMESH",21),
	("SCREW", "Screw","","MOD_SCREW",22),
	("SKIN", "Skin","","MOD_SKIN",23),
	("SOLIDIFY", "Solidify","","MOD_SOLIDIFY",24),
	("SUBSURF", "Subdivision Surface","","MOD_SUBSURF",25),
	("TRIANGULATE", "Triangulate","","MOD_TRIANGULATE",26),
	("WELD", "Weld","","AUTOMERGE_OFF",27),
	("WIREFRAME", "Wireframe","","MOD_WIREFRAME",28),
	('', 'Deform', 'description', 'None', 0) ,
	("ARMATURE", "Armature","","MOD_ARMATURE",29),
	("CAST", "Cast","","MOD_CAST",30),
	("CURVE", "Curve","","MOD_CURVE",31),
	("DISPLACE", "Displace","","MOD_DISPLACE",32),
	("HOOK", "Hook","","HOOK",33),
	("LAPLACIANDEFORM", "Laplacian Deform","","MOD_MESHDEFORM",34),
	("LATTICE", "Lattice","","MOD_LATTICE",35),
	("MESH_DEFORM", "Mesh Deform","","MOD_MESHDEFORM",36),
	("SHRINKWRAP", "Shrinkwrap","","MOD_SHRINKWRAP",37),
	("SIMPLE_DEFORM", "Simple Deform","","MOD_SIMPLEDEFORM",38),
	("SMOOTH", "Smooth","","MOD_SMOOTH",39),
	("CORRECTIVE_SMOOTH", "Smooth Corrective","","MOD_SMOOTH",40),
	("LAPLACIANSMOOTH", "Smooth Laplacian","","MOD_SMOOTH",41),
	("SURFACE_DEFORM", "Surface Deform","","MOD_MESHDEFORM",42),
	("WARP", "Warp","","MOD_WARP",43),
	("WAVE", "Wave","","MOD_WAVE",44),
	('', 'Physics', 'description', 'None', 0) ,
	("CLOTH", "Cloth","","MOD_CLOTH",46),
	("COLLISION", "Collision","","MOD_PHYSICS",47),
	("DYNAMIC_PAINT", "Dynamic Paint","","MOD_DYNAMICPAINT",48),
	("EXPLODE", "Explode","","MOD_EXPLODE",49),
	("OCEAN", "Ocean","","MOD_OCEAN",50),
	("PARTICLE_INSTANCE", "Particle Instance","","MOD_PARTICLE_INSTANCE",51),
	("PARTICLE_SYSTEM", "Particle System","","PARTICLES",52),
	("FLUID", "Fluid Simulation","","MOD_FLUID",53),
	("SOFT_BODY", "Soft Body","","MOD_SOFT",54),
	]


# グリースペンシル モディファイア
gp_mod_items = [
	('', 'Modify', 'description', 'None', 0) ,
	("GP_TEXTURE", "Texture Mapping", "Change stroke uv texture values", "MOD_UVPROJECT", 0),
	("GP_TIME", "Time Offset", "Offset keyframes", "MOD_TIME", 1),
	("GP_WEIGHT_ANGLE", "Vertex Weight Angle", "Generate Vertex Weights base on stroke angle", "MOD_VERTEX_WEIGHT", 2),
	("GP_WEIGHT_PROXIMITY", "Vertex Weight Proximity", "Generate Vertex Weights base on distance to object", "MOD_VERTEX_WEIGHT", 3),
	('', 'Generate', 'description', 'None', 0) ,
	("GP_ARRAY", "Array", "Create array of duplicate instances", "MOD_ARRAY", 4),
	("GP_BUILD", "Build", "Create duplication of strokes", "MOD_BUILD", 5),
	("GP_DASH", "Dot Dash", "Generate dot-dash styled strokes", "MOD_DASH", 6),
	("GP_LENGTH", "Length", "Extend or shrink strokes", "MOD_LENGTH", 7),
	("GP_LINEART", "Line Art", "Generate line art strokes from selected source", "MOD_LINEART", 8),
	("GP_MIRROR", "Mirror", "Duplicate strokes like a mirror", "MOD_MIRROR", 9),
	("GP_MULTIPLY", "Multiple Strokes", "Produce multiple strokes along one stroke", "GP_MULTIFRAME_EDITING", 10),
	("GP_SIMPLIFY", "Simplify", "Simplify stroke reducing number of points", "MOD_SIMPLIFY", 11),
	("GP_SUBDIV", "Subdivide", "Subdivide stroke adding more control points", "MOD_SUBSURF", 12),
	('', 'Deform', 'description', 'None', 0) ,
	("GP_ARMATURE", "Armature", "Deform stroke points using armature object", "MOD_ARMATURE", 13),
	("GP_HOOK", "Hook", "Deform stroke points using objects", "HOOK", 14),
	("GP_LATTICE", "Lattice", "Deform strokes using lattice", "MOD_LATTICE", 15),
	("GP_NOISE", "Noise", "Add noise to strokes", "MOD_NOISE", 16),
	("GP_OFFSET", "Offset", "Change stroke location, rotation or scale", "MOD_OFFSET", 17),
	("GP_SMOOTH", "Smooth", "Smooth stroke", "MOD_SMOOTH", 18),
	("GP_THICK", "Thickness", "Change stroke thickness", "MOD_THICKNESS", 19),
	("GP_COLOR", "Hue/Saturation", "Apply changes to stroke colors", "OPTIONS", 20),
	("GP_OPACITY", "Opacity", "Opacity of the strokes", "XRAY", 21),
	("GP_TINT", "Tint", "Tint strokes with new color", "RESTRICT_COLOR_OFF", 22),
]
