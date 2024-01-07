import bpy
from .PTB_Functions import word_wrap
from bpy.types import (
    Operator
)

from .PTB_Functions import dependencies


class PTB_OT_InstallDependencies(Operator):
    bl_idname = "pidgeontoolbag.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Install the Python dependencies required by the addon"

    
    def execute(self, context):
        dependencies_to_install = []
        if bpy.context.scene.sfr_settings.install_dependencies: dependencies_to_install.append("sfr")
        if bpy.context.scene.siu_settings.install_dependencies: dependencies_to_install.append("siu")

        if not dependencies_to_install:
            self.report({"ERROR"}, "No dependencies selected for installation.")
            return {'FINISHED'}
        
        try:
            dependencies.install_dependencies(dependencies_to_install)
        except ValueError as ve:
            self.report({"ERROR"}, f"Error installing package {ve.args[0]}.\n\nCheck the System Console for details.")
        if dependencies._error:
            return {'CANCELLED'}
        
        self.report({"INFO"}, "Restart Blender to complete installation!")
        return {'FINISHED'}
    
    def draw(self, context):
        mas_chars = 55
        layout = self.layout
        col = layout.column()
        col.label(text="Information about the installation of dependencies:")
        box = col.box()
        box.label(text="Duration of Installation:")
        word_wrap(
            string="Please be aware that installing dependencies may take a significant amount of time.\nThis duration can vary depending on the speed of your internet connection and the performance of your computer.",
            layout=box,
            max_char=mas_chars
        )
        box = col.box()
        box.label(text="Do Not Close Blender:")
        word_wrap(
            string="It's crucial that you do not close Blender while the dependencies are being installed.\nBut if you must close Blender, you can resume the installation at any time by clicking the 'Install Dependencies' button again.",
            layout=box,
            max_char=mas_chars
        )
        box = col.box()
        box.label(text="Monitoring Progress:")
        word_wrap(
            string="If you wish to monitor the progress of the installation, you can do so by opening the console. This can be done by clicking on the 'Toggle Console' button.\nThe console will provide you with real-time updates and messages regarding the installation process.",
            layout=box,
            max_char=mas_chars
        )
        box = col.box()
        box.label(text="Disk Space Consideration:")
        word_wrap(
            string="Be aware that choosing to install the full set of dependencies will require additional disk space.\nEnsure that your system has sufficient space available to accommodate these files.",
            layout=box,
            max_char=mas_chars
        )
        col.operator("wm.console_toggle", text="Toggle Console")
        col.label(text="Addons requiering additional Dependencies:")
        row = col.row()
        row.label(text="- Super Fast Render")
        row.prop(bpy.context.scene.sfr_settings, "install_dependencies", text="Install? (~230MB)", toggle=True)
        row = col.row()
        row.label(text="- Super Image Upscaler")
        row.prop(bpy.context.scene.siu_settings, "install_dependencies", text="Install? (~5GB)", toggle=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class PTB_OT_OpenAddonPrefs(Operator):
    bl_idname = "pidgeontoolbag.open_addon_prefs"
    bl_label = "Open Addon Prefs"
    bl_description = "Open the addon preferences"

    def execute(self, context):
        bpy.context.preferences.active_section = 'ADDONS'
        bpy.context.window_manager.addon_search = "Pidgeon Tool Bag"
        bpy.ops.screen.userpref_show()

        return {'FINISHED'}
    
    
classes = (
    PTB_OT_InstallDependencies,
    PTB_OT_OpenAddonPrefs,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")