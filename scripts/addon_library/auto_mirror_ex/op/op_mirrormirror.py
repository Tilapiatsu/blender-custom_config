import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import sort_top_mod


class AUTOMIRROR_OT_mirrormirror(Operator):
	bl_idname = "automirror.mirror_mirror"
	bl_label = "MirrorMirror"
	bl_description = "Mirror another object to an axis.\n First select the objects you want to mirror,\n Second select the objects you want to be axis and then execute.\n Set up a regular mirror if there is only one selected object"
	bl_options = {'REGISTER', 'UNDO'}

	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)
	use_existing_mod : BoolProperty(name="Use existing mirror modifier",description="Use existing mirror modifier")
	axis_x           : BoolProperty(default=True,name="Axis X")
	axis_y           : BoolProperty(name="Axis Y")
	axis_z           : BoolProperty(name="Axis Z")
	use_bisect_axis           : BoolProperty(name="Bisect")
	use_bisect_flip_axis           : BoolProperty(name="Bisect Flip")
	apply_mirror : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")


	@classmethod
	def poll(cls, context):
		return len(bpy.context.selected_objects)


	def invoke(self, context, event):
		props = bpy.context.scene.automirror
		props.mm_target_obj = bpy.context.view_layer.objects.active
		return self.execute(context)


	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self,"axis_x",text="X",icon="BLANK1",emboss=True)
		row.prop(self,"axis_y",text="Y",icon="BLANK1",emboss=True)
		row.prop(self,"axis_z",text="Z",icon="BLANK1",emboss=True)

		layout.prop(self,"sort_top_mod")
		layout.prop(self,"use_bisect_axis")
		layout.prop(self,"use_bisect_flip_axis")


		row = layout.row(align=True)
		row.label(text="",icon="CHECKBOX_HLT")
		row.prop(self, "apply_mirror", text="Apply Modifier")


	def run_mirror_mirror_mesh(self, context, obj, tgt_obj):
		mod = obj.modifiers.new("mirror_mirror","MIRROR")
		mod.use_axis[0] = False
		mod.use_axis[1] = False
		mod.use_axis[2] = False
		if self.axis_x:
			mod.use_axis[0] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[0] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[0] = True

		if self.axis_y:
			mod.use_axis[1] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[1] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[1] = True

		if self.axis_z:
			mod.use_axis[2] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[2] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[2] = True
		if tgt_obj:
			mod.mirror_object = tgt_obj

		sort_top_mod(self,context,obj,mod,1)

		if self.apply_mirror:
			current_mode = obj.mode
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.modifier_apply(modifier= mod.name)
			bpy.ops.object.mode_set(mode=current_mode)
		return mod


	def run_mirror_mirror_gp(self, context, obj, tgt_obj):
		mod = obj.grease_pencil_modifiers.new("mirror_mirror","GP_MIRROR")
		x = False
		y = False
		z = False
		if self.axis_x:
			x = True
		if self.axis_y:
			y = True
		if self.axis_z:
			z = True
		mod.use_axis_x = x
		mod.use_axis_y = y
		mod.use_axis_z = z
		if tgt_obj:
			mod.object = tgt_obj

		sort_top_mod(self,context,obj,mod,1)

		if self.apply_mirror:
			current_mode = obj.mode
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.gpencil_modifier_apply(modifier= mod.name)
			bpy.ops.object.mode_set(mode=current_mode)
		return mod


	def execute(self, context):
		props = bpy.context.scene.automirror


		# info text
		info_text = "Add"
		X = "*"
		Y = "*"
		Z = "*"
		if self.axis_x:
			X = "X"
		if self.axis_y:
			Y = "Y"
		if self.axis_z:
			Z = "Z"
		if self.apply_mirror:
			info_text = "Apply"


		# main run
		if len(bpy.context.selected_objects) == 1:
			obj = bpy.context.object
			if obj.type=="GPENCIL":
				self.run_mirror_mirror_gp(context, obj, None)
			else:
				if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
					self.run_mirror_mirror_mesh(context, obj, None)

			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s]" % (info_text, X, Y, Z))
			return{'FINISHED'}
		else:
			# Multi selected object
			tgt_obj = bpy.context.view_layer.objects.active
			tgt_obj.select_set(False)

			for obj in bpy.context.selected_objects:
				bpy.context.view_layer.objects.active = obj
				if obj.type=="GPENCIL":
					self.run_mirror_mirror_gp(context, obj, tgt_obj)
				else:
					if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
						self.run_mirror_mirror_mesh(context, obj, tgt_obj)

			sel_obj = str(len(bpy.context.selected_objects))
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s] to %s object" % (info_text, X, Y, Z, sel_obj))


		return {'FINISHED'}
