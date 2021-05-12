'''
Copyright (C) 2019 Dancing Fortune Software All Rights Reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    'name': 'Bake Wrangler',
    'description': 'Bake Wrangler aims to improve all baking tasks with a node based interface and provide additional common bake passes',
    'author': 'DFS',
    'version': (1, 0, "RC5"),
    'blender': (2, 83, 0),
    'location': 'Editor Type > Bake Node Editor',
    "warning": "Release Candidate",
    'wiki_url': 'https://bake-wrangler.readthedocs.io',
    "tracker_url": "https://blenderartists.org/t/bake-wrangler-node-based-baking-tool-set/",
    "support": "COMMUNITY",
    'category': 'Bake'}


import bpy
from . import nodes



# Preferences 
class BakeWrangler_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    # Message prefs
    text_msgs: bpy.props.BoolProperty(name="Messages to Text editor", description="Write messages to a text block in addition to the console", default=True)
    clear_msgs: bpy.props.BoolProperty(name="Clear Old Messages", description="Clear the text block before each new bake", default=True)
    wind_msgs: bpy.props.BoolProperty(name="Open Text in new Window", description="A new window will be opened displaying the text block each time a new bake is started (must be closed manually)", default=True)
    
    # Node prefs
    def_filter_mesh: bpy.props.BoolProperty(name="Meshes", description="Show mesh type objects", default=True)
    def_filter_curve: bpy.props.BoolProperty(name="Curves", description="Show curve type objects", default=True)
    def_filter_surface: bpy.props.BoolProperty(name="Surfaces", description="Show surface type objects", default=True)
    def_filter_meta: bpy.props.BoolProperty(name="Metas", description="Show meta type objects", default=True)
    def_filter_font: bpy.props.BoolProperty(name="Fonts", description="Show font type objects", default=True)
    def_filter_light: bpy.props.BoolProperty(name="Lights", description="Show light type objects", default=True)
    def_filter_collection: bpy.props.BoolProperty(name="Collections", description="Toggle only collections", default=False)
    def_show_adv: bpy.props.BoolProperty(name="Expand Advanced Settings", description="Expand advanced settings on node creation instead of starting with them collapsed", default=False)
    
    # Render prefs
    def_samples: bpy.props.IntProperty(name="Default Bake Samples", description="The number of samples per pixel that new Pass nodes will be set to when created", default=1, min=1)
    def_xres: bpy.props.IntProperty(name="Default Bake X Resolution", description="The X resolution new Pass nodes will be set to when created", default=1024, min=1, subtype='PIXEL')
    def_yres: bpy.props.IntProperty(name="Default Bake Y Resolution", description="The Y resolution new Pass nodes will be set to when created", default=1024, min=1, subtype='PIXEL')
    def_device: bpy.props.EnumProperty(name="Default Device", description="The render device new Pass nodes will be set to when created", items=nodes.node_tree.BakeWrangler_Bake_Pass.cycles_devices, default='CPU')
    def_raydist: bpy.props.FloatProperty(name="Default Ray Distance", description="The ray distance that new Mesh nodes will use when created", default=0.01, step=1, min=0.0, unit='LENGTH')
    def_margin: bpy.props.IntProperty(name="Default Margin", description="The margin that new Mesh nodes will use when created", default=0, min=0, subtype='PIXEL')
    def_mask_margin: bpy.props.IntProperty(name="Default Mask Margin", description="The mask margin that new Mesh nodes will use when created", default=0, min=0, subtype='PIXEL')    
    ignore_vis: bpy.props.BoolProperty(name="Objects Always Visible", description="Enable to ignore the visibility of selected objects when baking, making them visible regardless of settings in blender", default=False)
    
    # Ouput prefs
    def_format: bpy.props.EnumProperty(name="Default Output Format", description="The format new Output nodes will use when created", items=nodes.node_tree.BakeWrangler_Output_Image_Path.img_format, default='PNG')
    def_xout: bpy.props.IntProperty(name="Default Output X Resolution", description="The X resolution new Output nodes will be set to when created", default=1024, min=1, subtype='PIXEL')
    def_yout: bpy.props.IntProperty(name="Default Output Y Resolution", description="The Y resolution new Output nodes will be set to when created", default=1024, min=1, subtype='PIXEL')
    def_outpath: bpy.props.StringProperty(name="Default Output Path", description="The path new Output nodes will use when created", default="", subtype='DIR_PATH')
    def_outname: bpy.props.StringProperty(name="Default Output Name", description="The name new Output nodes will use when created", default="Image", subtype='FILE_NAME')
    make_dirs: bpy.props.BoolProperty(name="Create Paths", description="If selected path doesn't exist, try to create it", default=False)
    save_pass: bpy.props.BoolProperty(name="Save each Pass", description="Save output image after each bake pass, instead of after all contributing passes", default=False)
    
    # Dev prefs
    debug: bpy.props.BoolProperty(name="Debug", description="Enable additional debugging output", default=False)

    def draw(self, context):
        layout = self.layout
        
        coltext = layout.column(align=False)
        coltext.prop(self, "text_msgs")
        if self.text_msgs:
            box = coltext.box()
            box.prop(self, "clear_msgs")
            box.prop(self, "wind_msgs")
        
        # Node prefs
        colnode = layout.column(align=False)
        colnode.label(text="Node Defaults:")
        box = colnode.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="Filter:")
        row1 = row.row(align=True)
        row1.alignment = 'LEFT'
        row1.prop(self, "def_filter_mesh", text="", icon='MESH_DATA')
        row1.prop(self, "def_filter_curve", text="", icon='CURVE_DATA')
        row1.prop(self, "def_filter_surface", text="", icon='SURFACE_DATA')
        row1.prop(self, "def_filter_meta", text="", icon='META_DATA')
        row1.prop(self, "def_filter_font", text="", icon='FONT_DATA')
        row1.prop(self, "def_filter_light", text="", icon='LIGHT_DATA')
        if self.def_filter_collection:
            row1.enabled = False
        row2 = row.row(align=False)
        row2.alignment = 'LEFT'
        row2.prop(self, "def_filter_collection", text="", icon='GROUP')
        box.prop(self, "def_show_adv")
        
        # Render prefs
        colrend = layout.column(align=False)
        colrend.label(text="Render Defaults:")
        box = colrend.box()
        col = box.column(align=False)
        col.prop(self, "def_samples", text="Samples")
        col1 = col.column(align=True)
        col1.prop(self, "def_xres", text="X")
        col1.prop(self, "def_yres", text="Y")
        col.prop(self, "def_device", text="Device")
        col.prop(self, "def_margin", text="Margin")
        col.prop(self, "def_mask_margin", text="Mask Margin")
        col.prop(self, "def_raydist", text="Ray Distance")
        col.prop(self, "ignore_vis")
        
        # Output prefs
        colout = layout.column(align=False)
        colout.label(text="Output Defaults:")
        box = colout.box()
        col = box.column(align=False)
        col.prop(self, "def_format", text="Format")
        col1 = col.column(align=True)
        col1.prop(self, "def_xout", text="X")
        col1.prop(self, "def_yout", text="Y")
        col2 = col.column(align=True)
        col2.prop(self, "def_outpath", text="Path")
        col2.prop(self, "def_outname", text="Name")
        col.prop(self, "make_dirs")
        col.prop(self, "save_pass")
        
        # Dev prefs
        layout.prop(self, "debug")
        
        
        
def register():
    from bpy.utils import register_class
    register_class(BakeWrangler_Preferences)
    nodes.register()


def unregister():
    from bpy.utils import unregister_class
    nodes.unregister()
    unregister_class(BakeWrangler_Preferences)
