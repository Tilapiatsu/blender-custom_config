import bpy
from . import simulation

from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)

CLOTH_WEIGHT = 'cloth_weight'

class BystedtsClothBuilder_PT_simulation(bpy.types.Panel):
    bl_idname = "BCB_PT_simulation"
    bl_label = "Bystedts Cloth Builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B C B'
    
    def draw(self, context):
        layout = self.layout
        title_size = 0.6
        BCB_props = context.scene.BCB_props
        col = layout.column()
        col_global = layout.column()

        # Global settings
        col.label(text = "Simulation settings")
        if bpy.context.screen.is_animation_playing:
            col.operator('bcb.stop_simulation', icon = 'PAUSE')
        else:
            col.operator('bcb.run_simulation', icon = 'PLAY')

        if context.scene.frame_start != context.scene.frame_current:
            col.operator('bcb.reset_simulation', icon = 'TRIA_LEFT_BAR')

        #col.operator('bcb.test_operator')

        col.prop(BCB_props, "simulation_frames")
        
        # Global settings
        col.prop(BCB_props, "use_global_settings")
        if not BCB_props.use_global_settings:
            col_global.enabled = False
        col_global.prop(BCB_props, "sim_quality")
        col_global.prop(BCB_props, "collision_quality")
        col_global.prop(BCB_props, "collision_distance")



        
        

class BystedtsClothBuilder_PT_ObjectSettings(bpy.types.Panel):
    bl_idname = "BCB_PT_object_settings"
    bl_label = "Object settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B C B'
    
    def draw(self, context):    
        layout = self.layout
        BCB_props = context.scene.BCB_props
        col = layout.column()
        
        # Per object settings

        # If no objects selected
        if len(context.selected_objects) == 0:
            row = col.row()
            row.label(text = "No objects selected")
            return
        
        # Cloth modifier
        cloth_mods = simulation.get_modifiers(context, 'CLOTH', context.selected_objects)

        if not len(cloth_mods) == len(context.selected_objects):
            row = col.row()
            row.label(text = "Cloth")
            row.operator('bcb.add_cloth', icon = 'MOD_CLOTH')
            col.prop(BCB_props, "use_triangulate")
            
        if len(cloth_mods) > 0:
            row = col.row(align = True)
            row.label(text = "Cloth")
            row.prop(cloth_mods[0], 'show_viewport', text = '')
            row.operator('bcb.remove_cloth', icon = 'MOD_CLOTH')

        col.separator()

        # Collision modifier
        mods = simulation.get_modifiers(context, 'COLLISION', context.selected_objects)

        if not len(mods) == len(context.selected_objects):
            row = col.row(align = True)
            row.label(text = "Collision")
            row.operator('bcb.add_collision', icon = 'MOD_PHYSICS')
        
        if len(mods) > 0:
            row = col.row(align = True)
            row.label(text = "Collision")
            row.prop(context.object.collision, 'use', text = '', icon = 'RESTRICT_VIEW_ON')
            row.operator('bcb.remove_collision', icon = 'MOD_PHYSICS')

        col.separator()

        # Cloth settings
        if len(cloth_mods) > 0:
            col.prop(cloth_mods[0].collision_settings, 'use_self_collision')
            col.prop(cloth_mods[0].settings, 'use_pressure')
            col.prop(cloth_mods[0].settings, 'shrink_min')
            col.prop(cloth_mods[0].settings, 'uniform_pressure_force')
            col.prop(cloth_mods[0].settings, 'bending_stiffness')
            col.prop(cloth_mods[0].settings, 'bending_stiffness_max')
            col.prop(cloth_mods[0].settings, 'shrink_max')


class BystedtsClothBuilder_PT_pinning(bpy.types.Panel):
    bl_idname = "BCB_PT_pinning"
    bl_label = "Pinning"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B C B'
    
    def pin_is_selected(self, context):
        for object in context.selected_objects:
            if object.get('is_pin'):
                return True
        return False

    def draw(self, context):
        layout = self.layout
        title_size = 0.6
        BCB_props = context.scene.BCB_props
        col = layout.column()
        col2 = layout.column()
        col3 = layout.column()
        col4 = layout.column()

        if not context.mode == 'EDIT_MESH':
            col.label(text = "Enter edit mode to add pins")
            col2.enabled = False
        
        if not self.pin_is_selected(context):
            col3.enabled = False

        col.prop(BCB_props, "pin_scale")
        col.prop(BCB_props, "pin_shape")

        col2.operator('bcb.add_pin', icon = 'ADD')
        col3.operator('bcb.remove_pin', icon = 'REMOVE')

        col4.operator('bcb.clear_pins', icon = 'PANEL_CLOSE')
        col4.operator('bcb.remove_pins_in_scene', icon = 'CANCEL')
        col4.operator('bcb.reset_pins_from_mesh_object', icon = 'FULLSCREEN_EXIT')
        
    

class BystedtsClothBuilder_PT_shape(bpy.types.Panel):
    bl_idname = "BCB_PT_shape"
    bl_label = "Shape"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B C B'
    
    def draw(self, context):
        layout = self.layout
        title_size = 0.6
        BCB_props = context.scene.BCB_props
        col = layout.column()

        col.prop(BCB_props, "apply_subsurf_modifiers")
        col.operator('bcb.apply_base', icon = 'ADD')
        col.operator('bcb.save_shape_key', icon = 'ADD')
        col.operator('bcb.reshape_multires', icon = 'ADD')

class BystedtsClothBuilder_PT_utils(bpy.types.Panel):
    bl_idname = "BCB_PT_utils"
    bl_label = "Utils"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B C B'
    
    def draw(self, context):
        layout = self.layout
        title_size = 0.6
        BCB_props = context.scene.BCB_props
        col = layout.column()

        col.operator('bcb.open_asset_browser', icon = 'ASSET_MANAGER')
        col.operator('bcb.fit_to_active', icon = 'MATCLOTH')
        col.operator('bcb.paint_weight', icon = 'VPAINT_HLT')
        col.operator('bcb.shake_cloth', icon = 'FORCE_TURBULENCE')
        col.operator('bcb.make_duplicate', icon = 'DUPLICATE')
        props = col.operator('bcb.open_internet_link', text = "Video tutorial", icon = 'QUESTION')
        props.internet_link = "https://youtu.be/EAraCGAaLoU"

        

class BystedtsClothBuilder_PG(bpy.types.PropertyGroup):

    def update_all_modifier_settings(self, context):
        simulation.set_modifier_settings(context)

    orig_end_frame: IntProperty(
        name="Original end frame",
        default=250,
    )

    use_global_settings: BoolProperty(
        name = "Use global settings",
        description = ("Use global settings for thickness " 
        "etc. Otherwise use settings per modifier"),
        default = True
    )

    simulation_frames: IntProperty(
        name="Simulation frames",
        default=5000,
        update = update_all_modifier_settings,
        description = ("Global simulation frames for timeline "
            "and all cloth modifiers cache")
    )

    sim_quality: IntProperty(
        name="Simulation quality",
        default=4,
        min = 1,
        max = 20,
        soft_max = 5,
        update = update_all_modifier_settings,
        description = ("Global simulation quality for all"
            " cloth modifiers in the scene")
    )    

    collision_quality: IntProperty(
        name="Collision quality",
        default=2,
        min = 1,
        max = 20,
        soft_max = 5,
        update = update_all_modifier_settings,
        description = ("Global collision quality for all"
            " cloth modifiers in the scene")
    )    
    
    collision_distance: FloatProperty(
        name="Collision distance",
        default = 0.005,
        min = 0.00000001,
        description = ("Inner and outer collision distance "
            "for all cloth and collision modifiers in the scene"),
        update = update_all_modifier_settings
    )     

    apply_subsurf_modifiers: BoolProperty(
        name = "Apply subsurf modifiers",
        description = "Apply subsurface and multires modifiers before applying the shape",
        default = True
    )

    use_triangulate: BoolProperty(
        name = "Use triangulate modifier after cloth",
        description = "Use triangulate modifier after cloth modifier to fix wrinkles shapes",
        default = True
    )

    pin_scale: FloatProperty(
        name="Pin scale",
        default=0.1,
        min = 0,
        description = "Scale for all pins during creation",

    )        

    items = [('PLAIN_AXES', 'Plain axes', ""),
            ('ARROWS', 'Arrows', ""),
            ('SINGLE_ARROW', 'Single arrow', ""),
            ('CIRCLE', 'Circle', ""),
            ('CUBE', 'Cube', ""),
            ('SPHERE', 'Sphere', ""),
            ('CONE', 'Cone', ""),
    ]

    pin_shape: EnumProperty(
        name="Pin shape",
        items=items,
        )   


classes = (
    BystedtsClothBuilder_PT_simulation,
    BystedtsClothBuilder_PT_ObjectSettings,
    BystedtsClothBuilder_PT_pinning,
    BystedtsClothBuilder_PT_shape,
    BystedtsClothBuilder_PT_utils,
    BystedtsClothBuilder_PG,
    
)

def register():

    for clas in classes:
        bpy.utils.register_class(clas)

    bpy.types.Scene.BCB_props = bpy.props.PointerProperty(type = BystedtsClothBuilder_PG)

def unregister():
    
    for clas in classes:
        bpy.utils.unregister_class(clas)

    