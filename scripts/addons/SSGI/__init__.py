import bpy
import os

bl_info = {
    "name": "SSGI for Eevee",
    "description": "SSGI addon for Eevee",
    "author": "0451",
    "version": (0, 1, 0),
    "blender": (2, 83, 4),
    "location": "3D View > View",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}

from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class SSGI_Properties(PropertyGroup):

    my_bool: BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False
        )

    boost: FloatProperty(
        name = "Boost SSGI",
        description = "A float property",
        default = 0.1,
        min = 0.00,
        max = 1
        )    
    disable: FloatProperty(
        name = "Disable SSGI",
        description = "A float property",
        default = 0,
        min = 0.00,
        max = 1
        )
    roughness: FloatProperty(
        name = "Diffuse GI Roughness",
        description = "A float property",
        default = 0.75,
        min = 0.5,
        max = 1
        )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------






class One_Click_SetUp(Operator):
    bl_label = "Add SSGI"
    bl_idname = "wm.oneclicksetup"
    

    def execute(self, context):
        #set scene SSR settings
        bpy.context.scene.eevee.use_ssr = True
        bpy.context.scene.eevee.ssr_max_roughness = 1
        bpy.context.scene.eevee.ssr_thickness = 0.4
        bpy.context.scene.eevee.ssr_border_fade = 0
        bpy.context.scene.eevee.ssr_quality = 0.78
        bpy.context.scene.eevee.use_ssr_halfres = False
        print("SSR settings set to support SSGI materials")
        
        detectedNodegroups = False
        
        for mat in bpy.data.materials:
            if mat.name == '_SSGI_NodeGroups_':
                detectedNodegroups = True
                print("SSGI_NodeGroups found")
                
        if detectedNodegroups == False:
            print("no SSGI_NodeGroups found")
            os.path.abspath(__file__)
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSGI_Library.blend\\Material\\")
            material_name = "_SSGI_NodeGroups_"
            bpy.ops.wm.append( filename = material_name, directory = filepath)
            
            for mat in bpy.data.materials:
                if mat.use_nodes == True:
                    for node in mat.node_tree.nodes:
                        if mat.name == '_SSGI_NodeGroups_':
                            mat.use_fake_user=True
                            #add drivers
                            
                            #driver = bpy.data.node_groups["BOOST GI Control"].nodes["BOOST_GI_Node"].inputs[1].default_value
                            #var = driver.driver.variables.new()
                            #var.name = "variable"
                            #var.targets[0].data_path = "PATH"
                            #var.targets[0].id = "Target_Object_Name"
                            #driver.driver.expression = "variable"
                            
            print("appended SSGI_NodeGroups material")
        

            
        print("finished evaluating SSGI resources")
          
        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if node.type in ["BSDF_PRINCIPLED"] and mat.name != '_SSGI_NodeGroups_':
                        
                        #Define OLD NEW
                        old = node
                        new = mat.node_tree.nodes.new("ShaderNodeGroup")
                        #Set group object data
                        new.node_tree = bpy.data.node_groups['_SSGI_Principled_']

                        #SET new attributes from old
                        new.parent = old.parent
                        new.label = old.label
                        new.mute = old.mute
                        new.hide = old.hide
                        new.select = old.select
                        new.location = old.location
                        #cosmetics
                        new.use_custom_color = True
                        new.color = (0.42869, 0.610496, 0.53948)
                        #(0.854993, 0.514918, 0.274677)
                        new.width = 240

                        

                        
                        # inputs SET DEFAULT and LINK
                        for (name, point) in old.inputs.items():
                            input = new.inputs.get(name)
                            if input:
                                input.default_value = point.default_value
                                for link in point.links:
                                    new.id_data.links.new(link.from_socket, input)

                        # outputs SET BSDF Out links
                        for (name, point) in old.outputs.items():
                            output = new.outputs.get(name)
                            if output:
                                for link in point.links:
                                    new.id_data.links.new(output, link.to_socket)
                        
                        #Remove old
                        print("PRINCIPLED BSDF converted to SSGI nodegroup")
                        mat.node_tree.nodes.remove(old)
                        
        print("Finished converting PRINCIPLED BSDF")
        
        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if node.type in ["BSDF_DIFFUSE"] and mat.name != '_SSGI_NodeGroups_':
                        
                        #Define OLD NEW
                        old = node
                        new = mat.node_tree.nodes.new("ShaderNodeGroup")
                        #Set group object data
                        new.node_tree = bpy.data.node_groups['_SSGI_Diffuse_']

                        #SET new attributes from old
                        new.parent = old.parent
                        new.label = old.label
                        new.mute = old.mute
                        new.hide = old.hide
                        new.select = old.select
                        new.location = old.location
                        #cosmetics
                        new.use_custom_color = True
                        new.color = (0.42869, 0.610496, 0.53948)
                        new.width = 150
                        
                        # inputs SET DEFAULT and LINK
                        for (name, point) in old.inputs.items():
                            input = new.inputs.get(name)
                            if input:
                                input.default_value = point.default_value
                                for link in point.links:
                                    new.id_data.links.new(link.from_socket, input)

                        # outputs SET BSDF Out links
                        for (name, point) in old.outputs.items():
                            output = new.outputs.get(name)
                            if output:
                                for link in point.links:
                                    new.id_data.links.new(output, link.to_socket)
                                    
                        #Remove old
                        print("DIFFUSE BSDF converted to SSGI nodegroup")
                        mat.node_tree.nodes.remove(old)
                        
        print("Finished converting DIFFUSE BSDF")
        return {'FINISHED'}
    
    
    
    
    
    
    
    
    
    
    
    
class Append_SSGI_Nodegroups(Operator):
    bl_label = "1) Append SSGI resources"
    bl_idname = "wm.append_ssgi"
    

    def execute(self, context):
        
        detectedNodegroups = False
        
        for mat in bpy.data.materials:
            if mat.name == '_SSGI_NodeGroups_':
                detectedNodegroups = True
                print("SSGI_NodeGroups found")
                
        if detectedNodegroups == False:
            print("no SSGI_NodeGroups found")
            os.path.abspath(__file__)
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSGI_Library.blend\\Material\\")
            material_name = "_SSGI_NodeGroups_"
            bpy.ops.wm.append( filename = material_name, directory = filepath)
            
            for mat in bpy.data.materials:
                if mat.use_nodes == True:
                    for node in mat.node_tree.nodes:
                        if mat.name == '_SSGI_NodeGroups_':
                            mat.use_fake_user=True
                            #add drivers
                            
                            #driver = bpy.data.node_groups["BOOST GI Control"].nodes["BOOST_GI_Node"].inputs[1].default_value
                            #var = driver.driver.variables.new()
                            #var.name = "variable"
                            #var.targets[0].data_path = "PATH"
                            #var.targets[0].id = "Target_Object_Name"
                            #driver.driver.expression = "variable"
                            
            print("appended SSGI_NodeGroups material")
        

            
        print("finished evaluating SSGI resources")
        return {'FINISHED'}

class SET_SSR_Settings(Operator):
    bl_label = "2) Set SSR settings"
    bl_idname = "wm.ssr_settings"

    def execute(self, context):

        bpy.context.scene.eevee.use_ssr = True
        bpy.context.scene.eevee.ssr_max_roughness = 1
        bpy.context.scene.eevee.ssr_thickness = 0.4
        bpy.context.scene.eevee.ssr_border_fade = 0
        bpy.context.scene.eevee.ssr_quality = 0.78
        bpy.context.scene.eevee.use_ssr_halfres = False
        print("SSR settings set to support SSGI materials")
        return {'FINISHED'}
    
class Convert_Materials_To_SSGI(Operator):
    bl_label = "3) Convert materials to SSGI"
    bl_idname = "wm.convert_to_ssgi"

    def execute(self, context):
        
        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if node.type in ["BSDF_PRINCIPLED"] and mat.name != '_SSGI_NodeGroups_':
                        
                        #Define OLD NEW
                        old = node
                        new = mat.node_tree.nodes.new("ShaderNodeGroup")
                        #Set group object data
                        new.node_tree = bpy.data.node_groups['_SSGI_Principled_']

                        #SET new attributes from old
                        new.parent = old.parent
                        new.label = old.label
                        new.mute = old.mute
                        new.hide = old.hide
                        new.select = old.select
                        new.location = old.location
                        
                        # inputs SET DEFAULT and LINK
                        for (name, point) in old.inputs.items():
                            input = new.inputs.get(name)
                            if input:
                                input.default_value = point.default_value
                                for link in point.links:
                                    new.id_data.links.new(link.from_socket, input)

                        # outputs SET BSDF Out links
                        for (name, point) in old.outputs.items():
                            output = new.outputs.get(name)
                            if output:
                                for link in point.links:
                                    new.id_data.links.new(output, link.to_socket)
                        
                        #Remove old
                        print("PRINCIPLED BSDF converted to SSGI nodegroup")
                        mat.node_tree.nodes.remove(old)
                        
        print("Finished converting PRINCIPLED BSDF")
        
        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if node.type in ["BSDF_DIFFUSE"] and mat.name != '_SSGI_NodeGroups_':
                        
                        #Define OLD NEW
                        old = node
                        new = mat.node_tree.nodes.new("ShaderNodeGroup")
                        #Set group object data
                        new.node_tree = bpy.data.node_groups['_SSGI_Diffuse_']

                        #SET new attributes from old
                        new.parent = old.parent
                        new.label = old.label
                        new.mute = old.mute
                        new.hide = old.hide
                        new.select = old.select
                        new.location = old.location
                        
                        # inputs SET DEFAULT and LINK
                        for (name, point) in old.inputs.items():
                            input = new.inputs.get(name)
                            if input:
                                input.default_value = point.default_value
                                for link in point.links:
                                    new.id_data.links.new(link.from_socket, input)

                        # outputs SET BSDF Out links
                        for (name, point) in old.outputs.items():
                            output = new.outputs.get(name)
                            if output:
                                for link in point.links:
                                    new.id_data.links.new(output, link.to_socket)
                                    
                        #Remove old
                        print("DIFFUSE BSDF converted to SSGI nodegroup")
                        mat.node_tree.nodes.remove(old)
                        
        print("Finished converting DIFFUSE BSDF")
        return {'FINISHED'}
    
class Remove_SSGI_From_Materials(Operator):
    bl_label = "Remove SSGI"
    bl_idname = "wm.remove_ssgi"

    def execute(self, context):
        
        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if hasattr(node, 'node_tree') == True:
                        if hasattr(node.node_tree, 'name') == True:
                            if node.type in ["GROUP"] and node.node_tree.name == '_SSGI_Principled_' and mat.name != '_SSGI_NodeGroups_':   
                                #Define OLD NEW
                                old = node
                                new = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

                                #SET new attributes from old
                                new.parent = old.parent
                                new.label = old.label
                                new.mute = old.mute
                                new.hide = old.hide
                                new.select = old.select
                                new.location = old.location
                                
                                # inputs SET DEFAULT and LINK
                                for (name, point) in old.inputs.items():
                                    input = new.inputs.get(name)
                                    if input:
                                        input.default_value = point.default_value
                                        for link in point.links:
                                            new.id_data.links.new(link.from_socket, input)

                                # outputs SET BSDF Out links
                                for (name, point) in old.outputs.items():
                                    output = new.outputs.get(name)
                                    if output:
                                        for link in point.links:
                                            new.id_data.links.new(output, link.to_socket)

                                #Remove old
                                print(node.node_tree.name, "converted to PRINCIPLED BSDF")
                                mat.node_tree.nodes.remove(old)

        for mat in bpy.data.materials:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if hasattr(node, 'node_tree') == True:
                        if hasattr(node.node_tree, 'name') == True:
                            if node.type in ["GROUP"] and node.node_tree.name == '_SSGI_Diffuse_' and mat.name != '_SSGI_NodeGroups_':
                                
                                #Define OLD NEW
                                old = node
                                new = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')

                                #SET new attributes from old
                                new.parent = old.parent
                                new.label = old.label
                                new.mute = old.mute
                                new.hide = old.hide
                                new.select = old.select
                                new.location = old.location
                                
                                # inputs SET DEFAULT and LINK
                                for (name, point) in old.inputs.items():
                                    input = new.inputs.get(name)
                                    if input:
                                        input.default_value = point.default_value
                                        for link in point.links:
                                            new.id_data.links.new(link.from_socket, input)

                                # outputs SET BSDF Out links
                                for (name, point) in old.outputs.items():
                                    output = new.outputs.get(name)
                                    if output:
                                        for link in point.links:
                                            new.id_data.links.new(output, link.to_socket)
                                            
                                #Remove old
                                print(node.node_tree.name, "converted to DIFFUSE BSDF")
                                mat.node_tree.nodes.remove(old)
                        
        for mat in bpy.data.materials: #remove Fake user from lib material
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if mat.name == '_SSGI_NodeGroups_':
                        mat.use_fake_user=False
                        print("remove fake user from SSGI lib")
                        #WIP Remove from blend
        
        bpy.data.materials.remove(bpy.data.materials["_SSGI_NodeGroups_"])
        
        bpy.data.node_groups.remove(bpy.data.node_groups["_Alpha_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_BOOST GI Control_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_BOOST GI_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_Boost_SSGI_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_DIFFUSE GI Roughness_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_DiffuseRoughness Container_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_DISABLE SSGI_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_Fresnel_SSGI_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_Glossy_Dielectrics_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_Metallic SSR/SSGI switch_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI FIX Baking_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI Mix Controls_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_Diffuse_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_Principled_"])
        bpy.data.node_groups.remove(bpy.data.node_groups["_SubtractiveCol_"])
        
        
        print("Finished removing SSGI resources")
        return {'FINISHED'}
    
class Irradiance_Bake_Default(Operator):
    bl_label = "Bake Indirect Lighting (Default)"
    bl_idname = "wm.default_bake"

    def execute(self, context):

        bpy.ops.scene.light_cache_bake()
        
        print("Baked Default Irradiance Lighting")
        return {'FINISHED'}
    
class Irradiance_Bake(Operator):
    bl_label = "Bake Indirect Lighting (Alternative)"
    bl_idname = "wm.fixed_bake"

    def execute(self, context):

        bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Principled_BakeFix_"].inputs[1].default_value = 1
        bpy.ops.scene.light_cache_bake()
        bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Principled_BakeFix_"].inputs[1].default_value = 0
        
        print("Baked Fixed Irradiance Lighting")
        return {'FINISHED'}
    
class Irradiance_Bake_Delete(Operator):
    bl_label = "Delete Lighting Cache"
    bl_idname = "wm.delete_bake"

    def execute(self, context):

        bpy.ops.scene.light_cache_free()
        
        print("Deleted Lighting Cache")
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    UI
# ------------------------------------------------------------------------

class SSGI_UI(Panel):
    bl_label = "SSGI for Eevee"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSGI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ssgi_t = scene.ssgi_tool
        #layout.label(text="Enable while Baking Indirect Light:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        #layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Principled_BakeFix_"].inputs[1], "default_value",text="Fix While Baking")
        layout.operator("wm.default_bake")
        layout.operator("wm.fixed_bake")
        layout.operator("wm.delete_bake")
        #layout.prop(ssgi_t, "my_bool")
        #layout.prop(ssgi_t, "boost")
        #layout.prop(ssgi_t, "disable")
        #layout.prop(ssgi_t, "roughness")
        #layout.separator() wm.oneclicksetup
        layout.label(text="Setup SSGI:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.oneclicksetup")
        layout.operator("wm.remove_ssgi")
        #layout.label(text="set by step", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        #layout.operator("wm.append_ssgi")
        #layout.operator("wm.ssr_settings")
        #layout.operator("wm.convert_to_ssgi")
        layout.label(text="SSGI Controls:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.prop(bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1], "default_value",text="Boost SSGI")
        layout.prop(bpy.data.node_groups["_SSGI_"].nodes["_SubtractiveCol_Node_"].inputs[1], "default_value",text="Darken Direct Light")
        layout.prop(bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2], "default_value",text="Disable SSGI/SSR")
        layout.label(text="Tweaks:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.prop(bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0], "default_value",text="Diffuse GI Roughness")
        layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0], "default_value",text="Glossy Dielectrics")
        layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1], "default_value",text="Glossy Dielectrics Darken")
        layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3], "default_value",text="Rough Fresnel")
        layout.label(text="SSR Controls:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.prop(context.scene.eevee, "ssr_thickness",text="SSR Thickness")
        layout.prop(context.scene.eevee, "ssr_quality",text="SSR Trace Precision")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    One_Click_SetUp,
    Append_SSGI_Nodegroups,
    Convert_Materials_To_SSGI,
    Remove_SSGI_From_Materials,
    Irradiance_Bake_Default,
    Irradiance_Bake,
    Irradiance_Bake_Delete,
    SET_SSR_Settings,
    SSGI_Properties,
    SSGI_UI,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.ssgi_tool = PointerProperty(type=SSGI_Properties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ssgi_tool


if __name__ == "__main__":
    register()
