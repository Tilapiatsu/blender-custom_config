import bpy
import os
import textwrap
from bpy.props import EnumProperty, StringProperty


PREFERENCE_TABS = [("GENERAL", "General", ""),
                    ("ADDONS", "Addons", ""),
                    ("ABOUT", "About", "")]

ROOT_FOLDER = os.path.dirname(bpy.utils.script_path_user())

def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name():
    return os.path.basename(get_path())


def _label_multiline(context, text, parent):
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)

def _filter_items(self, context):
    self.draw(context)

class TILA_Config_Preferences(bpy.types.AddonPreferences):
    bl_idname = get_name()

    tabs: EnumProperty(name="Tabs", items=PREFERENCE_TABS, default="GENERAL")
    search_addons: StringProperty(name='Search Addons', default='', options={'TEXTEDIT_UPDATE'})

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        wm = bpy.context.window_manager
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = column.box()

        if self.tabs == "GENERAL":
            self.draw_general(box)

        elif self.tabs == "ADDONS":
            self.draw_addons(box, wm, context)

        elif self.tabs == "ABOUT":
            self.draw_about(box)

        box = column.box()

        self.draw_progress(box, wm)

    def draw_general(self, box):
        split = box.split()

        b = split.box()

        column = b.column(align=True)
        row = column.row()
        row.scale_y = 3
        row.operator("tila.config_setup_blender", text="Setup Blender", icon='SHADERFX')
        row.operator("tila.config_update_setup_blender", text="Update Blender Setup", icon='FILE_REFRESH')
        column.separator()
        column.operator("tila.config_print_addon_list", text="Print Addon List", icon='ALIGN_JUSTIFY')
        column.separator()
        column.operator("tila.config_remove", text="Remove Config", icon='TRASH')
        column.operator("tila.config_disable_addon_list", text="Disable All Addons", icon='CHECKBOX_DEHLT').force=True
        column.operator("tila.config_clean_addon_list", text="Clean Addon List", icon='BRUSH_DATA').force=False
        op = column.operator("tila.config_sync_addon_list", text="Sync Addon List", icon='URL')
        op.force = True
        op.overwrite = True
        column.operator("tila.config_link_addon_list", text="Link Addon List", icon='LINKED')
        column.operator("tila.config_enable_addon_list", text="Enable Addon List", icon='CHECKBOX_HLT')
        column.operator("tila.config_set_settings", text="Set Settings", icon='TOOL_SETTINGS')
        column.operator("tila.config_register_keymaps", text="Register Keymaps", icon='KEYINGSET').restore=True

    def draw_addons(self, box, wm, context):
        split = box.split()

        row = split.row()
        # rows = 11 if len(wm.tila_config_addon_list) > 10 else len(wm.tila_config_addon_list) + 1

        addon_col = row.column(align=True)
        addon_col.prop(self, 'search_addons', text='', icon='VIEWZOOM', placeholder="Search Add-ons")
        addon_col.separator()
        addon_col.separator()

        addon_box = addon_col.box()

        installed_header, installed_panel = addon_box.panel(idname="InstalledAddons", default_closed=False)
        addon_box.separator(type='LINE')
        uninstalled_header, uninstalled_panel = addon_box.panel(idname="UninstalledAddons", default_closed=False)

        installed_header.label(text='Installed')
        uninstalled_header.label(text='Available')

        searching = False
        if len(self.search_addons):
            searching = True

        for a in wm.tila_config_addon_list:
            if searching:
                if self.search_addons.lower() not in a.name.lower():
                    continue
            installed = a.name in context.preferences.addons
            if installed:
                if installed_panel:
                    self.draw_addon_item(context, installed_panel.box(), a, installed)
            else:
                if uninstalled_panel:
                    self.draw_addon_item(context, uninstalled_panel.box(), a, installed)

        c = row.column(align=True)
        c.operator('tila.config_import_addon_list', text='', icon='FILE_REFRESH')
        c.operator('tila.config_save_addon_list', text='', icon='CURRENT_FILE')
        c.operator('tila.config_add_addon', text='', icon='ADD')

    def draw_about(self, box):
        column = box.column(align=True)

        row = column.row(align=True)

        row.scale_y = 1.5
        # row.operator("wm.url_open", text='MACHIN3tools', icon='INFO').url = 'https://machin3.io/MACHIN3tools/'

    def draw_progress(self, box, wm):
        status = box.row(align=True)
        b1 = status.box()
        b1.label(text="Status")
        row = b1.row()
        rows = 11 if len(wm.tila_config_status_list) > 10 else len(wm.tila_config_status_list) + 1

        row.template_list('TILA_UL_Config_status_list', '', wm, 'tila_config_status_list', wm, 'tila_config_status_list_idx', rows=rows)
        row.operator('tila.config_clear_status_list', text='', icon='TRASH')

        b2 = status.box()
        b2.label(text="Progress")
        row = b2.row()
        rows = 11 if len(wm.tila_config_log_list) > 10 else len(wm.tila_config_log_list) + 1

        row.template_list('TILA_UL_Config_log_list', '', wm, 'tila_config_log_list', wm, 'tila_config_log_list_idx', rows=rows)

        row.operator('tila.config_clear_log_list', text='', icon='TRASH')

    def draw_addon_item(self, context, layout, item, installed:bool):
        # self.use_filter_sort_alpha = True
        main_col = layout.column(align=True)

        header, panel = main_col.panel(idname=item.name, default_closed=True)
        header_row = header.row(align=True)
        header_row.label(text=item.name, icon='IMPORT')
        rowsub = header.row()
        rowsub.alignment = 'RIGHT'

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

            if item.keymaps:
                col_a.label(text="Keymaps")
                op = col_b.operator('tila.config_register_keymaps', text=f'Apply Keymaps for {item.name}', icon='EVENT_K')
                op.name = item.name

            if len(item.paths):
                col_a.label(text="Link")
                col_b.operator('tila.config_link_addon_list', text=f'Link {item.name}', icon='LINK_BLEND').name = item.name
                if installed:
                    for i in range(len(item.paths)):
                        item_path = os.path.join(item.local_path, item.paths[i].local_subpath) if len(item.paths[i].local_subpath) else item.local_path
                        item_path = item_path.replace('#', ROOT_FOLDER)
                        if os.path.exists(item_path):
                            col_a.label(text="Path")
                            if os.path.isfile(item_path):
                                op = col_b.operator('file.external_operation', text='Open File')
                                op.filepath = item_path
                                op.operation='OPEN'
                            elif os.path.isdir(item_path):
                                op = col_b.operator('file.external_operation', text='Open Folder')
                                op.filepath = item_path
                                op.operation='FOLDER_OPEN'

classes = (TILA_Config_Preferences,)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)