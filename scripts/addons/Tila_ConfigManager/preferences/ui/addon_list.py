import bpy
from os import path
from Tila_ConfigManager.bversion import BVERSION

class TILA_Config_PathElement(bpy.types.PropertyGroup):
    is_enable       : bpy.props.BoolProperty(default=False)
    local_subpath   : bpy.props.StringProperty(default='')
    destination_path: bpy.props.StringProperty(default='')

class TILA_Config_AddonElement(bpy.types.PropertyGroup):
    name            : bpy.props.StringProperty(default='')
    is_enable       : bpy.props.BoolProperty(default=False)
    is_repository   : bpy.props.BoolProperty(default=False)
    is_extension    : bpy.props.BoolProperty(default=False)
    extension_id    : bpy.props.StringProperty(default='')
    is_sync         : bpy.props.BoolProperty(default=False)
    online_url      : bpy.props.StringProperty(default='')
    repository_url  : bpy.props.StringProperty(default='')
    branch          : bpy.props.StringProperty(default='')
    is_submodule    : bpy.props.BoolProperty(default=False)
    local_path      : bpy.props.StringProperty(default='')
    keymaps         : bpy.props.BoolProperty(default=False)
    paths           : bpy.props.CollectionProperty(type=TILA_Config_PathElement)

class TILA_Config_AddonList(bpy.types.UIList):
    bl_idname = "TILA_UL_Config_addon_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        self.use_filter_sort_alpha = True
        main_col = layout.column(align=True)

        header, panel = main_col.panel(idname=item.name, default_closed=True)
        header_row = header.row(align=True)
        header_row.label(text=item.name, icon='IMPORT')
        rowsub = header.row()
        rowsub.alignment = 'RIGHT'

        installed = item.name in context.preferences.addons

        if installed:
            rowsub.operator('tila.config_force_disable_addon', text='Disable', icon='CHECKBOX_HLT').name = item.name
        else:
            header_row.active = False
            rowsub.operator('tila.config_force_enable_addon', text='Enable', icon='CHECKBOX_DEHLT').name = item.name

        if panel:
            col = panel.column()

            row = col.row()
            row.operator('tila.config_edit_addon', text=f'Edit {item.name}', icon='GREASEPENCIL').name = item.name
            row.operator('tila.config_remove_addon', text=f'Remove {item.name}', icon='TRASH').name = item.name

            col.separator(type='LINE')

            col_info = col.column()
            col_info.active = installed
            split = col_info.split(factor=0.15)
            col_a = split.column()
            col_b = split.column()
            col_a.alignment = "RIGHT"
            if item.is_extension:
                col_a.label(text="Extension ID")
                col_b.label(text=item.extension_id)

            if len(item.online_url):
                col_a.label(text="Website")
                col_b.operator("wm.url_open", text=item.online_url, icon='URL').url = item.online_url

            if len(item.repository_url):
                col_a.label(text="Repository")
                col_b.operator("wm.url_open", text=item.repository_url, icon='PACKAGE').url = item.repository_url

                col_a.label(text="Submodule")
                col_b.label(text='Yes' if item.is_submodule else 'No')

                if len(item.branch):
                    col_a.label(text="Branch")
                    col_b.label(text=item.branch)

            if item.is_repository:
                col_a.label(text="Sync")
                op = col_b.operator('tila.config_sync_addon_list', text=f'Sync {item.name}', icon='FILE_REFRESH')
                op.name = item.name
                op.force = True
                op.overwrite = True


    def separator_iter(self, ui, iter) :
        for i in range(iter):
            ui.separator()

    def blank_space(self, ui):
        ui.label(text='', icon='BLANK1')


classes = (TILA_Config_PathElement,
           TILA_Config_AddonElement,
           TILA_Config_AddonList)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.tila_config_addon_list_idx = bpy.props.IntProperty()
    bpy.types.WindowManager.tila_config_addon_list = bpy.props.CollectionProperty(type=TILA_Config_AddonElement)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)