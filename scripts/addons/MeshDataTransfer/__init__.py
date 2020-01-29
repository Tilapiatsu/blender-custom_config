
import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty)
from .operators import (TransferShapeData, TransferShapeKeyData, TransferVertexGroupsData, TransferUVData)

bl_info = {
    "name" : "MeshDataTransfer",
    "author" : "Maurizio Memoli",
    "description" : "This add on will transfer geometry data from one mesh to another based on 3 different spaces:"
                    " 'world, object, uv' also will tranfer UVs based on topology",
    "blender" : (2, 80, 0),
    "version" : (1, 2, 1,),
    "location" : "(Object Mode) Mesh > ObjectData > Mesh Data Transfer ",
    "warning" : "",
    "wiki_url": "",
    "category" : "Mesh"
}




def scene_chosenobject_poll(self , object):
    if bpy.context.active_object == object:
        return False
    return object.type == 'MESH'


class MeshDataSettings(PropertyGroup):
    mesh_object_space: bpy.props.EnumProperty(
        items=[('WORLD', 'World', '', 1),('LOCAL', 'Local', '', 2), ('UVS', 'Active UV', '', 3), ('TOPOLOGY', 'Topology', '', 4)],
        name="Object Space", default = 'LOCAL')

    search_method: bpy.props.EnumProperty(
        items=[('CLOSEST', 'Closest', '', 1),('RAYCAST', 'Raycast', '', 2)],
        name="Search method")

    # transfer_shape: bpy.props.BoolProperty()
    #
    # transfer_shapekeys: bpy.props.BoolProperty()
    #
    # transfer_vertex_groups : bpy.props.BoolProperty()
    #
    # transfer_uv_data: bpy.props.BoolProperty ()

    mesh_source: bpy.props.PointerProperty(type=bpy.types.Object, poll=scene_chosenobject_poll)

    vertex_group_filter: bpy.props.StringProperty (name="Vertex Group")

    transfer_shape_as_key : bpy.props.BoolProperty ()

    transfer_modified_target : bpy.props.BoolProperty ()
    transfer_modified_source : bpy.props.BoolProperty ()

class MeshDataGlobalSettings(PropertyGroup):
    transfer_modified_target : bpy.props.BoolProperty ()
    transfer_modified_source : bpy.props.BoolProperty ()

class ShapeKeysProp(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty()
    enabled : bpy.props.BoolProperty()

#=========================================UI===============================================================

class DATA_PT_mesh_data_transfer(bpy.types.Panel):
    bl_label = "Mesh Data Transfer"
    bl_idname = "MESH_PT_mesh_data_transfer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mesh


    def draw(self, context):
        active = bpy.context.active_object
        ob_prop = context.object.mesh_data_transfer_object
        vg_prop = context.object.mesh_data_transfer_object
        sc_prop = context.scene.mesh_data_transfer_global
        ob = context.object

        # mesh_object_space layout
        main_box_layout = self.layout.box()
        sample_main_box = main_box_layout.box()

        option_label = sample_main_box.row()
        option_label.alignment = 'CENTER'
        option_label.label(text="Sample Space")
        option_row = sample_main_box.row()
        option_row.prop(ob_prop, "mesh_object_space", expand=True, text="Sample space")
        option_row2 = sample_main_box.row()
        option_row2.prop(ob_prop, 'search_method', expand=True, text="Search method")

        #option_row.use_property_split = True
        # sample_target_mod = main_box_layout.row ()
        # sample_target_mod.prop(ob_prop, 'transfer_modified_target', text="Sample Modified Target", icon='MESH_DATA')
        sample_source_mod = main_box_layout.row()
        sample_source_mod.prop(ob_prop, 'transfer_modified_source', text="Sample Modified Source", icon='MESH_DATA')

        if ob_prop.mesh_object_space not in {'WORLD', 'LOCAL', 'UVS'}:
            # sample_target_mod.enabled = False
            sample_source_mod.enabled = False

        #mesh picker layout
        mesh_picker_box_layout = main_box_layout.box()
        mesh_picker_box_layout.prop_search(ob_prop, "mesh_source", context.scene, "objects", text="Source: ")



        #top row
        top_row_layout = main_box_layout.row()
        left_top_row_box_layout = top_row_layout.box ()
        shape_cols_layout = left_top_row_box_layout.row()
        shape_cols_layout.operator ("object.transfer_shape_data" , text="Transfer Shape" , icon="MOD_DATA_TRANSFER")
        split = shape_cols_layout.split()
        split.prop (ob_prop , "transfer_shape_as_key" , text="", toggle=True, icon='SHAPEKEY_DATA')
        left_bottom_row_box_layout = left_top_row_box_layout.row()
        left_bottom_row_box_layout.operator("object.transfer_vertex_groups_data" , text="Transfer Vertex Groups" ,
                                                icon="GROUP_VERTEX")


        top_row_layout.split()
        right_top_row_box_layout = top_row_layout.box()
        right_top_row_box_layout.operator ("object.transfer_uv_data" , text="Transfer UV" ,
                                         icon="UV_DATA")
        right_bottom_row_box_layout = right_top_row_box_layout.row()
        right_bottom_row_box_layout.operator("object.transfer_shape_key_data" , text="Transfer Shape Keys" ,
                                                icon="SHAPEKEY_DATA")
        #mesh picker layout
        vgroup_picker_box_layout = main_box_layout.box()
        vgroup_picker_box_layout.prop_search(ob_prop, "vertex_group_filter", active, "vertex_groups")

#=================================================================================================================

classes = (DATA_PT_mesh_data_transfer, MeshDataSettings, MeshDataGlobalSettings, TransferShapeData,
           TransferShapeKeyData, TransferVertexGroupsData, TransferUVData)

def register():
    global classes
    for cl in classes:
        bpy.utils.register_class(cl)

    bpy.types.Object.mesh_data_transfer_object = PointerProperty (type=MeshDataSettings)
    bpy.types.Scene.mesh_data_transfer_global = PointerProperty (type=MeshDataGlobalSettings)

def unregister():
    global classes
    for cl in classes:
        print (cl)
        bpy.utils.unregister_class (cl)

    del bpy.types.Object.mesh_data_transfer_object
    del bpy.types.Scene.mesh_data_transfer_global

if __name__ == "__main__":
    register()
