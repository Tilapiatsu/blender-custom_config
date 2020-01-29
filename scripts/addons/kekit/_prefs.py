bl_info = {
	"name": "kekit_prefs",
	"author": "Kjell Emanuelsson",
	"category": "preferences",
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
}
import bpy
import re

from bpy.types import (
		PropertyGroup,
		Operator,
		)
from bpy.props import (
		BoolProperty,
		PointerProperty,
		StringProperty,
		IntProperty,
		FloatProperty,
		)

# GLOBAL SETTINGS --------------------------------------------------------------------------------

def write_prefs(data):
	path = bpy.utils.script_path_user()
	file_name = path + "//addons/kekit/ke_prefs"
	with open(file_name, "w") as text_file:
		text_file.write(str(data))


def read_prefs():
	try:
		path = bpy.utils.script_path_user()
		file_name = path + "//addons/kekit/ke_prefs"
		f = open(file_name, "r")
		prefs = f.read()
	except:
		prefs = None
	return prefs


def get_prefs(): # Everything down here floats
	set_values = (
		float(bpy.context.scene.kekit.fitprim_select),
		float(bpy.context.scene.kekit.fitprim_modal),
		float(bpy.context.scene.kekit.fitprim_item),
		float(bpy.context.scene.kekit.fitprim_sides),
		float(bpy.context.scene.kekit.fitprim_sphere_seg),
		float(bpy.context.scene.kekit.fitprim_sphere_ring),
		round(float(bpy.context.scene.kekit.fitprim_unit), 4),
		float(bpy.context.scene.kekit.unrotator_reset),
		float(bpy.context.scene.kekit.unrotator_connect),
		float(bpy.context.scene.kekit.unrotator_nolink),
		float(bpy.context.scene.kekit.opc1_obj_o[0] + bpy.context.scene.kekit.opc1_obj_p[0] +
			  bpy.context.scene.kekit.opc1_edit_o[0] + bpy.context.scene.kekit.opc1_edit_p[0]),
		float(bpy.context.scene.kekit.opc2_obj_o[0] + bpy.context.scene.kekit.opc2_obj_p[0] +
			  bpy.context.scene.kekit.opc2_edit_o[0] + bpy.context.scene.kekit.opc2_edit_p[0]),
		float(bpy.context.scene.kekit.opc3_obj_o[0] + bpy.context.scene.kekit.opc3_obj_p[0] +
			  bpy.context.scene.kekit.opc3_edit_o[0] + bpy.context.scene.kekit.opc3_edit_p[0]),
		float(bpy.context.scene.kekit.opc4_obj_o[0] + bpy.context.scene.kekit.opc4_obj_p[0] +
			  bpy.context.scene.kekit.opc4_edit_o[0] + bpy.context.scene.kekit.opc4_edit_p[0]))
	# print (set_values)
	return set_values


# WIP props ---------------------------------------------------------------------------------------
# Todo: Just use JSON...?

prefs_data = read_prefs()
prefs_data_default = 0, 1, 0, 16, 32, 16, 0.2, 1, 1, 0, 1111, 2335, 1315, 6464
o_dict = {1: "1GLOBAL", 2: "2LOCAL", 3: "3NORMAL", 4: "4GIMBAL", 5: "5VIEW", 6: "6CURSOR"}
p_dict = {1: "1MEDIAN_POINT", 2: "2BOUNDING_BOX_CENTER", 3: "3INDIVIDUAL_ORIGINS", 4: "4CURSOR", 5: "5ACTIVE_ELEMENT"}

if prefs_data:
	values = [float(v) for v in re.findall(r'-?\d+\.?\d*', prefs_data)]
	print("keKit Prefs file found - File settings applied")
else:
	values = prefs_data_default
	print("keKit Prefs file not found - Default settings applied")

# Enumprop hack...
opc1_nrs = [int(i) for i in str(int(values[10]))]
opc2_nrs = [int(i) for i in str(int(values[11]))]
opc3_nrs = [int(i) for i in str(int(values[12]))]
opc4_nrs = [int(i) for i in str(int(values[13]))]


class kekit_properties(PropertyGroup):
	# 0 - default: 0
	fitprim_select : BoolProperty(default=bool(values[0]))
	# 1 - default: 1
	fitprim_modal : BoolProperty(default=bool(values[1]))
	# 2 - default: 0
	fitprim_item : BoolProperty(default=bool(values[2]))
	# 3 - default: 16
	fitprim_sides : IntProperty(min=3, max=256, default=int(values[3]))
	# 4 - default: 32
	fitprim_sphere_seg : IntProperty(min=3, max=256, default=int(values[4]))
	# 5 - default: 16
	fitprim_sphere_ring : IntProperty(min=3, max=256, default=int(values[5]))
	# 6 - default: 0.2
	fitprim_unit : FloatProperty(min=.00001, max=256, default=float(values[6]))
	# 7 - default: 1
	unrotator_reset : BoolProperty(default=bool(values[7]))
	# 8 - default: 1
	unrotator_connect : BoolProperty(default=bool(values[8]))
	# 9 - default: 0
	unrotator_nolink : BoolProperty(default=bool(values[9]))
	# 10 - default: 1111
	opc1_obj_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc1_nrs[0]))
	opc1_obj_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc1_nrs[1]))
	opc1_edit_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc1_nrs[2]))
	opc1_edit_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc1_nrs[3]))
	# 11 - default: 2331
	opc2_obj_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc2_nrs[0]))
	opc2_obj_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc2_nrs[1]))
	opc2_edit_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc2_nrs[2]))
	opc2_edit_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc2_nrs[3]))
	# 12 - default: 2435
	opc3_obj_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc3_nrs[0]))
	opc3_obj_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc3_nrs[1]))
	opc3_edit_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc3_nrs[2]))
	opc3_edit_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc3_nrs[3]))
	# 13 - default: 6464
	opc4_obj_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc4_nrs[0]))
	opc4_obj_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc4_nrs[1]))
	opc4_edit_o: bpy.props.EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=o_dict.get(opc4_nrs[2]))
	opc4_edit_p: bpy.props.EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=p_dict.get(opc4_nrs[3]))


class VIEW3D_OT_ke_prefs_save(Operator):
	bl_idname = "view3d.ke_prefs_save"
	bl_label = "Save Settings"
	bl_description = "Saves current kit settings (prefs-file, global & persistent)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	def execute(self, context):
		prefs = get_prefs()
		write_prefs(prefs)
		return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	kekit_properties,
	VIEW3D_OT_ke_prefs_save,
	)

def register():

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.kekit = PointerProperty(type=kekit_properties)

	prefs = read_prefs()
	if not prefs:
		write_prefs(prefs_data_default)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	try:
		del bpy.types.Scene.kekit
	except Exception as e:
		print('unregister fail:\n', e)
		pass

if __name__ == "__main__":
	register()
