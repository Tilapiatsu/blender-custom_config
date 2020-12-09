import bpy, os
from bpy.props import *
from bpy.types import UIList

class RENTASKLIST_UL_rentask(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		if item.blendfile:
			layout.label(text="",icon="BLANK1")
		else:
			layout.operator("rentask.rentask_load_setting",text="",icon="IMPORT",emboss=False).item = index

		layout.prop(item, "name", text="", icon="NONE",emboss=False)
		if item.blendfile:
			bfile_name = os.path.basename(item.blendfile)
			layout.label(text=bfile_name,icon="NONE")

		layout.prop(item,"use_render",text="",icon="RESTRICT_RENDER_OFF" if item.use_render else "RESTRICT_RENDER_ON", emboss=False)


	def filter_items(self, context, data, propname):
		filtered = []
		ordered = []
		items = getattr(data, propname)
		helper_funcs = bpy.types.UI_UL_list

		# Filter
		# Initialize with all items visible
		filtered = [self.bitflag_filter_item] * len(items)

		# 名前でフィルター
		if self.filter_name:
			filtered = helper_funcs.filter_items_by_name(
			self.filter_name,
			self.bitflag_filter_item,
			items,
			"name",
			reverse=self.use_filter_sort_reverse)


		# if not filtered:
		# 	filtered = [self.bitflag_filter_item] * len(vgroups)


		if self.use_filter_sort_alpha:
			ordered = helper_funcs.sort_items_by_name(items, "name")

		self.my_data_filter(context,items,filtered)

		return filtered,ordered


	# フィルター
	def my_data_filter(self,context,items,filtered):
		sc = bpy.context.scene
		props = sc.rentask.rentask_main


		filter_type_l = []

		for i, item in enumerate(items):
			if props.bfile_type == "EXTERNAL":
				if not item.blendfile:
					filtered[i] &= ~self.bitflag_filter_item
			else:
				if item.blendfile:
					filtered[i] &= ~self.bitflag_filter_item

		return filtered
