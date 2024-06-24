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


import bpy, os
import numpy as np
from math import tau, pi, sin, cos
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import PropertyGroup, Panel, Operator, Menu, Header

# Add-on info
bl_info = {
    "name": "Easy HDRI",
    "author": "Monaime Zaim",
    "version": (2, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Properties > Easy HDRI",
    "description": "Load and test your HDRIs easily.", 
    "wiki_url": "",
    "tracker_url": "",      
    "category": "3D View"
}


# Preview collections
preview_collections = {}
# Addon path
addon_dir = os.path.dirname(__file__)
# List of nodes in the World shader
world_nodes_list = [
    'Texture Coordinate',
    'Mapping',
    'Background',
    'Math_multiply_2',
    'Environment',
    'Math_multiply',
    'Math_divide',
    'Math_add',
    'Color Multiply',
    'Saturation',
    'Gamma',
    'Environment Blured',
    'Color Mix',
    'Background2',
    'Mix Shader',
    'Light Path',
    'Group Input',
    'Group Output',
    'Ground Projection',
    'Environment Projected',
    'Color Mix 2'
]

###########################################################################################
################################### Functions #############################################
# It works just like os.walk, but you can pass it a level parameter
# that indicates how deep the recursion will go.
## http://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
def get_hdris(folder, filter, level):
    folder = bpy.path.abspath(folder)
    folder = os.path.abspath(folder)
    hdris = dict()
    unfiltered = []
    empty = 'Empty.png'
    
    if not os.path.isdir(folder):
        hdris[empty] = os.path.join(addon_dir, 'Images', empty)
        return hdris, unfiltered
    
    num_sep = folder.count(os.path.sep)
    for root, dirs, files in os.walk(folder):
        for fn in files:
            if fn in unfiltered:
                continue
            if fn.lower().endswith(".hdr") or fn.lower().endswith(".exr"):
                if filter in fn:
                    hdris[fn] = os.path.join(root, fn)
                unfiltered.append(fn)
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
    if not hdris:
        hdris[empty] = os.path.join(addon_dir, 'Images', empty)
    return hdris, unfiltered


# Generate Images Previews
def previews_enum(self, context):
    enum_items = []
    
    if context is None:
        return enum_items
    
    pcoll = preview_collections["hdris"]

    if not pcoll.refresh and len(pcoll):
        return pcoll.previews
    
    level = self.sub_dirs if self.recursive_search else 0
    hdris, unfiltered = get_hdris(self.previews_dir, self.filter, level)
        
    for i, (name, filepath) in enumerate(hdris.items()):
        thumb = pcoll.get(name)
        if thumb is None:
            thumb = pcoll.load(name, filepath, 'IMAGE')
        enum_items.append((name, name, filepath, thumb.icon_id, i))
    
    pcoll.previews = enum_items
    pcoll.unfiltered = unfiltered
    pcoll.refresh = False
    pcoll.update()
    return pcoll.previews

# Update the previews list if the folder changes
def update_dir(self, context):
    level = self.sub_dirs if self.recursive_search else 0
    hdris, unfiltered = get_hdris(self.previews_dir, self.filter, level)
    current_image = self.previews
    item = list(hdris.keys())[0]
    if hdris.get(current_image):
        item = current_image
    pcoll = preview_collections["hdris"]
    try:
        pcoll.refresh = True
    except:
        pass
    finally:
        self.previews = item
    return None

# Load Image
def load_image(context, force_load=False):
    scn = context.scene
    props = scn.easy_hdri_props
    image = props.previews
    if image == 'Empty.png':
        return
    
    images = bpy.data.images
    pcoll = preview_collections["hdris"]
    hdris = [i[0] for i in pcoll.previews]
    index = hdris.index(image)
    filepath = pcoll.previews[index][2]
    if not force_load and not props.dynamic_load:
        return
    if not scn.world:
        return
    if bpy.data.worlds.get('EasyHDRI') is None:
        return
    world_nodes = scn.world.node_tree.nodes
    node = world_nodes.get('Easy HDRI')
    if node is None:
        print('Easy HDRI Node Not Found')
        return
    if node.type != 'GROUP':
        print('Wrong Node')
        return 
    nodes = node.node_tree.nodes
    hdri = images.get(image)
    if hdri is None:
        if os.path.exists(filepath):
            hdri = images.load(filepath)
            
    if hdri is None:
        print('Cant load:', filepath)
        return
    
    env = nodes.get('Environment')
    env_projected = nodes.get('Environment Projected')
    env_blured = nodes.get('Environment Blured')
    env.image = hdri
    env_projected.image = hdri
    if props.dynamic_cleanup:
        cleanup_images()
    if props.set_projection:
        x, y = hdri.size
        projection = 'MIRROR_BALL' if x == y else 'EQUIRECTANGULAR'
        env.projection = projection
        env_projected.projection = projection
        env_blured.projection = projection
        

# Update the envirement map
def update_hdr(self, context):
    load_image(context)
    return None

# Remove unused images 
def cleanup_images():
    images = bpy.data.images
    for image in images:
        if image.users == 0:
            images.remove(image)
            
# Text filter            
def update_filter(self, context, text):
    pcoll = preview_collections["hdris"]
    hdris = [i for i in pcoll.unfiltered if text.lower() in i.lower()]
    return hdris

# Update Background display
def update_bg_display(self, context):
    scn = context.scene 
    bg = self.easyhdr_bg_display
    if check_world_nodes(context) != 'OK':
        return None
    world_nodes = scn.world.node_tree.nodes
    node = world_nodes.get('Easy HDRI')
    nodes = node.node_tree.nodes
    # Are we using the original image    
    node.inputs[7].default_value = bg != 'Original' or self.ground_projection
    # Are we using a solid background
    node.inputs[8].default_value = bg == 'Solid'
    # Use eaither a blured background or ground projection
    node.inputs[9].default_value = self.ground_projection and bg != 'Blured'
    return None


# Create EasyHDRI World        
def create_world_nodes(context):
    worlds = bpy.data.worlds
    world = worlds.get('EasyHDRI')
    if world is not None:
        worlds.remove(world)
        
    node_groups = bpy.data.node_groups
    ng = node_groups.get('Easy HDRI')
    if ng is not None:
        node_groups.remove(ng)
    
    # Load the EasyHDRI World
    blend = os.path.join(addon_dir, 'World.blend')
    libs = bpy.data.libraries
    with libs.load(blend, link=False) as (data_src, data_dst):
        data_dst.worlds = ['EasyHDRI',]
        
    world = worlds.get('EasyHDRI')
    if world is not None:
        context.scene.world = world
    # Load Image    
    load_image(context)
    # Update BG Display
    props = context.scene.easy_hdri_props
    bg = props.easyhdr_bg_display
    props.easyhdr_bg_display = bg
    
# Get active HDRI
def get_active_hdri(context):
    scn = context.scene     
    if check_world_nodes(context) != 'OK':
        return None
    world_nodes = scn.world.node_tree.nodes
    node = world_nodes.get('Easy HDRI')
    nodes = node.node_tree.nodes
    env = nodes.get('Environment')
    if env is not None:
        return env.image
    return None
    
# Check the World's node tree
def check_world_nodes(context):
    scn = context.scene
    worlds = bpy.data.worlds
    if not scn.world:
        return 'Create'
    world = worlds.get('EasyHDRI')
    if world is None:
        return 'Create'
    
    world_nodes = world.node_tree.nodes
    node = world_nodes.get('Easy HDRI')
    if node is None:
        return 'Fix'
    
    if node.type != 'GROUP':
        return 'Fix'
    
    nodes = node.node_tree.nodes
    if not len(nodes):
        print('No Nodes')
        return 'Fix'
    
    for n in world_nodes_list:
        if nodes.get(n) is None:
            print('Node not found:', n)
            return 'Fix'
    return 'OK'

# Generate and Save a Blured image from the active HDRI
def generate_blured_image(hdr):
    # Generate the blured image
    blured_img = hdr.copy()
    filename = os.path.splitext(hdr.name)[0]
    blured_img.name = f'Blured_{filename}.jpg'
    blured_img.scale(50, 25)
    # Save the blured image, to have it's own filepath, and to not generate it again
    new_path = hdr.filepath_raw.replace(hdr.name, '')
    blured_imgs_path = os.path.join(new_path, 'EasyHDRI_Blured_images', blured_img.name)
    blured_img.save_render(blured_imgs_path)
    blured_img.filepath = blured_imgs_path
    return blured_img

# Align an object to the brightest pixel of an image
def align_to_hdri(image, ob):
    # get image size
    w, h = image.size
    # get the pixels data (flat array)
    pixel_data = np.zeros((w*h*4), 'f')
    image.pixels.foreach_get(pixel_data)
    # concatenate the RGBA of every pixel
    pixels = np.resize(pixel_data, (w*h,4))
    # calculate the mean of the RGBA (brightness?)
    mean = np.mean(pixels, axis = 1)
    # the maximum (brightest)
    maximum = np.max(mean)
    # index of the brightest pixel
    idx = np.where(mean == maximum)[0][0]
    # position of the brightest pixel
    pos_x, pos_y = idx % w, idx // w
    # convert the position to (longitude, latitude)
    longitude = (pos_x / (w / tau)) - pi
    latitude = ((pos_y / (h / pi)) - (pi / 2))
    # credit to the creator of the hdri-sun-aligner add-on for this last part
    # https://github.com/akej74/hdri-sun-aligner
    # Calculate a vector pointing from the longitude and latitude to origo
    # See https://vvvv.org/blog/polar-spherical-and-geographic-coordinates 
    x = cos(latitude) * cos(longitude)
    y = cos(latitude) * sin(longitude)
    z = sin(latitude)
    # Define euler rotation according to the vector
    vector = Vector([x, -y, z]) # "-y" to match Blender coordinate system
    up_axis = Vector([0.0, 0.0, 1.0])
    angle = vector.angle(up_axis, 0)
    axis = up_axis.cross(vector)
    euler = Matrix.Rotation(angle, 4, axis).to_euler()
    ob.rotation_euler = euler
    
# Sun rotation drivers
def add_driver(ob, world):
    # remove any old driver
    ob.driver_remove('delta_rotation_euler')
    # add the drivers
    for i, axis in enumerate('xyz'):
        # Add a driver to the delta rotation
        driver = ob.driver_add('delta_rotation_euler', i)
        # Add a variable
        var = driver.driver.variables.new()
        # Variable properties
        var.name = axis
        var.type = 'SINGLE_PROP'
        var.targets[0].id_type = 'WORLD'
        var.targets[0].id = world
        path = f'node_tree.nodes["Easy HDRI"].inputs[2].default_value[{i}]'
        var.targets[0].data_path = path
        # Driver expression
        driver.driver.expression = axis
        
        
# Reset to default settings
def reset_default_settings(reset_type):
    scn = bpy.context.scene
    worlds = bpy.data.worlds
    world = worlds.get('EasyHDRI')
    if world is None:
        return
    
    world_nodes = world.node_tree.nodes
    node = world_nodes.get('Easy HDRI')
    
    if node is None:
        return
    nodes = node.node_tree.nodes
    # Main settings
    if reset_type == 'ALL' or reset_type == 'MAIN':
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 1.0
        nodes['Environment'].projection = 'EQUIRECTANGULAR'
        node.inputs[2].default_value = (0.0, 0.0, 0.0)
    
    # Background display
    if reset_type == 'ALL' or reset_type == 'BG':
        scn.easy_hdri_props.easyhdr_bg_display = 'Original'
        scn.easy_hdri_props.ground_projection = False
        node.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = (0.0, 0.0, 20.0)
        node.inputs[6].default_value = (0.0, 0.0, 0.0)
        nodes['Environment Projected'].projection = 'EQUIRECTANGULAR'
        nodes['Environment Blured'].projection = 'EQUIRECTANGULAR'
    
    # Color
    if reset_type == 'ALL' or reset_type == 'COL':
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0)
        node.inputs[11].default_value = 0.0
        node.inputs[12].default_value = 1.0
        node.inputs[13].default_value = 1.0
        
    # Sun Lamp
    if reset_type == 'ALL' or reset_type == 'SUN':
        if hasattr(scn.easy_hdri_props.sun_lamp, 'delta_rotation_euler'):
            scn.easy_hdri_props.sun_lamp.driver_remove('delta_rotation_euler')
        scn.easy_hdri_props.sun_lamp = None
        
# Get the list of favorites (enum)
def get_favs_enum(self, context):
    dirs = get_favs()
    if len(dirs) > 0:
        return [(i, i, '') for i in dirs]
    else: return [('Empty', '__Empty__', '')]

# return the list of favorites
def get_favs():
    dirs = []
    pardir = os.path.abspath(os.path.join(addon_dir, os.pardir))
    fav_file = os.path.join(pardir, "Favorites.fav")
    if not os.path.exists(fav_file):    
        return dirs
    with open(fav_file, 'r') as ff:
        lines = ff.read()
        fav_dirs = lines.splitlines()
        dirs = [i for i in fav_dirs if i.strip()]
    return dirs

# Update the previews directory when the favorite changes
def update_favs(self, context):
    if not self.favorites in ['Empty', '']:
        self.previews_dir = self.favorites
    return None

###########################################################################################
################################## Properties #############################################
###########################################################################################
# Sun lamp poll
def sun_lamp_poll(self, object):
    return object.type == 'LIGHT' and object.data.type == 'SUN'

# Property Group
class EasyHDRIProps(PropertyGroup):
    previews : EnumProperty(
        items = previews_enum,
        update = update_hdr
    )
    dynamic_load : BoolProperty(
        name = 'Load Dynamically',
        default = True,
        description = 'Load the HDRI when the preview changes'
    )
    dynamic_cleanup : BoolProperty(
        name = 'Cleanup Dynamically',
        default = False,
        description = 'Remove 0 user images dynamically'
    )
    all_axis : BoolProperty(
        name = 'All Rotation Axes',
        default = False,
        description = 'Display all the rotation axes'
    )
    recursive_search : BoolProperty(
        name = 'Search in sub-folders',
        default = False,
        update = update_dir,
        description = 'Enable/Disable Recursive file search'
    )
    set_projection : BoolProperty(
        name = 'Set Projection Dynamically',
        default = False,
        update = update_hdr,
        description = 'Set the image projection dynamically'
    )
    previews_dir : StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="",
        update = update_dir,
        description = 'Path to the folder containing the images'    
    )
    filter : StringProperty(
        name = 'Images Filter',
        default = '',
        update = update_dir,
        search = update_filter,
        search_options = {'SUGGESTION',},
        description = 'Live search filtering string',
    )
    sub_dirs : IntProperty(
        name = 'Recursion Level',
        default = 0,
        min = 0, max = 20,
        update = update_dir,
        description = 'Look for HDRIs in the sub folder(s) at this level, 0 = No recursion'
    )
    easyhdr_bg_display : EnumProperty(
        items = (
            ('Original', 'Original', ''),
            ('Solid', 'Solid', ''),
            ('Blured', 'Blured', '')
        ),
        update = update_bg_display,
        description = 'How to display the Background'
    )
    ground_projection : BoolProperty(
        name = 'Ground Projection',
        default = False,
        update = update_bg_display,
        description = 'Ground Projection'
    )
    sun_lamp : PointerProperty(
        name = 'Sun Lamp',
        type = bpy.types.Object,
        poll = sun_lamp_poll,
        description = 'Sun Lamp'
    )
    favorites : EnumProperty(
        name = 'Favorites',
        items = get_favs_enum,
        update = update_favs,
        description = 'List of the favorit folders'
    )
    
###########################################################################################
################################### Operators #############################################
###########################################################################################
# Create world nodes    
class EASYHDRI_OT_create_world(Operator):
    bl_idname = "easyhdr.create_world"
    bl_label = "Create World Nodes"
    bl_options = {'UNDO'}
    bl_description = "Create world nodes for EasyHDRI"

    def execute(self, context):
        create_world_nodes(context)
        return {'FINISHED'}
    
# Previous image
class EASYHDRI_OT_previous_image(Operator):
    bl_idname = "easyhdr.previous"
    bl_label = "Previous"
    bl_options = {'UNDO'}
    bl_description = "Previous Image"
    
    @classmethod
    def poll(cls, context):
        pcoll = preview_collections["hdris"]
        return len(pcoll.previews) > 1

    def execute(self, context):
        props = context.scene.easy_hdri_props
        pcoll = preview_collections["hdris"]
        hdris = [i[0] for i in pcoll.previews]
        active_hdri = props.previews
        count = len(hdris)
        index = hdris.index(active_hdri) - 1
        if index < 0:
            index = count-1
        image = hdris[index]     
        if image != active_hdri:
            props.previews = image
        return {'FINISHED'}
    
# Next image
class EASYHDRI_OT_next_image(Operator):
    bl_idname = "easyhdr.next"
    bl_label = "Next"
    bl_options = {'UNDO'}
    bl_description = "Next Image"
    
    @classmethod
    def poll(cls, context):
        pcoll = preview_collections["hdris"]
        return len(pcoll.previews) > 1

    def execute(self, context):        
        props = context.scene.easy_hdri_props
        pcoll = preview_collections["hdris"]
        hdris = [i[0] for i in pcoll.previews]
        active_hdri = props.previews
        count = len(hdris)
        index = hdris.index(active_hdri) + 1
        if index > count - 1:
            index = 0
        image = hdris[index]     
        if image != active_hdri:
            props.previews = image
        
        return {'FINISHED'}
    
# Load image    
class EASYHDRI_OT_load_image(Operator):
    bl_idname = "easyhdr.load_image"
    bl_label = "Load Image"
    bl_options = {'UNDO'}
    bl_description = "Load the selected image"
    
    @classmethod
    def poll(cls, context):
        return not context.scene.easy_hdri_props.dynamic_load

    def execute(self, context):
        load_image(context, force_load=True)
        return {'FINISHED'}
    
# Reload previews
class EASYHDRI_OT_reload_previews(Operator):
    bl_idname = "easyhdr.reload_previews"
    bl_label = "Reload previews"
    bl_options = {'UNDO'}
    bl_description = "Reload the previews"

    def execute(self, context):
        pcoll = preview_collections["hdris"]
        pcoll.clear()
        props = context.scene.easy_hdri_props
        # update
        props.previews_dir = props.previews_dir
        return {'FINISHED'}
    
# Remove unused images
class EASYHDRI_OT_remove_unused_images(Operator):
    bl_idname = "easyhdr.remove_unused_images"
    bl_label = "Remove unused images"
    bl_options = {'UNDO'}
    bl_description = "Remove 0 user images"
    
    def execute(self, context):
        cleanup_images()
        return {'FINISHED'}
    
# Generate a blured image from HDRI
class EASYHDRI_OT_generate_blured_image(Operator):
    bl_idname = "easyhdr.generate_blured_image"
    bl_label = "Generate Blured Image"
    bl_options = {'UNDO'}
    bl_description = "Generate a blured image from the current HDRI"

    def execute(self, context):
        scn = context.scene
        imgs = bpy.data.images
        hdr = get_active_hdri(context)
                
        if hdr is None:
            self.report({'WARNING'}, 'No Active HDRI Found') 
            return {'FINISHED'}
        blured_imgs_path = hdr.filepath_raw.replace(hdr.name, 'EasyHDRI_Blured_images')
        filename = os.path.splitext(hdr.name)[0]
        blured_img_name = f'Blured_{filename}.jpg'
        blured_img_path = os.path.join(blured_imgs_path, blured_img_name)
        img = imgs.get(blured_img_name)
        if img is None:
            if os.path.exists(blured_img_path):
                img = imgs.load(blured_img_path)                
            else:
                img = generate_blured_image(hdr)
                
        world_nodes = scn.world.node_tree.nodes
        node = world_nodes.get('Easy HDRI')
        nodes = node.node_tree.nodes
        blured_env = nodes.get('Environment Blured')
        if blured_env is not None:
            blured_env.image = img
                
        return {'FINISHED'}
    
# Load custom blured image
class EASYHDRI_OT_load_custom_image(Operator):
    bl_idname = "easyhdr.load_custom_image"
    bl_label = "Load Custom"
    bl_options = {'UNDO'}
    bl_description = "Load a Custom Image"
    
    filepath : StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        extentions = bpy.path.extensions_image
        filepath = bpy.path.abspath(self.filepath)
        if not os.path.exists(filepath):
            self.report({'WARNING'}, 'Wrong File Path') 
            return {'FINISHED'}
        filename, file_extension = os.path.splitext(filepath)            
        if not file_extension.lower() in extentions:
            self.report({'WARNING'}, 'File Format Not Supprted')
            return {'FINISHED'}
        imgs = bpy.data.images
        image = os.path.basename(filepath)
        world_nodes = context.scene.world.node_tree.nodes
        node = world_nodes.get('Easy HDRI')
        nodes = node.node_tree.nodes
        img = imgs.get(image)
        if img is None:
            img = imgs.load(filepath)
            
        blured_env = nodes.get('Environment Blured')
        if blured_env is not None:
            blured_env.image = img
        return {'FINISHED'}                    
    
    def invoke(self, context, event):        
        context.window_manager.fileselect_add(self)        
        return {'RUNNING_MODAL'}
    
# Align the brightest pixel of an HDRI to the sun lamp
class EASYHDRI_OT_align_sun(Operator):
    bl_idname = "easyhdr.align_sun"
    bl_label = "Align"
    bl_options = {'UNDO'}
    bl_description = "Align the Sun lamp to the brightest pixel of the active HDRI"

    def execute(self, context):
        hdr = get_active_hdri(context)
        if hdr is None:
            self.report({'WARNING'}, 'No Active HDRI Found') 
            return {'FINISHED'}
        
        scn = context.scene
        props = scn.easy_hdri_props
        imgs = bpy.data.images
        sun = props.sun_lamp
        if hasattr(sun, 'name') and sun.type == 'LIGHT':
            sun.data.type = 'SUN'
        else:
            data = bpy.data.lights.new(name = 'Sun Data', type = 'SUN')
            sun = bpy.data.objects.new(name = 'Sun', object_data = data)
            scn.collection.objects.link(sun)
            props.sun_lamp = sun
            
        align_to_hdri(hdr, sun)
        add_driver(sun, scn.world)
        return {'FINISHED'}
    
# Reset to default settings
class EASYHDRI_OT_reset_to_default(Operator):
    bl_idname = "easyhdr.reset_to_default"
    bl_label = "Reset to Default Values"
    bl_options = {'UNDO'}
    bl_description = "Reset to Default Values"
    
    reset_type : StringProperty(default = 'ALL')
    
    def execute(self, context):
        if check_world_nodes(context) == 'OK':
            reset_default_settings(self.reset_type)
        return {'FINISHED'}
    
# Add to favorites
class EASYHDRI_OT_add_to_fav(Operator):
    bl_idname = "easyhdr.add_to_fav"
    bl_label = "Add to fav"
    bl_options = {'UNDO'}
    bl_description = "Add the current folder to the favorites"

    def execute(self, context):
        props = context.scene.easy_hdri_props
        new_fav = bpy.path.abspath(props.previews_dir)
        new_fav = os.path.abspath(new_fav)
        if not os.path.exists(new_fav):
            self.report({'WARNING'}, 'Wrong Folder Path')
            return {'FINISHED'}
        
        dirs = get_favs()
        if new_fav in dirs:
            return {'FINISHED'}
            
        dirs.append(new_fav)
        pardir = os.path.abspath(os.path.join(addon_dir, os.pardir))
        fav_file = os.path.join(pardir, "Favorites.fav")
        with open(fav_file, 'w') as ff:
            for d in dirs:
                if not d.strip():
                    continue
                ff.write(d + '\n')
        return {'FINISHED'}
    
# Remove from favorites
class EASYHDRI_OT_remove_from_fav(Operator):
    bl_idname = "easyhdr.remove_from_fav"
    bl_label = "Remove"
    bl_options = {'UNDO'}
    bl_description = "Remove the current folder from the favorites"
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = context.scene.easy_hdri_props
        folder = bpy.path.abspath(props.previews_dir)
        folder = os.path.abspath(folder)
        layout = self.layout
        layout.separator()
        layout.label(text ='Remove this folder from the favorits:', icon = 'QUESTION')
        layout.label(text = folder, icon = 'BLANK1')
        layout.separator()

    def execute(self, context):
        props = context.scene.easy_hdri_props
        pardir = os.path.abspath(os.path.join(addon_dir, os.pardir))
        folder = bpy.path.abspath(props.previews_dir)
        folder = os.path.abspath(folder)
        fav_file = os.path.join(pardir, "Favorites.fav")                    
        dirs = get_favs()
        dirs.remove(folder)
        with open(fav_file, 'w') as ff:
            for d in dirs:
                if not d.strip():
                    continue
                ff.write(d + '\n')
        return {'FINISHED'}
    
###########################################################################################
##################################### The UI ##############################################
###########################################################################################          

# Settings Menu
class SettingsMenu(Menu):
    bl_idname = "EASYHDRI_MT_settings_menu"
    bl_label = "Settings"
    bl_description = "Settings"

    def draw(self, context):
        scn = context.scene
        props = scn.easy_hdri_props
        layout = self.layout
        layout.label(text = 'Cleanup:')    
        layout.operator("easyhdr.remove_unused_images", icon = 'RENDERLAYERS')
        layout.separator()
        layout.label(text = 'Loading Images:')
        layout.prop(props, 'dynamic_load')
        layout.prop(props, 'dynamic_cleanup')
        layout.prop(props, 'set_projection')
        layout.separator()
        layout.label(text = 'Recursive file search:')
        layout.prop(props, 'recursive_search')
        layout.separator()
        layout.label(text = 'Rotation:')
        layout.prop(props, 'all_axis')
        layout.separator()
        layout.separator()
        layout.label(text = 'Reset:')
        reset = layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK')
        reset.reset_type = 'ALL'
        
# Easy HDRI Panel
class EASYHDRI_PT_main(Panel):          
    bl_label = "Easy HDRI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Easy HDRI'
    
    def draw(self, context):
        layout = self.layout
        if bpy.app.version < (4, 1, 0):
            layout.alert = True
            layout.label(text = 'Works with Blender 4.1 and above', icon='ERROR')
            layout.label(text = 'Use the version 1.1.1', icon='BLANK1')
            return
        scn = context.scene
        props = scn.easy_hdri_props
        pcoll = preview_collections["hdris"]
        
        folder = bpy.path.abspath(props.previews_dir)
        folder = os.path.abspath(folder)
        recursion = props.recursive_search
        col = layout.column(align=True)
        row = col.row(align=True)
        favs = get_favs()
        if props.previews_dir.strip():
            if folder in favs:
                row.operator("easyhdr.remove_from_fav", text = '', icon = 'X')
            elif os.path.exists(folder):
                row.operator("easyhdr.add_to_fav", text = '', icon = 'SOLO_ON')
        row.prop(props, "previews_dir", text = '')
        if recursion:
            col.prop(props, "sub_dirs")
        col = layout.column(align=True)    
        col.prop(props, "filter", text = '', placeholder='Search...',icon = 'VIEWZOOM')
        row = col.row(align=True)
        row.enabled = len(pcoll.previews) > 1
        row.scale_y = 5.0
        row.operator("easyhdr.previous", text = '',  icon = 'TRIA_LEFT')
        row.template_icon_view(props, "previews", show_labels=True, scale = 1)
        row.operator("easyhdr.next", text = '', icon = 'TRIA_RIGHT')
        if not props.dynamic_load:
            col.operator("easyhdr.load_image", icon = 'IMPORT')
        box = col.box()
        row = box.row()
        row.scale_y, row.scale_x = (1.25, 1.25)
        row.alignment = 'CENTER'
        row.operator("easyhdr.reload_previews", text = '', icon = 'FILE_REFRESH')
        row.prop(props, 'favorites', icon = 'SOLO_ON', icon_only = True)
        row.menu("EASYHDRI_MT_settings_menu", text = '', icon = 'PREFERENCES')
        row.prop(scn.render, 'film_transparent', text = '', icon = 'TEXTURE')
        box = col.box()
        row = box.row()
        row.alignment = 'CENTER'
        name = props.previews[:-4] if props.previews else 'None'
        row.label(text = name)
        
        check = check_world_nodes(context)
        if check in ['Create', 'Fix']:
            col = layout.column()
            col.scale_y = 1.5
            text = check + ' World Nodes'
            col.operator("easyhdr.create_world", text = text, icon = 'WORLD_DATA')
            
            
# Template Sub-Panel
class EasyHDRI_Sub_Panel:
    bl_parent_id = "EASYHDRI_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Easy HDRI'
    
    @classmethod
    def poll(self, context):
        return check_world_nodes(context) == 'OK'
        
# Main Settings
class EASYHDRI_PT_main_settings(EasyHDRI_Sub_Panel, Panel):
    bl_label = "Main Settings"
    
    def draw_header(self, context):
        reset = self.layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK', text = '')
        reset.reset_type = 'MAIN'
    
    def draw(self, context):
        layout = self.layout
        world_nodes = context.scene.world.node_tree.nodes
        node = world_nodes.get('Easy HDRI')
        nodes = node.node_tree.nodes
        row = layout.row(align=True)
        row.separator()
        col = row.column()
        col.prop(node.inputs[0], "default_value", text = 'Sun Strength')
        col.prop(node.inputs[1], "default_value", text = 'Sky Strength')                    
        col.prop(nodes['Environment'], "projection", text = '')
        index = -1 if context.scene.easy_hdri_props.all_axis else 2
        col.prop(node.inputs[2], "default_value", text = "Rotation", index=index)
        
# Background Display
class EASYHDRI_PT_background(EasyHDRI_Sub_Panel, Panel):
    bl_label = "Background Display"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw_header(self, context):
        reset = self.layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK', text = '')
        reset.reset_type = 'BG'
    
    def draw(self, context):
        props = context.scene.easy_hdri_props
        layout = self.layout
        world_nodes = context.scene.world.node_tree.nodes
        node = world_nodes.get('Easy HDRI')
        nodes = node.node_tree.nodes
        row = layout.row(align=True)
        row.separator()
        col = row.column()
        row2 = col.row()
        row2.prop(props, 'easyhdr_bg_display', expand = True)
        if props.easyhdr_bg_display == 'Solid':
            col.prop(node.inputs[3], "default_value", text = "")
            col.prop(node.inputs[4], "default_value", text='Strength')
        elif props.easyhdr_bg_display == 'Blured':
            col.operator('easyhdr.generate_blured_image', icon = 'NODE_TEXTURE')
            col.operator('easyhdr.load_custom_image', icon = 'FILE_FOLDER')
            col.prop(nodes['Environment Blured'], "projection", text = '')
            col.prop(node.inputs[4], "default_value", text='Strength')
        else:
            col.prop(props, "ground_projection")
            if props.ground_projection:
                col.prop(node.inputs[5], "default_value",text='Size', index=2)
                col.prop(node.inputs[6], "default_value",text='Horizon', index=2)
                col.prop(nodes['Environment Projected'], "projection", text = '')
                col.prop(node.inputs[4], "default_value", text='Strength')
# Color
class EASYHDRI_PT_color(EasyHDRI_Sub_Panel, Panel):
    bl_label = "Color"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw_header(self, context):
        reset = self.layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK', text = '')
        reset.reset_type = 'COL'
    
    def draw(self, context):
        props = context.scene.easy_hdri_props
        layout = self.layout
        world_nodes = context.scene.world.node_tree.nodes
        node = world_nodes.get('Easy HDRI')
        row = layout.row(align=True)
        row.separator()
        col = row.column(align = True)
        col.prop(node.inputs[10], "default_value", text = "Tint")        
        col.prop(node.inputs[11], "default_value", text = "Factor")
        col.separator()
        col.prop(node.inputs[12], "default_value", text = "Gamma")
        col.separator()
        col.prop(node.inputs[13], "default_value", text = "Saturation")
        
# Sun Lamp
class EASYHDRI_PT_sun_lamp(EasyHDRI_Sub_Panel, Panel):
    bl_label = "Sun Lamp"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw_header(self, context):
        reset = self.layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK', text = '')
        reset.reset_type = 'SUN'
    
    def draw(self, context):
        props = context.scene.easy_hdri_props
        layout = self.layout
        nodes = context.scene.world.node_tree.nodes
        row = layout.row(align=True)
        row.separator()
        col = row.column()
        row2 = col.row(align = True)
        row2.prop(props, 'sun_lamp', text = '')
        row2.operator('easyhdr.align_sun', icon = 'LINKED', text ='')
        ob = props.sun_lamp
        if not hasattr(ob, 'type'):
            return
        if not ob.type == 'LIGHT':
            return
        if not ob.data.type == 'SUN':
            return
        col.prop(ob.data, 'color')
        col.prop(ob.data, 'energy')
        col.prop(ob.data, 'angle')
    
############################################################################################
################################ Register/Unregister #######################################
############################################################################################

classes = (
    EasyHDRIProps,
    EASYHDRI_OT_create_world,
    EASYHDRI_OT_previous_image,
    EASYHDRI_OT_next_image,
    EASYHDRI_OT_load_image,
    EASYHDRI_OT_reload_previews,
    EASYHDRI_OT_remove_unused_images,
    EASYHDRI_OT_generate_blured_image,
    EASYHDRI_OT_load_custom_image,
    EASYHDRI_OT_align_sun,
    EASYHDRI_OT_reset_to_default,
    EASYHDRI_OT_add_to_fav,
    EASYHDRI_OT_remove_from_fav,
    SettingsMenu,
    EASYHDRI_PT_main,
    EASYHDRI_PT_main_settings,
    EASYHDRI_PT_background,
    EASYHDRI_PT_color,
    EASYHDRI_PT_sun_lamp,
)

def register():
    from bpy.utils import register_class, previews
    for cls in classes:
        register_class(cls)
        
    pcoll = bpy.utils.previews.new()
    pcoll.previews = []
    pcoll.unfiltered = []
    pcoll.refresh = False
    preview_collections["hdris"] = pcoll
        
    bpy.types.Scene.easy_hdri_props = PointerProperty(type = EasyHDRIProps)

def unregister():
    from bpy.utils import unregister_class, previews
    for cls in reversed(classes):
        unregister_class(cls)
        
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Scene.easy_hdri_props

if __name__ == "__main__":
    register()