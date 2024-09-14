import bpy
from bpy.types import Operator

def move_UV_layer_up (obj, name):

    uvs = obj.data.uv_layers
    uvs.active_index = obj.data.uv_layers.find(name)

    if uvs.active_index == 0:
        return {'FINISHED'}

    uvs.active_index -= 1
    move_UV_layer_down(obj, uvs.active.name)
    obj.data.uv_layers.active = obj.data.uv_layers[name]

def move_UV_layer_down (obj, name):

    uvs = obj.data.uv_layers
    uvs.active_index = obj.data.uv_layers.find(name)
    orig_ind = uvs.active_index
    orig_name = uvs.active.name

    if orig_ind == len(uvs) - 1:
        return {'FINISHED'}

    # Move the layer after it
    name = obj.data.uv_layers[orig_ind + 1].name
    move_to_bottom(obj, name)

    #Move the layer we wanted to move
    name = obj.data.uv_layers[orig_ind].name
    move_to_bottom(obj, name)

    #Move the rest that are after
    for i in range(orig_ind, len(uvs) - 2):
        name = obj.data.uv_layers[orig_ind].name
        move_to_bottom(obj, name)

    #Set the active layer to the one we moved
    obj.data.uv_layers.active = obj.data.uv_layers[orig_name]

def move_to_bottom(obj, name):
    uvs = obj.data.uv_layers
    obj.data.uv_layers.active = obj.data.uv_layers[name]
    obj.data.uv_layers.new(name="_temp_")

    # delete the "old" one
    uvMap = obj.data.uv_layers.get(name)
    obj.data.uv_layers.remove(uvMap)

    # set the name of the last one
    uvs.active_index = len(uvs) - 1
    uvs.active.name = name

class OBJECT_OT_set_active_uv(bpy.types.Operator):
    """Syncs the active UV layer on all Objects in Selection, creates one if necessary"""
    bl_idname = "object.set_active_uv_for_selected_objects"
    bl_label = "Set UV Layer on all Objects in Selection, create one if necessary"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):   
        scene = context.scene
        target_uv = context.active_object.data.uv_layers.active
        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj != context.active_object:
                if target_uv.name in obj.data.uv_layers.keys():
                     #Active UV Layer = Target Layer
                    obj.data.uv_layers.active = obj.data.uv_layers[target_uv.name]
                else:
                    obj.data.uv_layers.new(name=target_uv.name)
                    obj.data.uv_layers.active = obj.data.uv_layers[target_uv.name]
        return {'FINISHED'}
    
class OBJECT_OT_delete_active_uv(bpy.types.Operator):
    """Deletes selected layer on all Selected Objects if a map with the same name exists"""
    bl_idname = "object.delete_active_uv_layer_for_selected_objects"
    bl_label = "Delete UV Layer on all Selected Objects if a map with the same name exists"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):   
            scene = context.scene
            #Setting the name of the UV map to delete
            target_uv = context.active_object.data.uv_layers.active.name
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                        try:
                           uvMap = obj.data.uv_layers.get(target_uv)
                           obj.data.uv_layers.remove(uvMap)
                        except:
                           pass
            return {'FINISHED'}

class OBJECT_OT_set_active_render_uv(bpy.types.Operator):
    """Sets the active UV render layer on all Objects in Selection if a map with the same name exists"""
    bl_idname = "object.set_active_uv_render_layer_for_selected_objects"
    bl_label = "Set UV Render Layer on Selected Objects if a map with the same name exists"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):
            scene = context.scene
            #Setting the name of the UV map to set
            target_uv = context.active_object.data.uv_layers.active
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                        try:
                           uvMap = obj.data.uv_layers.get(target_uv.name)
                           obj.data.uv_layers[uvMap.name].active_render = True
                        except:
                           pass
                        
                   
            return {'FINISHED'}

class OBJECT_OT_copy_unique_uv_layers(bpy.types.Operator):
    """Copies unique UV layers from selected objects to each selected object"""
    bl_idname = "object.copy_unique_uv_layers_for_selected_objects"
    bl_label = "Copy Unique UV Layers on all Objects in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):
        unique_uv_layers = []
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                for uv_layer in obj.data.uv_layers:
                    if uv_layer.name not in unique_uv_layers:
                        unique_uv_layers.append(uv_layer.name)

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                for uv_name in unique_uv_layers:
                    if uv_name not in [layer.name for layer in obj.data.uv_layers]:
                        obj.data.uv_layers.new(name=uv_name)
        return {'FINISHED'}

class OBJECT_OT_move_UV_layer_down(Operator):
    """Move the active UV layer down, active object only"""
    bl_idname = "object.move_uv_layer_down"
    bl_label = "Move Down"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context): 
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):
        #if 8 layers, cancel
        if len(context.active_object.data.uv_layers) == 8:
            return {'CANCELLED 7 Layers Max'}
        obj = context.active_object
        name = obj.data.uv_layers.active.name
        move_UV_layer_down(obj, name)
        return {'FINISHED'}

class OBJECT_OT_move_UV_layer_up(Operator):
    """Move the active UV layer up, active object only"""
    bl_idname = "object.move_uv_layer_up"
    bl_label = "Move Up"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context): 
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):
        #if 8 layers, cancel
        if len(context.active_object.data.uv_layers) == 8:
            return {'CANCELLED 7 Layers Max'}
        obj = context.active_object
        name = obj.data.uv_layers.active.name
        move_UV_layer_up (obj, name)

        return {'FINISHED'}

class OBJECT_OT_sync_uv_layer_order(Operator):
    """Reorder Layers on Selected Objects to match the active object, WIP doesn't always sort complex scenarios in first pass"""
    bl_idname = "object.sync_uv_layer_order_for_selected_objects"
    bl_label = "Sync UV Maps Order"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.uv_layers.active

    def execute(self, context):
        #if 8 layers, cancel
        if len(context.active_object.data.uv_layers) == 8:
            return {'CANCELLED 7 Layers Max'}
        active = bpy.context.active_object
        original_uv_layers = {layer.name: i for i, layer in enumerate(active.data.uv_layers)}
        iteration = 3
        other_objs = [obj for obj in bpy.context.selected_objects if obj != active]
        for obj in other_objs:
            
            if obj.type == 'MESH':
                for i in range(iteration):
                    uv_layer_index = {layer.name: i for i, layer in enumerate(obj.data.uv_layers)}
                    #Start from the bottom and move up, otherwise sorting bottom won't work
                    uvs = obj.data.uv_layers
                    for uv_layer in uvs:
                        uv_name = uv_layer.name
                        if uv_name not in original_uv_layers:
                            continue

                        #Getting the index of the active UV layer and the index of the UV layer we are looking at
                        original_index = original_uv_layers[uv_name]
                        current_uv_index = uv_layer_index[uv_name]
                        #Only moving layers down
                        if(current_uv_index < original_index):
                            for _ in range(original_index - current_uv_index):
                                #ofsetted the layer below, it moved up
                                if(current_uv_index + 1 < len(obj.data.uv_layers)):
                                    ofsettedUV = obj.data.uv_layers[current_uv_index + 1].name
                                    uv_layer_index[ofsettedUV] -= 1
                                move_UV_layer_down(obj, uv_name)
                                uv_layer_index[uv_name] += 1
                                current_uv_index += 1

        return {'FINISHED'}