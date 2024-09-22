import bpy
from mathutils import Vector

bl_info = {
	"name": "Tila : Edit Instanced Collection",
	"description": "Edit a Collection Instance's source Collection",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (3, 1, 0),
	"support": "COMMUNITY",
}

seen_popup = False

class EditInstancedCollection(bpy.types.Operator):
    """Edit the Collection referenced by this Collection Instance in a new Scene"""
    bl_idname = "object.edit_instanced_collection"
    bl_label = "Edit Instanced Collection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        coll = bpy.context.active_object.instance_collection

        if not coll:
            print("Active item is not a collection instance")
            self.report({"WARNING"}, "Active item is not a collection instance")
            return {"CANCELLED"}

        scene_name = f"temp:{coll.name}"
        bpy.ops.scene.new(type="EMPTY")
        new_scene = bpy.context.scene
        new_scene.name = scene_name
        bpy.context.window.scene = new_scene
        new_scene.collection.children.link(coll)

        # Select the collection and frame
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[coll.name]
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.object.select_all(action='DESELECT')


        return {"FINISHED"}
    

classes = (
	EditInstancedCollection,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()