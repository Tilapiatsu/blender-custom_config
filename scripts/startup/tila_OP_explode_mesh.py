import bpy
import bmesh

bl_info = {
    "name": "Tila : Explode_mesh",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}

def get_selected_objects():
    selected_objects = bpy.context.objects_in_mode
    objs = [o for o in selected_objects if o.data.total_vert_sel]
    return objs

class TILA_SeparateAndSelect(bpy.types.Operator):
    bl_idname = "mesh.explode_mesh"        # unique identifier for buttons and menu items to reference.
    bl_label = "Explode Mesh"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    select_linked : bpy.props.BoolProperty(name='Extend Selection to linked', default=True) 
    apply_modifier : bpy.props.BoolProperty(name='Apply Modifier', default=False) 

    multires_modifier_type = 'MULTIRES'

    @classmethod
    def poll(cls, context):
        if not len(context.selected_objects):
            return False
        
        selected = False

        objs = get_selected_objects()

        if len(objs):
            selected = True
        
        if not selected:
            print('Please select at least an element')

        return selected
    
    def get_layer_collection(self, layer_collection, collection_name):
        found = None
        if (layer_collection.name == collection_name):
            return layer_collection
        for layer in layer_collection.children:
            found = self.get_layer_collection(layer, collection_name)
            if found:
                return found

    def create_child_collection(self, context, name):
        collections = bpy.data.collections
        if name in collections:
            return collections[name], False
        else:
            new_collection = bpy.data.collections.new(name)
            context.collection.children.link(new_collection)
            return new_collection, True

    def set_active_collection(self, context, name):
        context.view_layer.active_layer_collection = self.get_layer_collection(context.view_layer.layer_collection, name)
    
    def duplicate_object(self, obj, data=True, actions=True, collection=None, suffix=''):
        obj_copy = obj.copy()
        if data:
            obj_copy.data = obj_copy.data.copy()
        if actions and obj_copy.animation_data:
            obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
        collection.objects.link(obj_copy)
        if len(suffix):
            obj_copy.name = obj.name + suffix
        return obj_copy

    def separate_selected(self, context):
        self.set_active_collection(context, self.current_object_to_proceed.users_collection[0].name)
        self.exploded_collection, _ = self.create_child_collection(context, self.current_object_to_proceed.name + '_exploded')

        group_name = f"P{self.suffix:03d}"
        duplicate = self.duplicate_object(self.current_object_to_proceed, data=False, collection=self.exploded_collection, suffix = f'_{group_name}')

        self.current_object_to_proceed.vertex_groups.new(name= group_name)
        # vertex_group.add(self.selected_polygons, 1.0, 'REPLACE')
        bpy.ops.object.vertex_group_assign()
        
        modifier = duplicate.modifiers.new(name=group_name, type='MASK')
        modifier.vertex_group = group_name

        multires = [m for m in duplicate.modifiers if m.type == self.multires_modifier_type]
        if len(multires):
            bpy.ops.object.modifier_move_to_index({'object': duplicate}, modifier=group_name, index=1)
        else:
            bpy.ops.object.modifier_move_to_index({'object': duplicate}, modifier=group_name, index=0)

    def select_next_polygon_island(self, object):
        poly_to_explode = self.polygons_to_explode[object.name]

        if not len(poly_to_explode):
            return False
        
        me = object.data
        bm = bmesh.from_edit_mesh(me)
        faces = bm.faces
        faces[poly_to_explode[0]].select = True  # select index 0

        bmesh.update_edit_mesh(me)

        bpy.ops.mesh.select_linked()

        self.selected_polygons = self.get_selected_polygons([object])[object.name]

        self.polygons_to_explode[object.name] = list(set(self.polygons_to_explode[object.name]) - set(self.selected_polygons))

        return True

    def modal(self, context, event):
        if self.cancelled:
            self.report({'ERROR'}, 'Exploded Cancelled')
            return {'FINISHED'}
        
        if self.finished:
            self.report({'INFO'}, 'Exploded Successfully')
            return {'FINISHED'}
        
        
        if event.type in ['ESC']:
            self.cancelled = True

        if event.type in ['TIMER']:
            if self.current_object_to_proceed is None:
                self.current_object_to_proceed = self.objects_to_proceed.pop()
                bpy.context.view_layer.objects.active = self.current_object_to_proceed
                self.suffix = 0
                
            bpy.ops.mesh.select_all(action='DESELECT')
            self.suffix += 1
            if self.select_next_polygon_island(self.current_object_to_proceed) :
                self.separate_selected(context)
            else:
                self.current_object_to_proceed = None

            if not len(self.objects_to_proceed) and self.current_object_to_proceed == None:
                self.finished = True
                return {'PASS_THROUGH'}
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        self.separated = False
        self.cancelled = False
        self.finished = False
        self.suffix = 0
        self.vertex_groups = {}
        self.exploded_collection = None
        self.objects_to_proceed = get_selected_objects()

        if not len(self.objects_to_proceed):
            self.report({'ERROR'}, 'No objects selected')
            return {'CANCELLED'}

        if self.select_linked:
            bpy.ops.mesh.select_linked(delimit=set())
        self.polygons_to_explode = self.get_selected_polygons(self.objects_to_proceed)
        self.current_object_to_proceed = self.objects_to_proceed.pop()
        bpy.context.view_layer.objects.active = self.current_object_to_proceed

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def get_selected_polygons(self, objects):
        polygons = {}

        for o in objects:
            polygons[o.name] = []

            me = o.data
            bm = bmesh.from_edit_mesh(me)
            faces = bm.faces

            for f in faces:
                if f.select:
                    polygons[o.name].append(f.index)

            bmesh.update_edit_mesh(me)

        return polygons

classes = (TILA_SeparateAndSelect,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()