import bpy
from bpy.props import *
from bpy.types import PropertyGroup


class AUTOMIRROR_Props(PropertyGroup):
	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)
	toggle_option : BoolProperty(name="Toggle Option")
	apply_mirror  : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")
	cut           : BoolProperty(default= True, description="If enabeled, cut the mesh in two parts and mirror it. If not, just make a loopcut")
	show_on_cage  : BoolProperty(description="Enable to edit the cage (it's the classical modifier's option)")
	threshold     : FloatProperty(default= 0.001, min= 0.001, description="Vertices closer than this distance are merged on the loopcut")
	toggle_edit   : BoolProperty(description="If not in edit mode, change mode to edit")
	use_clip      : BoolProperty(default=True, description="Use clipping for the mirror modifier")
	axis_x : BoolProperty(name="Axis X",default=True)
	axis_y : BoolProperty(name="Axis Y")
	axis_z : BoolProperty(name="Axis Z")
	axis          : EnumProperty(name="Axis", description="Axis used by the mirror modifier",items = [
	("x", "X", "", 1),
	("y", "Y", "", 2),
	("z", "Z", "", 3)])
	orientation   : EnumProperty(description="Choose the side along the axis of the editable part (+/- coordinates)",items = [
	("positive", "Positive", "", "ADD", 1),
	("negative", "Negative","", "REMOVE", 2)])

	mm_target_obj       : PointerProperty(name="Target Object", type=bpy.types.Object)
