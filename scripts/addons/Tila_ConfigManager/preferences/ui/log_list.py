import bpy
from ...logger import LOG
from ...config_const import LOG_FILENAME


class TILA_Config_LogElement(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default='')
    icon: bpy.props.StringProperty(default='BLANK1')

class TILA_Config_LogList(bpy.types.UIList):
    bl_idname = "TILA_UL_Config_log_list"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon=item.icon)

class TILA_Config_SatusList(bpy.types.UIList):
    bl_idname = "TILA_UL_Config_status_list"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon=item.icon)

class TILA_Config_Log():
    def __init__(self, log, index_name):
        self.log = log
        self.index_name = index_name

    def append(self, name, icon='BLANK1', add_to_satus=True):
        if add_to_satus:
            element = self.log.add()
            element.name = name
            element.icon = icon

        LOG.info(name)

        if LOG_FILENAME not in bpy.data.texts:
            bpy.data.texts.new(LOG_FILENAME)

        text = bpy.data.texts[LOG_FILENAME]
        text.write(name + "\n")

        setattr(bpy.context.window_manager, self.index_name, len(self.log)-1)
    
    def info(self, name):
        self.append(name, icon='INFO')

    def warning(self, name):
        self.append(name, icon='ERROR')

    def error(self, name):
        self.append(name, icon='CANCEL')

    def start(self, name):
        self.append(name, icon='TRIA_RIGHT')
    
    def done(self, name):
        self.append(name, icon='CHECKMARK')

    def separator(self, add_to_satus=False):
        self.append('-----------------------------------', add_to_satus=add_to_satus)

    def start_stage(self, name):
        self.separator()
        self.append(name, icon='TRIA_RIGHT')
        self.separator()

    def done_stage(self, name):
        self.separator()
        self.append(name, icon='CHECKMARK')
        self.separator()

classes = (TILA_Config_LogElement,
           TILA_Config_LogList,
           TILA_Config_SatusList)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
          
    bpy.types.WindowManager.tila_config_log_list_idx = bpy.props.IntProperty()
    bpy.types.WindowManager.tila_config_log_list = bpy.props.CollectionProperty(type=TILA_Config_LogElement)
    bpy.types.WindowManager.tila_config_status_list_idx = bpy.props.IntProperty()
    bpy.types.WindowManager.tila_config_status_list = bpy.props.CollectionProperty(type=TILA_Config_LogElement)

def unregister():
    del bpy.types.WindowManager.tila_config_status_list
    del bpy.types.WindowManager.tila_config_status_list_idx
    del bpy.types.WindowManager.tila_config_log_list
    del bpy.types.WindowManager.tila_config_log_list_idx

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
