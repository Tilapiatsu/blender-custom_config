import bpy
from os import path

class TILA_Config_PathElement(bpy.types.PropertyGroup):
	enable: bpy.props.BoolProperty(default=False)
	local_subpath: bpy.props.StringProperty(default='')
	destination_path: bpy.props.StringProperty(default='')

class TILA_Config_AddonElement(bpy.types.PropertyGroup):
	name : bpy.props.StringProperty(default='')
	enable : bpy.props.BoolProperty(default=False)
	is_repository  : bpy.props.BoolProperty(default=False)
	sync : bpy.props.BoolProperty(default=False)
	online_url : bpy.props.StringProperty(default='')
	repository_url : bpy.props.StringProperty(default='')
	branch : bpy.props.StringProperty(default='')
	submodule : bpy.props.BoolProperty(default=False)
	local_path : bpy.props.StringProperty(default='')
	keymaps : bpy.props.BoolProperty(default=False)
	paths : bpy.props.CollectionProperty(type=TILA_Config_PathElement)

class TILA_Config_AddonList(bpy.types.UIList):
	bl_idname = "TILA_Config_addon_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		self.use_filter_sort_alpha = True
		
		scn = context.scene

		grid = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=True, align=True)
		# row.alignment = 'RIGHT'
		# if item.enable:
		# 	icon = 'CHECKBOX_HLT'
		# else:
		# 	icon = 'CHECKBOX_DEHLT'
		
		col = grid.column()
		row = col.row(align=True)
		row.operator('tila.config_remove_addon', text='',icon='TRASH').addon_name = item.name
		row.label(text=f'{item.name}')
		
		col = grid.column()
		row = col.row(align=True)
		if item.is_repository:
			row.operator('tila.config_sync_addon_list', text='', icon='FILE_REFRESH').addon_name = item.name
			row.prop(item, 'sync', text='sync')
			# row = col.row(align=True)
		# else:
		# 	row.label(text='', icon='BLANK1')
		# 	row.label(text='', icon='BLANK1')

		col = grid.column()
		row = col.row(align=True)
		if len(item.paths):
			row.operator('tila.config_link_addon_list', text='', icon='LINK_BLEND').addon_name = item.name
		
			for i in range(len(item.paths)):
				item_path = path.join(item.local_path, item.paths[i].local_subpath)
				if i == 0:
					row.prop(item.paths[i], 'enable', text=path.basename(item_path))
				if i > 0:
					row = col.row(align=True)
					row.label(text='', icon='BLANK1')
					row.prop(item.paths[i], 'enable', text=path.basename(item_path))

		col = grid.column()
		row = col.row(align=True)
		row.operator('tila.config_enable_addon_list', text='', icon='CHECKBOX_HLT').addon_name = item.name
		row.prop(item, 'enable', text='enable')
		# row = col.row(align=True)

		col = grid.column()
		row = col.row(align=True)
		row.operator('tila.config_sync_addon_list', text='', icon='KEYINGSET').addon_name = item.name
		row.prop(item, 'keymaps', text='keymaps')
		# row = col.row(align=True)

		# col = grid.column()
		# row = col.row(align=True)
		# row.prop(item, 'submodule', text='submodule')
		# row = col.row(align=True)
		
		# row.label(text='{}'.format(item.render_camera), icon='CAMERA_DATA')
		
		# if context.scene.lm_asset_in_preview == item.name:
		# 	eye_icon = 'HIDE_ON'
		# 	asset = ''
		# else:
		# 	eye_icon = 'HIDE_OFF'
		# 	asset = item.name
			
		
		# row.label(text='{}'.format(item.name))
		# row = col.row(align=True)
		
		# row.alignment = 'LEFT'
		# row.label(text='{}'.format(item.render_camera), icon='CAMERA_DATA')
		# row.alignment = 'RIGHT'
		# row.label(text='{}'.format(item.section), icon='FILE_TEXT')
		
		# row = col.row(align=True)
		# row.alignment = 'RIGHT'

		# if len(scn.lm_asset_list[item.name].warnings):
		# 	row.operator('scene.lm_show_asset_warnings', text='', icon='ERROR').asset_name = item.name
		# else:
		# 	self.separator_iter(row, 3)

		# if scn.lm_asset_list[item.name].rendered:
		# 	row.operator('scene.lm_open_render_folder', text='', icon='RENDER_RESULT').asset_name = item.name
		# else:
		# 	self.separator_iter(row, 3)
		
		# if scn.lm_asset_list[item.name].asset_folder_exists:
		# 	row.operator('scene.lm_open_asset_folder', text='', icon='SNAP_VOLUME').asset_name = item.name
		# else:
		# 	self.separator_iter(row, 3)

		# row.operator('scene.lm_open_asset_catalog', text='', icon='FILE_BLEND').asset_name = item.name

		# op = row.operator('scene.lm_create_blend_catalog_file', text='', icon='IMPORT')
		# op.asset_name = item.name
		# op.mode = "ASSET"
		# row.operator('scene.lm_rename_asset', text='', icon='SMALL_CAPS').asset_name = item.name
		# op = row.operator('scene.lm_refresh_asset_status', text='', icon='FILE_REFRESH')
		# op.asset_name = item.name
		# op.mode='ASSET'
		
		# row.separator()
		# row.operator('scene.lm_print_asset_data', text='', icon='ALIGN_JUSTIFY' ).asset_name = item.name
		# row.operator('scene.lm_add_asset_to_render_queue', text='', icon='SORT_ASC').asset_name = item.name
		# row.operator('scene.lm_remove_asset', text='', icon='X').asset_name = item.name

		
	def separator_iter(self, ui, iter) :
		for i in range(iter):
			ui.separator()