import bpy

class TILA_Config_PathElement(bpy.types.PropertyGroup):
	enable: bpy.props.BoolProperty(default=False)
	local_subpath: bpy.props.StringProperty(default='')
	destination_path: bpy.props.StringProperty(default='')

class TILA_Config_AddonElement(bpy.types.PropertyGroup):
	name : bpy.props.StringProperty(default='')
	enable : bpy.props.BoolProperty(default=False)
	sync : bpy.props.BoolProperty(default=False)
	online_url : bpy.props.StringProperty(default='')
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

		col = layout.column_flow(columns=3, align=True)

		row = col.row(align=True)
		row.alignment = 'LEFT'
		row.label(text=f'{item.name}')
		
		# if context.scene.lm_asset_in_preview == item.name:
		# 	eye_icon = 'HIDE_ON'
		# 	asset = ''
		# else:
		# 	eye_icon = 'HIDE_OFF'
		# 	asset = item.name
			
		# row.operator('scene.lm_show_asset', text='', icon=eye_icon).asset_name = asset
		
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