bl_info = {
    "name": "B_GEN Hair System",
    "author": "Munorr",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > N",
    "description": "Control parameters from B_GEN geometry node hair system",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.types import Operator
from bpy.utils import register_class
from bpy.utils import unregister_class
    
    
# [Get node name]
# ============================================================
bgenType1 = "B-GEN_v4"
bgenType2 = "B-GEN_[Braids]_v4"

nodeID_1 = "ID:B-GEN_0001"
nodeID_2 = "ID:B-GEN_0002"
nodeID_3 = "ID:B-GEN_VtoS_0001"

def get_gNode(obj):
    #obj = bpy.context.active_object
    modName = ""
    nodeTreeName = "<NA base>"
    node_ID = ""
    if obj.modifiers:
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group:
                a = obj.modifiers.get(modifier.name)
                b = obj.modifiers.get(modifier.name).node_group.name
                c = obj.modifiers.get(modifier.name).node_group
                #modName = a
                #nodeTreeName = b
                if c:
                    for node in c.nodes:
                        if node.name == "ID:B-GEN_0001":
                            #print("Node present" , c.name)
                            modName = a
                            nodeTreeName = c.name
                            node_ID = "ID:B-GEN_0001"
                            break
                        elif node.name == "ID:B-GEN_0002":
                            #print("Node present" , c.name)
                            modName = a
                            nodeTreeName = c.name
                            node_ID = "ID:B-GEN_0002"
                            break
                
                #else:
                    #print("Node Absent")
                    #modName = a
                    #nodeTreeName = "<NA>"
            #else:
            #   print("Modifiers but No Node modifiers")
    #else:
            #print("No Node modifiers")
                    
            
            
            
            
    return modName, nodeTreeName, node_ID


def get_gNode_2(obj):
    #obj = bpy.context.active_object
    modName = ""
    nodeTreeName = "<NA>"
    node_ID = ""
    if obj.modifiers:
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group:
                a = obj.modifiers.get(modifier.name).node_group
                #modName = a
                #nodeTreeName = b
                if a:
                    for node in a.nodes:
                        if node.name == "ID:B-GEN_VtoS_0001":
                            #print("Node present" , c.name)
                            modName = a
                            nodeTreeName = a.name
                            node_ID = "ID:B-GEN_VtoS_0001"
                            break

    return modName, nodeTreeName, node_ID

'''
            if node_ID in sNodeGroup.name:
                modName = a
                nodeTreeName = b
            
            if b == bgenType1 or b == bgenType2:
                modName = a
                nodeTreeName = b
                
    return modName, nodeTreeName '''

#a_obj = bpy.context.active_object
#get_gNode(a_obj)
#print(get_gNode_2(a_obj))


#'''
# [Addon display]
# ============================================================

class B_GEN_HAIR(bpy.types.Panel):
    
    bl_label = "B-GEN"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
        
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        
        try:
            #lpSwitch = bpy.data.node_groups[bgenModName].nodes["Low Poly Switch"]
            lpSwitch = bpy.data.node_groups[bgenModName].nodes["lowPoly"].inputs[1]
            node = bpy.data.node_groups[bgenModName].nodes["lowPoly"]
            
            layout = self.layout                
            col = layout.column()
            box = col.box()
            box1 = box.box()
            box1.scale_y = 1.4
            box1.label(text = "Mod Type: [" + bgenModName + "]")
            
            #box = box.box()
            col = box.column()
            row1 = col.row()
            row1.scale_y = 1.4
            
            
            lpSwitch.draw(context, row1, node, text = 'Low Poly') 
        except:
            pass      
               
# [INITIALIZE]
# ============================================================        
class INITIALIZE(bpy.types.Panel):
    bl_label = "INITIALIZE"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1:       
            matCntr = bpy.data.node_groups[bgenModName].nodes["ID:MC_001"].inputs[0]
            node = bpy.data.node_groups[bgenModName].nodes["ID:MC_001"]
            # [INITIALIZE] 
            #col.label(text = "INITIALIZE")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            
            col_ = col1.column()
            col_.scale_y = 1.2
            col_.prop(bgenMod, '["Input_26"]', text = 'Vertex Stip')
            
            
            matCntr.draw(context, col1, node, text = 'Material')
            
            row1 = col1.row()
            row1.label(text = "Mesh Subdiv:")
            row1.prop(bgenMod, '["Input_22"]', text = '')
            
            row1 = col1.row()
            row1.label(text = "Seed:")
            row1.prop(bgenMod, '["Input_17"]', text = '')
            #col1.prop(bgenMod, '["Input_39"]', text = '')
                 
            box1 = col.box()
            box1.scale_y = 1.2
            col2 = box1.column(align = True, heading = "Attach To:")
            col2.prop(bgenMod, '["Input_30"]', text = '')
            col2.prop(bgenMod, '["Input_31"]', text = 'Start Size')
            
            
        elif bgenNodeID == nodeID_2:
            matCntr = bpy.data.node_groups[bgenModName].nodes["ID:MC_002"].inputs[0]
            node = bpy.data.node_groups[bgenModName].nodes["ID:MC_002"]
            # [INITIALIZE] 
            #col.label(text = "INITIALIZE")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_11"]', text = 'Curve')
            col1.prop(bgenMod, '["Input_19"]', text = 'Reverse Curve')
            matCntr.draw(context, col1, node, text = 'Material')
            
            box1 = col.box()
            box1.scale_y = 1.2
            col1 = box1.column(align = True, heading = "Attach To:")
            col1.prop(bgenMod, '["Input_30"]', text = '')
            col1.prop(bgenMod, '["Input_31"]', text = 'Start Size')
            
            #col1.prop(bgenMod, '["Input_30"]', text = 'Attach To')
            #col1.prop(bgenMod, '["Input_31"]', text = 'Start Size')

'''        
# [STRAND CONTROL]
# ============================================================        
class STRAND_CONTROL(bpy.types.Panel):
    bl_label = "STRAND CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()        
        
        if bgenNodeID == nodeID_1:
            # [STARND CONTROL] 
            col.label(text = "STRAND CONTROL")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_30"]', text = 'Attach To')
            col1.prop(bgenMod, '["Input_31"]', text = 'Start Size')
            col1.prop(bgenMod, '["Input_17"]', text = 'Seed')
            
        elif bgenNodeID == nodeID_2:
            # [STARND CONTROL] 
            col.label(text = "STRAND CONTROL")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            
            col1.label(text = "Hair Radius")
            col1.prop(bgenMod, '["Input_14"]', text = 'Root')
            col1.prop(bgenMod, '["Input_15"]', text = 'Tip')
            col1.label(text = "Hair Strand")
            col1.prop(bgenMod, '["Input_6"]', text = 'Hair Resolution')
            col1.prop(bgenMod, '["Input_7"]', text = 'Amount')
            col1.prop(bgenMod, '["Input_40"]', text = 'Length Variation')
'''        
        
# [HAIR CONTROL]
# ============================================================        
class HAIR_CONTROL(bpy.types.Panel):
    bl_label = "HAIR CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()
      
        if bgenNodeID == nodeID_1: 
            # [HAIR CONTROL] 
            col.label(text = "HAIR CONTROL")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.label(text = "Hair Radius")
            col1.prop(bgenMod, '["Input_13"]', text = 'Root')
            col1.prop(bgenMod, '["Input_14"]', text = 'Tip')
            col1.prop(bgenMod, '["Input_32"]', text = 'Length Variation')
            col1.label(text = "Strand Amount")
            col1.prop(bgenMod, '["Input_4"]', text = 'Amount')
            col1.prop(bgenMod, '["Input_12"]', text = 'Hair Children')
            col1.label(text = "Strand Resolution")
            col1.prop(bgenMod, '["Input_11"]', text = 'Point Count')
            col1.prop(bgenMod, '["Input_27"]', text = 'Hair Resolution')      
        
        elif bgenNodeID == nodeID_2:
            # [HAIR CONTROL] 
            col.label(text = "STRAND CONTROL")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            
            col1.label(text = "Hair Radius")
            col1.prop(bgenMod, '["Input_14"]', text = 'Root')
            col1.prop(bgenMod, '["Input_15"]', text = 'Tip')
            col1.label(text = "Hair Strand")
            col1.prop(bgenMod, '["Input_7"]', text = 'Amount')
            col1.prop(bgenMod, '["Input_6"]', text = 'Resolution')
            col1.prop(bgenMod, '["Input_40"]', text = 'Length Variation')  
        

# [DISPLACEMENT CONTROL]
# ============================================================        
class DISPLACEMENT_CONTROL(bpy.types.Panel):
    bl_label = "DISPLACEMENT CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        #floatCurve = bpy.data.node_groups["Hair Displacement (v3)"].nodes['Float Curve']
        #floatCurve = bpy.data.node_groups[bgenModName].nodes['Clump Profile']
        
        layout = self.layout                
        col = layout.column()
      
        if bgenNodeID == nodeID_1:
            # [DISPLACEMENT CONTROL]
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Clump Profile'] 
            col.label(text = "DISPLACEMENT")
            box = col.box()
            col1 = box.column()
            row1 = col1.row()
            col1.scale_y = 1.5
            
            row1.prop(bgenMod, '["Input_21"]', text = 'Flat hair')
            row1.prop(bgenMod, '["Input_47"]', text = 'Tilt')
            col1.prop(bgenMod, '["Input_46"]', text = 'Normal Tilt')
            col1.label(text = "DISPLACEMENT")
            
            col1.prop(bgenMod, '["Input_7"]', text = 'X')
            col1.prop(bgenMod, '["Input_24"]', text = 'Y')
            col1.prop(bgenMod, '["Input_28"]', text = 'Z')
            
            #col1 = box.column()
            #col1.scale_y = 1.5
            col1.prop(bgenMod, '["Input_8"]', text = 'Hair Children')
            #col1.label(text = "CLUMP SCALE")
            

            box = col.box()
            col1 = box.column()
            
            # ========== Drop Down (5) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp5",
            icon="TRIA_DOWN" if obj.my_exp5 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Clump Profile")
            if obj.my_exp5:
                floatCurve.draw_buttons_ext(context, col1)
            
            
            
        elif bgenNodeID == nodeID_2:
            # [HAIR CONTROL] 
            col.label(text = "<Not Applicable>")                         
        
# [NOISE CONTROL]
# ============================================================        
class NOISE_CONTROL(bpy.types.Panel):
    bl_label = "NOISE CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]

        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1:
            # [NOISE CONTROL] 
            col.label(text = "NOISE")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_9"]', text = 'Amplitude')
            col1.prop(bgenMod, '["Input_29"]', text = 'Radius')
            col1.label(text = "Fly Away Hairs:")
            col1.prop(bgenMod, '["Input_18"]', text = 'Amount')
            col1.prop(bgenMod, '["Input_19"]', text = 'Displacement')
            col1.prop(bgenMod, '["Input_49"]', text = 'Length')
            col1.prop(bgenMod, '["Input_48"]', text = 'Seed')
        elif bgenNodeID == nodeID_2:
            # [HAIR CONTROL] 
            col.label(text = "<Not Applicable>")
        
        
# [CURL CONTROL]
# ============================================================        
class CURL_CONTROL(bpy.types.Panel):
    bl_label = "CURL CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        #floatCurve = bpy.data.node_groups["Hair Curl (v3)"].nodes['curlProfile']
        #floatCurve = bpy.data.node_groups[bgenModName].nodes['Curl Profile']
        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1:
            # [CURL CONTROL] 
            #col.label(text = "CURL")
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Curl Profile']
            box = col.box()
            col1 = box.column(heading = "Curl")
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_20"]', text = 'Path')
            col1.prop(bgenMod, '["Input_16"]', text = 'Amplitude')
            col1.prop(bgenMod, '["Input_10"]', text = 'Radius')
            
            
            #col.separator()
            col = col.column()
            box = col.box()
            col1 = box.column()
            
            # ========== Drop Down (3) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp3",
            icon="TRIA_DOWN" if obj.my_exp3 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Curl Profile")
            if obj.my_exp3:
                floatCurve.draw_buttons_ext(context, col1)
            
        elif bgenNodeID == nodeID_2:
            # [CURL CONTROL] 
            #col.label(text = "CURL")
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Curl Profile']
            box = col.box()
            col1 = box.column(heading = "Curl")
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_23"]', text = 'Path')
            col1.prop(bgenMod, '["Input_24"]', text = 'Amplitude')
            col1.prop(bgenMod, '["Input_25"]', text = 'Radius')
            
            #col.separator()
            col = col.column()
            box = col.box()
            col1 = box.column()
            
            # ========== Drop Down (3) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp3",
            icon="TRIA_DOWN" if obj.my_exp3 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Curl Profile")
            if obj.my_exp3:
                floatCurve.draw_buttons_ext(context, col1)
        
        
class BRAID_CONTROL(bpy.types.Panel):
    bl_label = "BRAID CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        #floatCurve = bpy.data.node_groups["Braid_Shape (v3)"].nodes['Braid Profile']
        
        layout = self.layout                
        col = layout.column()
        col.scale_y = 1
        
        if bgenNodeID == nodeID_1:
            # [BRAID CONTROL] 
            col.label(text = "<Not Applicable>")
            
        elif bgenNodeID == nodeID_2:
            # [BRAID CONTROL] 
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Braid Profile']
            col.label(text = "BRAID CONTROL")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.label(text = "Braid Knot")
            col1.prop(bgenMod, '["Input_4"]', text = 'Frequency')
            col1.prop(bgenMod, '["Input_16"]', text = 'Rotation')
            col1.prop(bgenMod, '["Input_9"]', text = 'Width')
            col1.label(text = "Braid Displacement")
            col1.prop(bgenMod, '["Input_8"]', text = 'Strand Disp')
            col1.prop(bgenMod, '["Input_18"]', text = 'Clump Disp')
            
            #col.label(text = "BRAID PROFILE")
            #col.separator()
            box = col.box()
            col1 = box.column()
            
            # ========== Drop Down (4) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp4",
            icon="TRIA_DOWN" if obj.my_exp4 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Braid Profile")
            if obj.my_exp4:
                floatCurve.draw_buttons_ext(context, col1)
            
            #col.separator()
            box = col.box()
            col1 = box.column()
            #col1.label(text = "Braid Profile")
            col1.scale_y = 1.2
            
            col1.label(text = "Unravle Braid")
            col1.prop(bgenMod, '["Input_21"]', text = 'Top')
            col1.prop(bgenMod, '["Input_22"]', text = 'Bottom')
            col1.label(text = "Fly Away Hairs")
            col1.prop(bgenMod, '["Input_42"]', text = 'Amount')
            col1.prop(bgenMod, '["Input_41"]', text = 'Scale')
            
        
class HAIR_INTERPOLATION(bpy.types.Panel):
    bl_label = "HAIR INTERPOLATION"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1: 
            # [INTERPOLATION] 
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Interpulated Curve']
            col.label(text = "INTERPOLATION")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.label(text = "Extra Amount")
            col1.prop(bgenMod, '["Input_41"]', text = 'Amount')
            col1.label(text = "Displacement")
            col1.prop(bgenMod, '["Input_42"]', text = 'X')
            col1.prop(bgenMod, '["Input_43"]', text = 'Y')
            col1.prop(bgenMod, '["Input_44"]', text = 'Z')
            col1.label(text = "Variation")
            col1.prop(bgenMod, '["Input_45"]', text = 'Seed')
            
            col.separator()
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            
            # ========== Drop Down (2) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp2",
            icon="TRIA_DOWN" if obj.my_exp2 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Interpulation Profile")
            if obj.my_exp2:
                floatCurve.draw_buttons_ext(context, col1)
                
            
        elif bgenNodeID == nodeID_2:
            # [INTERPOLATION] 
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Interpulated Curve']
            col.label(text = "INTERPOLATION")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.label(text = "Extra Amount")
            col1.prop(bgenMod, '["Input_34"]', text = 'Amount')
            col1.label(text = "Displacement")
            col1.prop(bgenMod, '["Input_35"]', text = 'X')
            col1.prop(bgenMod, '["Input_36"]', text = 'Y')
            col1.prop(bgenMod, '["Input_37"]', text = 'Z')
            col1.label(text = "Variation")
            col1.prop(bgenMod, '["Input_38"]', text = 'Seed')
            col1.prop(bgenMod, '["Input_39"]', text = 'normal tilt')
            
            col.separator()
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            
            # ========== Drop Down (2) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp2",
            icon="TRIA_DOWN" if obj.my_exp2 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Interpulation Profile")
            if obj.my_exp2:
                floatCurve.draw_buttons_ext(context, col1)
        

class ROOT_CONTROL(bpy.types.Panel):
    bl_label = "ROOT CONTROL"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1:
            # [ROOT CONTROL] 
            col.label(text = "<Not Applicable>")
            
        elif bgenNodeID == nodeID_2:
            # [ROOT CONTROL] 
            col.label(text = "ROOT HAIR")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_44"]', text = 'Switch')
            col1.label(text = "Hair Strands")
            col1.prop(bgenMod, '["Input_45"]', text = 'Length')
            col1.prop(bgenMod, '["Input_46"]', text = 'Amount')
            col1.label(text = "Displacement")
            col1.prop(bgenMod, '["Input_47"]', text = 'X')
            col1.prop(bgenMod, '["Input_48"]', text = 'Y')
            col1.prop(bgenMod, '["Input_49"]', text = 'Z')
            
        
class SCALP_HAIR(bpy.types.Panel):
    bl_label = "SCALP HAIR"
    bl_parent_id = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode(obj)[0]
        bgenModName = get_gNode(obj)[1]
        bgenNodeID = get_gNode(obj)[2]
        
        layout = self.layout                
        col = layout.column()
        
        if bgenNodeID == nodeID_1:
            # [Scalp Hair] 
            col.label(text = "<Not Applicable>")
            
        elif bgenNodeID == nodeID_2:    
            # [SCALP HAIR] 
            col.label(text = "Scalp Hair")
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            col1.prop(bgenMod, '["Input_51"]', text = 'Switch')
            col1.prop(bgenMod, '["Input_52"]', text = 'Trim Root')
            col1.prop(bgenMod, '["Input_53"]', text = 'Trim Tip')
            col1.label(text = "Scalp Hair Control")
            col1.prop(bgenMod, '["Input_54"]', text = 'Spline Count')
            col1.prop(bgenMod, '["Input_55"]', text = 'Rotation')
            col1.prop(bgenMod, '["Input_56"]', text = 'Distance')
            col1.prop(bgenMod, '["Input_57"]', text = 'Length')
            col1.prop(bgenMod, '["Input_58"]', text = 'Amount')
            col1.label(text = "Displacement")
            col1.prop(bgenMod, '["Input_59"]', text = 'X')
            col1.prop(bgenMod, '["Input_60"]', text = 'Y')
            col1.prop(bgenMod, '["Input_61"]', text = 'Z')



# [Hair Sim]
# ============================================================
''' Currently empty button '''
class execOperator(bpy.types.Operator):
    bl_idname = "exec.operator"
    bl_label = "My Operator"
    def execute(self, context):
        print("Hello World!")
        return {'FINISHED'}
    
#'''
# [Properties]
# ============================================================
''' Adds all the collections to a list of collections'''

def collection_List():
    #try:
    opNum = 1
    coll_List = []
    colls = bpy.data.collections.keys()
    for obj in colls:
        #opVal = "OP" + str(opNum)
        #coll_List.append(opVal)
        coll_List.append(obj)
        coll_List.append(obj)
        coll_List.append("")
        opNum += 1
    
    coll_List_tup = [x for x in zip(*[iter(coll_List)]*3)]
    return(coll_List_tup)
    print("Collection list has been ran successfully")
    #except:
    #   pass

# [Properties]
# ============================================================

def cloth_Settings():
    #gName = bpy.context.scene.bgen_tools.my_enum
    #group_obj = bpy.context.collection[gName].objects   #use this with different concept
    try:
        gName = bpy.context.scene.bgen_tools.my_string1
        group_obj = bpy.data.collections[gName].objects 
        #collection name
        collection = bpy.data.collections.get(gName)
        collectionKeys = bpy.data.collections.keys()
        
        # Context Values
        quality_Val = bpy.context.scene.bgen_tools.my_int1
        mass_Val = bpy.context.scene.bgen_tools.my_float1
        gravity_Val = bpy.context.scene.bgen_tools.my_float2
        stifTension_Val = bpy.context.scene.bgen_tools.my_float3
        clsnColl = bpy.context.scene.bgen_tools.my_string2
        
        # Collection loop
        # ================================================== #
        '''
        # Test for Child Collections
        try:
            if collection:
                # Check if there are any child collections
                child_collections = [child for child in collection.children if isinstance(child, bpy.types.Collection)]
                if child_collections:
                    print("Collection '{}' has child collections:".format(collection_name))
                    for child in child_collections:
                        print(child.name)
                else:
                    print("Collection '{}' has no child collections.".format(collection_name))
            else:
                print("Collection '{}' not found.".format(collection_name))
            
        
        except:
            pass
        '''
        for obj in group_obj:
            
            if obj.modifiers['Cloth']:
                cloth_modifier = obj.modifiers["Cloth"]
                cs = cloth_modifier.settings
                cs.quality = quality_Val
                cs.mass = mass_Val
                cs.tension_stiffness = stifTension_Val
                cs.effector_weights.gravity = gravity_Val
    
                for clsn in collectionKeys:
                    if clsnColl != clsn:
                        pass
                    #if not clsnColl:
                    #   pass
                    
                    else:
                        cloth_modifier.collision_settings.collection = bpy.data.collections[clsnColl]
                
                # =========================== #
                # For loop delets all Vertex groups and adds them to a new one
                for vg in obj.vertex_groups:
                    obj.vertex_groups.remove(vg)
                new_vg = obj.vertex_groups.new(name="Group")
                
                cloth_modifier.settings.vertex_group_mass = "Group"  # Sets Pin group
                cloth_modifier.collision_settings.vertex_group_object_collisions = "Group" # Sets Collision group
                cloth_modifier.collision_settings.distance_min = 0.001
    except:
        pass
        print("No Valid cloth modifiers")
        
#print(collection_List)   
#collection_List() 
#'''



#'''    
# [Property_01]
# ============================================================
class bgenProperties(bpy.types.PropertyGroup):
    
    #my_exp1 : bpy.props.BoolProperty(default=True)
    
    my_string1 : bpy.props.StringProperty(name= "")
    my_string2 : bpy.props.StringProperty(name= "")
    
    my_int1 : bpy.props.IntProperty(name= "", soft_min= 0, soft_max= 20, default= (1))
    
    my_float1 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 20, default= (0.1))
    my_float2 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 1, default= (1))
    my_float3 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 50, default= (15))
    my_float4 : bpy.props.FloatProperty(name= "", soft_min= 0.01, soft_max= 1, default= (.02))
    
    my_float_vector : bpy.props.FloatVectorProperty(name= "", soft_min= 0, soft_max= 20, default= (1,1,1))

    my_enum : bpy.props.EnumProperty(
        name= "",
        description= "sample text",
        items= [])

#'''  

class bgenExpandProp(bpy.types.PropertyGroup):
    
    my_exp1 : bpy.props.BoolProperty(default=True)
    my_exp2 : bpy.props.BoolProperty(default=True)
    my_exp3 : bpy.props.BoolProperty(default=True)
    my_exp4 : bpy.props.BoolProperty(default=True)
    my_exp5 : bpy.props.BoolProperty(default=True)
    my_exp6 : bpy.props.BoolProperty(default=True)
    my_exp7 : bpy.props.BoolProperty(default=True)
    


#''' 
# [Addon display]
# ============================================================
class HAIR_SIM_SETTINGS(bpy.types.Panel):   
    bl_label = "HAIR SIM"
    bl_parent_id = "OBJECT_PT_panel"
    bl_idname = "OBJECT_PT_HairSim_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    bl_context = "scene"
    
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode_2(obj)[0]
        bgenModName = get_gNode_2(obj)[1]
        bgenNodeID = get_gNode_2(obj)[2]
        
        layout = self.layout 
                  
        col = layout.column()
        #box1 = col.box()   
        #box1.scale_y = 1.5
        #box1.operator("exec.operator", text = "Edit Sim") 
        box = col.box()
        
        try:

            if bgenNodeID == nodeID_3:
                box1 = box.box()
                box1.scale_y = 1.2
                box1.label(text = "Mod Type: [" + bgenModName + "]")
            
              
            # ================================================ #
            
            flow = box.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)
            col1 = box.column()
            col1.scale_y = 1.2
            col2 = flow.column()
            col2.scale_y = 1.2
            
            mytool = context.scene.bgen_tools
            col2.prop(mytool, "my_string1", text = "Hair Collection")
            col2.prop(mytool, "my_string2", text = "Collision Collection")
            
            col1.label(text="Simulation Values")
            col1.prop(mytool, "my_int1", text = "Quality")
            col1.prop(mytool, "my_float1", text = "Mass")
            col1.prop(mytool, "my_float2", text = "Gravity")
            col1.prop(mytool, "my_float3", text = "Tension")
            
            col1 = box.column()
            col1.scale_y = 2
            col1.operator("addonname.myop_operator")
            
            box = box.box()
            col1 = box.column()
  
            col1.label(text = 'Simulation Cache')
            
            row1 = col1.row()
            row1.scale_y = 1.5
            row1.operator("ptcache.bake_all")
            row1.operator("ptcache.free_bake_all")
            
        
        except:
            pass
#'''


# [Addon display]
# ============================================================
class HAIR_SIM_SETTING(bpy.types.Panel):
    
    bl_label = "VERTEX STRIPS"
    bl_parent_id = "OBJECT_PT_HairSim_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B-GEN HAIR"
    bl_context = "scene"
    
    
    def draw(self, context):
        obj = context.active_object
        bgenMod = get_gNode_2(obj)[0]
        bgenModName = get_gNode_2(obj)[1]
        bgenNodeID = get_gNode_2(obj)[2]
          
        layout = self.layout                
        col = layout.column()
      
        if bgenNodeID == nodeID_3:
            pScale = bpy.data.node_groups[bgenModName].nodes["Proxy Scale"].inputs[0]
            node = bpy.data.node_groups[bgenModName].nodes["Proxy Scale"]
            
            
            # [DISPLACEMENT CONTROL]
            floatCurve = bpy.data.node_groups[bgenModName].nodes['Vertex_Paint_FC'] 
            #col.label(text = "STRIPS CONTROL")

            col.scale_y = 1.6
            pScale.draw(context, col, node, text = 'Proxy Scale')
            
            col = layout.column()
            box = col.box()
            col1 = box.column()
            col1.scale_y = 1.2
            #col1.label(text = "WEIGHT PAINTING")
            
            # ========== Drop Down (1) ========== #
            row1 = col1.row()
            obj = context.object.bgen_expand
            
            row1.prop(obj, "my_exp1",
            icon="TRIA_DOWN" if obj.my_exp1 else "TRIA_RIGHT",
            icon_only=True, emboss=False
            )
            row1.label(text="Weight Paint")
            if obj.my_exp1:
                floatCurve.draw_buttons_ext(context, col1)
        
        
        
           
# [Execute Property]
# ============================================================
class EXECUTE_PROPERTY(bpy.types.Operator):
    bl_label = "Execute settings"
    bl_idname = "addonname.myop_operator"
    bl_context = "scene"
    
    def execute(self, context):
                
        scene = context.scene
        mytool = scene.bgen_tools 
        
        cloth_Settings()
        return {'FINISHED'}

#'''       
# [Register]
# ============================================================       
        
#bgenClasses = [MyProperties, HAIR_SIM_SETTINGS, EXECUTE_PROPERTY]

        
# [Registers]
# ============================================================

bgenClasses = (bgenProperties, bgenExpandProp, execOperator, EXECUTE_PROPERTY, B_GEN_HAIR, INITIALIZE, 
                HAIR_CONTROL, DISPLACEMENT_CONTROL, NOISE_CONTROL, BRAID_CONTROL, 
                CURL_CONTROL, HAIR_INTERPOLATION, ROOT_CONTROL, SCALP_HAIR,
                HAIR_SIM_SETTINGS, HAIR_SIM_SETTING)
                
#bgenClasses_A = (BRAID_CONTROL, BRAID_DISPLACEMENT, ROOT_CONTROL, SCALP_HAIR)
                
#bgenClasses_B = (DISPLACEMENT_CONTROL, NOISE_CONTROL)

def register():  
    for cls in bgenClasses:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bgen_tools = bpy.props.PointerProperty(type= bgenProperties)
    bpy.types.Object.bgen_expand = bpy.props.PointerProperty(type= bgenExpandProp)
                           
def unregister(): 
    for cls in bgenClasses:
        unregister_class(cls)
    del bpy.types.Scene.bgen_tools
    del bpy.types.Object.bgen_expand

                       
if __name__ == "__main__":
    register()
    #unregister()

    
#'''