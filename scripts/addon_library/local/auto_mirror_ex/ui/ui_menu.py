import bpy
from bpy.props import *
from bpy.types import Menu
from ..utils import (
		mesh_mod_items,
		gp_mod_items,
	)


class AUTOMIRROR_MT_modifier_add(Menu):
	bl_label = "Add Modifier to selected object"

	def draw(self, context):
		layout = self.layout
		act_obj = bpy.context.active_object
		if not act_obj:
			layout.label(text="No Active Object",icon="NONE")
			return


		if act_obj.type == "GPENCIL":
			global gp_mod_items
			tgt_mod_items =  gp_mod_items
		else:
			global mesh_mod_items
			tgt_mod_items =  mesh_mod_items


		sp = layout.split()
		for keyname, label, desc, icon_val, num  in tgt_mod_items:
			if keyname == "":
				col = sp.column(align=True)
				col.label(text=label,icon="NONE")
				continue
			op = col.operator("automirror.modifier_add", text=label, icon=icon_val)
			if act_obj.type == "GPENCIL":
				op.gp_mod_type = keyname
			else:
				op.mesh_mod_type = keyname
