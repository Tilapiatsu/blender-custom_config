bl_info = {
    "name":"Light Manager",
    "author":"Paulo C. R. Silva",
    "version":(1,1,3),
    "blender":(2,83,0),
    "location":"View3D > Sidebar > LM",
    "description":"Viewport Light Manager based on fstops",
    "warning":"",
    "wiki_url":"",
    "category":"Scene"
    }

import bpy

# classes
class OBJECT_OT_plusMinusFStop(bpy.types.Operator):
    """Changes a lights energy based on fstops"""
    bl_label = "fchange"
    bl_idname = "light.fchange"
    bl_options = {'REGISTER', 'UNDO'}
    
    light_name: bpy.props.StringProperty(
        name = "Name",
        default = "",
        description = "Name of the light to change"
        )
    
    fstop_change: bpy.props.FloatProperty(
        name = "fstop",
        default = 1.0,
        description = "fstop change"
        )
    
    def execute(self, context):
        ratio = 1 + self.fstop_change
        if bpy.data.objects[self.light_name].data.energy > 0.001:
            bpy.data.objects[self.light_name].data.energy = bpy.data.objects[self.light_name].data.energy * ratio
        elif ratio > 1:
            if bpy.data.objects[self.light_name].data.type == "SUN":
                bpy.data.objects[self.light_name].data.energy = 0.1
            else:
                bpy.data.objects[self.light_name].data.energy = 1
        
        return {'FINISHED'}
    
def sel_all_lights(context):
    bpy.ops.object.select_by_type(type="LIGHT")
    
class SCENE_OT_selLights(bpy.types.Operator):
    """Select all lights"""
    bl_label = "select all lights"
    bl_idname = "scene.sel_all_lights"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        sel_all_lights(context)
        return {'FINISHED'}

def hide_light(light):
    light.hide_render = True
    light.hide_viewport = True
    
def show_light(light):
    light.hide_render = False
    light.hide_viewport = False

class SCENE_OT_SoloLight(bpy.types.Operator):
    """Turns off all lights except this one"""
    bl_label = "Solo light"
    bl_idname = "scene.lmsolo_light"
    bl_options = {'REGISTER', 'UNDO'}
    
    light_name: bpy.props.StringProperty(
        name = "Name",
        default = "",
        description = "Name of the light to solo"
        )
    def execute(self, context):
        if(bpy.context.scene.lm_in_solo_mode and self.light_name == bpy.context.scene.lm_solo_light_name):
            # show all lights:
            for ob in bpy.data.objects:
                if(ob.type == "LIGHT"):
                    show_light(ob)
                bpy.context.scene.lm_in_solo_mode = False
        else:
            # solo light
            for ob in bpy.data.objects:
                if(ob.type == "LIGHT"):
                    hide_light(ob)
            show_light(bpy.data.objects[self.light_name])
            # select light:
            bpy.data.objects[self.light_name].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[self.light_name]
            bpy.context.scene.lm_in_solo_mode = True
            bpy.context.scene.lm_solo_light_name = self.light_name
        return {'FINISHED'}
    
class viewport_light_manager(bpy.types.Panel):
    """Viewport Light manager"""
    # panel attributes
    bl_label = "Viewport-Light-Manager"
    bl_idname = "OBJECT_PT_vlm" #internal name, must be unique # convention
    bl_space_type = "VIEW_3D" # "VIEW_3D" #what view to draw the panel on
    bl_region_type = "UI" # region
    bl_category = "LM" # tab of region
    bl_context = "objectmode"
    # light ratios:
    # 1.6 ratio > "feels" right
    m_one = -0.375
    m_half = -0.20942
    p_half = 0.2649
    p_one = 0.6
    
    # draw function
    def draw(self, context):
        if not bpy.context.scene.lm_use_smaller_stops: # checked: use 1.6 ratio, unchecked: use 2.0 ratio (Mathematically correct, but a bit unpratical)
        # double power every fstops
            self.m_one = -0.5
            self.m_half = -0.292893218813452
            self.p_half = 0.414213562373095
            self.p_one = 1
        layout = self.layout
        row = layout.row()
        row.prop(bpy.context.scene, "lm_show_all_lights", text="Show all lights")
        layout.prop(bpy.context.scene, 'lm_use_smaller_stops', text="Smaller increment")
        p = layout.operator(SCENE_OT_selLights.bl_idname)
        layout.label(text="World", icon='WORLD')
        row = layout.row(align=True)
        row.prop(bpy.data.worlds[0].node_tree.nodes["Background"].inputs[1], "default_value", text="")
        row.prop(bpy.data.worlds[0].node_tree.nodes["Background"].inputs[0], "default_value", text="")
        if(bpy.context.scene.lm_show_all_lights):
            lights = bpy.data.objects # show all lights
        else:
            lights = bpy.context.selected_objects  # show only selected lights
        for ob in lights: 
            if ob.type == 'LIGHT':
                box = layout.box()
#                box.alert = bpy.context.active_object.name == ob.name # alert if active light 
                row = box.row()
                col = row.column()
                col.alert = bpy.context.scene.lm_in_solo_mode and not ob.hide_render # alert if solo light
                col.scale_x = 1
                pb = col.operator( SCENE_OT_SoloLight.bl_idname, text="", icon='OUTLINER_DATA_LIGHT')
                pb.light_name = ob.name
                if bpy.context.active_object and bpy.context.active_object.name == ob.name: # has icon if active light 
                    row.prop(ob, "name", text="", icon='TRIA_RIGHT')
                else:
                    row.prop(ob, "name", text="")
                row = box.row()
                row.prop(ob.data, "type")
                if ob.data.type == "AREA":
                    row.prop(ob.data, "size")
                if ob.data.type == "POINT":
                    row.prop(ob.data, "shadow_soft_size")
                if ob.data.type == "SPOT":
                    row.prop(ob.data, "spot_size")
                if ob.data.type == "SUN":
                    row.prop(ob.data, "angle")
                
                row = box.row(align=True)
                row.prop(ob.data, "energy")
                row.prop(ob.data, "color", text="")
                layout.split()

                row = box.row(align=True)
                pb = row.operator( OBJECT_OT_plusMinusFStop.bl_idname, text="-1")
                pb.light_name = ob.name
                pb.fstop_change = self.m_one
                p = row.operator( OBJECT_OT_plusMinusFStop.bl_idname, text="-.5")
                p.light_name = ob.name
                p.fstop_change = self.m_half
                p = row.operator( OBJECT_OT_plusMinusFStop.bl_idname, text="+.5")
                p.light_name = ob.name
                p.fstop_change = self.p_half
                pb = row.operator( OBJECT_OT_plusMinusFStop.bl_idname, text="+1")
                pb.light_name = ob.name
                pb.fstop_change = self.p_one

# registration
def register():
    
    bpy.types.Scene.lm_in_solo_mode = bpy.props.BoolProperty(
        name = "lm_in_solo_mode",
        default = False,
        description = "Flag to check if light manager is in solo mode"
        )
        
    bpy.types.Scene.lm_solo_light_name = bpy.props.StringProperty(
        name = "lm_solo_light_name",
        default = "",
        description = "Name of the light in solo mode"
        )
    bpy.types.Scene.lm_show_all_lights = bpy.props.BoolProperty(
        name = "lm_show_all_lights",
        default = False,
        description = "Flag to check if light manager show all lights or just the selected one"
        )
    bpy.types.Scene.lm_use_smaller_stops = bpy.props.BoolProperty(
        name = "lm_use_smaller_stops",
        default = False,
        description = "Check this to use smaller power increments\nLess than a full stop, but more control"
        )
    bpy.utils.register_class(OBJECT_OT_plusMinusFStop)
    bpy.utils.register_class(SCENE_OT_selLights)
    bpy.utils.register_class(SCENE_OT_SoloLight)
    bpy.utils.register_class(viewport_light_manager)
    

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_plusMinusFStop)
    bpy.utils.unregister_class(SCENE_OT_selLights)
    bpy.utils.unregister_class(SCENE_OT_SoloLight)
    bpy.utils.unregister_class(viewport_light_manager)
    
    del bpy.types.Scene.lm_in_solo_mode
    del bpy.types.Scene.lm_solo_light_name
    del bpy.types.Scene.lm_show_all_lights
    del bpy.types.Scene.lm_use_smaller_stops

if __name__ == "__main__":
    register()