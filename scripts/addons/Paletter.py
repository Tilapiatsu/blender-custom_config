import bpy
from math import floor, ceil, sqrt
import bmesh
import time

bl_info = {
    "name": "Paletter",
    "description": "Bakes materials colors and assigns UVs to new baked texture.",
    "author": "Roman Chumak",
    "version": (0, 2, 1, 0),
    "blender": (2, 90, 0),
    "doc_url": "https://phygitalism.com/en/paletter-addon-en/",
    "location": "Properties / Material",
    "category": "Material"} 

class PALETTER_Properties(bpy.types.PropertyGroup):
    replace_uv: bpy.props.BoolProperty(default=False, description="Replace active UV Map instead of adding new one.")
    replace_mats: bpy.props.BoolProperty(default=False, description="Replace all materials with new one.")

class PALETTER_bake(bpy.types.Operator):
    """Bake materials colors and reassign UVs to new texture."""
    bl_idname = 'paletter.bake'
    bl_label = 'Bake palette!'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        replace_uv = bpy.context.scene.paletter.replace_uv
        replace_mats = bpy.context.scene.paletter.replace_mats
        colors = []
        obj = bpy.context.active_object

        for slot in obj.material_slots:
            col = slot.material.diffuse_color
            colors.append(col)

        image_name = obj.name + "_" + str(time.time_ns())
        cn = len(colors)
        size_x = ceil(sqrt(cn))
        size_y = ceil(cn/size_x)
        side = max(size_x, size_y)

        bpy.ops.object.select_all(action='DESELECT')
        
        obj.select_set(True) 
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="SELECT")
        
        if not replace_uv:
            bpy.ops.mesh.uv_texture_add()
            obj.data.uv_layers[-1].name = "Palette"
            obj.data.uv_layers[-1].active = True
        bpy.ops.uv.reset()




        bpy.ops.object.editmode_toggle()  

        image = bpy.data.images.new(image_name, alpha=1, width=side, height=side)
        pixels = []
        for c in colors:
            for i in range(4):
                pixels.append(c[i])

        image.pixels = pixels
        palette_uv = obj.data.uv_layers.active
        sf = 1.0

        for polygon in obj.data.polygons:
            polygondata = ()
            for i in polygon.loop_indices:
                polygondata += palette_uv.data[i].uv[:]
            
            mat_id = polygon.material_index
            for i in polygon.loop_indices:
                uv_loop = palette_uv.data[i]
                uv_loop.uv.x /= side * sf
                uv_loop.uv.y /= side * sf
                uv_loop.uv.x += mat_id % (side) / side + (1/side-1/(side*sf))/2
                uv_loop.uv.y += floor(mat_id / (side)) / side + (1/side-1/(side*sf))/2

        if replace_mats:
            for mat in obj.material_slots:
                obj.active_material_index = 0
                bpy.ops.object.material_slot_remove()

            mat_name = image_name
            material = bpy.data.materials.new(mat_name)
            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            texture = nodes.new(type='ShaderNodeTexImage')
            texture.image = image
            texture.interpolation = 'Closest'

            principled_bsdf = nodes['Principled BSDF']
            material.node_tree.nodes.remove(principled_bsdf)
            bg = nodes.new(type='ShaderNodeBackground')
            mix = nodes.new(type="ShaderNodeMixShader")
            transparent = nodes.new(type="ShaderNodeBsdfTransparent")
            output = nodes['Material Output']

            link_color = links.new(texture.outputs['Color'], bg.inputs[0])
            link_alpha = links.new(texture.outputs['Alpha'], mix.inputs[0])
            link_trans = links.new(transparent.outputs[0], mix.inputs[1])
            link_bg = links.new(bg.outputs[0], mix.inputs[2])
            link_mix = links.new(mix.outputs[0], output.inputs[0])

            material.blend_method = 'CLIP'
            material.alpha_threshold = 0
            obj.data.materials.append(material)

        return {'FINISHED'}


class PALETTER_PT_Panel(bpy.types.Panel):
    bl_label = "Paletter"
    bl_idname = "PALETTER_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        paletter_ui = layout.column()
        paletter_ui.prop(context.scene.paletter, 'replace_uv', text="Replace UV")
        paletter_ui.prop(context.scene.paletter, 'replace_mats', text="Replace Materials")

        obj = bpy.context.active_object
        if obj==None or obj.type != 'MESH':
            paletter_ui.label(text="Mesh objects only allowed.")
        elif obj.mode != 'OBJECT':
            paletter_ui.label(text="Return to Object Mode.")
        elif len(obj.material_slots) == 0:
            paletter_ui.label(text="No materials, nothing to bake.")
        else:
            paletter_ui.operator('paletter.bake', icon="TEXTURE")



def register():
    bpy.utils.register_class(PALETTER_bake)
    bpy.utils.register_class(PALETTER_PT_Panel)
    bpy.utils.register_class(PALETTER_Properties)
    bpy.types.Scene.paletter = bpy.props.PointerProperty(type=PALETTER_Properties)

def unregister():
    bpy.utils.unregister_class(PALETTER_bake)
    bpy.utils.unregister_class(PALETTER_PT_Panel)
    bpy.utils.unregister_class(PALETTER_Properties)
