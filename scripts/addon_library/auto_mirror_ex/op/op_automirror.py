import bpy
from bpy.props import *
from bpy.types import Operator
from mathutils import Vector

from ..utils import sort_top_mod


class AUTOMIRROR_OT_automirror(Operator):
	""" Automatically cut an object along an axis """
	bl_idname = "automirror.automirror"
	bl_label = "AutoMirror"
	bl_options = {'REGISTER', 'UNDO'}

	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)

	apply_mirror : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")
	cut          : BoolProperty(default= True, description="If enabeled, cut the mesh in two parts and mirror it. If not, just make a loopcut")
	show_on_cage : BoolProperty(description="Enable to edit the cage (it's the classical modifier's option)")
	threshold    : FloatProperty(default= 0.001, min= 0, description="Vertices closer than this distance are merged on the loopcut")
	toggle_edit  : BoolProperty(default= False, description="If not in edit mode, change mode to edit")
	use_clip     : BoolProperty(default=True, description="Use clipping for the mirror modifier")

	axis_x : BoolProperty(name="Axis X",default=True)
	axis_y : BoolProperty(name="Axis Y")
	axis_z : BoolProperty(name="Axis Z")


	axis_quick_override : BoolProperty(name="axis_quick_override", description="Axis used by the mirror modifier")

	orientation  : EnumProperty(description="Choose the side along the axis of the editable part (+/- coordinates)",items = [
	("positive", "Positive", "", "ADD", 0),
	("negative", "Negative","", "REMOVE", 1)])



	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == "MESH"


	def invoke(self, context, event):
		props = bpy.context.scene.automirror
		self.apply_mirror = props.apply_mirror
		self.cut = props.cut
		self.show_on_cage = props.show_on_cage
		self.threshold = props.threshold
		self.toggle_edit = props.toggle_edit
		self.use_clip = props.use_clip
		self.orientation = props.orientation

		if not self.axis_quick_override:
			self.axis_x = props.axis_x
			self.axis_y = props.axis_y
			self.axis_z = props.axis_z

		return self.execute(context)


	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self,"axis_x",text="X",toggle=True)
		row.prop(self,"axis_y",text="Y",toggle=True)
		row.prop(self,"axis_z",text="Z",toggle=True)

		row = layout.row(align=True)
		row.prop(self, "orientation", text="Orientation", expand=True)
		layout.prop(self, "threshold", text="Threshold")
		layout.prop(self, "toggle_edit", text="Toggle Edit")
		layout.prop(self, "cut", text="Cut and Mirror")
		if self.cut:
			layout.label(text="Mirror Modifier:")
			row = layout.row(align=True)
			row.label(text="",icon="AUTOMERGE_ON")
			row.prop(self, "use_clip", text="Use Clip")
			row = layout.row(align=True)
			row.label(text="",icon="OUTLINER_DATA_MESH")
			row.prop(self, "show_on_cage", text="Editable")
			row = layout.row(align=True)
			row.label(text="",icon="SORT_DESC")
			row.prop(self, "sort_top_mod")
			row = layout.row(align=True)
			row.label(text="",icon="CHECKBOX_HLT")
			row.prop(self, "apply_mirror", text="Apply Modifier")
		else:
			layout.label(text="Only Bisect")


	def get_local_axis_vector(self, context, X, Y, Z, orientation,obj):
		loc = obj.location
		bpy.ops.object.mode_set(mode="OBJECT") # Needed to avoid to translate vertices

		v1 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(X*orientation, Y*orientation, Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')
		v2 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(-X*orientation, -Y*orientation, -Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')

		bpy.ops.object.mode_set(mode="EDIT")

		return v2-v1


	def bisect_main(self, context, X, Y, Z, orientation,obj):
		cut_normal = self.get_local_axis_vector(context, X, Y, Z, orientation,obj)
		# plane_no=[X*orientation,Y*orientation,Z*orientation],

		# Cut the mesh
		bpy.ops.mesh.bisect(
				plane_co=(
				obj.location[0],
				obj.location[1],
				obj.location[2]
				),
				plane_no=cut_normal,
				use_fill= False,
				clear_inner= self.cut,
				clear_outer= 0,
				threshold= self.threshold)


	def execute(self, context):
		props = bpy.context.scene.automirror
		sc = bpy.context.scene
		if not (self.axis_x or self.axis_y or self.axis_z):
			self.report({'WARNING'}, "No axis")
			return {'FINISHED'}


		# info text
		info_text = "Add"
		text_X = "*"
		text_Y = "*"
		text_Z = "*"
		if self.axis_x:
			text_X = "X"
		if self.axis_y:
			text_Y = "Y"
		if self.axis_z:
			text_Z = "Z"
		if self.apply_mirror:
			info_text = "Apply"

		if self.orientation == 'positive':
			orientation = 1
		else:
			orientation = -1

		# 選択オブジェクトを回す
		old_obj = bpy.context.view_layer.objects.active
		old_sel = bpy.context.selected_objects
		for obj in bpy.context.selected_objects:
			obj.select_set(False)

		for obj in old_sel:
			if obj.type == "MESH":
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				X,Y,Z = 0,0,0
				current_mode = obj.mode # Save the current mode

				if obj.mode != "EDIT":
					bpy.ops.object.mode_set(mode="EDIT") # Go to edit mode

				##############################################
				# 反対側を削除
				if self.axis_x:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 1
					Y = 0
					Z = 0
					self.bisect_main(context, X, Y, Z, orientation,obj)

				if self.axis_y:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 0
					Y = 1
					Z = 0
					self.bisect_main(context, X, Y, Z, orientation,obj)

				if self.axis_z:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 0
					Y = 0
					Z = 1
					self.bisect_main(context, X, Y, Z, orientation,obj)


				##############################################
				# Modifier
				if self.cut:
					mod = obj.modifiers.new("Mirror","MIRROR")
					mod.use_axis[0] = self.axis_x # Choose the axis to use, based on the cut's axis
					mod.use_axis[1] = self.axis_y
					mod.use_axis[2] = self.axis_z
					mod.use_clip = self.use_clip
					mod.show_on_cage = self.show_on_cage

					sort_top_mod(self,context,obj,mod,1)

					if self.apply_mirror:
						bpy.ops.object.mode_set(mode='OBJECT')
						bpy.ops.object.modifier_apply(modifier= mod.name)
						if self.toggle_edit:
							bpy.ops.object.mode_set(mode='EDIT')
						else:
							bpy.ops.object.mode_set(mode=current_mode)


				if not self.toggle_edit:
					bpy.ops.object.mode_set(mode=current_mode) # Reload previous mode
				obj.select_set(False)


		for obj in old_sel:
			obj.select_set(True)
		bpy.context.view_layer.objects.active = old_obj



		# 変更した設定をシーン設定に反映
		props.apply_mirror = self.apply_mirror
		props.cut = self.cut
		props.show_on_cage = self.show_on_cage
		props.threshold = self.threshold
		props.toggle_edit = self.toggle_edit
		props.use_clip = self.use_clip
		props.orientation = self.orientation

		if not self.axis_quick_override:
			props.axis_x = self.axis_x
			props.axis_y = self.axis_y
			props.axis_z = self.axis_z
		else:
			self.axis_quick_override = False

		if len(bpy.context.selected_objects) == 1:
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s]" % (info_text, text_X, text_Y, text_Z))
		else:
			sel_obj = str(len(bpy.context.selected_objects))
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s] to %s object" % (info_text, text_X, text_Y, text_Z, sel_obj))

		return {'FINISHED'}
