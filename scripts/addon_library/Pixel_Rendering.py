bl_info = {
    "name": "Pixel Rendering",
    "author": "Lars Hinnerk Grevsmühl (aka Mezaka)",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "description": "Helps with rendering Pixel Art.",
    "category": "Render",
}

import bpy
import os

class PixelPropertyGroup(bpy.types.PropertyGroup):
    preview_samples : bpy.props.IntProperty(name='Preview Samples', soft_min=1, soft_max=100,default = 10)
    final_samples : bpy.props.IntProperty(name='Final Samples', soft_min=1, soft_max=1000, default = 100)

#material helper
def createMaterial(materialName, materialType):
    if materialName in bpy.data.materials:
        print("Material "+materialName+" already existed - skipping")
        return
    mat = bpy.data.materials.new(name=materialName)
    mat.use_fake_user = True
    mat.use_nodes = True
    matOld = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(matOld)
    matOut = mat.node_tree.nodes["Material Output"]
    matOut.location = (0,0)
    matShader = mat.node_tree.nodes.new(type=materialType)
    matShader.location = (-200,0)
    matShader.inputs[0].default_value = (1,1,1,1)
    mat.node_tree.links.new(matShader.outputs[0],matOut.inputs[0])
    return mat

def createBuffer(bufferName):
    if bufferName in bpy.data.images:
        print("Texture "+bufferName+" already existed - skipping")
        return
    scene = bpy.data.scenes["Scene"]
    rw = scene.render.resolution_x
    rh = scene.render.resolution_y
    bpy.ops.image.new(name=bufferName,width=rw,height=rh)
    bpy.data.images[bufferName].use_fake_user = True
    
def createExampleMaterial():
    if "PixelExample" not in bpy.data.materials:
        #create custom group for mapping
        createCustomMappingGroup()
        #create nodes
        matPix = createMaterial("PixelExample",'ShaderNodeEmission')
        
        mappingNode = matPix.node_tree.nodes.new(type="ShaderNodeGroup")
        mappingNode.node_tree = bpy.data.node_groups["CustomCameraMapping"]
        mappingNode.location = (-1000,0)
        mixNode = matPix.node_tree.nodes.new("ShaderNodeMixRGB")
        mixNode.location = (-400,0)
        borderNode = matPix.node_tree.nodes.new("ShaderNodeValue")
        borderNode.location = (-700,100)
        borderNode.label = "IsBorder"
        borderNode.outputs[0].default_value = 0
        rampNode = matPix.node_tree.nodes.new("ShaderNodeValToRGB")
        rampNode.location = (-700,0)
        rampNode.color_ramp.interpolation = 'CONSTANT'
        rampNode.color_ramp.elements[0].position = 0.0
        rampNode.color_ramp.elements[0].color = (0.037,0.01,0.019,1)
        rampNode.color_ramp.elements[1].position = 0.076
        rampNode.color_ramp.elements[1].color = (0.068,0.034,0.042,1)
        rampNode.color_ramp.elements.new(0.225)        
        rampNode.color_ramp.elements[2].color = (0.105,0.107,0.054,1)
        rampNode.color_ramp.elements.new(0.459)
        rampNode.color_ramp.elements[3].color = (0.181,0.175,0.078,1)
        rampNode.color_ramp.elements.new(0.791)
        rampNode.color_ramp.elements[4].color = (0.279,0.266,0.095,1)
        #connect nodes
        links = matPix.node_tree.links
        links.new(mappingNode.outputs[0],rampNode.inputs[0])
        links.new(rampNode.outputs[0],mixNode.inputs[1])
        links.new(borderNode.outputs[0],mixNode.inputs[0])
        links.new(mixNode.outputs[0],matPix.node_tree.nodes["Emission"].inputs[0])

def createCustomMappingGroup():
    if "CustomCameraMapping" in bpy.data.node_groups:
        return 
    #create node group
    group = bpy.data.node_groups.new(type="ShaderNodeTree", name="CustomCameraMapping")
    #create input
    input_node = group.nodes.new("NodeGroupInput")
    input_node.location = (-1000, 0)
    #create output
    group.outputs.new("NodeSocketFloat", "LightingData")
    output_node = group.nodes.new("NodeGroupOutput")
    output_node.location = (0, 0)
    #create nodes
    nodes = group.nodes
    
    textureNode = nodes.new('ShaderNodeTexImage')
    textureNode.location = (-400,0)
    textureNode.image = bpy.data.images["DIFFUSE_BUFFER"]
    textureNode.extension = 'CLIP'
    textureNode.interpolation = 'Closest'
    
    offsetNode = nodes.new('ShaderNodeVectorMath')
    offsetNode.location = (-700,0)
    offsetNode.inputs[1].default_value = (0.5,0.5,0.5)
    offsetNode.operation = 'ADD'
    
    combineNode = nodes.new('ShaderNodeCombineXYZ')
    combineNode.location = (-1000,0)
    
    scaleXNode = nodes.new('ShaderNodeMath')
    scaleXNode.location = (-1300,0)
    scaleXNode.operation = 'DIVIDE'
    
    scaleYNode = nodes.new('ShaderNodeMath')
    scaleYNode.location = (-1300,-300)
    scaleYNode.operation = 'DIVIDE'
    
    separateNode = nodes.new('ShaderNodeSeparateXYZ')
    separateNode.location = (-1600,0)
    
    cameraScaleYNode = nodes.new('ShaderNodeMath')
    cameraScaleYNode.location = (-1600,-300)
    cameraScaleYNode.operation = 'MULTIPLY'
    
    cameraScaleNode = nodes.new('ShaderNodeValue')
    cameraScaleNode.location = (-1900,-300)
    cameraScaleNode.label = 'CameraScale'
    cameraScaleNode.outputs[0].default_value = bpy.data.cameras["Camera"].ortho_scale
    
    cameraRatioNode = nodes.new('ShaderNodeMath')
    cameraRatioNode.location = (-1900,-600)
    cameraRatioNode.operation = 'DIVIDE'
    
    cameraResXNode = nodes.new('ShaderNodeValue')
    cameraResXNode.location = (-2200,-600)
    cameraResXNode.label = "ResolutionX"
    cameraResXNode.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_x
    
    cameraResYNode = nodes.new('ShaderNodeValue')
    cameraResYNode.location = (-2200,-900)
    cameraResYNode.label = "ResolutionY"
    cameraResYNode.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_y
    
    coordNode = nodes.new('ShaderNodeTexCoord')
    coordNode.location = (-2200,0)
    coordNode.object = bpy.data.objects["Camera"]
    
    #create connections
    links = group.links
    
    links.new(textureNode.outputs[0],output_node.inputs[0])
    links.new(offsetNode.outputs[0],textureNode.inputs[0])
    links.new(combineNode.outputs[0],offsetNode.inputs[0])
    links.new(scaleXNode.outputs[0],combineNode.inputs[0])
    links.new(scaleYNode.outputs[0],combineNode.inputs[1])
    links.new(separateNode.outputs[0],scaleXNode.inputs[0])
    links.new(separateNode.outputs[1],scaleYNode.inputs[0])
    links.new(coordNode.outputs[3],separateNode.inputs[0])
    links.new(cameraScaleYNode.outputs[0],scaleYNode.inputs[1])
    links.new(cameraScaleNode.outputs[0],scaleXNode.inputs[1])
    links.new(cameraScaleNode.outputs[0],cameraScaleYNode.inputs[0])
    links.new(cameraRatioNode.outputs[0],cameraScaleYNode.inputs[1])
    links.new(cameraResYNode.outputs[0],cameraRatioNode.inputs[0])
    links.new(cameraResXNode.outputs[0],cameraRatioNode.inputs[1])

class RENDER_OT_PIXELART_SETUP(bpy.types.Operator):
    bl_label = "Setup Pixelart Rendering"
    bl_idname = "render.pixelart_setup" 
    
    def execute(self, context):
        print("Pixelart Setup")
        #set basic render settings
        d = bpy.data
        scene = d.scenes["Scene"]
        cycles = scene.cycles
        scene.render.engine = "CYCLES"
        cycles.samples = 1
        cycles.max_bounces = 0
        cycles.diffuse_bounces = 0
        cycles.glossy_bounces = 0
        cycles.filter_width = 0.01
        scene.view_settings.view_transform = "Standard"
        scene.render.dither_intensity = 0
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0
        #create override diffuse (+shield)
        createMaterial("OVERRIDE_DIFFUSE",'ShaderNodeBsdfPrincipled')
        #create override white
        createMaterial("OVERRIDE_EMISSION",'ShaderNodeEmission')
        #create empty render buffers
        createBuffer("DIFFUSE_BUFFER")
        createBuffer("FREESTYLE_BUFFER")
        createBuffer("BORDER_BUFFER")
        bpy.ops.file.pack_all()
        #create example material
        createExampleMaterial()
        #set up freestyle
        scene.render.line_thickness_mode = 'RELATIVE'
        bpy.data.linestyles["LineStyle"].thickness = 4.4
        bpy.data.linestyles["LineStyle"].thickness_position = 'INSIDE'
        #Set up compositor
        bpy.data.scenes["Scene"].use_nodes = True
        compTree = bpy.data.scenes["Scene"].node_tree 
        if len(compTree.nodes)<3:
            #create nodes
            outNode = compTree.nodes["Composite"]
            outNode.location = (0,0)
            renderNode = compTree.nodes["Render Layers"]
            renderNode.location = (-600,-600)
            mixNode = compTree.nodes.new("CompositorNodeMixRGB")
            mixNode.location = (-300,0)
            freestyleNode = compTree.nodes.new("CompositorNodeImage")
            freestyleNode.location = (-600,600)
            freestyleNode.image = bpy.data.images["FREESTYLE_BUFFER"]
            borderNode = compTree.nodes.new("CompositorNodeImage")
            borderNode.location = (-600,0)
            borderNode.image = bpy.data.images["BORDER_BUFFER"]
            #create links
            compTree.links.new(mixNode.outputs[0],outNode.inputs[0])
            compTree.links.new(freestyleNode.outputs[0],mixNode.inputs[0])
            compTree.links.new(borderNode.outputs[0],mixNode.inputs[1])
            compTree.links.new(renderNode.outputs[0],mixNode.inputs[2])
        else:
            print("Compositor appears to be full - skipping")
            
        return {'FINISHED'}

#render buffer helper
def renderBuffer(buffername):
    #set new temp render path
    oldPath = bpy.data.scenes["Scene"].render.filepath
    newPath = "//"+buffername+".png"
    bpy.data.scenes["Scene"].render.filepath = newPath
    #save render to new file and restore path
    bpy.ops.render.render(use_viewport=True, write_still=True)
    bpy.data.scenes["Scene"].render.filepath = oldPath
    #read buffer from file
    tex = bpy.data.images[buffername]
    tex.source = "FILE"
    tex.filepath = newPath
    tex.reload()
    tex.pack()
    #delete file
    os.remove(bpy.path.abspath(newPath))
    
#set node helper
def setNodeData(node, is_border):
    #IsBorder
    if node.label == "IsBorder":
        if is_border:
            node.outputs[0].default_value = 1
        else:
            node.outputs[0].default_value = 0
    #CameraScale
    if node.label == "CameraScale":
        node.outputs[0].default_value = bpy.data.cameras["Camera"].ortho_scale
    #ResolutionX
    if node.label == "ResolutionX":
        node.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_x
    #ResolutionX
    if node.label == "ResolutionY":
        node.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_y
    
#render settings helper
def setRenderSettings(samples = 1, denoising = False, freestyle = False, diffuse_override = False, emission_override = False, is_border = False, use_compositor = False):
    #shorthands
    scene = bpy.data.scenes["Scene"]
    viewLayer = scene.view_layers["View Layer"]
    #basic settings
    scene.cycles.samples = samples
    scene.cycles.use_denoising = denoising
    scene.render.use_freestyle = freestyle
    scene.use_nodes = use_compositor
    #material override
    viewLayer.material_override = None
    if diffuse_override:
        viewLayer.material_override = bpy.data.materials["OVERRIDE_DIFFUSE"]
    if emission_override:
        viewLayer.material_override = bpy.data.materials["OVERRIDE_EMISSION"]
    #shader nodes - search for all nodes and set with right label
    for material in bpy.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                setNodeData(node,is_border)
    for nodeGroup in bpy.data.node_groups:
        for node in nodeGroup.nodes:
            setNodeData(node, is_border)            

def renderPixelArt(samples):
    assert bpy.data.filepath # abort if .blend is unsaved
    print("Rendering Pixelart")
    #set material mapping settings
    nodes = bpy.data.node_groups["CustomCameraMapping"].nodes
    links = bpy.data.node_groups["CustomCameraMapping"].links
    scene = bpy.data.scenes['Scene']
    resX = scene.render.resolution_x
    resY = scene.render.resolution_y
    isLandscape = resX>=resY
    if bpy.data.cameras["Camera"].type == 'ORTHO' and isLandscape:
        #connect to custom node
        links.new(nodes["Vector Math"].outputs[0], nodes["Image Texture"].inputs[0])
    else:
        #connect to screen mapping
        links.new(nodes["Texture Coordinate"].outputs[5], nodes["Image Texture"].inputs[0])
    #render diffuse
    setRenderSettings(samples = samples, denoising = True, diffuse_override = True)
    renderBuffer("DIFFUSE_BUFFER")
    #render freestyle
    setRenderSettings(freestyle = True, emission_override = True)
    renderBuffer("FREESTYLE_BUFFER")
    #render border
    setRenderSettings(is_border = True)
    renderBuffer("BORDER_BUFFER")
    #render final
    setRenderSettings(use_compositor = True)
    bpy.ops.render.render(use_viewport=True, write_still=True)                  
                    

class RENDER_OT_PIXELART_RENDERALL(bpy.types.Operator):
    bl_label = "Render Pixelart"
    bl_idname = "render.pixelart_renderall"
    
    def execute(self, context):
        renderPixelArt(context.scene.pixel_props.final_samples)
        return {'FINISHED'}
    
class RENDER_OT_PIXELART_RENDERALLPREVIEW(bpy.types.Operator):
    bl_label = "Render Pixelart Preview"
    bl_idname = "render.pixelart_renderallpreview"
    
    def execute(self, context):
        renderPixelArt(context.scene.pixel_props.preview_samples)
        return {'FINISHED'}
    
class RENDER_OT_PIXELART_RENDERANIMATION(bpy.types.Operator):
    bl_label = "Render Pixelart Animation"
    bl_idname = "render.pixelart_renderanimation"
    
    def execute(self, context):
        scene = context.scene
        start = scene.frame_start
        end = scene.frame_end
        path = scene.render.filepath
        oldPath = path+""
        for frame in range(start,end):   
            scene.frame_current = frame
            scene.render.filepath = oldPath+str(frame)
            renderPixelArt(context.scene.pixel_props.final_samples)
        scene.render.filepath = oldPath
        return {'FINISHED'}

class RENDER_PT_PIXELART(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Pixelart"
    bl_idname = "RENDER_PT_PIXELART"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        op = row.operator("render.pixelart_setup")
        
        row = layout.row()
        row.operator("render.pixelart_renderall")
        
        row = layout.row()
        row.operator("render.pixelart_renderallpreview")
        
        row = layout.row()
        row.prop(context.scene.pixel_props, 'final_samples')
        
        row = layout.row()
        row.prop(context.scene.pixel_props, 'preview_samples')
        
        row = layout.row()
        row.operator("render.pixelart_renderanimation")

def register():
    bpy.utils.register_class(PixelPropertyGroup)
    bpy.types.Scene.pixel_props = bpy.props.PointerProperty(type=PixelPropertyGroup)
    bpy.utils.register_class(RENDER_OT_PIXELART_SETUP)
    bpy.utils.register_class(RENDER_OT_PIXELART_RENDERALL)
    bpy.utils.register_class(RENDER_OT_PIXELART_RENDERALLPREVIEW)
    bpy.utils.register_class(RENDER_OT_PIXELART_RENDERANIMATION)
    bpy.utils.register_class(RENDER_PT_PIXELART)
    

def unregister():
    del bpy.types.Scene.pixel_props 
    bpy.utils.unregister_class(PixelPropertyGroup)
    bpy.utils.unregister_class(RENDER_OT_PIXELART_SETUP)
    bpy.utils.unregister_class(RENDER_OT_PIXELART_RENDERALL)
    bpy.utils.unregister_class(RENDER_OT_PIXELART_RENDERALLPREVIEW)
    bpy.utils.unregister_class(RENDER_OT_PIXELART_RENDERANIMATION)
    bpy.utils.unregister_class(RENDER_PT_PIXELART)


if __name__ == "__main__":
    register()
    print("registered pixelart renderer")