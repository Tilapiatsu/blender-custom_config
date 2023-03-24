import bpy
from bpy.props import BoolProperty, IntVectorProperty
from . common import isFamily, findLightGrp, getLightMesh, family, refreshMaterials

class SelectionOperator(bpy.types.Operator):
    """ Custom selection """
    bl_idname = "view3d.select_custom" 
    bl_label = "Custom selection"
    bl_options = {"UNDO", "UNDO_GROUPED"}

    extend: BoolProperty(default = False)
    deselect: BoolProperty(default = False)
    toggle: BoolProperty(default = False)
    center: BoolProperty(default = False)
    enumerate: BoolProperty(default = False)
    object: BoolProperty(default = False)
    location: IntVectorProperty(default = (0,0),subtype ='XYZ', size = 2)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'
    
    def execute(self, context):
        #deactivate=False
        #if context.active_object:
        #    obname = context.active_object.name
        #    deactivate = obname.startswith('BLS_CONTROLLER.') or obname.startswith('BLS_LIGHT_MESH.')
            
        #result = bpy.ops.view3d.select(extend=self.extend, deselect=self.deselect, toggle=self.toggle, center=self.center, enumerate=self.enumerate, object=self.object)
        result = bpy.ops.view3d.select(extend=self.extend, deselect=self.deselect, toggle=self.toggle, center=self.center, enumerate=self.enumerate, object=self.object, location=(self.location[0], self.location[1]))
        if 'FINISHED' not in result:
            return {'PASS_THROUGH'}
        if context.active_object:
            obname = context.active_object.name
            if obname.startswith('BLS_CONTROLLER.'):
                lm = getLightMesh()
                if lm:
                    lm.select = True
                
            #if deactivate or obname.startswith('BLS_CONTROLLER.') or obname.startswith('BLS_LIGHT_MESH.'):
            #    refreshMaterials()
                    
            context.scene.frame_current = context.scene.frame_current
            refreshMaterials()
        
        if context.user_preferences.inputs.select_mouse == 'RIGHT':
            return {'FINISHED'}
        elif self.toggle:
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.location[0] = event.mouse_region_x
        self.location[1] = event.mouse_region_y
        return self.execute(context)

addon_keymaps = []
addin_kmis = []
def add_shortkeys():
    def prepKmi(kmi):
        kmi.properties.toggle = False
        kmi.properties.center = False
        kmi.properties.object = False
        kmi.properties.enumerate = False
        kmi.properties.extend = False
        kmi.properties.deselect = False
        
    wm = bpy.context.window_manager
    addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    prepKmi(addon_kmi)
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.shift = True
    prepKmi(addon_kmi)
    addon_kmi.properties.toggle = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.ctrl = True
    prepKmi(addon_kmi)
    addon_kmi.properties.center = True
    addon_kmi.properties.object = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.alt = True
    addon_kmi.properties.enumerate = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.shift = True
    addon_kmi.ctrl = True
    prepKmi(addon_kmi)
    addon_kmi.properties.center = True
    addon_kmi.properties.extend = True
    addon_kmi.properties.toggle = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.ctrl = True
    addon_kmi.alt = True
    prepKmi(addon_kmi)
    addon_kmi.properties.center = True
    addon_kmi.properties.enumerate = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.shift = True
    addon_kmi.alt = True
    prepKmi(addon_kmi)
    addon_kmi.properties.enumerate = True
    addon_kmi.properties.toggle = True
    addin_kmis.append(addon_kmi)
    
    addon_kmi = addon_km.keymap_items.new(SelectionOperator.bl_idname, 'SELECTMOUSE', 'PRESS')
    addon_kmi.shift = True
    addon_kmi.ctrl = True
    addon_kmi.alt = True
    prepKmi(addon_kmi)
    addon_kmi.properties.center = True
    addon_kmi.properties.enumerate = True
    addon_kmi.properties.toggle = True
    addin_kmis.append(addon_kmi)
    
    addon_keymaps.append(addon_km)
    
def remove_shortkeys():        
    for km in addon_keymaps:
        for kmi in addin_kmis:
            km.keymap_items.remove(kmi)
            
    addon_keymaps.clear()
    addin_kmis.clear()