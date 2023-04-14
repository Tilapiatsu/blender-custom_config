import bpy
from os import path

class TILA_Config_PathElement(bpy.types.PropertyGroup):
	is_enable: bpy.props.BoolProperty(default=False)
	local_subpath: bpy.props.StringProperty(default='')
	destination_path: bpy.props.StringProperty(default='')

class TILA_Config_AddonElement(bpy.types.PropertyGroup):
	name : bpy.props.StringProperty(default='')
	is_enable : bpy.props.BoolProperty(default=False)
	is_repository  : bpy.props.BoolProperty(default=False)
	is_sync : bpy.props.BoolProperty(default=False)
	online_url : bpy.props.StringProperty(default='')
	repository_url : bpy.props.StringProperty(default='')
	branch : bpy.props.StringProperty(default='')
	is_submodule : bpy.props.BoolProperty(default=False)
	local_path : bpy.props.StringProperty(default='')
	keymaps : bpy.props.BoolProperty(default=False)
	paths : bpy.props.CollectionProperty(type=TILA_Config_PathElement)

class TILA_Config_AddonList(bpy.types.UIList):
	bl_idname = "TILA_UL_Config_addon_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		self.use_filter_sort_alpha = True

		grid = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=True, align=True)
		
		col = grid.column()
		row = col.row(align=True)
		row.operator('tila.config_remove_addon', text='', icon='TRASH').name = item.name
		row.operator('tila.config_edit_addon', text='', icon='GREASEPENCIL').name = item.name
		if len(item.online_url):
			row.operator("wm.url_open", text='', icon='URL').url = item.online_url
		else:
			self.blank_space(row)

		if len(item.repository_url):
			row.operator("wm.url_open", text='', icon='PACKAGE').url = item.repository_url
		else:
			self.blank_space(row)

		if item.name in context.preferences.addons:
			row.operator('tila.config_force_disable_addon', text='', icon='CHECKBOX_HLT').name = item.name
		else:
			row.operator('tila.config_force_enable_addon', text='', icon='CHECKBOX_DEHLT').name = item.name
		
		row.label(text=f'{item.name}')
		
		col = grid.column()
		row = col.row(align=True)
		if item.is_repository:
			row.operator('tila.config_sync_addon_list', text='', icon='FILE_REFRESH').name = item.name
			row.prop(item, 'is_sync', text='sync')

		col = grid.column()
		row = col.row(align=True)
		if len(item.paths):
			row.operator('tila.config_link_addon_list', text='', icon='LINK_BLEND').name = item.name
		
			for i in range(len(item.paths)):
				item_path = path.join(item.local_path, item.paths[i].local_subpath) if len(item.paths[i].local_subpath) else item.local_path
				if i == 0:
					row.prop(item.paths[i], 'is_enable', text=path.basename(item_path))
				if i > 0:
					row = col.row(align=True)
					row.label(text='', icon='BLANK1')
					row.prop(item.paths[i], 'is_enable', text=path.basename(item_path))

		col = grid.column()
		row = col.row(align=True)
		row.operator('tila.config_enable_addon_list', text='', icon='CHECKBOX_HLT').name = item.name
		row.prop(item, 'is_enable', text='enable')

		# col = grid.column()
		# row = col.row(align=True)
		# row.operator('tila.config_sync_addon_list', text='', icon='KEYINGSET').name = item.name
		# row.prop(item, 'keymaps', text='keymaps')

		
	def separator_iter(self, ui, iter) :
		for i in range(iter):
			ui.separator()
	
	def blank_space(self, ui):
		ui.label(text='', icon='BLANK1')