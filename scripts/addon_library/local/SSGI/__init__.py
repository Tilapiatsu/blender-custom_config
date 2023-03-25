import bpy
import os
from mathutils import Color, Vector

bl_info = {
    "name": "SSGI for Eevee",
    "description": "SSGI addon for Eevee - (Addon Only Version)",
    "author": "0451",
    "version": (0, 1, 4),
    "blender": (2, 92, 0),
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

    tester: BoolProperty(
        name="Enable or Disable",
        description="___",
        default = False
        )
    """
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
    """


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
        bpy.context.scene.eevee.ssr_thickness = 1
        bpy.context.scene.eevee.ssr_border_fade = 0
        bpy.context.scene.eevee.ssr_quality = 1
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
            #Material
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSGI_Library.blend\\Material\\")
            material_name = "_SSGI_NodeGroups_"
            bpy.ops.wm.append( filename = material_name, directory = filepath)
            #World
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSGI_Library.blend\\World\\")
            material_name = "_SSGI_WorldNodeGroups_"
            bpy.ops.wm.append( filename = material_name, directory = filepath)
            
            for mat in bpy.data.materials:
                if mat.use_nodes == True:
                    for node in mat.node_tree.nodes:
                        if mat.name == '_SSGI_NodeGroups_':
                            mat.use_fake_user=True
                            
            for mat in bpy.data.worlds:
                if mat.use_nodes == True:
                    for node in mat.node_tree.nodes:
                        if mat.name == '_SSGI_WorldNodeGroups_':
                            mat.use_fake_user=True
                            
            print("appended _SSGI_NodeGroups_ & _SSGI_WorldNodeGroups_ materials")
        

            
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
        
        #WORLD MATERIAL
        for mat in bpy.data.worlds:
            if mat.use_nodes == True:
                #print(mat)
                for node in mat.node_tree.nodes:
                    #print(node)
                    if node.type in ["OUTPUT_WORLD"] and mat.name != '_SSGI_WorldNodeGroups_': #FINDS World output and adds a note to it. 
                        print("Found output world")
                        
                        worldoutput = node
                        surfacein = worldoutput.inputs[0]
                        
                        
                        if (surfacein.is_linked):
                            print("Surface output is linked, adding world material controller")
                            
                                                
                            controller = mat.node_tree.nodes.new("ShaderNodeGroup")
                            controller.node_tree = bpy.data.node_groups['_SSGI_WorldController_']

                            #SET attributes from World Output Node
                            controller.parent = worldoutput.parent
                            controller.label = worldoutput.label
                            #controller.mute = worldoutput.mute
                            #controller.hide = worldoutputd.hide
                            #controller.select = worldoutput.select
                            controller.location = worldoutput.location
                            controller.location -= Vector((75.0, 0))
                            #cosmetics
                            controller.use_custom_color = True
                            controller.color = (0.42869, 0.610496, 0.53948)
                            controller.width = 50
                            
                            
                            # Set node input
                            for (name, point) in worldoutput.inputs.items():
                                print("W INPUT NAME IS: ", name)
                                input = controller.inputs.get(name)
                                if input:
                                    for link in point.links:
                                        print("W LINK NAME IS: ", link)
                                        controller.id_data.links.new(link.from_socket, input)
                           
                            
                            controller.id_data.links.new(controller.outputs["Output"], worldoutput.inputs[0])
                               
                        else:
                            print("Surface output not linked, world material controller not added")
        
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
        
        #Remove World                        
        for mat in bpy.data.worlds:
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if hasattr(node, 'node_tree') == True:
                        if hasattr(node.node_tree, 'name') == True:
                            if node.type in ["GROUP"] and node.node_tree.name == '_SSGI_WorldController_' and mat.name != '_SSGI_WorldNodeGroups_':
                                print("Removing World Output controller:")
                                
                                controller = node
                                #don't do stuff like this:
                                check_in = 0
                                check_out = 0

                                #get node connected to input
                                for con_inputs in controller.inputs:
                                    for node_links in con_inputs.links:
                                        print("World controller input: ", node_links.from_node.name)
                                        controller_in = node_links.from_node
                                        check_in = 1
                                        

                                #get node connected to output
                                for con_outputs in controller.outputs:
                                    for node_links in con_outputs.links:
                                        print("World controller output: ", node_links.to_node.name)
                                        controller_out = node_links.to_node
                                        check_out = 1
                                
                                #link input node to output node
                                #controller_in.id_data.links.new(controller_in.outputs[0], controller_out.inputs[0])
                                if check_in == 1 and check_out == 1:
                                    print("Attempting to link world output back")
                                    mat.node_tree.links.new(controller_in.outputs[0], controller_out.inputs[0])
                                
                                #Remove controller
                                mat.node_tree.nodes.remove(controller)
                        
        for mat in bpy.data.materials: #remove Fake user from lib material
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if mat.name == '_SSGI_NodeGroups_':
                        mat.use_fake_user=False
                        print("remove fake user from SSGI lib")
                        #WIP Remove from blend
                        
        for mat in bpy.data.worlds: #remove Fake user from lib material
            if mat.use_nodes == True:
                for node in mat.node_tree.nodes:
                    if mat.name == '_SSGI_WorldNodeGroups_':
                        mat.use_fake_user=False
                        print("remove fake user from SSGI World lib")
        
       
        ###################################### ---------------- move to list, loop + catch with try -------------------#########################
        for mat in bpy.data.materials:
            if mat.name == '_SSGI_NodeGroups_':
                bpy.data.materials.remove(bpy.data.materials["_SSGI_NodeGroups_"])
                
        for mat in bpy.data.node_groups:
            if mat.name == '_Boost_SSGI_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_Boost_SSGI_"]) #deprecated
        
        for mat in bpy.data.node_groups:
            if mat.name == '_Alpha_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_Alpha_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_BOOST GI Control_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_BOOST GI Control_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_BOOST GI_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_BOOST GI_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_DIFFUSE GI Roughness_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_DIFFUSE GI Roughness_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_DiffuseRoughness Container_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_DiffuseRoughness Container_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_DISABLE SSGI_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_DISABLE SSGI_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_Fresnel_SSGI_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_Fresnel_SSGI_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_Glossy_Dielectrics_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_Glossy_Dielectrics_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_Metallic SSR/SSGI switch_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_Metallic SSR/SSGI switch_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI FIX Baking_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI FIX Baking_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI Mix Controls_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI Mix Controls_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_Diffuse_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_Diffuse_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_Principled_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_Principled_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SubtractiveCol_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SubtractiveCol_"])
        
        for mat in bpy.data.worlds:
            if mat.name == '_SSGI_WorldNodeGroups_':
                bpy.data.worlds.remove(bpy.data.worlds["_SSGI_WorldNodeGroups_"]) #remove world materials#
                
        for mat in bpy.data.node_groups:
            if mat.name == '_ClampInputs_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_ClampInputs_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_Dielectric_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_Dielectric_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_ScatterNormals_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_ScatterNormals_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_WorldController_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_WorldController_"])
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_WCtrl_':
                bpy.data.node_groups.remove(bpy.data.node_groups["_SSGI_WCtrl_"])
        
        
        print("Finished removing SSGI resources")
        return {'FINISHED'}
    ################################################################################################################################################################################
    
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
    
class Cubemap_Bake_Default(Operator):
    bl_label = "Bake Cubemap Only (Default)"
    bl_idname = "wm.default_cubemap_bake"

    def execute(self, context):

        bpy.ops.scene.light_cache_bake(subset='CUBEMAPS')
        
        print("Baked Default Cubemap Only")
        return {'FINISHED'}
    
class Cubemap_Bake(Operator):
    bl_label = "Bake Cubemap Only (Alternative)"
    bl_idname = "wm.fixed_cubemap_bake"

    def execute(self, context):

        bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Principled_BakeFix_"].inputs[1].default_value = 1
        bpy.ops.scene.light_cache_bake(subset='CUBEMAPS')
        bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Principled_BakeFix_"].inputs[1].default_value = 0
        
        print("Baked Fixed Cubemap Only")
        return {'FINISHED'}
    
class Irradiance_Bake_Delete(Operator):
    bl_label = "Delete Lighting Cache"
    bl_idname = "wm.delete_bake"

    def execute(self, context):

        bpy.ops.scene.light_cache_free()
        
        print("Deleted Lighting Cache")
        return {'FINISHED'}
    
class Update_SSGI_Materials(Operator): # refactor all into functions - ####################################################################################################
    bl_label = "Update SSGI materials"
    bl_idname = "wm.update_materials"

    def execute(self, context):
        print("Refreshing materials...")
        #check if number function
        def is_number(s):
            try:
                float(s)
                return True
            except (TypeError, ValueError):
                return False
                        
        #copy ui values ----------------------------------------------------------------------------------------------------
        #Create list with no specific values
        
        """ #- values for reference
        #0 bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1].default_value
        #1 bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0].default_value
        #2 bpy.data.node_groups["_BOOST GI Control_"].nodes["_ClampInputsNode_"].inputs[1].default_value
        #3 bpy.data.node_groups["_SSGI_"].nodes["_SSGI_ScatterNormalsNode_"].inputs[2].default_value
        #4 bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0].default_value
        #5 bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[1].default_value
        #6 bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[2].default_value
        #7 bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[3].default_value
        #8 bpy.data.node_groups["_SSGI_"].nodes["_SubtractiveCol_Node_"].inputs[1].default_value
        #9 bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1].default_value
        #10 bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3].default_value
        #11 bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2].default_value
        """
        #create empty list
        ui_values_list = []
        #fill with strings (float check on setting back on)
        i = 0
        while i < 12:
            ui_values_list.insert(i,"missing")
            i += 1
        
        #if exist, add to list except(KeyError)
        try:
            ui_values_list.insert(0, bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(1, bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(2, bpy.data.node_groups["_BOOST GI Control_"].nodes["_ClampInputsNode_"].inputs[1].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(3, bpy.data.node_groups["_SSGI_"].nodes["_SSGI_ScatterNormalsNode_"].inputs[2].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(4, bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(5, bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[1].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(6, bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[2].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(7, bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[3].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(8, bpy.data.node_groups["_SSGI_"].nodes["_SubtractiveCol_Node_"].inputs[1].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(9, bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(10, bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
        try:
            ui_values_list.insert(11, bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2].default_value)
        except (TypeError, KeyError):
            print("missing value on copy settings")
            
        #create duplicate list
        ui_values_list_floats = ui_values_list[:]
        
        #convert copy to floats #can be skipped?
        print("converting copy to floats...")
        for item in ui_values_list_floats:
            if is_number(item) == True:
                float(item)
                print("SSGI setting converted:", item)
        
        #        
        """
        i = 1
        for item in ui_values_list:
            if is_number(item) == True:
                item = ui_values_list_floats[i]
                print("SSGI setting copied:", item, "at index:", i)
                i = i + 1
            else:
                print("setting skipped at index:", i)
                i = i + 1
        """
        
        #
        """
        intensity = bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1].default_value
        ssr = bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0].default_value
        clamp = bpy.data.node_groups["_BOOST GI Control_"].nodes["_ClampInputsNode_"].inputs[1].default_value
        scatter = bpy.data.node_groups["_SSGI_"].nodes["_SSGI_ScatterNormalsNode_"].inputs[2].default_value
        roughness = bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0].default_value
        cameraray = bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[1].default_value
        diffuseray = bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[2].default_value
        glossyray = bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[3].default_value
        
        ssrbrightness = bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1].default_value
        gifresnel = bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3].default_value
        disable = bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2].default_value
        """

        
        
        
        
        
        
        #remove master materials -----------------------------------------------------------------------------------------
        bpy.ops.wm.remove_ssgi()
        #add master materials - make sure no numeric suffix on append (remove takes care of that currently) --------------
        bpy.ops.wm.oneclicksetup()
        
        #remove duplicates with numeric suffix ---------------------------------------------------------------------------
        ssgi_nodegroups_list = (
            "_Boost_SSGI_",
            "_Alpha_",
            "_BOOST GI Control_",
            "_BOOST GI_",
            "_DIFFUSE GI Roughness_",
            "_DiffuseRoughness Container_",
            "_DISABLE SSGI_",
            "_Fresnel_SSGI_",
            "_Glossy_Dielectrics_",
            "_Metallic SSR/SSGI switch_",
            "_SSGI FIX Baking_",
            "_SSGI_",
            "_SSGI_Diffuse_",
            "_SSGI_Principled_",
            "_SubtractiveCol_",
            "_ClampInputs_",
            "_SSGI_Dielectric_",
            "_SSGI_ScatterNormals_",
            "_SSGI_WorldController_",
            "_SSGI_WCtrl_",
            
        )

        def main():
            
            print("Removing duplicate SSGI nodegroups...")
            #iterate nodegroups - call eliminate
            for group in bpy.data.node_groups:
                for node in group.nodes:
                    if hasattr(node, 'node_tree') == True:
                        if hasattr(node.node_tree, 'name') == True:
                            if node.type == 'GROUP':
                                replace(node)

            #iterate nodegroups - call replace
            mats = list(bpy.data.materials)
            worlds = list(bpy.data.worlds)
            
            for mat in mats + worlds:
                if mat.use_nodes:
                    for node in mat.node_tree.nodes:
                        if hasattr(node, 'node_tree') == True:
                            if hasattr(node.node_tree, 'name') == True:
                                replace(node)
            
            print("Finished removing duplicates...")


        def replace(node):

            #separate name
            (base, sep, ext) = node.node_tree.name.rpartition('.')

            #if numeric suffix has base and in list
            if ext.isnumeric():
                if base in bpy.data.node_groups and base in ssgi_nodegroups_list:
                    
                    print("Duplicate node name is:", node.node_tree.name)
                    print("  Replace ", node.node_tree.name, " with ", base)
                    
                    #remove fake user
                    node.node_tree.use_fake_user = False
                    #replace
                    node.node_tree = bpy.data.node_groups.get(base)

        #Call Main
        main()
        
        
        #set settings from copy floats -----------------------------------------------------------------------------------------------
        print("setting values...")
        #move to single loop and dont test like this
        for mat in bpy.data.node_groups:
            if mat.name == "_BOOST GI_":
                if is_number(ui_values_list_floats[0]) == True:
                    print("0")
                    bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1].default_value = ui_values_list_floats[0]
        for mat in bpy.data.node_groups:
            if mat.name == '_Glossy_Dielectrics_':
                if is_number(ui_values_list_floats[1]) == True:
                    print("1")
                    bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0].default_value = ui_values_list_floats[1]
        for mat in bpy.data.node_groups:
            if mat.name == '_ClampInputs_':
                if is_number(ui_values_list_floats[2]) == True:
                    print("2")
                    bpy.data.node_groups["_BOOST GI Control_"].nodes["_ClampInputsNode_"].inputs[1].default_value = ui_values_list_floats[2]
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_ScatterNormals_':
                if is_number(ui_values_list_floats[3]) == True:
                    print("3")
                    bpy.data.node_groups["_SSGI_"].nodes["_SSGI_ScatterNormalsNode_"].inputs[2].default_value = ui_values_list_floats[3]
        for mat in bpy.data.node_groups:
            if mat.name == '_DIFFUSE GI Roughness_':
                if is_number(ui_values_list_floats[4]) == True:
                    print("4")
                    bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0].default_value = ui_values_list_floats[4]
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_WCtrl_':
                if is_number(ui_values_list_floats[5]) == True:
                    print("5")
                    bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[1].default_value = ui_values_list_floats[5]
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_WCtrl_':
                if is_number(ui_values_list_floats[6]) == True:
                    print("6")
                    bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[2].default_value = ui_values_list_floats[6]
        for mat in bpy.data.node_groups:
            if mat.name == '_SSGI_WCtrl_':
                if is_number(ui_values_list_floats[7]) == True:
                    print("7")
                    bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[3].default_value = ui_values_list_floats[7]
        for mat in bpy.data.node_groups:########
            if mat.name == '_SSGI_WCtrl_':
                if is_number(ui_values_list_floats[8]) == True:
                    print("8")
                    bpy.data.node_groups["_SSGI_"].nodes["_SubtractiveCol_Node_"].inputs[1].default_value = ui_values_list_floats[8]
        for mat in bpy.data.node_groups:
            if mat.name == '_Glossy_Dielectrics_':
                if is_number(ui_values_list_floats[9]) == True:
                    print("9")
                    bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1].default_value = ui_values_list_floats[9]
        for mat in bpy.data.node_groups:
            if mat.name == '_Fresnel_SSGI_':
                if is_number(ui_values_list_floats[10]) == True:
                    print("10")
                    bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3].default_value = ui_values_list_floats[10]
        for mat in bpy.data.node_groups:
            if mat.name == '_DISABLE SSGI_':
                if is_number(ui_values_list_floats[11]) == True:
                    print("11")
                    bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2].default_value = ui_values_list_floats[11]
        
        print("Finished updating SSGI materials")
        return {'FINISHED'}
    
    
#bpy.ops.wm.test_class()
class test_class(Operator): ##############################################################
    bl_label = "Test Stuff"
    bl_idname = "wm.test_class"

    def execute(self, context):
        print("!!!test class called!!!")
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    UI
# ------------------------------------------------------------------------

class SSGI_UI(Panel):
    #Dev v2
    bl_label = "SSGI for Eevee 0.1.4 - Addon Ver."
    bl_idname = "OBJECT_PT_custom_panel_1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSGI'
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ssgi_t = scene.ssgi_tool
        
        #layout.prop(ssgi_t, "boost")
        
        #SETUP - ADD REMOVE REFRESH
        layout.label(text="Setup SSGI:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.oneclicksetup")
        layout.operator("wm.remove_ssgi")
        layout.label(text="Refresh SSGI:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.update_materials")
        
        #Check for outdated nodegroups --------------------------------------------------------------------------        
        #check if _SSGi_ nodegroup exists --- do this properly in future
        check_outdated_a = False
        check_outdated_b = False
        
        
        for mat in bpy.data.node_groups: #check if nodegroup exists - check if version input exists
            if mat.name == "_SSGI_":
                try:
                    float(bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Node_"].inputs[4].default_value)
                except (IndexError, KeyError):
                    print("a has no version number")
                    check_outdated_a = True
                try:
                    float(bpy.data.node_groups["_SSGI_Diffuse_"].nodes["_SSGI_Node_"].inputs[4].default_value)
                except (IndexError, KeyError):
                    print("b has no version number")
                    check_outdated_b = True
            
                #check version number if existance isn't eliminated
                if check_outdated_a == False:
                    if round(bpy.data.node_groups["_SSGI_Principled_"].nodes["_SSGI_Node_"].inputs[4].default_value, 1) != 1.4:
                        check_outdated_a = True
                if check_outdated_b == False:
                    if round(bpy.data.node_groups["_SSGI_Diffuse_"].nodes["_SSGI_Node_"].inputs[4].default_value, 1) != 1.4:
                        check_outdated_b = True
        
        #if somewhere true draw
        if check_outdated_a == True or check_outdated_b == True:
            layout.label(text="Materials Outdated", text_ctxt="", translate=False, icon='ERROR', icon_value=0)
            layout.separator()
        
        #check for missing nodegroups and draw
        check_mat = False
        for mat in bpy.data.materials:
            if mat.name == '_SSGI_NodeGroups_':
                #print("SSGI_NodeGroups found for UI")
                layout.label(text="Controls:", text_ctxt="", translate=False, icon='NONE', icon_value=0)

                layout.prop(bpy.data.node_groups["_BOOST GI Control_"].nodes["_BOOST_GI_Node_"].inputs[1], "default_value",text="Intensity")
                layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[0], "default_value",text="Blend to SSR on Dielectrics")
                
                layout.label(text="Tweaks:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
                layout.prop(bpy.data.node_groups["_BOOST GI Control_"].nodes["_ClampInputsNode_"].inputs[1], "default_value",text="Clamp Input Colors")
                layout.prop(bpy.data.node_groups["_SSGI_"].nodes["_SSGI_ScatterNormalsNode_"].inputs[2], "default_value",text="Scatter Diffuse Normals")
                layout.prop(bpy.data.node_groups["_DiffuseRoughness Container_"].nodes["_DIFFUSE_SSGI_Rougness_Node_"].inputs[0], "default_value",text="Diffuse Roughness")
                
                check_mat = True
        if check_mat == False:
            layout.separator()
            layout.label(text="NO SSGI MATERIALS PRESENT", text_ctxt="", translate=False, icon='ERROR', icon_value=0)
            layout.separator()
            
        check_worldmat = False
        for mat in bpy.data.worlds:
            if mat.name == '_SSGI_WorldNodeGroups_':
                #world controller
                layout.label(text="World Material Ray Visibility:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
                layout.prop(bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[1], "default_value",text="Camera Strength")
                layout.prop(bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[2], "default_value",text="Diffuse Strength")
                layout.prop(bpy.data.node_groups["_SSGI_WorldController_"].nodes["_SSGI_WCtrlNode_"].inputs[3], "default_value",text="Glossy Strength (broken)")
                check_worldmat = True
        if check_worldmat == False:
            layout.separator()
            layout.label(text="NO SSGI WORLD MATERIALS PRESENT", text_ctxt="", translate=False, icon='ERROR', icon_value=0)
            layout.separator()
        
class SSGI_UI_Tweaks(Panel):
    bl_label = "SSGI Settings"
    bl_idname = "OBJECT_PT_custom_panel_2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSGI'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ssgi_t = scene.ssgi_tool
        
        check_mat = False
        for mat in bpy.data.materials:
            if mat.name == '_SSGI_NodeGroups_':
                #print("SSGI_NodeGroups found for UI")
                layout.label(text="Tweaks:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        
                layout.prop(bpy.data.node_groups["_SSGI_"].nodes["_SubtractiveCol_Node_"].inputs[1], "default_value",text="Remove Unneeded BSDF")
                layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Glossy_Dielectrics_Node_"].inputs[1], "default_value",text="Reduce SSR brightness (1 - correct)")
                layout.prop(bpy.data.node_groups["_SSGI_Principled_"].nodes["_Fresnel_SSGI_Node_"].inputs[3], "default_value",text="Add Fresnel to SSGI")
                layout.prop(bpy.data.node_groups["_SSGI Mix Controls_"].nodes["_DISABLE_SSGI_Node_"].inputs[2], "default_value",text="Disable SSGI/SSR")
                layout.label(text="SSR Controls:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
                layout.prop(context.scene.eevee, "ssr_thickness",text="SSR Thickness")
                layout.prop(context.scene.eevee, "ssr_quality",text="SSR Trace Precision")
                check_mat = True
        if check_mat == False:
            layout.separator()
            layout.label(text="NO SSGI MATERIALS PRESENT", text_ctxt="", translate=False, icon='ERROR', icon_value=0)
            layout.separator()
            
class SSGI_UI_Baking(Panel):
    bl_label = "Baking"
    bl_idname = "OBJECT_PT_custom_panel_3"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSGI'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ssgi_t = scene.ssgi_tool
            
        #BAKING
        layout.label(text="Indirect:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.default_bake")
        layout.operator("wm.fixed_bake")
        layout.label(text="Cubemap:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.default_cubemap_bake")
        layout.operator("wm.fixed_cubemap_bake")
        layout.label(text="Delete:", text_ctxt="", translate=False, icon='NONE', icon_value=0)
        layout.operator("wm.delete_bake")
 
# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    One_Click_SetUp,
    Remove_SSGI_From_Materials,
    Update_SSGI_Materials,
    Irradiance_Bake_Default,
    Irradiance_Bake,
    Cubemap_Bake_Default,
    Cubemap_Bake,
    Irradiance_Bake_Delete,
    SSGI_Properties,
    SSGI_UI,
    SSGI_UI_Tweaks,
    SSGI_UI_Baking,
    test_class,
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
