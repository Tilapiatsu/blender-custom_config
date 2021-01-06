bl_info = {
	"name": "kekit_prefs",
	"author": "Kjell Emanuelsson",
	"category": "preferences",
	"version": (2, 0, 2),
	"blender": (2, 80, 0),
}
from bpy import utils
import json

from bpy.types import (
		PropertyGroup,
		Operator,
		Scene,
		AddonPreferences,
		)
from bpy.props import (
		BoolProperty,
		PointerProperty,
		FloatVectorProperty,
		IntProperty,
		FloatProperty,
		EnumProperty,
		StringProperty,
		)

# -------------------------------------------------------------------------------------------------
# EXTERNAL FILE PREFS
# -------------------------------------------------------------------------------------------------

# IO

def write_prefs(data):
    jsondata = json.dumps(data, indent=1, ensure_ascii=True)
    wpath = utils.script_path_user()
    file_name = wpath + "/ke_prefs" + ".json"
    with open(file_name, "w") as text_file:
        text_file.write(jsondata)
    text_file.close()


def read_prefs():
    wpath = utils.script_path_user()
    file_name = wpath + "/ke_prefs.json"
    try:
        with open(file_name, "r") as jf:
            prefs = json.load(jf)
            jf.close()
    except (OSError,IOError):
        prefs = None
    return prefs


def get_scene_prefs(context):
	pd = {}
	for key in context.scene.kekit.__annotations__.keys():
		k = getattr(context.scene.kekit, key)
		if str(type(k)) == "<class 'bpy_prop_array'>":
			pd[key] = k[:]
		else:
			pd[key] = k
	return  pd


# DEFAULTS

default_values = {
	'fitprim_select'		: False,
	'fitprim_modal'			: True,
	'fitprim_item'			: False,
	'fitprim_sides'			: 16,
	'fitprim_sphere_seg'	: 32,
	'fitprim_sphere_ring'	: 16,
	'fitprim_unit'			: 0.2,
	'fitprim_quadsphere_seg': 8,
	'unrotator_reset'		: True,
	'unrotator_connect'		: True,
	'unrotator_nolink'		: False,
	'unrotator_nosnap'		: True,
	'unrotator_invert'		: False,
	'unrotator_center'		: False,
	'opc1_obj_o'			: "1GLOBAL",
	'opc1_obj_p'			: "1MEDIAN_POINT",
	'opc1_edit_o'			: "1GLOBAL",
	'opc1_edit_p'			: "1MEDIAN_POINT",
	'opc2_obj_o'			: "2LOCAL",
	'opc2_obj_p'			: "3INDIVIDUAL_ORIGINS",
	'opc2_edit_o'			: "3NORMAL",
	'opc2_edit_p'			: "5ACTIVE_ELEMENT",
	'opc3_obj_o'			: "1GLOBAL",
	'opc3_obj_p'			: "3INDIVIDUAL_ORIGINS",
	'opc3_edit_o'			: "2LOCAL",
	'opc3_edit_p'			: "3INDIVIDUAL_ORIGINS",
	'opc4_obj_o'			: "6CURSOR",
	'opc4_obj_p'			: "4CURSOR",
	'opc4_edit_o'			: "6CURSOR",
	'opc4_edit_p'			: "4CURSOR",
	'selmode_mouse'			: False,
	'quickmeasure'			: True,
	'fit2grid'				: 0.01,
	'vptransform'			: False,
	'loc_got'				: True,
	'rot_got'				: True,
	'scl_got'				: True,
	'qs_user_value'			: 1.0,
	'qs_unit_size'			: True,
	'clean_doubles'			: True,
	'clean_doubles_val'		: 0.0001,
	'clean_loose'			: True,
	'clean_interior'		: True,
	'clean_degenerate'		: True,
	'clean_degenerate_val'	: 0.0001,
	'clean_collinear'		: True,
	'cursorfit'				: True,
	'lineararray_go'		: True,
	'idm01'					: (1.0, 0.0, 0.0, 1.0),
	'idm02'					: (0.6, 0.0, 0.0, 1.0),
	'idm03'					: (0.3, 0.0, 0.0, 1.0),
	'idm04'					: (0.0, 1.0, 0.0, 1.0),
	'idm05'					: (0.0, 0.6, 0.0, 1.0),
	'idm06'					: (0.0, 0.3, 0.0, 1.0),
	'idm07'					: (0.0, 0.0, 1.0, 1.0),
	'idm08'					: (0.0, 0.0, 0.6, 1.0),
	'idm09'					: (0.0, 0.0, 0.3, 1.0),
	'idm10'					: (1.0, 1.0, 1.0, 1.0),
	'idm11'					: (0.5, 0.5, 0.5, 1.0),
	'idm12'					: (0.0, 0.0, 0.0, 1.0),
	'idm01_name'			: "ID_RED",
	'idm02_name'			: "ID_RED_M",
	'idm03_name'			: "ID_RED_L",
	'idm04_name'			: "ID_GREEN",
	'idm05_name'			: "ID_GREEN_M",
	'idm06_name'			: "ID_GREEN_L",
	'idm07_name'			: "ID_BLUE",
	'idm08_name'			: "ID_BLUE_M",
	'idm09_name'			: "ID_BLUE_L",
	'idm10_name'			: "ID_ALPHA",
	'idm11_name'			: "ID_ALPHA_M",
	'idm12_name'			: "ID_ALPHA_L",
	'object_color' 			: False,
	'matvp_color' 			: False,
	'vpmuted' 				: False
}


# PROCESS

path = utils.script_path_user()
v = read_prefs()

# Default values if no prefs-file
if not v:
	v = default_values
	write_prefs(v)
	print("keKit Prefs file not found - Default settings applied")

# Update prefs if new prop is added
elif len(default_values) > len(v):
	for p in default_values:
		if p not in v:
			v[p] = default_values.get(p)
	write_prefs(v)
	print("keKit Prefs is old/missing items - Updating prefs")

else:
	print("keKit Prefs location:", path)
	print("keKit Prefs found - File Settings Applied")


# PROPERTIES

class kekit_properties(PropertyGroup):
	# Fitprim
	fitprim_select : BoolProperty(default=v["fitprim_select"])
	fitprim_modal : BoolProperty(default=v["fitprim_modal"])
	fitprim_item : BoolProperty(default=v["fitprim_item"])
	fitprim_sides : IntProperty(min=3, max=256, default=v["fitprim_sides"])
	fitprim_sphere_seg : IntProperty(min=3, max=256, default=v["fitprim_sphere_seg"])
	fitprim_sphere_ring : IntProperty(min=3, max=256, default=v["fitprim_sphere_ring"])
	fitprim_unit : FloatProperty(min=.00001, max=256, default=v["fitprim_unit"])
	fitprim_quadsphere_seg : IntProperty(min=1, max=128, default=v["fitprim_quadsphere_seg"])
	# Unrotator
	unrotator_reset : BoolProperty(default=v["unrotator_reset"])
	unrotator_connect : BoolProperty(default=v["unrotator_connect"])
	unrotator_nolink : BoolProperty(default=v["unrotator_nolink"])
	unrotator_nosnap : BoolProperty(default=v["unrotator_nosnap"])
	unrotator_invert : BoolProperty(default=v["unrotator_invert"])
	unrotator_center: BoolProperty(default=v["unrotator_center"])
	# Orientation & Pivot Combo 1
	opc1_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc1_obj_o"])
	opc1_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc1_obj_p"])
	opc1_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")], name="Orientation", default=v["opc1_edit_o"])
	opc1_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc1_edit_p"])
	# Orientation & Pivot Combo 2
	opc2_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc2_obj_o"])
	opc2_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc2_obj_p"])
	opc2_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default=v["opc2_edit_o"])
	opc2_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc2_edit_p"])
	# Orientation & Pivot Combo 3
	opc3_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc3_obj_o"])
	opc3_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc3_obj_p"])
	opc3_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc3_edit_o"])
	opc3_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc3_edit_p"])
	# Orientation & Pivot Combo 4
	opc4_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=v["opc4_obj_o"])
	opc4_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=v["opc4_obj_p"])
	opc4_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=v["opc4_edit_o"])
	opc4_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=v["opc4_edit_p"])
	# Mouse Over Mode Toggle
	selmode_mouse : BoolProperty(description="Mouse-Over Mode Toggle", default=v["selmode_mouse"])
	# QuickMeasure  - default: 1
	quickmeasure : BoolProperty(default=v["quickmeasure"])
	# Fit2Grid - default : 0.01
	fit2grid : FloatProperty(min=.00001, max=10000, default=v["fit2grid"])
	# ViewPlane Contextual - default : 1
	vptransform : BoolProperty(description="VPAutoGlobal - Sets Global orientation. Overrides GOT options",default=v["vptransform"])
	loc_got : BoolProperty(description="Grab GlobalOrTool - VPGrab when Global, otherwise Transform (gizmo)",default=v["loc_got"])
	rot_got : BoolProperty(description="Rotate GlobalOrTool - VPRotate when Global, otherwise Rotate (gizmo)",default=v["rot_got"])
	scl_got : BoolProperty(description="Scale GlobalOrTool - VPResize when Global, otherwise Scale (gizmo)",default=v["scl_got"])
	# Quick Scale
	qs_user_value : FloatProperty(default=v["qs_user_value"], precision=3)
	qs_unit_size : BoolProperty(default=v["qs_unit_size"])
	# Cleaning Tools
	clean_doubles : BoolProperty(default=v["clean_doubles"])
	clean_doubles_val : FloatProperty(default=v["clean_doubles_val"], precision=4)
	clean_loose : BoolProperty(default=v["clean_loose"])
	clean_interior : BoolProperty(default=v["clean_interior"])
	clean_degenerate : BoolProperty(default=v["clean_degenerate"])
	clean_degenerate_val : FloatProperty(default=v["clean_degenerate_val"], precision=4)
	clean_collinear : BoolProperty(default=v["clean_collinear"])
	# Cursor Fit OP Option
	cursorfit : BoolProperty(description="Also set Orientation & Pivot to Cursor", default=v["cursorfit"])
	# Linear Array Global Only Option
	lineararray_go : BoolProperty(description="Applies Rotation and usese Global Orientation & Pivot during modal", default=v["lineararray_go"])
	# Material ID Colors
	idm01 : FloatVectorProperty(name="IDM01", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm01"])
	idm02 : FloatVectorProperty(name="IDM02", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm02"])
	idm03 : FloatVectorProperty(name="IDM03", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm03"])
	idm04 : FloatVectorProperty(name="IDM04", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm04"])
	idm05 : FloatVectorProperty(name="IDM05", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm05'])
	idm06 : FloatVectorProperty(name="IDM06", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm06'])
	idm07 : FloatVectorProperty(name="IDM07", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm07'])
	idm08 : FloatVectorProperty(name="IDM08", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm08'])
	idm09 : FloatVectorProperty(name="IDM09", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm09'])
	idm10 : FloatVectorProperty(name="IDM10", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm10'])
	idm11 : FloatVectorProperty(name="IDM11", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm11'])
	idm12 : FloatVectorProperty(name="IDM12", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm12'])
	# Material ID Names
	idm01_name : StringProperty(default=v["idm01_name"])
	idm02_name : StringProperty(default=v["idm02_name"])
	idm03_name : StringProperty(default=v["idm03_name"])
	idm04_name : StringProperty(default=v["idm04_name"])
	idm05_name : StringProperty(default=v["idm05_name"])
	idm06_name : StringProperty(default=v["idm06_name"])
	idm07_name : StringProperty(default=v["idm07_name"])
	idm08_name : StringProperty(default=v["idm08_name"])
	idm09_name : StringProperty(default=v["idm09_name"])
	idm10_name : StringProperty(default=v["idm10_name"])
	idm11_name : StringProperty(default=v["idm11_name"])
	idm12_name : StringProperty(default=v["idm12_name"])
	# Material ID Options
	object_color : BoolProperty(description="Set ID color also to Object Viewport Display",default=v["object_color"])
	matvp_color : BoolProperty(description="Set ID color also to Material Viewport Display", default=v["matvp_color"])
	vpmuted : BoolProperty(description="Tone down ID colors slightly for Viewport Display (only)", default=v["vpmuted"])

# MENU OP FOR PREFS SAVING

class VIEW3D_OT_ke_prefs_save(Operator):
	bl_idname = "view3d.ke_prefs_save"
	bl_label = "Save Settings"
	bl_description = "Saves current kit settings (prefs-file, global & persistent)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	def execute(self, context):
		prefs = get_scene_prefs(context)
		write_prefs(prefs)
		self.report({"INFO"}, "keKit Settings Saved!")
		return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Add-On Preferences
# -------------------------------------------------------------------------------------------------

class kekit_addon_preferences(AddonPreferences):
	bl_idname = __package__

	modal_color_header  : FloatVectorProperty(name="Modal Header Text Color", subtype='COLOR',
											  size=4, default=[0.8, 0.8, 0.8, 1.0])
	modal_color_text    : FloatVectorProperty(name="Modal Text Color", subtype='COLOR',
											  size=4, default=[0.8, 0.8, 0.8, 1.0])
	modal_color_subtext : FloatVectorProperty(name="Modal Sub-Text Color", subtype='COLOR',
											  size=4, default=[0.5, 0.5, 0.5, 1.0])

	def draw(self, context):
		layout = self.layout
		box = layout.box()
		row = box.row()
		row.prop(self, 'modal_color_header')
		row = box.row()
		row.prop(self, 'modal_color_text')
		row = box.row()
		row.prop(self, 'modal_color_subtext')


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	kekit_properties,
	VIEW3D_OT_ke_prefs_save,
	kekit_addon_preferences,
	)

def register():

	for cls in classes:
		utils.register_class(cls)

	Scene.kekit = PointerProperty(type=kekit_properties)

	prefs = read_prefs()
	if not prefs:
		print("keKit Prefs file not found - Default settings applied")
		write_prefs(default_values)

def unregister():
	for cls in reversed(classes):
		utils.unregister_class(cls)
	try:
		del Scene.kekit
	except Exception as e:
		print('unregister fail:\n', e)
		pass

if __name__ == "__main__":
	register()
