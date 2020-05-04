bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (1, 3, 2),
    'blender': (2, 80, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': 'Mesh',
}


import os
import sys
import importlib  
from bpy.types import AddonPreferences, PropertyGroup
import bpy.utils.previews 
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, FloatProperty



class PS_settings(PropertyGroup):

    def run_draw(self, context):
        if self.draw_advance == True:
            bpy.ops.ps.draw_mesh('INVOKE_DEFAULT')
    
    draw_advance: BoolProperty(name="Advance Draw Mesh", default=False, update=run_draw)





# Addon preferences
class PS_preferences(AddonPreferences):
    bl_idname = __package__
    
    
    """ def run_draw(self, context):
        if self.draw == True:
            bpy.ops.ps.draw_mesh('INVOKE_DEFAULT')

    draw: BoolProperty(name="Advance Draw Mesh", default=False, update=run_draw) """


    #draw_advance: BoolProperty(name="Advance Draw Mesh", default=False)



    header: BoolProperty(name="Header", default=False)
    viewHeader_L: BoolProperty(name="Viewport Header Left", default=True)
    viewHeader_R: BoolProperty(name="Viewport Header Right", default=False)
    toolHeader: BoolProperty(name="Tool Header", default=False)


    line_smooth: BoolProperty(name="Line Smooth(If You Need Accelerate)", default=True)


    tabs : EnumProperty(name="Tabs", items = [("GENERAL", "General", ""), ("KEYMAPS", "Keymaps", "")], default="GENERAL")



    # draw mesh
    edge_width: FloatProperty(name="Edge Width", description="Edge Width", min=1.0, soft_max=5.0, default=2.5, subtype='FACTOR')

    z_bias: FloatProperty(name="Z-Bias", description="Z-Bias", min=0.0001, soft_max=1.0, default=0.5, subtype='FACTOR')
    opacity: FloatProperty(name="Opacity", description="Face Opacity", min=0.0, max=1.0, default=0.8, subtype='PERCENTAGE')






    vertex_color: FloatVectorProperty(name="Vertex Color", subtype='COLOR', default=(0.0, 0.0, 0.0), min=0.0, max=1.0, description="Select color for Vertex")
    edge_color: FloatVectorProperty(name="Edge & Vertex Color", subtype='COLOR', default=(0.0, 0.0, 0.0), min=0.0, max=1.0, description="Select color for Edges & Vertex")
    face_color: FloatVectorProperty(name="Face Color", subtype='COLOR', default=(0.0, 0.3, 1.0), min=0.0, max=1.0, description="Select color for Face")

    select_items_color: FloatVectorProperty(name="Select Color Vertex/Edges", subtype='COLOR', default=(1.0, 0.07, 0.0), min=0.0, max=1.0)
    #select_faces_color: FloatVectorProperty(name="Select Color Faces", subtype='COLOR', default=(1.0, 1.0, 1.0), min=0.0, max=1.0)

  
    non_manifold_color: FloatVectorProperty(name="Non Manifold Color", subtype='COLOR', default=(1.0, 0.0, 0.0), min=0.0, max=1.0)


    bound_col: FloatVectorProperty(name="Bound Color", subtype='COLOR', default=(0.5, 0.0, 1.0), min=0.0, max=1.0)
    e_pole_col: FloatVectorProperty(name="E-Pole Color", subtype='COLOR', default=(1.0, 0.5, 0.0), min=0.0, max=1.0)
    n_pole_col: FloatVectorProperty(name="N-Pole Color", subtype='COLOR', default=(1.0, 1.0, 0.0), min=0.0, max=1.0)
    f_pole_col: FloatVectorProperty(name="More 5 Pole Color", subtype='COLOR', default=(1.0, 0.0, 1.0), min=0.0, max=1.0)

    tris_col: FloatVectorProperty(name="Tris Color", subtype='COLOR', default=(0.0, 0.5, 0.9), min=0.0, max=1.0)
    ngone_col: FloatVectorProperty(name="NGone Color", subtype='COLOR', default=(1.0, 0.1, 0.0), min=0.0, max=1.0)







    xray: BoolProperty(name="X-Ray", default=False)

    retopo_mode: BoolProperty(name="Retopology Mode", default=False)

    non_manifold_check: BoolProperty(name="Non Manifold", default=False)
    v_alone: BoolProperty(name="Vertex Alone", default=False)
    v_bound: BoolProperty(name="Vertex Boundary", default=False)
    e_pole: BoolProperty(name="Vertex E-Pole", default=False)
    n_pole: BoolProperty(name="Vertex N-Pole", default=False)
    f_pole: BoolProperty(name="More 5 Pole", default=False)

    tris: BoolProperty(name="Tris", default=False)
    ngone: BoolProperty(name="N-Gone", default=False)


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        box = layout.box()

        if self.tabs == "GENERAL":
            self.draw_general(box)

        elif self.tabs == "KEYMAPS":
            self.draw_keymaps(context, box)


    def draw_general(self, layout):
        pcoll = preview_collections["main"]
        market_icon = pcoll["market_icon"]
        gumroad_icon = pcoll["gumroad_icon"]
        artstation_icon = pcoll["artstation_icon"]
        discord_icon = pcoll["discord_icon"]



        
        col = layout.column()
        col.prop(self, "header", text="Header(Not Suport Advance Draw Mesh)")
        col.prop(self, "viewHeader_L")
        col.prop(self, "viewHeader_R")
        col.prop(self, "toolHeader")
        

        box = layout.box()
        box.prop(self, "line_smooth")


        row = box.row()
        row.prop(self, "non_manifold_color")
        row = box.row()
        box.label(text="Advance Draw Mesh")
        row = box.row()
        row.prop(self, "vertex_color")
        row = box.row()
        row.prop(self, "edge_color")
        row = box.row()
        row.prop(self, "face_color")
        row = box.row()
        row.prop(self, "select_items_color")

        
        box.label(text="Check")
        row = box.row()
        row.prop(self, "bound_col")
        row = box.row()
        row.prop(self, "e_pole_col")
        row = box.row()
        row.prop(self, "n_pole_col")
        row = box.row()
        row.prop(self, "f_pole_col")
        row = box.row()
        row.prop(self, "tris_col")
        row = box.row()
        row.prop(self, "ngone_col")



        col = layout.column()
        col.label(text="Links")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("wm.url_open", text="Blender Market", icon_value=market_icon.icon_id).url = "https://blendermarket.com/creators/derksen"
        row.operator("wm.url_open", text="Gumroad", icon_value=gumroad_icon.icon_id).url = "https://gumroad.com/derksenyan"
        row.operator("wm.url_open", text="Artstation", icon_value=artstation_icon.icon_id).url = "https://www.artstation.com/derksen"
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("wm.url_open", text="Discord Channel", icon_value=discord_icon.icon_id).url = "https://discord.gg/SBEDbmK"


    def draw_keymaps(self, context, layout):
        col = layout.column()
        col.label(text="Keymap")
        
        keymap = context.window_manager.keyconfigs.user.keymaps['3D View']
        keymap_items = keymap.keymap_items

        col.prop(keymap_items["mesh.ps_ngons"], 'type', text='NGons', full_event=True)
        col.prop(keymap_items["mesh.ps_quads"], 'type', text='Quads', full_event=True)
        col.prop(keymap_items["mesh.ps_tris"], 'type', text='Tris', full_event=True)

        col.label(text="*some hotkeys may not work because of the use of other addons")




addon_keymaps = []  
preview_collections = {}



from . import PS_draw_mesh
from . import PS_panel






classes = [
    PS_settings,
    PS_preferences,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    PS_panel.register()
    PS_draw_mesh.register()
 




    bpy.types.Scene.polySource_set = bpy.props.PointerProperty(type=PS_settings)

  
    

    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon

    kc = addon_keyconfig
    if not kc:
        return

    

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    # Pie
    kmi = km.keymap_items.new("mesh.ps_ngons", type = "ONE",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("mesh.ps_quads", type = "TWO",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("mesh.ps_tris", type = "THREE",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    del addon_keyconfig

    

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("market_icon", os.path.join(my_icons_dir, "market.png"), 'IMAGE')
    pcoll.load("gumroad_icon", os.path.join(my_icons_dir, "gumroad.png"), 'IMAGE')
    pcoll.load("artstation_icon", os.path.join(my_icons_dir, "artstation.png"), 'IMAGE')
    pcoll.load("discord_icon", os.path.join(my_icons_dir, "discord.png"), 'IMAGE')
    preview_collections["main"] = pcoll


    #bpy.app.handlers.load_post.append(run_draw)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    PS_panel.unregister()
    PS_draw_mesh.unregister()




    #remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    #bpy.app.handlers.load_post.remove(run_draw)