#==============================
# THIS ADDON WAS WRITEN BY ND9H (nguyen dang huy)
#==============================
bl_info={
    "name": "HGen",
    "description": "A Blender hair generation addon",
    "author": "nguyen dang huy (ND9H)",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "VIEWPORT 3D -> UI",
    "warning": "",
    "tracker_url": "https://www.facebook.com/ND9H.Official/",
    "support": "COMMUNITY",
    "category": "ND9H_tools",
}
import bpy,webbrowser
from bpy.types import Operator, PropertyGroup, Menu
from re import search
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty

class H_Gen_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "H-Gen"
    bl_idname = "OBJECT_PT_hgen_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    def draw(self, context):
    
        layout = self.layout
        obj = context.object
        Hgen_properties = context.scene.ND9H_HGen
        target = Hgen_properties.target_mesh
        
        row = layout.row()
        row.label(text="",icon="OUTLINER_OB_HAIR")
        row.label(text="",icon="EVENT_H")
        row.label(text="",icon="EVENT_G")
        row.label(text="",icon="EVENT_E")
        row.label(text="",icon="EVENT_N")
        row.label(text="",icon="OUTLINER_OB_HAIR")
        row = layout.row()
        row.prop(Hgen_properties,"target_mesh")
        row = layout.row()
        try:
            active_particles = target.particle_systems.active.name
            row.label(text="active particles: "+active_particles) 
        except:
            pass
        row.operator(particle_to_guide.bl_idname,icon = "GP_SELECT_STROKES")
        #row = layout.row()
        #row.label(text="Active object is: " + obj.name)
        #row = layout.row()
        #row.prop(obj, "name")
        row = layout.row()
        row.operator("nd9h.create_hair") 
        row = layout.row()
        row.operator("nd9h.generate_hair",icon="OUTLINER_OB_HAIR") 
        row = layout.row() 
        row.prop(Hgen_properties,"hair_mat") 
        row = layout.row() 
        row.prop(Hgen_properties,"display_type")
        if bpy.context.scene.ND9H_HGen.display_type == 'STRIP':

            row = layout.row()
            row.prop(Hgen_properties,"guide_root_radius")
          
class guide_operator_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Guide Operator"
    bl_idname = "OBJECT_PT_Guide_O_Panel"
    bl_parent_id = "OBJECT_PT_hgen_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        Hgen_properties = context.scene.ND9H_HGen
        row.operator("nd9h.draw_hair_guide")
#        row = layout.row()
#        row.operator("nd9h.mesh_to_guide") 
        row = layout.row()
        row.prop(Hgen_properties,"decimate_ratio") 
        row.operator("nd9h.optimize_curve_guide")
        row = layout.row()
        row.operator("nd9h.duplicate_curve_guide")   
        row = layout.row()
        row.operator("nd9h.delete_curve_guide")
        row = layout.row()
        row.prop(Hgen_properties,"target_paricle")   
              
class draw_guide_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Draw setting"
    bl_idname = "OBJECT_PT_DGuide_Panel"
    bl_parent_id = "OBJECT_PT_Guide_O_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        row.prop(gp_settings, "active_smooth_factor")
        row = layout.row()
        row.prop(gp_settings, "use_settings_stabilizer", text="brush stabilizer")
        row = layout.row()
        
class hair_settings_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hair Settings"
    bl_idname = "OBJECT_PT_HSettings_Panel"
    bl_parent_id = "OBJECT_PT_hgen_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        Hgen_properties = context.scene.ND9H_HGen
        
        #obj = context.object
        vail = False
        selected_objs = bpy.context.selected_objects
        for obj in selected_objs:
            if context.selected_objects is not None and bpy.context.object.type == 'CURVE':
                vail = True
            else:
                vail = False
                
        if vail == True:
            row.prop(Hgen_properties, "number")
            row = layout.row()
            row.prop(Hgen_properties, "guide_clump_amount")   
            row = layout.row()
            row.prop(Hgen_properties, "guide_clump_shape") 
            row = layout.row()
            row.prop(Hgen_properties, "display_step")
        else:
            row.label(text="select H-Gen hair guide object to setting")
                    
class children_settings_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Children"
    bl_idname = "OBJECT_PT_HChildren_Panel"
    bl_parent_id = "OBJECT_PT_HSettings_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.selected_objects is not None and bpy.context.object.type == 'CURVE'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        Hgen_properties = context.scene.ND9H_HGen
        row.prop(Hgen_properties, "children")
        if bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED':
            row = layout.row()
            row.prop(Hgen_properties, "child_nbr")
            row = layout.row()
            row.prop(Hgen_properties, "child_length", slider=True) 
            row = layout.row()
            row.prop(Hgen_properties, "child_radius")            
            row = layout.row()
            row.prop(Hgen_properties, "child_roundness", slider=True)
            
class children_kink_settings_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Kink"
    bl_idname = "OBJECT_PT_HChildren_Kink_Panel"
    bl_parent_id = "OBJECT_PT_HChildren_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    default = "CLOSED"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED'
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        Hgen_properties = context.scene.ND9H_HGen
        
        row = layout.row()
        row.prop(Hgen_properties, "children_kink")
        if bpy.context.scene.ND9H_HGen.children_kink == 'NO':
            print('kink_off')
        else:
            row = layout.row()
            row.prop(Hgen_properties, "children_amplitude")
            row = layout.row()
            row.prop(Hgen_properties, "children_frequency") 
            row = layout.row()
            row.prop(Hgen_properties, "children_shape")
                    
class children_clumping_settings_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Clumpimg"
    bl_idname = "OBJECT_PT_HChildren_Clumping_Panel"
    bl_parent_id = "OBJECT_PT_HChildren_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    default = "CLOSED"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED'
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        Hgen_properties = context.scene.ND9H_HGen
        if bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED':
            row = layout.row()
            row.prop(Hgen_properties, "children_clump_factor", slider=True)
            row = layout.row()
            row.prop(Hgen_properties, "clump_shape", slider=True)
            row = layout.row()
            row.prop(Hgen_properties, "twist")  
            
class children_roughness_settings_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Roughness"
    bl_idname = "OBJECT_PT_HChildren_Roughness_Panel"
    bl_parent_id = "OBJECT_PT_HChildren_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    default = "CLOSED"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED'
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        Hgen_properties = context.scene.ND9H_HGen
        if bpy.context.scene.ND9H_HGen.children == 'SIMPLE' or bpy.context.scene.ND9H_HGen.children == 'INTERPOLATED':
            row = layout.row()
            row.prop(Hgen_properties, "roughness_1")
            row = layout.row()
            row.prop(Hgen_properties, "roughness_1_size")
            row = layout.row()
            row.prop(Hgen_properties, "roughness_endpoint") 
            row = layout.row()
            row.prop(Hgen_properties, "roughness_end_shape") 
            row = layout.row()
            row.prop(Hgen_properties, "roughness_2") 
            row = layout.row()
            row.prop(Hgen_properties, "roughness_2_size") 
            row = layout.row()
            row.prop(Hgen_properties, "roughness_2_threshold") 
            
class info_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Info"
    bl_idname = "OBJECT_PT_Info"
    bl_parent_id = "OBJECT_PT_hgen_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "ND9H tools"
    bl_category = "ND9H tools"
    default = "CLOSED"
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.label(text="H-Gen basic |") 
        row.label(text="ver: 2020.8") 
        row = layout.row()
        row.label(text="author: ND9H |")  
        row.label(text="nd9h001@gmail.com") 
        row = layout.row()
        row.operator("nd9h.paypal_donate",icon="FUND")
        row = layout.row()
        row.operator("nd9h.discord_support_server",icon = "USER")
        row = layout.row()
        row.operator("nd9h.documentation",icon = "HELP")    
                                                                                                               
def active_object_get():
    active_object = bpy.context.view_layer.objects.active
    return (active_object)

def obj_array_for_boolean_get():
    obj_array=[]
    selected_obj = bpy.context.selected_objects
    scene = bpy.context.scene
    active_object = bpy.context.view_layer.objects.active
    for obj in selected_obj:
        obj_array.append(obj.name)
    obj_array.remove(active_object.name)
    print (obj_array)
    return(obj_array)

#hair_Settongs
def particle_number(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].count = bpy.context.scene.ND9H_HGen.number
        
def childen_type(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].child_type = bpy.context.scene.ND9H_HGen.children
        
def children_child_length(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].child_length = bpy.context.scene.ND9H_HGen.child_length
        
def children_child_radius(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].child_radius = bpy.context.scene.ND9H_HGen.child_radius
        
def children_child_roundness(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].child_roundness = bpy.context.scene.ND9H_HGen.child_roundness

def childen_kink_type(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].kink = bpy.context.scene.ND9H_HGen.children_kink

def childen_kink_amplitude(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].kink_amplitude = bpy.context.scene.ND9H_HGen.children_amplitude
        
def childen_kink_frequency(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].kink_frequency = bpy.context.scene.ND9H_HGen.children_frequency
        
def childen_kink_shape(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].kink_shape = bpy.context.scene.ND9H_HGen.children_shape
        
def children_clump(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].clump_factor = bpy.context.scene.ND9H_HGen.children_clump_factor

def children_clump_shape(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].clump_shape = bpy.context.scene.ND9H_HGen.clump_shape

def children_twist(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].twist = bpy.context.scene.ND9H_HGen.twist
        
#roughness        
def children_roughness_1(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_1 = bpy.context.scene.ND9H_HGen.roughness_1
        
def children_roughness_1_size(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_1_size = bpy.context.scene.ND9H_HGen.roughness_1_size
        
def children_roughness_endpoint(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_endpoint = bpy.context.scene.ND9H_HGen.roughness_endpoint  
              
def children_roughness_end_shape(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_end_shape = bpy.context.scene.ND9H_HGen.roughness_end_shape
        
def children_roughness_2(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_2 = bpy.context.scene.ND9H_HGen.roughness_2
        
def children_roughness_2_size(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_2_size = bpy.context.scene.ND9H_HGen.roughness_2_size
        
def children_roughness_2_threshold(self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].roughness_2_threshold = bpy.context.scene.ND9H_HGen.roughness_2_threshold
        
def hair_display_type(self,context):
    if bpy.context.scene.ND9H_HGen.display_type == 'STRAND':
        bpy.context.scene.render.hair_type = 'STRAND'
    if bpy.context.scene.ND9H_HGen.display_type == 'STRIP':
        bpy.context.scene.render.hair_type = 'STRIP'
        
def children_child_nbr (self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].child_nbr = bpy.context.scene.ND9H_HGen.child_nbr
        bpy.data.particles[obj.name].rendered_child_count = bpy.context.scene.ND9H_HGen.child_nbr

def guide_clump_amount_update (self,context):
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.objects[obj.name].field.guide_clump_amount = bpy.context.scene.ND9H_HGen.guide_clump_amount
        #bpy.context.object.field.guide_clump_amount = bpy.context.scene.ND9H_HGen.guide_clump_amount
        
def guide_clump_shape_update (self,context): 
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.objects["_HG.018"].field.guide_clump_shape = bpy.context.scene.ND9H_HGen.guide_clump_shape
        bpy.context.object.field.guide_clump_shape = bpy.context.scene.ND9H_HGen.guide_clump_shape
        
def display_step_update(self,context): 
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].display_step = bpy.context.scene.ND9H_HGen.display_step

def root_radius_update(self,context): 
    selected_objs = bpy.context.selected_objects
    for obj in selected_objs:
        bpy.data.particles[obj.name].root_radius = bpy.context.scene.ND9H_HGen.guide_root_radius


#this function is kinda buggy because of blender bugs
def you_made_an_oopsie_droopsie_no_target_hahaaaa(self, context):
    self.layout.label(text="Please lock on target first")
def you_made_an_oopsie_droopsie_lolllll(self, context):
    self.layout.label(text="Material does not exist in target object")
    
def hair_material_update(self,context): 
    #bpy.data.particles["_HG"].material_slot = 'Material.001'
    target = bpy.context.scene.ND9H_HGen.target_mesh
    if target is not None:
        bpy.context.view_layer.objects.active=bpy.data.objects[target.name]
        targets_mat= target.material_slots.keys() #list material of target object
        selected_objs = bpy.context.selected_objects
        if bpy.context.scene.ND9H_HGen.hair_mat.name in targets_mat:
            for obj in selected_objs:
                try:
                    bpy.data.particles[obj.name].material_slot = bpy.context.scene.ND9H_HGen.hair_mat.name
                except:
                    pass
        if bpy.context.scene.ND9H_HGen.hair_mat.name not in targets_mat:
            bpy.context.window_manager.popup_menu(you_made_an_oopsie_droopsie_lolllll, title="Error", icon='ERROR')
    else:
        bpy.context.window_manager.popup_menu(you_made_an_oopsie_droopsie_no_target_hahaaaa, title="Error", icon='ERROR')
        
#=========================================================================================  
                                          
def my_handler(scene):
    active_object = bpy.context.view_layer.objects.active
    selected_objs = bpy.context.selected_objects
    target = bpy.context.scene.ND9H_HGen.target_mesh 
    if len(selected_objs) ==1:
        bpy.context.scene.ND9H_HGen.number =bpy.data.particles[active_object.name].count        
        bpy.context.scene.ND9H_HGen.children =bpy.data.particles[active_object.name].child_type 
        bpy.context.scene.ND9H_HGen.child_length =bpy.data.particles[active_object.name].child_length 
        bpy.context.scene.ND9H_HGen.child_radius =bpy.data.particles[active_object.name].child_radius 
        bpy.context.scene.ND9H_HGen.child_roundness =bpy.data.particles[active_object.name].child_roundness
        bpy.context.scene.ND9H_HGen.children_kink =bpy.data.particles[active_object.name].kink
        bpy.context.scene.ND9H_HGen.children_amplitude =bpy.data.particles[active_object.name].kink_amplitude 
        bpy.context.scene.ND9H_HGen.children_frequency =bpy.data.particles[active_object.name].kink_frequency
        bpy.context.scene.ND9H_HGen.children_shape =bpy.data.particles[active_object.name].kink_shape
        bpy.context.scene.ND9H_HGen.children_clump_factor =bpy.data.particles[active_object.name].clump_factor
        bpy.context.scene.ND9H_HGen.clump_shape =bpy.data.particles[active_object.name].clump_shape
        bpy.context.scene.ND9H_HGen.twist =bpy.data.particles[active_object.name].twist
        bpy.context.scene.ND9H_HGen.roughness_1 =bpy.data.particles[active_object.name].roughness_1
        bpy.context.scene.ND9H_HGen.roughness_1_size =bpy.data.particles[active_object.name].roughness_1_size
        bpy.context.scene.ND9H_HGen.roughness_endpoint =bpy.data.particles[active_object.name].roughness_endpoint        
        bpy.context.scene.ND9H_HGen.roughness_end_shape =bpy.data.particles[active_object.name].roughness_end_shape
        bpy.context.scene.ND9H_HGen.roughness_2 =bpy.data.particles[active_object.name].roughness_2
        bpy.context.scene.ND9H_HGen.roughness_2_size =bpy.data.particles[active_object.name].roughness_2_size
        bpy.context.scene.ND9H_HGen.roughness_2_threshold =bpy.data.particles[active_object.name].roughness_2_threshold
        bpy.context.scene.ND9H_HGen.child_nbr = bpy.data.particles[obj.name].child_nbr
        bpy.context.scene.ND9H_HGen.display_step = bpy.data.particles[obj.name].display_step
        bpy.context.scene.ND9H_HGen.guide_root_radius = bpy.data.particles[obj.name].root_radius
        bpy.context.scene.ND9H_HGen.hair_material.items = hair_material_list_update() 
        bpy.context.scene.ND9H_HGen.guide_root_radius = bpy.data.particles[active_object.name].root_radius
         
pre_handlers = bpy.app.handlers.depsgraph_update_pre
pre_handlers.append(my_handler) 
                                            
class draw_hair_guide(Operator):
    bl_idname = "nd9h.draw_hair_guide"
    bl_label = "draw guide"
    bl_description = "draw hair guide"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
              
        bpy.ops.view3d.snap_cursor_to_selected() 
        bpy.ops.object.gpencil_add(type='EMPTY') 
        bpy.ops.gpencil.layer_add()
        bpy.context.object.data.layers["GP_Layer"].info = "_HG"
        bpy.ops.gpencil.paintmode_toggle()
        gp_mat =bpy.data.materials.new(name="HG")
        bpy.data.materials.create_gpencil_data(gp_mat)
        gp_mat.grease_pencil.color = (1, 1, 0, 1)
        bpy.context.active_object.data.materials.append(gp_mat)
        

        return {'FINISHED'}
    
class generate_hair_from_guide(Operator):
    bl_idname = "nd9h.generate_hair"
    bl_label = "H Gen"
    bl_description = "generate hair follow the selected guide"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        selected_objs = bpy.context.selected_objects 
        try:
            return context.active_object.type == 'GPENCIL' and bpy.context.scene.ND9H_HGen.target_mesh is not None #and len(selected_objs) ==2
        except AttributeError:
            pass
        
    def execute(self, context):
        #get and save hair spawn target
        target = bpy.context.scene.ND9H_HGen.target_mesh
        
        
        bpy.data.objects[target.name].select_set(False)
        
        #G_pencil to curve
        bpy.ops.gpencil.convert(type='POLY', use_timing_data=True)

        #select converted curve object only
        selected_objs = bpy.context.selected_objects 
        for obj in selected_objs:
            bpy.context.view_layer.objects.active=bpy.data.objects[obj.name]
            if context.active_object.type == 'GPENCIL':
                bpy.context.object.hide_viewport = True #hide GP object
                bpy.context.object.hide_render = True
                bpy.data.objects[obj.name].select_set(False)
            else:
                context.active_object.type == 'CURVE'
                bpy.context.view_layer.objects.active=bpy.data.objects[obj.name]
                bpy.data.objects[obj.name].select_set(True)
                
        #curve to mesh and seperate
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #move to new collection       
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="Hair Guide")
        
        #mesh to curve            
        bpy.ops.object.convert(target='CURVE')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.spline_type_set(type='BEZIER')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.curve.decimate(ratio=0.05)
        bpy.ops.transform.transform(mode='CURVE_SHRINKFATTEN', value=(0.333, 0, 0, 0))
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #add curve guide force          
        selected_obj = bpy.context.selected_objects      
        for obj in selected_obj: 
            bpy.ops.object.select_all(action='DESELECT')
            #bpy.data.objects[target.name].select_set(False)
            #self.report({'INFO'}, obj.name)  
            
            bpy.data.objects[obj.name].select_set(True)
            bpy.context.view_layer.objects.active=bpy.data.objects[obj.name]
        #create collection
            bpy.ops.collection.create(name=obj.name)
        #add forge
            bpy.ops.object.forcefield_toggle()
            bpy.context.object.field.type = 'GUIDE' 
            bpy.context.object.data.use_path = True
            bpy.context.object.field.guide_minimum = 0
        #create curve mesh
            bpy.context.object.data.bevel_depth = 0.01
            bpy.context.object.data.bevel_resolution = 0
            bpy.context.object.show_in_front = True
            bpy.ops.object.shade_smooth()
        #create and add yellow material
        
#            mat_vaild=False
#            for mat in bpy.data.objects[obj.name].material_slots.keys():
#                if mat != "Hair_Guide":
#                    mat_vaild = True
#                else:
#                    mat_vaild = False
#                    
#            if mat_vaild == True:
#                bpy.ops.object.material_slot_add()
#                obj.material_slots[0].material = bpy.data.materials['Hair_Guide']
#            else:  
#                mat=bpy.data.materials.new(name="Hair_Guide")
#                obj.data.materials.append(mat)
#                bpy.context.object.active_material.diffuse_color = (1, 1, 0,1)
#                bpy.context.object.active_material.use_nodes = False
                        
        #select hair spawn target
        bpy.data.objects[target.name].select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects[target.name]
        
        particles_sys_idx= len(bpy.data.objects[target.name].particle_systems.keys())
        for obj in selected_obj:
            active_obj = bpy.context.active_object
            active_obj.modifiers.new(obj.name, type='PARTICLE_SYSTEM')
            part = active_obj.particle_systems[particles_sys_idx] #####
            settings = part.settings
            settings.type ='HAIR'
            settings.effector_weights.collection = bpy.data.collections[obj.name]
            settings.use_advanced_hair = True
            settings.display_step = 5 
            settings.count = 100                  
            particles_sys_idx+=1
        return {'FINISHED'}
    
    
class optimize_guide(Operator):
    bl_idname = "nd9h.optimize_curve_guide"
    bl_label = "Optimize Guide"
    bl_description = "optimize guide curve"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.object.type == 'CURVE'
    
    def execute(self, context):
        decimate_ratio = bpy.context.scene.ND9H_HGen.decimate_ratio
        bpy.ops.curve.decimate(ratio=decimate_ratio)
        return{'FINISHED'}
       
class duplicate_guide(Operator):
    bl_idname = "nd9h.duplicate_curve_guide"
    bl_label = "Duplicate guide"
    bl_description = "duplicate hair guide and it's particles"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.object.type == 'CURVE' and bpy.context.scene.ND9H_HGen.target_mesh != None
    def execute(self, context): 
        count=0
        child_type = ''
        child_length = 0.0
        child_radius = 0.0
        child_roundness = 0.0
        kink  = ''
        kink_amplitude = 0.0
        kink_frequency  = 0.0
        kink_shape = ''
        clump_factor = 0.0
        clump_shape = 0.0
        twist = 0.0
        roughness_1 = 0.0
        roughness_1_size = 0.0
        roughness_endpoint = 0.0    
        roughness_end_shape = 0.0
        roughness_2 = 0.0
        roughness_2_size = 0.0
        roughness_2_threshold = 0.0
        child_nbr = 0
        
        selected_objs_before = bpy.context.selected_objects
        for obj in selected_objs_before:
            count = bpy.data.particles[obj.name].count
            child_type = bpy.data.particles[obj.name].child_type
            child_length = bpy.data.particles[obj.name].child_length
            child_radius = bpy.data.particles[obj.name].child_radius
            child_roundness = bpy.data.particles[obj.name].child_roundness
            kink  = bpy.data.particles[obj.name].kink
            kink_amplitude = bpy.data.particles[obj.name].kink_amplitude 
            kink_frequency  = bpy.data.particles[obj.name].kink_frequency
            kink_shape = bpy.data.particles[obj.name].kink_shape
            clump_factor = bpy.data.particles[obj.name].clump_factor
            clump_shape = bpy.data.particles[obj.name].clump_shape
            twist = bpy.data.particles[obj.name].twist
            roughness_1 = bpy.data.particles[obj.name].roughness_1
            roughness_1_size = bpy.data.particles[obj.name].roughness_1_size
            roughness_endpoint = bpy.data.particles[obj.name].roughness_endpoint      
            roughness_end_shape = bpy.data.particles[obj.name].roughness_end_shape
            roughness_2 = bpy.data.particles[obj.name].roughness_2
            roughness_2_size = bpy.data.particles[obj.name].roughness_2_size
            roughness_2_threshold = bpy.data.particles[obj.name].roughness_2_threshold
            child_nbr = bpy.data.particles[obj.name].child_nbr        
        
        bpy.ops.object.duplicate_move('INVOKE_DEFAULT')
        selected_objs = bpy.context.selected_objects
        target = bpy.context.scene.ND9H_HGen.target_mesh
        #create collection
        for obj in selected_objs:
            bpy.ops.object.select_all(action='DESELECT') 
            bpy.context.view_layer.objects.active=bpy.data.objects[obj.name]
            bpy.data.objects[obj.name].select_set(True)
            bpy.ops.collection.create(name=obj.name) #create collection
    
            target.modifiers.new(obj.name, type='PARTICLE_SYSTEM') #create new particles ???????????????
            
            target_particle_idx = bpy.data.objects[target.name].particle_systems.find(obj.name) #find duplicated object's particle system index
            bpy.data.objects[target.name].particle_systems.active_index = target_particle_idx
             
            part = target.particle_systems[target_particle_idx]
            settings = part.settings
            settings.type ='HAIR'
            settings.effector_weights.collection = bpy.data.collections[obj.name]
            settings.use_advanced_hair = True
            settings.display_step = 5 
            
            settings.count = count
            settings.child_type = child_type
            settings.child_length = child_length
            settings.child_radius = child_radius
            settings.child_roundness = child_roundness
            settings.kink = kink
            settings.kink_amplitude = kink_amplitude
            settings.kink_frequency = kink_frequency
            settings.kink_shape = kink_shape
            settings.clump_factor = clump_factor
            settings.clump_shape = clump_shape
            settings.twist = twist
            settings.roughness_1 = roughness_1
            settings.roughness_1_size = roughness_1_size
            settings.roughness_endpoint = roughness_endpoint
            settings.roughness_end_shape = roughness_end_shape
            settings.roughness_2 = roughness_2
            settings.roughness_2_size = roughness_2_size
            settings.roughness_2_threshold = roughness_2_threshold
            settings.child_nbr = child_nbr       
            
        return{'FINISHED'}    
    
class delete_guide(Operator):
    bl_idname = "nd9h.delete_curve_guide"
    bl_label = "Delete Guide"
    bl_description = "delete hair particles guide and it's particles"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.object.type == 'CURVE' and bpy.context.scene.ND9H_HGen.target_mesh != None

     
    def execute(self, context):
        selected_objs = bpy.context.selected_objects
        target = bpy.context.scene.ND9H_HGen.target_mesh
        for obj in selected_objs:
            bpy.ops.object.delete(use_global=False)
            
            bpy.context.view_layer.objects.active=bpy.data.objects[target.name]
            target_particle_idx = bpy.data.objects[target.name].particle_systems.find(obj.name)
            bpy.data.objects[target.name].particle_systems.active_index = target_particle_idx
            bpy.ops.object.particle_system_remove()
        return{'FINISHED'}
                
#class mesh_to_guide(Operator):
#    bl_idname = "nd9h.mesh_to_guide"
#    bl_label = "Mesh 2 Guide"
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None and context.active_object.type == 'MESH'
#    
#    def execute(self, context):
#        selected_objs = bpy.context.selected_objects
#        target = bpy.context.scene.ND9H_HGen.target_mesh
#        for obj in selected_objs:
#            bpy.ops.object.convert(target='CURVE')
#            bpy.ops.object.mode_set(mode='EDIT')
#            bpy.ops.curve.select_all(action='SELECT')
#            bpy.ops.curve.spline_type_set(type='BEZIER')
#            bpy.ops.curve.handle_type_set(type='AUTOMATIC')
#            bpy.ops.object.mode_set(mode='OBJECT')
#            bpy.ops.object.convert(target='GPENCIL')
#        return{'FINISHED'}
    
class create_hair_particles(Operator):
    bl_idname = "nd9h.create_hair"
    bl_label = "Create Hair"
    bl_description = "create hair particles"
    bl_options = {'REGISTER', 'UNDO'}
    
    number = bpy.props.IntProperty(name='number: ',default=50)
    
    @classmethod
    def poll(cls, context):
        target = bpy.context.scene.ND9H_HGen.target_mesh
        #target_parts = target.particle_systems.active
        return bpy.context.scene.ND9H_HGen.target_mesh is not None and target.particle_systems.active is None
    
    def execute(self, context):
        target = bpy.context.scene.ND9H_HGen.target_mesh
        #active_obj = bpy.context.active_object
        target.modifiers.new(target.name, type='PARTICLE_SYSTEM')
        part = target.particle_systems[0]
        settings = part.settings
        settings.type ='HAIR'
        settings.use_advanced_hair = True
        settings.display_step = 5 
        
        settings.count = self.number    
        return{'FINISHED'}
    
    def invoke (self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class particle_to_guide(Operator):
    bl_idname = "nd9h.particles_to_guide"
    bl_label = "P2G"
    bl_description = "convert active particle system to hair guide"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        target = bpy.context.scene.ND9H_HGen.target_mesh
        return target is not None and target.particle_systems.active is not None
    
    def execute(self, context):
        target = bpy.context.scene.ND9H_HGen.target_mesh
        target_mods = bpy.data.objects[target.name].modifiers.keys()
        active_particles = target.particle_systems.active.name
        try:
            #bpy.data.objects['hair_spawn'].modifiers["ParticleSettings.002"].particle_system.name

            if bpy.ops.object.modifier_convert(modifier=active_particles) == {'CANCELLED'}:
                #FIX MODIFIER NAME BUG wrong modifier name will causing convert modifier canceled
                for modi_name in target_mods:
                    try:
                        print("")
                        print("==UNFIXED==")
                        print(modi_name)
                        print(bpy.data.objects[target.name].modifiers[modi_name].particle_system.name)
                        modi_particle_sys_name = bpy.data.objects[target.name].modifiers[modi_name].particle_system.name
                        bpy.context.object.modifiers[modi_name].name = modi_particle_sys_name
                        print("==FIXED==")
                        print(modi_name)
                        print(bpy.data.objects[target.name].modifiers[modi_particle_sys_name].particle_system.name)
                        print("")
                    except AttributeError:
                        pass
                    
            bpy.ops.object.modifier_convert(modifier=active_particles)     
            
            bpy.ops.object.convert(target='CURVE')
            bpy.ops.object.convert(target='GPENCIL')
            
            bpy.context.view_layer.objects.active=bpy.data.objects[target.name]
            bpy.data.objects[target.name].select_set(True)
            #bpy.ops.object.particle_system_remove()
            bpy.context.object.modifiers[active_particles].show_render = False
            bpy.context.object.modifiers[active_particles].show_viewport = False


        except RuntimeError:
            self.report({'ERROR'}, 'TARGET NOT FOUND')
        except AttributeError:
            self.report({'ERROR'}, 'LOCK ON TARGET FIRST')


        return{'FINISHED'}
 
class paypal_donate(Operator):
    bl_idname = "nd9h.paypal_donate"
    bl_label = "DONATE"
    bl_description = "buy me a cup of coffee <3"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        link = "https://www.paypal.com/paypalme/nd9h"
        webbrowser.open_new(link)
        return{'FINISHED'}
    
class discord_support_server(Operator):
    bl_idname = "nd9h.discord_support_server"
    bl_label = "SUPPORT chat server"
    bl_description = "a discord server for supporting users"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        link = "https://discord.gg/vFzHvJs"
        webbrowser.open_new(link)
        return{'FINISHED'}    
       
class documentation(Operator):
    bl_idname = "nd9h.documentation"
    bl_label = "Document"
    bl_description = "a basic guide"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        link = "https://docs.google.com/document/d/1GccbGKcODk7Phki1wR3tcTa10jndxKFX_o4uVIeqFCc/edit?usp=sharing"
        webbrowser.open_new(link)
        return{'FINISHED'}               
#--------------------------------addon-properties
hair_children_type = [
    ("NONE", "None", "", 1),
    ("SIMPLE", "Simple", "", 2),
    ("INTERPOLATED", "interpolated", "", 3)
]
hair_kink_type = [
    ("SPIRAL", "Spiral", "", 1),
    ("BRAID", "Braid", "", 2),
    ("WAVE", "Wave", "", 3),
    ("RADIAL", "radial", "", 4),
    ("CURL", "curl", "", 5),
    ("NO", "nothing", "", 6)
]
hair_display_type_items=  [
    ("STRAND", "strand", "", 1),
    ("STRIP", "strip", "", 2),
]

class ND9H_Hgen_properties(PropertyGroup):
    
    display_step = IntProperty (
        name="Resolution",
        description="strand steps",
        default= 5, 
        min = 0,
        update = display_step_update
    )
        
    display_type = EnumProperty(
        items =hair_display_type_items, 
        name="display", 
        description="", 
        default='STRAND', 
        update=hair_display_type
    )
        
    decimate_ratio = FloatProperty (
        name="Ratio",
        description="",
        default= 0.5,
        min = 0.0,
        max = 1.0, 
        update = None
    )  
            
    number = IntProperty (
        name="Emission Number",
        description="hair particle number",
        default= 10, 
        min = 0,
        update = particle_number
    )
        
    child_nbr = IntProperty (
        name="Children Number",
        description="Children hair particle number",
        default= 10, 
        min = 0,
        update = children_child_nbr
    )
        
    target_mesh: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target"
    )
        
    children = EnumProperty(
        items =hair_children_type, 
        name="child", 
        description="", 
        default=None, 
        update=childen_type
    )
    
    child_length = FloatProperty (
        name="Length",
        description="",
        default= 1.0,
        min = 0.0,
        max = 1.0, 
        update = children_child_length
    )   
         
    child_radius = FloatProperty (
        name="Radius",
        description="",
        default= 0.2,
        min = 0.0,
        max = 10.0, 
        update = children_child_radius
    )  
        
    child_roundness = FloatProperty (
        name="Roundness",
        description="",
        default= 0.0,
        min = 0.0,
        max = 1.0, 
        update = children_child_roundness
    )
                      
    children_kink = EnumProperty(
        items =hair_kink_type, 
        name="kink", 
        description="", 
        default=None, 
        update=childen_kink_type
    )
    
    children_amplitude = FloatProperty (
        name="Amplitude",
        description="",
        default= 0.0, 
        update = childen_kink_amplitude
    )
        
    children_frequency = FloatProperty (
        name="Frequency",
        description="",
        default= 0.0, 
        update = childen_kink_frequency
    )
        
    children_shape = FloatProperty (
        name="Shape",
        description="",
        default= 0.0, 
        update = childen_kink_shape
    )
        
    children_clump_factor = FloatProperty (
        name="Clump",
        description="",
        default= 0.0,
        min = -1.0,
        max = 1.0, 
        update = children_clump
    )
        
    clump_shape = FloatProperty (
        name="Shape",
        description="",
        default= 0.0,
        min = -1.0,
        max = 1.0, 
        update = children_clump_shape
    )
        
    twist = FloatProperty (
        name="Twist",
        description="",
        default= 0.0,
        min = -10.0,
        max = 10.0, 
        update = children_twist
    )
        
    roughness_1 = FloatProperty (
        name="Uniform",
        description="",
        default= 0.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_1
    )
        
    roughness_1_size = FloatProperty (
        name="Size",
        description="",
        default= 1.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_1_size
    )
        
    roughness_endpoint = FloatProperty (
        name="Endpoint",
        description="",
        default= 0.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_endpoint
    )
        
    roughness_end_shape = FloatProperty (
        name="Shape",
        description="",
        default= 0.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_end_shape
    )

    roughness_2 = FloatProperty (
        name="Random",
        description="",
        default= 0.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_2
    )
    roughness_2_size = FloatProperty (
        name="Size",
        description="",
        default= 0.0,
        min = 0.0,
        max = 10.0, 
        update = children_roughness_2_size
    ) 
            
    roughness_2_threshold = FloatProperty (
        name="Threshold",
        description="",
        default= 0.0,
        min = 0.0,
        max = 1.0, 
        update = children_roughness_2_threshold
    )
        
    guide_clump_amount = FloatProperty (
        name="Clump",
        description="Overall clump",
        default= 0.0,
        min = -1.0,
        max = 1.0, 
        update = guide_clump_amount_update
    )      
          
    guide_clump_shape = FloatProperty (
        name="Shape",
        description="Overall clump shape",
        default= 0.0,
        min = -1.0,
        max = 1.0, 
        update = guide_clump_shape_update
    )       
         
    guide_root_radius = FloatProperty (
        name="root radius",
        description="strip root radius",
        default= 0.005,
        min = 0.0,
        max = 10.0, 
        update = root_radius_update
    ) 
        
    hair_mat: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Material",
        update=hair_material_update
    )
                                                    
addon_classes=[
H_Gen_Panel,
guide_operator_panel,
draw_guide_panel,
draw_hair_guide,
generate_hair_from_guide,
hair_settings_panel,
ND9H_Hgen_properties,
children_settings_panel,
children_kink_settings_panel,
children_clumping_settings_panel,
children_roughness_settings_panel,
optimize_guide,
duplicate_guide,
delete_guide,
#mesh_to_guide,
create_hair_particles,
particle_to_guide,
info_panel,
paypal_donate,
discord_support_server,
documentation
]

def register():
    for clss in addon_classes:
        bpy.utils.register_class(clss)
    #reg properties
    bpy.types.Scene.ND9H_HGen = bpy.props.PointerProperty(type=ND9H_Hgen_properties) 
    
def unregister():
    for clss in addon_classes:
        bpy.utils.unregister_class(clss)
    #del properties
    del bpy.types.Scene.ND9H_HGen
    
if __name__ == "__main__":
    register()
