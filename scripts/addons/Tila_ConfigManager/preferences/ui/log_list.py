import bpy
from enum import StrEnum
from Tila_ConfigManager.logger import LOG
from Tila_ConfigManager.config_const import LOG_FILENAME

class MessageType(StrEnum):
    NONE = 'BLANK1'
    INFO = 'INFO'
    DEBUG = 'ALIGN_JUSTIFY'
    WARNING = 'ERROR'
    ERROR = 'CANCEL'
    START = 'TRIA_RIGHT'
    DONE = 'CHECKMARK'

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
    def __init__(self, log_list, index_name, context:str=None):
        self.log_list = log_list
        self.index_name = index_name
        if context is not None:
            LOG.context = context

    def append(self, name:str, message_type:MessageType = MessageType.NONE, add_to_satus=True):
        if add_to_satus:
            element = self.log_list.add()
            element.name = name
            element.icon = str(message_type)

        if message_type in [MessageType.INFO, MessageType.START, MessageType.DONE]:
            LOG.info(name)
        if message_type in [MessageType.ERROR, MessageType.WARNING]:
            if message_type == MessageType.ERROR:
                LOG.error(name)
            elif message_type == MessageType.WARNING:
                LOG.warning(name)

        if LOG_FILENAME not in bpy.data.texts:
            bpy.data.texts.new(LOG_FILENAME)

        text = bpy.data.texts[LOG_FILENAME]
        text.write(name + "\n")

        setattr(bpy.context.window_manager, self.index_name, len(self.log_list)-1)

    def info(self, name:str):
        self.append(name, message_type=MessageType.INFO)

    def warning(self, name:str):
        self.append(name, message_type=MessageType.WARNING)

    def error(self, name:str):
        self.append(name, message_type=MessageType.ERROR)

    def start(self, name:str):
        self.append(name, message_type=MessageType.START)

    def done(self, name:str):
        self.append(name, message_type=MessageType.DONE)

    def separator(self, add_to_satus=False):
        self.append('-----------------------------------', message_type=MessageType.NONE, add_to_satus=add_to_satus)

    def start_stage(self, name:str):
        self.separator()
        self.append(name, message_type=MessageType.START)
        self.separator()

    def done_stage(self, name:str):
        self.separator()
        self.append(name, message_type=MessageType.DONE)
        self.separator()

    def log_failure(self):
        if LOG.failure_count > 0:
            self.separator()
            self.append('Summary :', message_type=MessageType.NONE, add_to_satus=False)
            self.append(f'{LOG.failure_count} issue(s) occures durring the process :', message_type=MessageType.NONE, add_to_satus=False)
            self.separator()
        for key, messages in LOG.failure.items():
            for message in messages:
                self.append(f'{key} : {message}', message_type=MessageType.NONE, add_to_satus=False)
        LOG.reset_log()


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

