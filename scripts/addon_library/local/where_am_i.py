import bpy
bl_info = {
    "name": "Where am I",
    "author": "Nezumi",
    "version": (0, 0, 1),
    "blender": (2, 83, 1),
    "location": "Search menu",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "Development",
    "support": "TESTING"
}


class WM_OT_where_am_i(bpy.types.Operator):
    """Print area and region types to console"""
    bl_idname = "wm.where_am_i"
    bl_label = "Where am I"

    def execute(self, context):
        print(f"Area: {context.area.type}")
        print(f'UI_Type: {context.area.ui_type}')
        for i, a in enumerate(context.screen.areas):
            if context.area == a:
                print(f"index: {i}")
#        for region in context.area.regions:
#            print(f"\tRegion: {region.type}")
        return {'FINISHED'}


classes = [WM_OT_where_am_i,
           ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
