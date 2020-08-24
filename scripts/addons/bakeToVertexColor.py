# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)
import bpy
import time
import numpy
import math



bl_info = {
    "name": "Bake to vertex color",
    "description": "Runs through selected objects. Bakes a temporary image and then transfers to vertex color. Temporary bake uv's can be created as well. Cycles used for baking, but the addon is usable in the Eevee render settings",
    "author": "Daniel Bystedt, twitter: @3dbystedt",
    "version": (1, 0, 6),
    "blender": (2, 80, 0),
    "location": "properties > render & search menu",
    # "wiki_url": "",
    # "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Render"
}


#------------#
# PROPERTIES #
#------------#
class OBJECT_PG_bake_to_vertex_col(bpy.types.PropertyGroup):

    samples: IntProperty(
        name="Samples",
        description="Render samples",
        min=1, max=512,
        default=1,
    )

    create_temp_lightmap_uv: BoolProperty(
        name="Create temp lightmap uv",
        description="Create temporary uv based on the lighmap pack algorithm",
        default=False,
    )
    smooth_vertex_colors: BoolProperty(
        name="Smooth vertex colors",
        description="Create temporary uv based on the lighmap pack algorithm",
        default=True,
    )

    delete_bake_image: BoolProperty(
        name="Delete bake image",
        description="Delete the bake image after baking is done",
        default=True,
    )

    vertex_color_name: StringProperty(
        name="Vertex color bake target name",
        description="The name of the vertex color pixel_index where the bake will be stored. Created if it does not exist",
        default='bakedVertexCol'
    )

    popup_menu_message: StringProperty(
        name="Message for the popup menu",
        description="",
        default="Message",
    )

    def item_callback(self, context):
        return(

            ('128', '128', ""),
            ('256', '256', ""),
            ('512', '512', ""),
            ('1024', '1024', ""),
            ('2048', '2048', ""),
            ('4096', '4096', ""),
        )

    resolution: EnumProperty(
        name="Resolution",
        description="Light map resolution",
        items=item_callback
    )

    def item_callback_uv(self, context):
        return(

            ('current_uv', 'current uv',
             "use current uv when baking. Overlapping uv's can create artifacts"),
            ('lightmap', 'lightmap pack',
             "use lightmap algorithm when creating temporary baking uv"),
            ('smartUv', 'smart uv project',
             "use smart uv project algorithm when creating temporary baking uv"),
        )
    bake_uv_type: EnumProperty(
        name="Temp uv type",
        description="Temporary non overlapping uv type used for baking",
        items=item_callback_uv
    )

    def item_callback_pass(self, context):
        return(

            ('DIFFUSE', 'Diffuse', ''),
            ('DIFFUSE_COLOR_ONLY', 'Diffuse color only', ''),
            ('COMBINED', 'Combined', ''),
            ('AO', 'Ambient occlusion', ''),
            ('SHADOW', 'Shadow', ''),
            ('NORMAL', 'Normal', ''),
            ('UV', 'Uv', ''),
            ('ROUGHNESS', 'Roughness', ''),
            ('EMIT', 'Emit', ''),
            ('ENVIRONMENT', 'Environment', ''),
            ('GLOSSY', 'Glossy', ''),
            ('TRANSMISSION', 'Transmission', ''),
        )    

    def debugTest(self, context):
        return(
            ('TEST1', 'test1', 'so much test 1'),
            ('TEST2', 'test2', 'so much test 2'),
        )

    bake_pass: EnumProperty(
        name="Bake pass type",
        description="Which pass to bake",
        items=item_callback_pass
    )

    def execute(self, context):
        self.resolution = '256'


class OBJECT_OT_bake_vertex_color(bpy.types.Operator):
    bl_idname = "object.bake_to_vertex_col"
    bl_label = "Bake pass to vertex color"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Bakes temporary image with cycles and transfers the pixel values over to vertex colors of the selected object(s)"

    resolution: IntProperty(
        name="Resolution",
        description="Light map resolution",
        min=128, max=4096,
        default=256,
    )

    samples: IntProperty(
        name="Samples",
        description="Render samples",
        min=1, max=512,
        default=1,
    )

    smooth_vertex_colors: BoolProperty(
        name="Smooth vertex colors",
        description="Create temporary uv based on the lighmap pack algorithm",
        default=True,
    )
    
    delete_bake_image: BoolProperty(
        name="Delete bake image",
        description="Delete the bake image after baking is done",
        default=True,
    )

    vertex_color_name: StringProperty(
        name="Vertex color bake target name",
        description="The name of the vertex color pixel_index where the bake will be stored. Created if it does not exist",
        default='bakedVertexCol'
    )

    def item_callback_uv(self, context):
        return(

            ('current_uv', 'current uv',
             "use current uv when baking. Overlapping uv's can create artifacts"),
            ('lightmap', 'lightmap pack',
             "use lightmap algorithm when creating temporary baking uv"),
            ('smartUv', 'smart uv project',
             "use smart uv project algorithm when creating temporary baking uv"),
        )

    bake_uv_type: EnumProperty(
        name="Temp uv type",
        description="Temporary non overlapping uv type used for baking",
        items=item_callback_uv
    )

    def item_callback_pass(self, context):
        return(

            ('DIFFUSE', 'Diffuse', ''),
            ('DIFFUSE_COLOR_ONLY', 'Diffuse color only', ''),
            ('COMBINED', 'Combined', ''),
            ('AO', 'Ambient occlusion', ''),
            ('SHADOW', 'Shadow', ''),
            ('NORMAL', 'Normal', ''),
            ('UV', 'Uv', ''),
            ('ROUGHNESS', 'Roughness', ''),
            ('EMIT', 'Emit', ''),
            ('ENVIRONMENT', 'Environment', ''),
            ('GLOSSY', 'Glossy', ''),
            ('TRANSMISSION', 'Transmission', ''),
        )     

    bake_pass: EnumProperty(
        name="Bake pass type",
        description="Which pass to bake",
        items=item_callback_pass
    )

    @classmethod
    def poll(cls, context):
        # I had to use len because of potential outliner selection (or that is my assumption)
        return len(bpy.context.selected_objects) is not 0

    def execute(self, context):
        time_start = time.time()
        image_name = 'vertex_color_bake'

        # Store original render/bake settings
        render_engine = context.scene.render.engine
        orig_bake_pass = bpy.context.scene.cycles.bake_type
        orig_use_pass_direct = bpy.context.scene.render.bake.use_pass_direct
        orig_use_pass_indirect = bpy.context.scene.render.bake.use_pass_indirect
        orig_use_pass_color = bpy.context.scene.render.bake.use_pass_color
        if bpy.app.version_string >= '2.90.0':
            # Optix does not work well with denoising. Turn off denoising temporarily. Feature was added in 2.90.0
            orig_denoising = bpy.context.scene.cycles.use_denoising


        # Temporarily set cycles as current render engine and change bake settings
        context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.use_denoising = False
        if self.bake_pass == 'DIFFUSE_COLOR_ONLY':
            bpy.context.scene.cycles.bake_type = 'DIFFUSE'
            bpy.context.scene.render.bake.use_pass_direct = 0
            bpy.context.scene.render.bake.use_pass_indirect = 0
            bpy.context.scene.render.bake.use_pass_color = 1     
        else:
            bpy.context.scene.cycles.bake_type = self.bake_pass

        # Change to object mode
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Store original object selection for reselection later
        selected_objects = context.selected_objects
        active_object = context.view_layer.objects.active

        # Remove old bake image from shader editor. Important in order to bake to new resolution
        self.delete_image(context, image_name)

        for object in context.selected_objects:
            context.view_layer.objects.active = object
            self.bake_to_image(context, image_name) #TO DO: check this function. need to assign material 
            self.delete_image_node(context, image_name)
            self.transfer_image_to_vertex_color(context, image_name)
            # remove temporary uv
            if not self.bake_uv_type == 'current_uv':
                self.delete_active_uv(context)
            
            self.select_vertex_color(context)

            if self.smooth_vertex_colors == True:
                bpy.ops.paint.vertex_color_smooth()
                pass

        context.view_layer.objects.active = active_object
        context.scene.render.engine = render_engine
        bpy.context.scene.cycles.bake_type = orig_bake_pass
        bpy.context.scene.render.bake.use_pass_direct = orig_use_pass_direct 
        bpy.context.scene.render.bake.use_pass_indirect = orig_use_pass_indirect
        bpy.context.scene.render.bake.use_pass_color = orig_use_pass_color
        if bpy.app.version_string >= '2.90.0':
            bpy.context.scene.cycles.use_denoising = orig_denoising

        # Restore selection
        for obj in selected_objects:
            bpy.data.objects[obj.name].select_set(True)
            context.view_layer.objects.active = active_object

        # Delete bake image data block
        if self.delete_bake_image == True:
            pass
            self.delete_image(context, image_name)

        print("Bake to vertex color finished: %.4f sec" %
              (time.time() - time_start))

        return {'FINISHED'}

    def delete_active_uv(self, context):
        '''
        Delete the active uv 
        '''
       # I need to set area type (i.e context) to 'VIEW_3D' for removing uv
        area = context.area
        old_type = area.type
        area.type = 'VIEW_3D'
        bpy.ops.mesh.uv_texture_remove()
        area.type = old_type

    def transfer_image_to_vertex_color(self, context, image_name):
        '''
        Transfer pixel colors to vertex color of the active object\n
        '''
        image = bpy.data.images[image_name]

        width = image.size[0]
        height = image.size[1]

        # Set object mode to vertex paint
        object = context.active_object
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')

        # Save image pixel values to array
        image_pixels = []
        image_pixels = self.image_to_pixel_array(context, image_name)

        for face in object.data.polygons:
            for loop_id in face.loop_indices:
                uv_coord = object.data.uv_layers.active.data[loop_id].uv
                # Refit uv coordinates between 0-1
                uv_coord.x = abs(uv_coord.x) % 1
                uv_coord.y = abs(uv_coord.y) % 1

                # Create vertex color if needed
                if context.active_object.data.vertex_colors.find(self.vertex_color_name) < 0:
                    context.active_object.data.vertex_colors.new(name=self.vertex_color_name)

                # Transfer pixel color to vertex color
                r, g, b, a = 0, 1, 2, 3
                target_vertex_color = context.active_object.data.vertex_colors[self.vertex_color_name].data[loop_id]
                pixel_average_value = self.pixel_sample(context, image_pixels, uv_coord.x, uv_coord.y, 0)
                # Sample larger pixel radius if alpha is below 1 (indicates non ray hit)
                if pixel_average_value[a] < 1:
                    pixel_average_value = self.pixel_sample(context, image_pixels, uv_coord.x, uv_coord.y, 1)
                target_vertex_color.color = pixel_average_value
                

    def pixel_sample(self, context, image_pixels, x, y, sample_size):
        '''
        image_pixels = array with pixels from an image, sorted like array[y][x][r,g,b,a] \n
        returns r,g,b,a color as list from sampled pixel(s) at the normalized x,y coordinates. \n
        Set sample_size = 0 to sample one pixel only, 1 to sample 3x3 pixels, 2 to sample 5x5 pixels etc. \n
        x and y should be normalized coordinates (i.e. between 0-1) \n
        Pixels with alpha = 0 will not be sampled
        '''
        width = len(image_pixels[0])
        # height = len(image_pixels[0][0])
        height = width
        r, g, b, a = 0, 1, 2, 3

        # Convert normalized coordinates to pixel coordinates
        x = math.floor(x * width)
        y = math.floor(y * height)

        # Sample pixels in a 3x3 box around sample pixel. Only sample inside of image (hence min/max)
        pixel_average = [0,0,0,0]
        pixel_sample_count = 0

        sample_x_start = max(x - sample_size, 0)
        sample_x_end = min(x + sample_size + 1, width)
        sample_y_start = max(y - sample_size, 0)
        sample_y_end = min(y + sample_size + 1, height)

        for sampleY in range(sample_y_start, sample_y_end):
            for sampleX in range(sample_x_start,sample_x_end):
                # Avoid sampling pixels without alpha   
                #print('working with pixel X:' + str(sampleX) +", Y:"+ str(sampleY))
                #print(image_pixels[sampleY][sampleX])
                if image_pixels[sampleY][sampleX][a] > 0: 
                    #print('checking pixel at x: ' + str(sampleX) + ', y: ' + str(sampleY) + ' had NOT 0 alpha')
                    pixel_average[r] += image_pixels[sampleY][sampleX][r]
                    pixel_average[g] += image_pixels[sampleY][sampleX][g]
                    pixel_average[b] += image_pixels[sampleY][sampleX][b]
                    pixel_average[a] += image_pixels[sampleY][sampleX][a]
                    pixel_sample_count += 1
        
        if pixel_sample_count > 0:
            pixel_average[r] = pixel_average[r] / pixel_sample_count
            pixel_average[g] = pixel_average[g] / pixel_sample_count
            pixel_average[b] = pixel_average[b] / pixel_sample_count
            pixel_average[a] = pixel_average[a] / pixel_sample_count

        return pixel_average
        
    def image_to_pixel_array(self, context, image_name):
        '''
        returns list/array with image pixels like 
        array[y][x][r,g,b,a]
        '''

        image = bpy.data.images[image_name]
        width = image.size[0]
        height = image.size[1]
        r, g, b, a = 0, 1, 2, 3

        # Separate pixels in list per channel
        # Save image pixel values. First pixels values (rgba) are stored in bpy.data.images[image_name].pixels[0:3] and so on
        image_pixel_list = list(image.pixels[:])
        image_pixels = []

        # Arrange pixel values in a proper array of lists
        # NOTE: Since we split up per row, the x, y coordinates will be switched like this: image_pixels[y][x]
        for i in range(0,len(image_pixel_list), 4):
            pixel = []
            for j in range(0,4):
                pixel.append(image_pixel_list[i+j])
            image_pixels.append(pixel)
        image_pixels = numpy.array_split(image_pixels, width)

        return image_pixels

    def create_material_if_missing(self, context):
        # Create material if there is no material assigned to the active object
        material = context.active_object.active_material
        if material is None:
            # Create material
            material = bpy.data.materials.new(name="Material")

            if context.active_object.data.materials:
                # Assign to 1st material slot
                context.active_object.data.materials[0] = material
                print('Added ' + material.name + ' to material slot')
            else:
                # No slots
                context.active_object.data.materials.append(material)
                print('Created slot and added ' + material.name + ' to material slot')

            context.active_object.active_material.use_nodes = True
      
    def create_bake_image_if_missing(self, context, image_name):  
        bake_image = None
        # Check images if bake image already exists
        for image in bpy.data.images:
            if image.name == image_name:
                image.generated_height = self.resolution
                image.generated_width = self.resolution
                bake_image = image

        # Create bake image if none is found
        if bake_image == None:
            bake_image = bpy.ops.image.new(name=image_name, width=self.resolution, height=self.resolution)

    def add_bake_image_to_materials(self, context, image_name):
        if context.active_object == None:
            print('No active object during add_bake_image_to_materials')
            return

        for material_slot in context.active_object.material_slots:            
            material = material_slot.material
            node_tree = material.node_tree
            image_node = node_tree.nodes.new(type='ShaderNodeTexImage')
            image_node.name = image_name

            # Set image to image node and select, make active
            image_node.image = bpy.data.images[image_name]
            image_node.select = True
            node_tree.nodes.active = image_node


    def select_only_active_object(self, context):
        # Select only the object that should be baked in order for cycles baker to work
        active_object = context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[active_object.name].select_set(True)
        context.view_layer.objects.active = active_object

    def bake_to_image(self, context, image_name):
        # Bake the pass choosen in UI to [image_name]
        print('init bake_to_image with the selected objects')
        print(context.selected_objects)

        # Store selection
        selected_objects = context.selected_objects
        active_object = context.active_object

        self.select_only_active_object(context)
        
        # Create uv if the user has made that choice
        if not self.bake_uv_type == 'current_uv':
            self.create_vertex_color_uv(context, 'vertex_color_bake_uv')

        # Bake with cycles by using temp copy of object since we want to remove "generate" modifiers
        bpy.ops.object.duplicate(linked=False)
        self.create_material_if_missing(context)
        self.create_bake_image_if_missing(context, image_name)
        self.add_bake_image_to_materials(context, image_name)
        self.remove_modifiers_for_bake(context)

        # Store original bake settings
        origMargin = bpy.context.scene.render.bake.margin

        bpy.context.scene.render.bake.margin = 0
        bpy.ops.object.bake(type=context.scene.cycles.bake_type)

        # Restore original bake settings
        bpy.context.scene.render.bake.margin = origMargin

        # Cleanup temp object and bake image in material
        self.delete_image_node(context, image_name) 
        bpy.ops.object.delete(use_global=False) 

        # Restore selection
        for obj in selected_objects:
            bpy.data.objects[obj.name].select_set(True)
        context.view_layer.objects.active = active_object
          

    def remove_modifiers_for_bake(self, context):
        # Remove modifiers that are not optimal for baking (array, solidify etc)
        for mod in context.active_object.modifiers:
            if(mod.type == 'ARRAY' or
               mod.type == 'BEVEL' or
               mod.type == 'BUILD' or
               mod.type == 'MASK' or
               mod.type == 'MIRROR' or
               mod.type == 'REMESH' or
               mod.type == 'SCREW' or
               mod.type == 'SKIN' or
               mod.type == 'SOLIDIFY' or
               mod.type == 'WELD' or
               mod.type == 'WIREFRAME'
               ):
                bpy.ops.object.modifier_remove(modifier=mod.name)

    def create_vertex_color_uv(self, context, uv_name):

        area = context.area
        old_type = area.type
        area.type = 'VIEW_3D'

        # Need to set area type (i.e context) to 'VIEW_3D' for this to work properly
        bpy.ops.mesh.uv_texture_add()
        area.type = old_type

        temp_uv = context.active_object.data.uv_layers.active
        temp_uv.name = uv_name
        context.active_object.data.uv_layers[temp_uv.name].active_render = True

        if self.bake_uv_type == 'lightmap':
            bpy.ops.uv.lightmap_pack( PREF_IMG_PX_SIZE=128, PREF_MARGIN_DIV=0.4)
        elif self.bake_uv_type == 'smartUv':
            bpy.ops.uv.smart_project(
                angle_limit=81.61, island_margin=0.05, user_area_weight=1)

    def delete_image_node(self, context, image_name):
        for material_slot in context.active_object.material_slots:
            material = material_slot.material
            node_tree = material.node_tree

            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    if node.name.startswith(image_name):
                        material.node_tree.nodes.remove(node)

    def delete_image(self, context, image_name):
        for image in bpy.data.images:
            if image.name == image_name:
                print('found and removing image ' + image_name)
                bpy.data.images.remove(image)

    def select_vertex_color(self, context):
        vertex_color_index = context.active_object.data.vertex_colors.find(
            self.vertex_color_name)
        context.active_object.data.vertex_colors.active_index = vertex_color_index

#------------#
# UI         #
#------------#
class OBJECT_PT_bake_vertex_color(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Bake vertex color"
    bl_idname = "RENDER_PT_bake_vertex_color"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        row.label(text="Bake type")
        #row.prop(scene.cycles, "bake_type", text="")
        row.prop(scene.bake_to_vertex_color_props, "bake_pass", text="")


        row = layout.row()
        row.label(text="Bake uv")
        row.prop(scene.bake_to_vertex_color_props, "bake_uv_type", text="")

        row = layout.row()
        row.label(text="Light map resolution")
        row.prop(scene.bake_to_vertex_color_props, "resolution", text="")

        row = layout.row()
        row.label(text="Render samples")
        row.prop(scene.bake_to_vertex_color_props, "samples", text="")

        row = layout.row()
        row.label(text="Smooth vertex colors")
        row.prop(scene.bake_to_vertex_color_props,
                 "smooth_vertex_colors", text="")

        row = layout.row()
        row.label(text="Delete bake image")
        row.prop(scene.bake_to_vertex_color_props,
                 "delete_bake_image", text="")

        row = layout.row()
        row.label(text="Vertex color name")
        row.prop(scene.bake_to_vertex_color_props,
                 "vertex_color_name", text="")

        row = layout.row()
        row.scale_y = 1.5
        row.separator()

        row = layout.row()
        row.scale_y = 1.5
        myOp = row.operator('object.bake_to_vertex_col', icon='RENDER_STILL')
        myOp.resolution = int(scene.bake_to_vertex_color_props.resolution)
        myOp.samples = scene.bake_to_vertex_color_props.samples
        myOp.vertex_color_name = scene.bake_to_vertex_color_props.vertex_color_name
        myOp.smooth_vertex_colors = scene.bake_to_vertex_color_props.smooth_vertex_colors
        myOp.bake_uv_type = scene.bake_to_vertex_color_props.bake_uv_type
        myOp.delete_bake_image = scene.bake_to_vertex_color_props.delete_bake_image
        myOp.bake_pass = scene.bake_to_vertex_color_props.bake_pass


def register():
    bpy.utils.register_class(OBJECT_OT_bake_vertex_color)
    bpy.utils.register_class(OBJECT_PT_bake_vertex_color)
    bpy.utils.register_class(OBJECT_PG_bake_to_vertex_col)
    bpy.types.Scene.bake_to_vertex_color_props = bpy.props.PointerProperty(
        type=OBJECT_PG_bake_to_vertex_col)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_bake_vertex_color)
    bpy.utils.register_class(OBJECT_PT_bake_vertex_color)
    bpy.utils.unregister_class(OBJECT_PG_bake_to_vertex_col)
    del bpy.types.Scene.bake_to_vertex_color_props


if __name__ == "__main__":
    register()
