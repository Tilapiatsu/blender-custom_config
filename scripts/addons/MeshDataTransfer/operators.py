import bpy
from .mesh_data_transfer import MeshDataTransfer

class TransferShapeData(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.transfer_shape_data"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        sample_space = context.object.mesh_data_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.mesh_data_transfer_object.mesh_source is not None\
               and sample_space != "TOPOLOGY" and bpy.context.object.mode == "OBJECT"

    def execute(self, context):

        active = context.active_object
        active_prop = context.object.mesh_data_transfer_object
        deformed_source = active_prop.transfer_modified_source
        # sc_prop = context.scene.mesh_data_transfer_global
        as_shape_key = active_prop.transfer_shape_as_key
        source = active.mesh_data_transfer_object.mesh_source
        mask_vertex_group = active_prop.vertex_group_filter
        invert_mask = active_prop.invert_vertex_group_filter
        # target_prop = target.mesh_data_transfer_global

        world_space = False
        uv_space = False

        search_method = active_prop.search_method
        sample_space = active_prop.mesh_object_space
        if sample_space == 'UVS':
            uv_space = True

        if sample_space == 'LOCAL':
            world_space = False

        if sample_space == 'WORLD':
            world_space = True
        transfer_data = MeshDataTransfer(target=active, source =source, world_space=world_space,
                                         deformed_source=deformed_source,invert_vertex_group = invert_mask,
                                         uv_space=uv_space, search_method=search_method, vertex_group=mask_vertex_group)
        transferred = transfer_data.transfer_vertex_position(as_shape_key=as_shape_key)
        transfer_data.free()
        if not transferred:
            self.report({'INFO'}, 'Unable to perform the operation.')
            return{'CANCELLED'}

        return {'FINISHED'}


class TransferShapeKeyData(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.transfer_shape_key_data"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        sample_space = context.object.mesh_data_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.mesh_data_transfer_object.mesh_source is not None\
               and sample_space != "TOPOLOGY" and bpy.context.object.mode == "OBJECT"

    def execute(self, context):

        active = context.active_object
        active_prop = context.object.mesh_data_transfer_object

        deformed_source = active_prop.transfer_modified_source
        # sc_prop = context.scene.mesh_data_transfer_global
        as_shape_key = active_prop.transfer_shape_as_key
        source = active.mesh_data_transfer_object.mesh_source
        mask_vertex_group = active_prop.vertex_group_filter
        invert_mask = active_prop.invert_vertex_group_filter
        # target_prop = target.mesh_data_transfer_global

        world_space = False
        uv_space = False

        search_method = active_prop.search_method
        sample_space = active_prop.mesh_object_space
        if sample_space == 'UVS':
            uv_space = True

        if sample_space == 'LOCAL':
            world_space = False

        if sample_space == 'WORLD':
            world_space = True
        transfer_data = MeshDataTransfer(target=active, source =source, world_space=world_space,
                                         uv_space=uv_space,deformed_source= deformed_source , invert_vertex_group= invert_mask,
                                         search_method=search_method, vertex_group=mask_vertex_group)
        transferred = transfer_data.transfer_shape_keys()
        transfer_data.free()
        if not transferred:
            self.report({'INFO'}, 'Unable to perform the operation.')
            return{'CANCELLED'}

        return {'FINISHED'}


class TransferVertexGroupsData(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.transfer_vertex_groups_data"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        sample_space = context.object.mesh_data_transfer_object.mesh_object_space

        return context.active_object is not None \
               and context.active_object.mesh_data_transfer_object.mesh_source is not None \
               and sample_space != "TOPOLOGY" and bpy.context.object.mode == "OBJECT"


    def execute(self, context):

        active = context.active_object
        active_prop = context.object.mesh_data_transfer_object

        # sc_prop = context.scene.mesh_data_transfer_global
        as_shape_key = active_prop.transfer_shape_as_key
        source = active.mesh_data_transfer_object.mesh_source
        mask_vertex_group = active_prop.vertex_group_filter
        invert_mask = active_prop.invert_vertex_group_filter
        # target_prop = target.mesh_data_transfer_global

        world_space = False
        uv_space = False

        search_method = active_prop.search_method
        sample_space = active_prop.mesh_object_space
        if sample_space == 'UVS':
            uv_space = True

        if sample_space == 'LOCAL':
            world_space = False

        if sample_space == 'WORLD':
            world_space = True
        transfer_data = MeshDataTransfer(target=active, source =source, world_space=world_space,
                                         invert_vertex_group = invert_mask, uv_space=uv_space, search_method=search_method,
                                         vertex_group=mask_vertex_group)
        transferred = transfer_data.transfer_vertex_groups()
        transfer_data.free()
        if not transferred:
            self.report({'INFO'}, 'Unable to perform the operation.')
            return{'CANCELLED'}

        return {'FINISHED'}

class TransferUVData(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.transfer_uv_data"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mesh_data_transfer_object.mesh_source is not None \
               and bpy.context.object.mode == "OBJECT"

    def execute(self, context):

        active = context.active_object
        active_prop = context.object.mesh_data_transfer_object

        # sc_prop = context.scene.mesh_data_transfer_global
        as_shape_key = active_prop.transfer_shape_as_key
        source = active.mesh_data_transfer_object.mesh_source
        # target_prop = target.mesh_data_transfer_global
        mask_vertex_group = active_prop.vertex_group_filter
        invert_mask = active_prop.invert_vertex_group_filter

        world_space = False
        topology = False
        search_method = active_prop.search_method
        sample_space = active_prop.mesh_object_space
        if sample_space == 'UVS':
            uv_space = True

        if sample_space == 'LOCAL':
            world_space = False

        if sample_space == 'WORLD':
            world_space = True

        if sample_space == 'TOPOLOGY':
            topology = True

        #transfer_uvs(active, target, world_space)
        transfer_data = MeshDataTransfer(target=active, source =source, world_space=world_space,
                                         invert_vertex_group = invert_mask, search_method=search_method,
                                         topology=topology, vertex_group=mask_vertex_group)
        transfer_data.transfer_uvs()
        transfer_data.free()


        return {'FINISHED'}
