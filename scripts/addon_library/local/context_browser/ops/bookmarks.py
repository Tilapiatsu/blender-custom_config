import bpy
from ..addon import prefs, temp_prefs, ic


class CB_OT_bookmark(bpy.types.Operator):
    bl_idname = "cb.bookmark"
    bl_label = ""
    bl_description = (
        "Click to apply\n"
        "Shift+Click to rename\n"
        "Alt+Click to remove"
    )
    bl_options = {'INTERNAL'}

    bookmark: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.shift:
            bpy.ops.cb.bookmark_rename(
                'INVOKE_DEFAULT', path=self.bookmark)
        elif event.alt:
            prefs().remove_bookmark(self.bookmark)
        else:
            temp_prefs().cd.update_lists(self.bookmark)
        return {'FINISHED'}


class CB_OT_bookmark_add(bpy.types.Operator):
    bl_idname = "cb.bookmark_add"
    bl_label = ""
    bl_description = "Add bookmark"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        pr = prefs()
        pr.add_bookmark(temp_prefs().cd.path)
        return {'FINISHED'}


class CB_OT_bookmark_rename(bpy.types.Operator):
    bl_idname = "cb.bookmark_rename"
    bl_label = "Rename Bookmark"
    bl_options = {'INTERNAL'}
    bl_property = "name"

    path: bpy.props.StringProperty()
    name: bpy.props.StringProperty()

    def check(self, context):
        return True

    def draw(self, context):
        self.layout.prop(self, "name", text="", icon=ic('SOLO_ON'))

    def execute(self, context):
        prefs().rename_bookmark(self.path, self.name)
        return {'FINISHED'}

    def invoke(self, context, modal):
        pr = prefs()
        for b in pr.bookmarks:
            if b.path == self.path:
                self.name = b.name
                break
        return context.window_manager.invoke_props_dialog(self)
