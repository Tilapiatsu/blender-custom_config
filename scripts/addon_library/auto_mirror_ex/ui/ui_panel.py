import bpy
from bpy.props import *
from bpy.types import Panel


class AUTOMIRROR_PT_panel(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tools'
	bl_label = "Auto Mirror"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return bpy.context.object


	def draw(self, context):
		layout = self.layout

		draw_automirror(self, layout)


		draw_mirrormirror(self, layout)


		draw_multi_mod(self, layout)


# Auto Mirror
def draw_automirror(self, layout):
	box = layout.box()
	row = box.row(align=True)
	row.scale_y = 1.2
	row.operator("automirror.automirror")
	row.separator()
	rows = row.row(align=True)
	row.scale_x = 1.5
	rows.operator("automirror.toggle_mirror",text="",icon="RESTRICT_VIEW_OFF")
	rows.operator("automirror.target_set",text="",icon="OBJECT_DATAMODE")

	sp = box.split(align=True,factor=0.3)
	sp.label(text="Quick Axis")
	row = sp.row()
	row.scale_y = 1.2
	am = row.operator("automirror.automirror",text="X")
	am.axis_quick_override = True
	am.axis_x = True
	am.axis_y = False
	am.axis_z = False
	am = row.operator("automirror.automirror",text="Y")
	am.axis_quick_override = True
	am.axis_x = False
	am.axis_y = True
	am.axis_z = False
	am = row.operator("automirror.automirror",text="Z")
	am.axis_quick_override = True
	am.axis_x = False
	am.axis_y = False
	am.axis_z = True

	draw_automirror_option(self, box)


def draw_automirror_option(self, layout):
	props = bpy.context.scene.automirror

	row = layout.row(align=True)
	row.alignment="LEFT"
	row.prop(props, "toggle_option", text="Option", icon="TRIA_DOWN" if props.toggle_option else "TRIA_RIGHT", emboss=False)

	if not props.toggle_option:
		return
	# draw_main_fanc_option(self,context,layout)

	box = layout.box()
	col = box.column()
	row = col.row(align=True)
	row.prop(props,"axis_x",text="X",toggle=True)
	row.prop(props,"axis_y",text="Y",toggle=True)
	row.prop(props,"axis_z",text="Z",toggle=True)
	# row.prop(props, "axis", text="Mirror Axis", expand=True)
	row = col.row(align=True)
	row.prop(props, "orientation", text="Orientation", expand=True)
	col.prop(props, "threshold", text="Threshold")
	col.prop(props, "toggle_edit", text="Toggle Edit")
	col.prop(props, "cut", text="Cut and Mirror")
	if props.cut:
		col = box.column(align=True)
		col.label(text="Mirror Modifier:")
		row = col.row(align=True)
		row.label(text="",icon="AUTOMERGE_ON")
		row.prop(props, "use_clip", text="Use Clip")
		row = col.row(align=True)
		row.label(text="",icon="OUTLINER_DATA_MESH")
		row.prop(props, "show_on_cage", text="Editable")
		row = col.row(align=True)
		row.label(text="",icon="SORT_DESC")
		row.prop(props, "sort_top_mod")
		row = col.row(align=True)
		row.label(text="",icon="CHECKBOX_HLT")
		row.prop(props, "apply_mirror", text="Apply Mirror")
	else:
		box.label(text="Only Bisect")


# mirror mirror
def draw_mirrormirror(self, layout):
	box = layout.box()
	sp = box.split(align=True,factor=0.3)
	sp.label(text="Mirror Mirror")
	row = sp.row()
	row.scale_y = 1.2
	mm = row.operator("automirror.mirror_mirror",text="X")
	mm.axis_x = True
	mm.axis_y = False
	mm.axis_z = False
	mm = row.operator("automirror.mirror_mirror",text="Y")
	mm.axis_x = False
	mm.axis_y = True
	mm.axis_z = False
	mm = row.operator("automirror.mirror_mirror",text="Z")
	mm.axis_x = False
	mm.axis_y = False
	mm.axis_z = True


# 一括操作
def draw_multi_mod(self, layout):
	row = layout.row(align=True)
	row.scale_x = 1.2
	row.menu("AUTOMIRROR_MT_modifier_add",text="",icon="ADD")
	row.separator()
	row.operator("automirror.apply",text="Apply",icon="FILE_TICK")
	row.operator("automirror.remove",text="Remove",icon="X")
	row.separator()
	row.operator("automirror.modifier_sort",text="",icon="SORT_DESC")
