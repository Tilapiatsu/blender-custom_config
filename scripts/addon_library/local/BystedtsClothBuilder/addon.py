import bpy
from . import simulation
import webbrowser

from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)

class BystedtsClothBuilder_OT_test_operator(bpy.types.Operator):
    bl_idname = "bcb.test_operator"
    bl_label = "TEST"

    def execute(self, context):
        simulation.add_default_vertex_groups_on_objects(context, context.selected_objects)
        return {'FINISHED'}

# Run simulation
class BystedtsClothBuilder_OT_run_simulation(bpy.types.Operator):
    bl_idname = "bcb.run_simulation"
    bl_label = "Run sim"
    bl_description = "Runs simulation in the current scene. Forces end frame of sim caches and scene to UI end frame."

    def execute(self, context):
        simulation.run_simulation(context)
        return {'FINISHED'}

# Stop simulation
class BystedtsClothBuilder_OT_stop_simulation(bpy.types.Operator):
    bl_idname = "bcb.stop_simulation"
    bl_label = "Stop sim"
    bl_description = 'Stops simulation'

    def execute(self, context):
        simulation.stop_simulation(context)
        return {'FINISHED'}

# Reset simulation
class BystedtsClothBuilder_OT_reset_simulation(bpy.types.Operator):
    bl_idname = "bcb.reset_simulation"
    bl_label = "Reset sim"
    bl_description = 'Jumps to first frame and resets pin transformations'

    def execute(self, context):
        simulation.reset_simulation(context)
        return {'FINISHED'}

# Add cloth
class BystedtsClothBuilder_OT_add_cloth(bpy.types.Operator):
    bl_idname = "bcb.add_cloth"
    bl_label = "Add cloth to selected"
    bl_description = ('Add cloth modifiers to selected objects '
        'that does not already have one. Sets properties from ui '
        'on the cloth modifiers')

    def execute(self, context):
        simulation.add_cloth_to_objects(context)
        return {'FINISHED'}

# Remove cloth
class BystedtsClothBuilder_OT_remove_cloth(bpy.types.Operator):
    bl_idname = "bcb.remove_cloth"
    bl_label = "Remove cloth from selected"
    bl_description = 'Removes cloth modifers from selected objects'

    def execute(self, context):
        simulation.remove_cloth_from_objects(context)
        return {'FINISHED'}

# Add collision
class BystedtsClothBuilder_OT_AddCollision(bpy.types.Operator):
    bl_idname = "bcb.add_collision"
    bl_label = "Add collision to selected"
    bl_description = 'Adds collision modifiers to selected objects with settings from UI'

    def execute(self, context):
        simulation.add_collision_to_objects(context)
        return {'FINISHED'}

# Remove collision
class BystedtsClothBuilder_OT_RemoveCollision(bpy.types.Operator):
    bl_idname = "bcb.remove_collision"
    bl_label = "Remove collision from selected"
    bl_description = 'Removes collision modifiers from selected objects'

    def execute(self, context):
        simulation.remove_collision_from_objects(context)
        return {'FINISHED'}


# Add pin
class BystedtsClothBuilder_OT_add_pin(bpy.types.Operator):
    bl_idname = "bcb.add_pin"
    bl_label = "Add pin"
    bl_description = ('Add pins to selected objects selected vertices '
        'during EDIT MODE. Pins are used for transforming '
        'cloth during simulation. Selected vertices are added to '
        'the vertex group ' + r"'" + simulation.PIN_GROUP_NAME + r"'")

    def execute(self, context):
        anim_playing = bpy.context.screen.is_animation_playing
        simulation.stop_simulation(context)
        simulation.reset_simulation(context)
        simulation.add_pin(context)

        if anim_playing:
            simulation.run_simulation(context)

        return {'FINISHED'}

# Remove pin
class BystedtsClothBuilder_OT_remove_pin(bpy.types.Operator):
    bl_idname = "bcb.remove_pin"
    bl_label = "Remove pin"
    bl_description = ('Remove selected pin objects and their '
        'associated vertices from the vertex group '
         + r"'" + simulation.PIN_GROUP_NAME + r"'")

    def execute(self, context):
        simulation.remove_selected_pins(context)
        simulation.reset_simulation(context)
        return {'FINISHED'}

# Clear pins
class BystedtsClothBuilder_OT_clear_pins(bpy.types.Operator):
    bl_idname = "bcb.clear_pins"
    bl_label = "Remove pins from mesh"
    bl_description = 'Removes all pins from the selected objects'

    def execute(self, context):
        simulation.clear_pins(context)
        return {'FINISHED'}

# Remove pins in scene
class BystedtsClothBuilder_OT_remove_pins_in_scene(bpy.types.Operator):
    bl_idname = "bcb.remove_pins_in_scene"
    bl_label = "Remove pins in scene"
    bl_description = 'Removes all pins from the active scene'

    def execute(self, context):
        simulation.remove_pins_in_scene(context)
        return {'FINISHED'}

# Reset pins on selected mesh objects
class BystedtsClothBuilder_OT_reset_pins_from_mesh_object(bpy.types.Operator):
    bl_idname = "bcb.reset_pins_from_mesh_object"
    bl_label = "Reset pins"
    bl_description = ("Reset pins on selected mesh. This means "
        'that their current location will be their default location')

    def execute(self, context):
        simulation.reset_hook_modifiers(context, context.selected_objects)
        return {'FINISHED'}

# Apply base
class BystedtsClothBuilder_OT_apply_base(bpy.types.Operator):
    bl_idname = "bcb.apply_base"
    bl_label = "Apply base"
    bl_description = ('Apply the current shape of the cloth to '
        'the mesh objects vertices')

    def execute(self, context):
        simulation.apply_base(context)
        return {'FINISHED'}

# Add as shape key
class BystedtsClothBuilder_OT_save_shape_key(bpy.types.Operator):
    bl_idname = "bcb.save_shape_key"
    bl_label = "Save shape key"
    bl_description = ('Save the current shape of the cloth to the'
        'mesh objects as a shape key.')

    def execute(self, context):
        simulation.save_shape_key(context)
        return {'FINISHED'}

# Reshape multires modifier
class BystedtsClothBuilder_OT_reshape_multires(bpy.types.Operator):
    bl_idname = "bcb.reshape_multires"
    bl_label = "Reshape multires"
    bl_description = "Reshapes the multires modifier by the current simulated shape"

    def execute(self, context):
        simulation.reshape_multires_modifiers(context, context.selected_objects)
        return {'FINISHED'}

# Open asset browser window
class BystedtsClothBuilder_OT_open_asset_browser(bpy.types.Operator):
    bl_idname = "bcb.open_asset_browser"
    bl_label = "Open asset browser"
    bl_description = ('Opens a new asset browser window with the ' 
        + simulation.ADDON_NAME + 'assets in the asset browser')

    def execute(self, context):
        simulation.open_asset_browser_window(context)
        return {'FINISHED'}

# Paint weight
class BystedtsClothBuilder_OT_paint_weight(bpy.types.Operator):
    bl_idname = "bcb.paint_weight"
    bl_label = "Paint cloth weight"
    bl_description = ('Paints weight for cloth modifier')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.screen.animation_cancel(restore_frame = True)
        simulation.reset_simulation(context)

        # Turn off geo nodes
        if self.turn_off_geo_nodes:
            geo_node_mods = simulation.get_modifiers(context, 'NODES', [context.object])
            for mod in geo_node_mods:
                mod.show_viewport = False
    
        try:
            print("Changing vtx grp to " + self.weight)
            bpy.ops.object.vertex_group_set_active(group = self.weight)
            if not context.mode == 'PAINT_WEIGHT':
                print("entering wieght paint mode")
                bpy.ops.paint.weight_paint_toggle()
        except:
            pass

        return {'FINISHED'}

    items = [
            (simulation.PIN_GROUP_NAME, simulation.PIN_GROUP_NAME, ""),
            (simulation.STIFFNESS_GROUP_NAME, simulation.STIFFNESS_GROUP_NAME, ""),
            (simulation.SHRINKING_GROUP_NAME, simulation.SHRINKING_GROUP_NAME, ""),
            (simulation.PRESSURE_GROUP_NAME, simulation.PRESSURE_GROUP_NAME, ""),
            ]
 
    weight: EnumProperty(
        name = "Weight",
        items = items
    )

    turn_off_geo_nodes: BoolProperty(
        name = "Turn off geo nodes",
        default = True,
        description = ('Geometry nodes can in some cases make '
            'weights not visible during weight painting. '
            'This option turn off geometry nodes before painting')
    )

# Shake cloth
class BystedtsClothBuilder_OT_shake_cloth(bpy.types.Operator):
    bl_idname = "bcb.shake_cloth"
    bl_label = "Shake cloth"
    bl_description = ('Shrink and restore selected objects '
        'with cloth modifier in order to create random wrinkles')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        simulation.shake_cloth(context, 
            objects = context.selected_objects,
            shrink = self.shrink,
            frames = self.frames
            )

        return {'FINISHED'}

    shrink: FloatProperty(
        name = "Shrink amount",
        description = "Amount to shrink and restore to shake the cloth",
        default = 0.07,
        soft_max = 0.3
    )

    frames: IntProperty(
        name = 'Frames',
        description = 'Frames between shrink and restore of cloth',
        default = 20
    )

class BystedtsClothBuilder_OT_make_duplicate(bpy.types.Operator):
    bl_idname = "bcb.make_duplicate"
    bl_label = "Make duplicate"
    bl_description = ("Make a duplicate opy of the mesh")
    bl_options = {'REGISTER', 'UNDO'}

    apply_geo_nodes: BoolProperty(
        default = False,
        description = "Apply geometry nodes during duplication"
    )

    apply_multires_on_duplicate: BoolProperty(
        default = True,
        description = "Apply multires on duplicated geometry"
    )


    def execute(self, context):
        simulation.make_duplicate(context, self.apply_geo_nodes, self.apply_multires_on_duplicate)
        return {'FINISHED'}

# Fit mesh to selected
class BystedtsClothBuilder_OT_fit_to_selected(bpy.types.Operator):
    bl_idname = "bcb.fit_to_active"
    bl_label = "Fit to active"
    bl_description = ("Fit the selected meshes to the active object "
        "using shrinkwrap and smooth corrective modifiers")
    bl_options = {'REGISTER', 'UNDO'}

    offset: FloatProperty(
        default = 0.01,
        description = "Offset from surface shrinkwrap"
    )

    corrective_iterations: IntProperty(
        default = 5,
        min = 0,
        max = 20,
        description = "Amount of corrective smooth iterations"
    )

    keep_modifiers: BoolProperty(
        default = False,
        description = 'Keeps the modifiers used in the process'
    )

    def execute(self, context):
        simulation.fit_to_active(
            context, self.offset, 
            self.corrective_iterations, self.keep_modifiers
        )
        return {'FINISHED'}

class BystedtsClothBuilder_OT_open_internet_link(bpy.types.Operator):
    '''
    Open internet link
    '''
    bl_idname = "bcb.open_internet_link"
    bl_label = "Open internet link"
    bl_description = "Open internet link"
    

    internet_link: StringProperty(
        name="Internet_link",
        default=""
    )    

    def execute(self, context):   
        
        try:
            webbrowser.open(self.internet_link)        
        except:
            self.report({'ERROR'}, "Could not open the link link: " + self.internet_link)
        return {'FINISHED'}  
    
classes = (
    BystedtsClothBuilder_OT_test_operator,
    BystedtsClothBuilder_OT_run_simulation,
    BystedtsClothBuilder_OT_stop_simulation,
    BystedtsClothBuilder_OT_reset_simulation,
    BystedtsClothBuilder_OT_add_pin,
    BystedtsClothBuilder_OT_reset_pins_from_mesh_object,
    BystedtsClothBuilder_OT_remove_pin,
    BystedtsClothBuilder_OT_clear_pins,
    BystedtsClothBuilder_OT_remove_pins_in_scene,
    BystedtsClothBuilder_OT_apply_base,
    BystedtsClothBuilder_OT_save_shape_key,
    BystedtsClothBuilder_OT_add_cloth,
    BystedtsClothBuilder_OT_remove_cloth,
    BystedtsClothBuilder_OT_AddCollision,
    BystedtsClothBuilder_OT_RemoveCollision,
    BystedtsClothBuilder_OT_open_asset_browser,
    BystedtsClothBuilder_OT_reshape_multires,
    BystedtsClothBuilder_OT_fit_to_selected,
    BystedtsClothBuilder_OT_paint_weight,
    BystedtsClothBuilder_OT_shake_cloth,
    BystedtsClothBuilder_OT_make_duplicate,
    BystedtsClothBuilder_OT_open_internet_link
)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)