import bpy

bl_info = {
    "name": "Tila : Convert Empty To Collection",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Object",
}

class TILA_ConvertEmptyToCollection(bpy.types.Operator):
    bl_idname = "object.tila_convert_empty_to_collection"
    bl_label = "TILA: Convert Empty to Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_parent_collection(self, object):
        parent_collection = ''
        collections = {}
        
        collection_name = object.users_collection[0].name
        if collection_name not in collections.keys():
            collections[object.users_collection[0].name] = 1
        else:
            collections[object.users_collection[0].name] += 1
        
        parent_collection = ''
        max_item = 0
        for c,n in collections.items():
            if n>max_item:
                max_item = n
                parent_collection = c

        return parent_collection

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        for o in selected_objects:
            if o.type != 'EMPTY':
                continue
            parent_collection_name = self.get_parent_collection(o)

            if parent_collection_name == 'Scene Collection':
                parent_collection = bpy.context.scene.collection
            else:
                parent_collection = bpy.data.collections[parent_collection_name]

            new_collection = bpy.data.collections.new(o.name)
            parent_collection.children.link(new_collection)
            
            for c in o.children:
                new_collection.objects.link(c)
                world_loc = c.matrix_world.to_translation()
                c.parent = None
                c.matrix_world.translation = world_loc
                if c.name in (parent_collection.objects):
                    parent_collection.objects.unlink(c)
                
            bpy.data.objects.remove(o, do_unlink=True)

        return {'FINISHED'}


def menu_item_draw_func(self, context):
    # Replace the next line with your menu draw code
    self.layout.separator()
    self.layout.operator('object.tila_convert_empty_to_collection', icon='OUTLINER_COLLECTION', text='Convert Empty to Collection')

addon_keymaps = []

classes = (TILA_ConvertEmptyToCollection,)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.OUTLINER_MT_object.append(menu_item_draw_func)

def unregister():
    bpy.types.OUTLINER_MT_object.remove(menu_item_draw_func)

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()