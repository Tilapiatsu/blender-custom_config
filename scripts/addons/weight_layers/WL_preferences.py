import bpy
from bpy.props import *
from .WL_constants import IS_AT
from .WL_ui import WEIGHTLAYER_PT_main_panel

# parent class that can be inherited by both standalone and alpha trees prefs. 
class WeightLayersPrefsParent():
    
    def draw_wl_prefs(self, layout, context):
        layout.prop(self, "layer_order")
        layout.prop(self, "wl_panel_location")
        if self.wl_panel_location == "N_PANEL":
            layout.prop(self, "wl_panel_category")
    
    def wl_panel_loc_update(self, context):
        panels = [WEIGHTLAYER_PT_main_panel]
        for panel in panels:
            try:
                bpy.utils.unregister_class(panel)
            except RuntimeError:
                # Not yet registered
                pass
            n_panel = self.wl_panel_location == "N_PANEL"
            panel.bl_space_type = "VIEW_3D" if n_panel else "PROPERTIES"
            panel.bl_region_type = "UI" if n_panel else "WINDOW"
            if n_panel:
                panel.bl_category = self.wl_panel_category
                panel.bl_context = ""
            else:
                panel.bl_context = "data"
            bpy.utils.register_class(panel)
        
    wl_panel_location: EnumProperty(
        items=(
            ("N_PANEL", "N-Panel", "Put the Weight Layers panel in the N-Panel in the 3D viewport"),
            ("DATA", "Data properties", "Put the Weight Layers panel in the data section of the properties editor"),
        ),
        default="N_PANEL",
        name="Panel location",
        update=wl_panel_loc_update
    )
    
    wl_panel_category: StringProperty(
        name="Panel category",
        description="The tab that the weight layers panel is located in in the 3D viewport",
        default = "Alpha Trees" if IS_AT else "Weight Layers",
        update=wl_panel_loc_update
    )

    layer_order: EnumProperty(
        items=(
            ("DEFAULT", "Output at the bottom (like modifiers)", "Displays the layers in an order similar to modifiers, with the output at the bottom"),
            ("REVERSED", "Output at the top (like photoshop layers)", "Displays the layers in an order similar to photoshop layers, with the output at the bottom"),
        ),
        name="Layer order"
    )

class WeightLayersPrefs(WeightLayersPrefsParent, bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        self.draw_wl_prefs(layout, context)

classes = [] if IS_AT else [WeightLayersPrefs]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)