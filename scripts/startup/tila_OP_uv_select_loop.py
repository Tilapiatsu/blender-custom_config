import bpy


class TILA_uv_select(bpy.types.Operator):
    bl_label = "TILA: UV select"
    bl_idname = "uv.tila_uv_select"
    bl_options = {"REGISTER", "UNDO"}

    extend: bpy.props.BoolProperty(name="Extend", default=False)
    loop: bpy.props.BoolProperty(name="Loop", default=False)
    deselect: bpy.props.BoolProperty(name="Deselect", defaul=False)
    deselect_all: bpy.props.BoolProperty(name="Deselect All", default=False)
    toggle: bpy.props.BoolProperty(name="Toggle", defaul=False)

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):
        if self.loop:
            command = bpy.ops.uv.select_loop
            args = {"extend": self.extend}
        else:
            command = bpy.ops.uv.select
            args = {
                "extend": self.extend,
                "deselect": self.deselect,
                "deselect_all": self.deselect_all,
                "toggle": self.toggle,
            }

        command("INVOKE_DEFAULT", **args)

        if self.loop and bpy.context.scene.tool_settings.uv_select_mode != "VERTEX":
            command("INVOKE_DEFAULT", **args)

        return {"FINISHED"}


classes = (TILA_uv_select,)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
