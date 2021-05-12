import bpy



class BakeWrangler_ValueGroups(bpy.types.Panel):
    '''Panel in node editor to manage grouped/linked values'''
    bl_label = "Value Groups"
    bl_idname = "OBJECT_PT_BW_ValueGroups"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "area"
    bl_category = "Bake Wrangler"
    
    @classmethod
    def poll(cls, context):
        # Only display if the edited tree is of the correct type
        return (context.area and context.area.ui_type == 'BakeWrangler_Tree')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Upcoming feature to manage setting values")



# Classes to register
classes = (
    BakeWrangler_ValueGroups,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()