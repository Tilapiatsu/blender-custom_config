import bpy
import re

bl_info = {
	"name": "Tila : Copy Mirror Vertex Group",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

class TILA_UVMap_Add(bpy.types.Operator):
    bl_idname = "object.tila_uvmap_add"
    bl_label = "TILA: Add UV Map on All Selected Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    name : bpy.props.StringProperty(name='Name', default='UVMap')

    compatible_type = ['MESH']

    def invoke(self, context, event):

        self.name = context.active_object.data.uv_layers.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

        for o in self.object_to_process:
            o.data.uv_layers.new(name=self.name)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "name")

class TILA_UVMap_Remove(bpy.types.Operator):
    bl_idname = "object.tila_uvmap_remove"
    bl_label = "TILA: Remove UV Map on All Selected Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    name : bpy.props.StringProperty(name='Name', default='UVMap')

    compatible_type = ['MESH']

    def execute(self, context):
        self.name = context.active_object.data.uv_layers.active.name
        self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

        for o in self.object_to_process:
            if self.name not in o.data.uv_layers:
                continue

            uv_layer = o.data.uv_layers[self.name]
            o.data.uv_layers.remove(layer=uv_layer)

        return {'FINISHED'}

#  move from APEC : https://blender.stackexchange.com/questions/67266/changing-order-of-uv-maps
class TILA_UVMap_Move(bpy.types.Operator):
    bl_idname = "object.tila_uvmap_move"
    bl_label = "TILA: Move UV Map on All Selected Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    direction : bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")], default="UP")
    uv_layer_name = 'UVMap'

    compatible_type = ['MESH']

    def execute(self, context):
        self.uv_layer_name = context.active_object.data.uv_layers.active.name

        self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]
        for o in self.object_to_process:
            self.move(o)

        return {'FINISHED'}

    def move(self, o):
        uv_layers = o.data.uv_layers
        if self.uv_layer_name not in uv_layers:
            return

        self.make_active(self.uv_layer_name, uv_layers)

        if self.direction == "UP":
            self.move_up(uv_layers, self.uv_layer_name)
        elif self.direction == "DOWN":
            self.move_down(uv_layers, self.uv_layer_name)

    def move_up(self, uv_layers, layer_name):
        if uv_layers.active_index == 0:
            return

        uv_layers.active_index -= 1

        self.move_down(uv_layers, uv_layers.active.name)
        self.make_active(layer_name, uv_layers)

    def move_down(self, uv_layers, layer_name):
        orig_ind = uv_layers.active_index

        if orig_ind == len(uv_layers) - 1:
            return

        # use "trick" on the one after it
        self.move_to_bottom(orig_ind + 1, uv_layers)

        # use the "trick" on the UV map
        self.move_to_bottom(orig_ind, uv_layers)
        

        # use the "trick" on the rest that are after where it was
        for i in range(orig_ind, len(uv_layers) - 2):
            self.move_to_bottom(orig_ind, uv_layers)

        self.make_active(layer_name, uv_layers)


    def move_to_bottom(self, index, uv_layers):
        uv_layers.active_index = index
        new_name = uv_layers.active.name

        uv_layers.new(name='temp')

        # delete the "old" one
        self.make_active(new_name, uv_layers)
        uv_layers.remove(uv_layers.active)

        # set the name of the last one
        uv_layers.active_index = len(uv_layers) - 1
        uv_layers.active.name = new_name
    
    def make_active(self, name, uv_layers):
        if name not in uv_layers:
            return
        uv_layers.active = uv_layers[name]

def menu_draw(self, context):
    layout = self.layout
    row = layout.row()
    column = row.column()
    column.operator("object.tila_uvmap_add", text='Add', icon='ADD')
    column.operator("object.tila_uvmap_remove", text='Remove', icon='REMOVE')
    column = row.column()
    column.operator("object.tila_uvmap_move", icon='TRIA_UP', text='Move Up').direction='UP'
    column.operator("object.tila_uvmap_move", icon='TRIA_DOWN', text='Move Down').direction='DOWN'

classes = (TILA_UVMap_Add, TILA_UVMap_Remove, TILA_UVMap_Move)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.DATA_PT_uv_texture.append(menu_draw)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.DATA_PT_uv_texture.remove(menu_draw)


if __name__ == "__main__":
    register()
