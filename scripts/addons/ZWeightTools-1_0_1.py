bl_info = {
    "name": "Vertex Weight Tools",
    "description": "Various Vertex Weight Tools",
    "author": "Zach Eastin",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tools",
    "support": "COMMUNITY",
    "category": "3D View"
    }

import bpy, bmesh, math, inspect, time
from timeit import default_timer as timer
from bpy.props import (BoolVectorProperty,FloatVectorProperty,IntProperty,StringProperty, BoolProperty, EnumProperty, PointerProperty,FloatProperty)
from bpy.types import (PropertyGroup,Panel,Operator)
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class VWeightSettings(PropertyGroup):
    vweightDebugBool : BoolProperty(name = "Debug", description = "Turn on Vertex Weight Debugging Tools", default = False)
    pasteWeightBlendItems = [('REP','Replace','',1),('INV','Invert','',2),('ADD','Add','',3),('AVG','Average','',4),('SUB','Subtract','',5),('NOR','Normalize','',6),('WEI','Weighted Normalize','',7)]
    methItems = [('LEN','Length','',1),('LIN','Linear','',2)]
    rangeItems = [('SEL','Selection','',1),('PAR','Parellel (all)','',2)]
    pasteWeightBlendEnum : EnumProperty(items=pasteWeightBlendItems, name='Blend', default='REP', description='How copied values are pasted onto mesh')
    methEnum : EnumProperty(items=methItems, name='Method', default='LEN', description='Decide between Linear or by Length to determine gradienting method')
    rangeEnum : EnumProperty(items=rangeItems, name='Range', default='PAR', description='Decide between gradienting only the selected verts or Edge Loops')
    vSelectNum : FloatProperty(name="Weight to Select", step=0.1, min=0.0, max=1.0, description="Weight to Select")
    selWeightItems = [('<','<','',5),('<=','<=','',4),('=','=','',3),('>=','>=','',2),('>','>','',1)]
    selWeightEnum: EnumProperty(items=selWeightItems, name='What to Select', default='=', description="Comparison checkers to decide what to select")
    normBool : BoolProperty(name = "Weighted Normalize Bool", description = "Use Weighted Normalize", default = False)
class CopyPasteVWeight():
    vertWeights = []
class DebugHolder():
    verts = []
class GradOps(object):
    def getSel(self,bm):
        return [vert for vert in bm.verts if vert.select]
    def deselAll(self,bm):
        for v in bm.verts:
            v.select=False
    def selAll(self,bm):
        for v in bm.verts:
            v.select=True
    def checkVGroup(self,bm):
        obj = bpy.context.object
        if len(obj.vertex_groups) == 0:
            obj.vertex_groups.new(name="Group")
            bm = bmesh.from_edit_mesh(obj.data)
        return bm

    def isInGroup(self,bm,vLst,actInd,wlay):
        #Make sure all verts are in vertex group
        vs = [ v.index for v in bpy.context.object.data.vertices if actInd in [ vg.group for vg in v.groups ] ]
        for v in vLst:
            try:
                v[wlay][actInd]
            except:
                self.assignVWeight(bm,v,0.0,actInd,wlay,False)

    def arrangeVerts(self,selVerts,actVert,actInd,wlay):
        obj = bpy.context.object
        bm = bmesh.from_edit_mesh(obj.data)
        print('Active Vert:',actVert.index)
        eLst = []
        totEdgeLen = 0
        eLen = 0
        grad = GradOps()
        selVertsLen = len(selVerts).real

        ###REORDER###
        #Append to orderVerts
        orderVerts = []
        orderVerts.append(actVert)

        #Remove from selVerts
        selVerts.remove(actVert)
        print([v.index for v in selVerts])

        #for loop checking edges for actVert first
        for l in actVert.link_loops:
            othVert = l.link_loop_next.vert
            nv = l.link_loop_next.vert
            pv = l.link_loop_prev.vert
            if nv in selVerts:
                actVert = nv
                orderVerts.append(nv)
                eLst.append(l.edge)
                totEdgeLen += l.edge.calc_length()
                break
            elif pv in selVerts:
                actVert = pv
                orderVerts.append(pv)
                eLst.append(l.edge)
                totEdgeLen += l.edge.calc_length()
                break

        #Go through all connted verts and check to see if in selVerts
        i = 1
        print(selVertsLen)
        while selVerts:
            selVerts.remove(actVert)
            print('Removed',actVert.index)
            print([v.index for v in selVerts])
            print(i,actVert.index)
            test = True
            for l in actVert.link_loops:
                print('-',l.index)
                nv = l.link_loop_next.vert
                pv = l.link_loop_prev.vert
                if nv in selVerts:
                    print('--',nv.index)
                    actVert = nv
                    orderVerts.append(nv)
                    eLst.append(l.edge)
                    totEdgeLen += l.edge.calc_length()
                    test = False
                    break
                elif pv in selVerts:
                    print('--',pv.index)
                    actVert = pv
                    orderVerts.append(pv)
                    eLst.append(l.edge)
                    totEdgeLen += l.edge.calc_length()
                    test = False
                    break
            if test:
                print('---------Did not find next vert while ordering---------')
            i += 1
        #New Variables
        fInd = orderVerts[0].index
        lInd = orderVerts[-1].index
        fWeight = bm.verts[fInd][wlay][actInd]
        lWeight = bm.verts[lInd][wlay][actInd]

        #Determine direction
        if fWeight > lWeight:
            numer = fWeight - lWeight
            rev = False
            minWeight = lWeight
            maxWeight = fWeight
        elif fWeight < lWeight:
            numer = lWeight - fWeight
            rev = True
            minWeight = fWeight
            maxWeight = lWeight
        else:
            numer = 1
            rev = False
            minWeight = 0
            maxWeight = 1
        return [orderVerts,eLst,totEdgeLen,numer,rev,maxWeight,minWeight]

    def loopSel(self,verts):
        start = timer()
        e = None
        for e in verts[0].link_edges:
            if e.other_vert(verts[0]) == verts[1]:
                break
        if e == None:
            self.report({'ERROR'},'Could not find an edge with selected verts for parrellel function: orthoClickStuff.py'+str(lineno()))
            return {'CANCELLED'}

        vlst = [verts[0],verts[1]]

        #Get Edge from verts
        e = None

        for e in verts[0].link_edges:
            if e.other_vert(verts[0]) == verts[1]:
                break
        vlst = [verts[0],verts[1]]

        for l in e.link_loops:

            if len(l.vert.link_loops) == 4:
                for v in e.verts:
                    if v not in vlst:
                        vlst.append(v)

                while len(l.vert.link_edges) == 4:
                    start = timer()
                    # jump between BMLoops to the next BMLoop we need
                    l = l.link_loop_prev.link_loop_radial_prev.link_loop_prev
                    if not l.vert.select:
                        vlst.append(l.vert)
                        # following edge in the edge loop
                        if l.edge.hide:
                            break
                    else:
                        break

        return vlst
    def assignVWeight(self,bm,verts,weight,actInd,wlay,multiple):
        if multiple:
            for v in verts:
                v[wlay][actInd] = weight
        else:
            verts[wlay][actInd] = weight

    def gradWeightLinear(self,bm,orderVerts,numer,rev,maxWeight,thrAwa,actInd,wlay):
        obj = bpy.context.object
        grad = GradOps()
        if bpy.context.scene.vweight_tools.rangeEnum == 'SEL':
            i = 0
            chg = numer / (len(orderVerts) - 1)
            if rev:
                orderVerts.reverse()
            for v in orderVerts:
                subAm = chg * i
                newWeight = maxWeight - subAm
                self.assignVWeight(bm,v,newWeight,actInd,wlay,False)
                i+=1
        else:
            restOfOriginalLoop = []
            for v in thrAwa:
                if v not in orderVerts:
                    restOfOriginalLoop.append(v)
            lpTwoInd = []
            #self.deselAll()
            chg = numer / (len(orderVerts) - 1)
            selectedVerts = []
            if rev:
                orderVerts.reverse()
            for i, v in enumerate(orderVerts):
                #self.deselAll()
                for e in v.link_edges:
                    if e.other_vert(v) not in orderVerts and e.other_vert(v) not in restOfOriginalLoop:
                        v2 = e.other_vert(v)
                        verts = [v,v2]
                        vs = grad.loopSel(verts)
                        subAm = chg * i
                        newWeight = maxWeight - subAm
                        self.assignVWeight(bm,vs,newWeight,actInd,wlay,True)
                        selectedVerts.append(vs)
                        i+=1
                        break
            for list in selectedVerts:
                for v in list:
                    if not v.select:
                        v.select = True

    def gradWeightLength(self,bm,orderVerts,numer,totEdgeLen,eLst,rev,maxWeight,thrAwa,minWeight,actInd,wlay):
        #Variables
        obj = bpy.context.object
        grad = GradOps()
        eLen = 0

        #Decide between just selected verts or parallel loops
        if bpy.context.scene.vweight_tools.rangeEnum == 'SEL':
            #Reverse list or not
            if not rev:
                orderVerts.reverse()
                eLst.reverse()
            #get Average
            avg = maxWeight-minWeight
            for i, v in enumerate(orderVerts):
                num = i - 1
                if num < 0:
                    num = 0
                if i == 0:
                    newWeight = minWeight
                else:
                    #get length between two neighboring selected verts
                    eLen += eLst[num].calc_length()
                    newWeight = avg * (eLen/totEdgeLen) + minWeight
                self.assignVWeight(bm,v,newWeight,actInd,wlay,False)
                i += 1
        else:
            restOfOriginalLoop = []
            for v in thrAwa:
                if v not in orderVerts:
                    restOfOriginalLoop.append(v)
            if not rev:
                orderVerts.reverse()
                eLst.reverse()

            avg = maxWeight-minWeight
            selectedVerts = []
            #wm = bpy.context.window_manager
            #wm.progress_begin(0,100)
            for i, v in enumerate(orderVerts):
                for l in v.link_loops:
                    v2 = l.link_loop_next.vert
                    if v2 not in orderVerts and v2 not in restOfOriginalLoop:
                        verts = [v,v2]
                        loopsrt = timer()
                        vs = grad.loopSel(verts)
                        num = i - 1
                        if num < 0:
                            num = 0
                        if i == 0:
                            newWeight = minWeight
                        else:
                            eLen += eLst[num].calc_length()
                            newWeight = (avg * (eLen/totEdgeLen)) + minWeight
                        self.assignVWeight(bm,vs, newWeight,actInd,wlay,True)
                        selectedVerts.append(vs)
                        i+=1
                        break
                #updte = (i/len(orderVerts)*100)
                #wm.progress_update(updte)
            #wm.progress_end()

            for list in selectedVerts:
                for v in list:
                    if not v.select:
                        v.select = True
def init_bm():
    if bpy.context.mode == "EDIT_MESH":
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(bpy.context.object.data)
    return bm

################################### --- GRADIENT OPERATOR --- ###################################
class MESH_OT_WeightGradient(Operator):
    """Get Vertices and Assign in a Gradient Fashion"""
    bl_idname = "mesh.weight_gradient"
    bl_label = "Gradient"
    bl_options = {"UNDO"}

    def execute(self, context):
        print()
        total = timer()
        #Variables
        wTool = bpy.context.scene.vweight_tools
        obj = bpy.context.object
        me = obj.data
        mesh = bpy.types.Mesh
        bm = bmesh.from_edit_mesh(me)
        grad = GradOps()


        #Make sure there is a vertex group to add to
        bm = grad.checkVGroup(bm)
        actInd  = obj.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        actVert = bm.select_history.active

        #Put selected vertices in a list
        selVerts = grad.getSel(bm)

        #Make sure active vert is actually an end vert
        print('Active Vert:',actVert.index)
        check = []
        for l in actVert.link_loops:
            if l.link_loop_next.vert.select:
                if l.link_loop_next.vert not in check:
                    check.append(l.link_loop_next.vert)
            if l.link_loop_prev.vert.select:
                if l.link_loop_prev.vert not in check:
                    check.append(l.link_loop_prev.vert)

        if len(check) != 1:
            endVs = []
            for v in selVerts:
                check = []
                for l in v.link_loops:
                    if l.link_loop_next.vert.select:
                        if l.link_loop_next.vert not in check:
                            check.append(l.link_loop_next.vert)
                    if l.link_loop_prev.vert.select:
                        if l.link_loop_prev.vert not in check:
                            check.append(l.link_loop_next.vert)
                if len(check) == 1:
                    endVs.append(v)
            actVert = endVs[0]

        #Check for active vertex
        if actVert == None:
            self.report({'ERROR'},'Active Vertex Could Not Be Found: orthoClickStuff.py '+str(lineno()))
            return {'CANCELLED'}

        #Make sure all verts are in vertex group
        grad.isInGroup(bm,selVerts,actInd,wlay)

        ###REORDER###
        #arVrtOtpt = grad.arrangeVerts(selVerts,origVerts,actVert,actInd,wlay)
        arVrtOtpt = grad.arrangeVerts(selVerts,actVert,actInd,wlay)

        orderVerts = arVrtOtpt[0]
        eLst = arVrtOtpt[1]
        totEdgeLen = arVrtOtpt[2]
        numer = arVrtOtpt[3]
        rev = arVrtOtpt[4]
        maxWeight = arVrtOtpt[5]
        minWeight = arVrtOtpt[6]

        #Check to see if using linear or length method
        if wTool.methEnum == 'LIN':
            #start = timer()
            grad.gradWeightLinear(bm,orderVerts,numer,rev,maxWeight,selVerts,actInd,wlay,)
            #print('Linear:',timer()-start)
        else:
            #start = timer()
            grad.gradWeightLength(bm,orderVerts,numer,totEdgeLen,eLst,rev,maxWeight,selVerts,minWeight,actInd,wlay)
            #print('Length:',timer()-start)
        me.update()
        print(timer()-total)
        print()

        return {"FINISHED"}

################################### --- BUTTONASSIGN OPERATOR --- ###################################
class MESH_OT_buttAss(Operator):
    """Buttons to assign common vertex weights"""
    bl_idname = "mesh.button_assign"
    bl_label = "Set vertext to..."
    bl_options = {"UNDO"}

    id: bpy.props.IntProperty()

    def execute(self, context):
        #Variables
        C = bpy.context
        me = C.object.data
        mode = C.mode
        bm = init_bm()
        denom = C.scene.buttInt
        grad = GradOps()
        verts = grad.getSel(bm)
        actInd = C.object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()

        if mode != "EDIT_MESH":
            if self.id == 0:
                bpy.ops.object.vertex_group_remove_from()
            else:
                newWeight = self.id/denom
                grad.assignVWeight(bm,bm.verts, newWeight,actInd,wlay,True)
            bm.to_mesh(me)
        else:
            if self.id == 0:
                bpy.ops.object.vertex_group_remove_from()
            else:
                newWeight = self.id/denom
                if len(verts) == 1:
                    grad.assignVWeight(bm,verts[0],newWeight,actInd,wlay,False)
                else:
                    grad.assignVWeight(bm,verts,newWeight,actInd,wlay,True)
        me.update()

        return{'FINISHED'}

class SceneItems(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty()

###################################### --- COPY VERT WEIGHT --- #######################################
# ---- Copy Vertex Weights ---- #
class MESH_OT_copyVWeight(Operator):
    """Copy Verts Weight"""
    bl_idname = "mesh.copy_weight"
    bl_label = "Copy Weight"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        aVG = bpy.context.edit_object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        selVerts = []
        vCopy = bpy.context.scene.copy_vweight
        for v in bm.verts:
            if v.select:
                if aVG in v[wlay]:
                    vwght = v[wlay][aVG]
                    selVerts.append([v.index.real,vwght])
                else:
                    vwght = 0.0
                    selVerts.append([v.index.real,vwght])
        vCopy.vertWeights = selVerts

        return{'FINISHED'}
# ---- Paste Vertex Weights ---- #
class MESH_OT_pasteVWeight(Operator):
    """Paste Verts Weight"""
    bl_idname = "mesh.paste_weight"
    bl_label = "Paste Weight"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        vCopy = bpy.context.scene.copy_vweight
        grad = GradOps()
        aVG = bpy.context.edit_object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        pasteSelection = []
        wTool = context.scene.vweight_tools
        if wTool.pasteWeightBlendEnum == 'REP':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                v[wlay][aVG] = weight
        elif wTool.pasteWeightBlendEnum == 'INV':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = 1-i[1]
                v[wlay][aVG] = weight
        elif wTool.pasteWeightBlendEnum == 'WEI':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                for key in v[wlay].keys():
                    curweight = v[wlay][key]
                    if curweight == 0.0:
                        nweight = weight
                    else:
                        nweight = curweight*(1-weight)
                    v[wlay][key] = nweight
                if aVG in v[wlay]:
                    #curweight = v[wlay][aVG]
                    v[wlay][aVG] = weight
                else:
                    v[wlay][aVG] = 0.0
        elif wTool.pasteWeightBlendEnum == 'NOR':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                sumweight = 0
                for weight in v[wlay].values():
                    sumweight+=weight
                v[wlay][aVG] = curweight/sumweight
        elif wTool.pasteWeightBlendEnum == 'ADD':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                curweight = v[wlay][aVG]
                v[wlay][aVG] = weight+curweight
        elif wTool.pasteWeightBlendEnum == 'SUB':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                if aVG in v[wlay]:
                    curweight = v[wlay][aVG]
                    v[wlay][aVG] = curweight-weight
                else:
                    v[wlay][aVG] = 0.0
        elif wTool.pasteWeightBlendEnum == 'AVG':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                curweight = v[wlay][aVG]
                v[wlay][aVG] = (weight+curweight)/2
        me.update()

        return{'FINISHED'}
# ---- Recursive Blend Vertex Weights ---- #
class MESH_OT_recursiveBlend(Operator):
    """Take all Vertex Groups with names starting the same and blend them"""
    bl_idname = "mesh.recursive_blend"
    bl_label = "Recursive Blend"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.object.vertex_groups) > 1

    def copy(self, bm,vg,aVG,wlay,vCopy):
        vs = []
        for v in bm.verts:
            if vg.index in v[wlay]:
                start = timer()
                vwght = v[wlay][vg.index]
                vs.append([v.index,vwght])
        vCopy.vertWeights = vs

    def paste(self,bm,vCopy,grad,aVG,wlay):
        wTool = bpy.context.scene.vweight_tools
        if wTool.pasteWeightBlendEnum == 'REP':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                v[wlay][aVG] = weight
        elif wTool.pasteWeightBlendEnum == 'ADD':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                curweight = v[wlay][aVG]
                v[wlay][aVG] = weight+curweight
        elif wTool.pasteWeightBlendEnum == 'AVG':
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                curweight = v[wlay][aVG]
                v[wlay][aVG] = (weight+curweight)/2
        else:
            for i in vCopy.vertWeights:
                v = bm.verts[i[0]]
                weight = i[1]
                if aVG in v[wlay]:
                    curweight = v[wlay][aVG]
                    v[wlay][aVG] = curweight-weight


    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        vCopy = bpy.context.scene.copy_vweight
        grad = GradOps()
        aVG = bpy.context.edit_object.vertex_groups.active
        wlay = bm.verts.layers.deform.verify()
        vCopy = bpy.context.scene.copy_vweight
        vCopy.vertWeights.clear()
        vgroups = []
        #Gather all VG's that start with aVG .name
        for vg in bpy.context.edit_object.vertex_groups:
            if vg.name.startswith(aVG.name+'_') and vg != aVG:
                self.report({"INFO"},"Blended: "+str(vg.name))
                vgroups.append(vg)
        #for each VG
        for vg in vgroups:
            #Copy All weights in VG
            self.copy(bm,vg,aVG.index,wlay,vCopy)
            #Paste with blend onto aVG
            self.paste(bm,vCopy,grad,aVG.index,wlay)
        me.update()
        self.report({"INFO"},"Main Vertex Group: "+str(aVG.name))
        return{'FINISHED'}
# ---- Copy weights from nearest vertex ---- #
class MESH_OT_copyNearest(Operator):
    """Copy vertex weights of active vertex group from nearest vertex"""
    bl_idname = "mesh.copy_nearest"
    bl_label = "Copy Nearest"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.object.vertex_groups) > 1

    def calcDist(self,v1,v2):
        vco = v1.co
        nvco = v2.co
        return math.sqrt( (vco[0] - nvco[0])**2 + (vco[1] - nvco[1])**2 + (vco[2] - nvco[2])**2)

    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        wlay = bm.verts.layers.deform.verify()
        actInd = ob.vertex_groups.active_index

        vlst = [v for v in bm.verts if actInd in v[wlay] and not v.select]
        selv = [v for v in bm.verts if v.select]

        for v in selv:
            nearestVert = None
            nearestVertDist = None
            curDist = None
            for nv in vlst:
                if nearestVert == None:
                    nearestVert = nv
                    nearestVertDist = self.calcDist(v,nv)
                    curDist = self.calcDist(v,nearestVert)
                else:
                    newDist = self.calcDist(v,nv)
                    if newDist < curDist:
                        nearestVert = nv
                        nearestVertDist = newDist
                        curDist = self.calcDist(v,nearestVert)
                        if curDist == 0.0:
                            break
            v[wlay][actInd] = nearestVert[wlay][actInd]
        me.update()
        return{'FINISHED'}

###################################### --- WEIGHT EYEDROPPER --- #######################################
class MESH_OT_weightEyeDrop(Operator):
    """Set weight to selected vertex weight"""
    bl_idname = "mesh.weight_eye_drop"
    bl_label = "Weight Eye Dropper"
    bl_options = {"UNDO"}

    def execute(self, context):
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        aVG = bpy.context.edit_object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        actv = bm.select_history.active
        if actv == None:
            self.report({'ERROR'},'No active vertex found. Please select a vertex.')
            return {'CANCELLED'}

        bpy.context.scene.tool_settings.vertex_group_weight = actv[wlay][aVG]

        return{'FINISHED'}

###################################### --- NORMALIZE --- #######################################
class MESH_OT_Normalize(Operator):
    """Make all weights on selected verticies add up to 1"""
    bl_idname = "mesh.vweight_normalize"
    bl_label = "Normalize"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        aVGInd = bpy.context.edit_object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        selVerts = [v for v in bm.verts if v.select]
        wTool=bpy.context.scene.vweight_tools
        if wTool.normBool:
            for v in selVerts:
                if aVGInd in v[wlay]:
                    weight = v[wlay][aVGInd]
                    for key in v[wlay].keys():
                        if key != aVGInd:
                            curweight = v[wlay][key]
                            if curweight == 0.0:
                                nweight = weight
                            else:
                                nweight = curweight*(1-weight)
                            v[wlay][key] = nweight
                else:
                    weight = 0.0
                    for key in v[wlay].keys():
                        if key != aVGInd:
                            curweight = v[wlay][key]
                            if curweight == 0.0:
                                nweight = weight
                            else:
                                nweight = curweight
                            v[wlay][key] = nweight
        else:
            for v in selVerts:
                sumweight = 0
                for weight in v[wlay].values():
                    sumweight+=weight
                for key in v[wlay].keys():
                    v[wlay][key] = v[wlay][key]/sumweight
        bpy.context.object.data.update()

        return{'FINISHED'}

###################################### --- COPY ACTIVE WEIGHT --- #######################################
class MESH_OT_copyActWeight(Operator):
    """Copy Active Weight to other Selected Verts"""
    bl_idname = "mesh.copy_active_weight"
    bl_label = "Copy"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        aVGInd = bpy.context.edit_object.vertex_groups.active_index
        wlay = bm.verts.layers.deform.verify()
        actVert = bm.select_history.active
        selVerts = [v for v in bm.verts if v.select]
        grad = GradOps()
        weight = actVert[wlay][aVGInd]
        grad.assignVWeight(bm,selVerts,weight,True)

        bpy.context.object.data.update()

        return{'FINISHED'}

###################################### --- SELECT VIA WEIGHT --- #######################################
class MESH_OT_selectViaWeight(Operator):
    """Select by Weight"""
    bl_idname = "mesh.select_by_weight"
    bl_label = "Select"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        wTool = bpy.context.scene.vweight_tools
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        aVG = bpy.context.edit_object.vertex_groups.active_index
        vSelectNum = wTool.vSelectNum
        if wTool.selWeightEnum == '<=':
            for v in bm.verts:
                try:
                        vwght = bpy.context.edit_object.vertex_groups[aVG].weight(v.index)
                        if vwght <= vSelectNum:
                            v.select = True
                except:
                    pass
        elif wTool.selWeightEnum == '<':
            for v in bm.verts:
                try:
                        vwght = bpy.context.edit_object.vertex_groups[aVG].weight(v.index)
                        if vwght < vSelectNum:
                            v.select = True
                except:
                    pass
        elif wTool.selWeightEnum == '=':
            for v in bm.verts:
                try:
                        vwght = bpy.context.edit_object.vertex_groups[aVG].weight(v.index)
                        if vwght == vSelectNum:
                            v.select = True
                except:
                    pass
        elif wTool.selWeightEnum == '>=':
            for v in bm.verts:
                try:
                        vwght = bpy.context.edit_object.vertex_groups[aVG].weight(v.index)
                        if vwght >= vSelectNum:
                            v.select = True
                except:
                    pass
        elif wTool.selWeightEnum == '>':
            for v in bm.verts:
                try:
                        vwght = bpy.context.edit_object.vertex_groups[aVG].weight(v.index)
                        if vwght > vSelectNum:
                            v.select = True
                except:
                    pass
        bpy.context.object.data.update()

        return{'FINISHED'}

###################################### --- DEBUGGING --- #######################################
#Select NonNormalized Verts
class MESH_OT_selectUnnormVerts(Operator):
    """Select verticies if their weights add up to more than 1"""
    bl_idname = "mesh.select_unnorm_verts"
    bl_label = "Select"
    bl_options = {"UNDO"}

    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        wlay = bm.verts.layers.deform.verify()
        holder = bpy.context.scene.debug_holder
        holder.verts.clear()
        for v in bm.verts:
            sumweights = 0
            for weight in v[wlay].values():
                sumweights+=weight
                if sumweights > 1.0000001:
                    v.select = True
                    holder.verts.append(v.index)
                    break
                else:
                    v.select = False
        me.update()
        return{'FINISHED'}
#Select Individual NonNormalized Verts
class MESH_OT_selectSingleUnnormVerts(Operator):
    """Select this vertex"""
    bl_idname = "mesh.select_single_unnorm_vert"
    bl_label = "Select"
    bl_options = {"UNDO"}

    index : bpy.props.IntProperty()

    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        for v in bm.verts:
            if v.index == self.index:
                v.select = True
            else:
                v.select = False
        me.update()
        return{'FINISHED'}
#Remove Individual NonNormalized Verts
class MESH_OT_removeSingleUnnormVerts(Operator):
    """Remove this vertex from list"""
    bl_idname = "mesh.remove_single_unnorm_vert"
    bl_label = "Remove"
    bl_options = {"UNDO"}

    index : bpy.props.IntProperty()

    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        holder = bpy.context.scene.debug_holder
        holder.verts.remove(self.index)
        return{'FINISHED'}

###################################### --- EXTRAS --- #######################################
# ---- REMOVE 0 WEIGHTS ---- #
class MESH_OT_remove_zeros(Operator):
    """Remove 0 weighted vertexes"""
    bl_idname = "mesh.remove_zeros"
    bl_label = "Remove 0's"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        wTool = bpy.context.scene.vweight_tools
        obj = bpy.context.object
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        wlay = bm.verts.layers.deform.verify()
        totv = len(bm.verts)
        bpy.ops.object.mode_set(mode='OBJECT')
        finvnum = 0
        for i,vg in enumerate(obj.vertex_groups):
            vs = []
            for v in bm.verts:
                if i in v[wlay].keys():
                    if v[wlay][i] == 0.0:
                        vs.append(v.index)
                        finvnum += 1
            obj.vertex_groups[i].remove(vs)
        self.report({'INFO'},'Removed '+str(finvnum)+' 0 weights from all Vertex Groups')
        bpy.ops.object.mode_set(mode='EDIT')

        return{'FINISHED'}
# ---- LOAD VERTEX GROUP NAMES ---- #
class OBJECT_OT_vGroupNames(Operator):
    """Load selected objects' names into active object's vertex groups"""
    bl_idname = "object.vertex_group_names"
    bl_label = "Load Vertex Groups"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        C = bpy.context
        vNames = []
        if len(C.selected_objects) == 1:
            self.report({'ERROR'},'Only one object selected: myStuff 191')
            return{'CANCELLED'}
        else:
            for obj in C.selected_objects:
                if obj.type == "MESH":
                    if obj != C.object and obj.name not in C.object.vertex_groups:
                        if 'tibia' in obj.name.lower():
                            vNames.append('Tibia')
                        elif 'fibula' in obj.name.lower():
                            vNames.append('Fibula')
                        elif 'bone' in obj.name.lower():
                            vNames.append(obj.name[5:])
                        else:
                            vNames.append(obj.name)
            for name in vNames:
                C.object.vertex_groups.new(name=name)

        return{'FINISHED'}

########################################## --- PANEL --- ##########################################
# ---- Stock Vertex Group Panel ---- #
class PANEL_PT_vertex_groupsProps(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Weight Groups"
    bl_category = 'Vertex Tools'

    @classmethod
    def poll(cls, context):
        layPanel = context.preferences.addons['ZWeightTools-1_0_1'].preferences.weightGroupsTog
        return  len(context.selected_objects)>0 and layPanel


    def draw(self, context):
        layout = self.layout

        ob = context.object
        group = ob.vertex_groups.active

        rows = 3
        if group:
            rows = 5

        row = layout.row()
        row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)

        col = row.column(align=True)

        col.operator("object.vertex_group_add", icon='ADD', text="")
        props = col.operator("object.vertex_group_remove", icon='REMOVE', text="")
        props.all_unlocked = props.all = False

        col.separator()

        col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")

        if group:
            col.separator()
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if (
                ob.vertex_groups and
                (ob.mode == 'EDIT' or
                 (ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex))
        ):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.vertex_group_assign", text="Assign")
            sub.operator("object.vertex_group_remove_from", text="Remove")

            sub = row.row(align=True)
            sub.operator("object.vertex_group_select", text="Select")
            sub.operator("object.vertex_group_deselect", text="Deselect")

            row = layout.row(align=True)
            row.prop(context.tool_settings, "vertex_group_weight", text="Weight")
            row.operator("mesh.weight_eye_drop", icon='EYEDROPPER', text="")
# ---- Stock Vertex Weight Panel ---- #
class PANEL_PT_vertexWeightLayersPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Vertex Weights"
    bl_category = 'Vertex Tools'

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH' and context.object.type == "MESH":
            bm = init_bm()
            layPanel = context.preferences.addons['ZWeightTools-1_0_1'].preferences.vertexWeightsTog
            return  len(bm.verts.layers.deform.keys()) > 0 and layPanel
        else:
            return False

    weightflt : FloatProperty(name='weight',description='The weight of this vertex',min=0.0,max=1.0)

    def draw(self, context):
        layout = self.layout
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        wlay = bm.verts.layers.deform.verify()
        vgs = context.object.vertex_groups

        col = layout.column(align = True)

        for key in bm.select_history.active[wlay].keys():
            ind = bm.select_history.active.index
            row = col.row(align = True)
            if key != vgs.active_index:
                row.active = False
            #Operator to change active vertex group \ also needs name of group
            row.operator("object.vertex_weight_set_active",text=vgs[key].name).weight_group = key
            #Int Property displaying current weight
            weight = bm.verts[ind][wlay][key]
            self.weightflt = weight
            row.label(text=str(self.weightflt))
            #Copy weight operator
            row.operator("mesh.copy_weight",text='',icon="COPYDOWN")
            #Paste weight operator
            row.operator("mesh.paste_weight",text='',icon="PASTEDOWN")
            #Remove weight operator
            row.operator("object.vertex_weight_delete",text='',icon="PANEL_CLOSE").weight_group = key
# ---- My Vertex Weight Panel ---- #
class PANEL_PT_vWeightPanel(Panel):
    bl_label = "Weight Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vertex Tools'

    @classmethod
    def poll(self, context):
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        if context.mode == 'OBJECT':
            layout.operator("object.vertex_group_names")

        elif context.mode == 'EDIT_MESH':
            scene = bpy.context.scene
            wTool = scene.vweight_tools
            me = bpy.context.object.data
            bm = bmesh.from_edit_mesh(me)

            overlay = bpy.context.area.spaces[0].overlay
            layout.prop(overlay, "show_weight")

            layout.separator()
            row = layout.row()
            col = row.column()
            col.prop(wTool, "methEnum")
            col.prop(wTool, "rangeEnum")
            row = layout.row(align = True)
            row.scale_y = 1.75
            row.operator('mesh.weight_gradient', text = "Gradient")

            layout.separator()
            row = layout.row(align=True)
            row.operator("object.vertex_group_invert", text="Invert")
            row.operator("object.vertex_group_smooth", text = "Smooth")
            row.operator("mesh.copy_active_weight")
            row.operator("object.vertex_group_mirror", text="Mirror")

            layout.separator()
            grid = layout.grid_flow(row_major=True)
            grid.scale_x = 0.6
            grid.prop(wTool, "normBool",text='Weighted Normalize')
            grid.operator("mesh.vweight_normalize")

class PANEL_PT_vWeightPanel_SelectByWeight(Panel):
    bl_label = "Select By Weight"
    bl_parent_id = "PANEL_PT_vWeightPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.mode == 'EDIT_MESH'

    def draw (self, context):
        layout = self.layout
        scene = bpy.context.scene
        wTool = scene.vweight_tools
        row = layout.row()
        row.alignment = "CENTER"
        row.operator("mesh.select_by_weight")
        row.label(text="if")
        row.prop(wTool,'selWeightEnum',text='')
        row.prop(wTool, "vSelectNum")
class PANEL_PT_vWeightPanel_CopyPaste(Panel):
    bl_label = "Copy Paste"
    bl_parent_id = "PANEL_PT_vWeightPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.mode == 'EDIT_MESH'

    def draw (self, context):
        layout = self.layout
        scene = bpy.context.scene
        wTool = scene.vweight_tools
        layout.prop(wTool,'pasteWeightBlendEnum',text='')
        grid = layout.grid_flow(row_major=True,align=True)
        grid.scale_x = 0.6
        grid.operator("mesh.copy_weight")
        grid.operator("mesh.paste_weight")
        layout.separator()
        grid = layout.grid_flow(row_major=True,align=True)
        grid.scale_x = 0.6
        grid.operator("mesh.recursive_blend")
        grid.operator("mesh.copy_nearest")
class PANEL_PT_vWeightPanel_QuickWeights(Panel):
    bl_label = "Quick Weights"
    bl_parent_id = "PANEL_PT_vWeightPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.mode == 'EDIT_MESH' or context.mode == 'OBJECT'

    def draw (self, context):
        layout = self.layout
        scene = bpy.context.scene
        wTool = scene.vweight_tools
        layout.prop(scene, "buttInt", text='Denom')
        denom = scene.buttInt
        row = layout.row(align = True)
        row.operator("mesh.button_assign",text = '0.0').id = 0
        for i in range(context.scene.buttInt):
            if i != 0:
                txt = str(i/denom)
                row.operator("mesh.button_assign",text = txt).id = i
        row.operator("mesh.button_assign",text = '1.0').id = context.scene.buttInt
        layout.operator("mesh.remove_zeros")
class PANEL_PT_vWeightPanel_Debug(Panel):
    bl_label = "Debug"
    bl_parent_id = "PANEL_PT_vWeightPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.mode == 'EDIT_MESH'

    def draw (self, context):
        layout = self.layout
        scene = bpy.context.scene
        wTool = scene.vweight_tools
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        holder = bpy.context.scene.debug_holder
        row = layout.row()
        if len(bm.select_history) > 0:
            v = bm.select_history.active
            wlay = bm.verts.layers.deform.verify()
            sumweight = 0.0
            for weight in v[wlay].values():
                sumweight+=weight
            row.label(text=str(sumweight))
        layout.prop(wTool,"vweightDebugBool")
        layout.operator("mesh.select_unnorm_verts")
        if wTool.vweightDebugBool:
            grid = layout.grid_flow(row_major=True,even_columns=False,align=True)
            for index in holder.verts:
                row = grid.row(align=True)
                row.operator("mesh.select_single_unnorm_vert",text = str(index)).index = index
                row.operator("mesh.remove_single_unnorm_vert",text = '',icon='PANEL_CLOSE').index = index

class vWeight_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    weightGroupsTog: BoolProperty(
        name="Show Weight Groups",
        description='Show Blender\'s stock "Vertex Groups" panel in the viewport', default=True)

    vertexWeightsTog: BoolProperty(
        name="Show Vertex Weights Panel",
        description='Show Blender\'s stock "Vertex Weights" panel in the viewport', default=True)

    def draw(self, context):
        layout = self.layout
        grid = layout.grid_flow(row_major=True)
        grid.prop(self,"weightGroupsTog")
        grid.prop(self,"vertexWeightsTog")

###################################################################################################
######################################## --- REGISTER --- #########################################
###################################################################################################
def AddButtonOperator(self, context):
    wTool = context.scene

    int = len(bpy.context.scene.gradCollection) - 1
    for item in bpy.context.scene.gradCollection:
        bpy.context.scene.gradCollection.remove(int)
        int-=1

    i = 0
    denom = wTool.buttInt
    while i < denom:
        id = len(context.scene.gradCollection)
        new = context.scene.gradCollection.add()
        new.name = str(id/denom)
        new.value = id
        i+=1

classes = [
                    MESH_OT_weightEyeDrop,
                    VWeightSettings,
                    OBJECT_OT_vGroupNames,
                    MESH_OT_remove_zeros,
                    MESH_OT_copyNearest,
                    MESH_OT_selectSingleUnnormVerts,
                    MESH_OT_removeSingleUnnormVerts,
                    MESH_OT_selectUnnormVerts,
                    MESH_OT_Normalize,
                    MESH_OT_recursiveBlend,
                    MESH_OT_copyActWeight,
                    MESH_OT_selectViaWeight,
                    MESH_OT_copyVWeight,
                    MESH_OT_pasteVWeight,
                    SceneItems,
                    MESH_OT_buttAss,
                    MESH_OT_WeightGradient,
                    PANEL_PT_vertex_groupsProps,
                    PANEL_PT_vertexWeightLayersPanel,
                    PANEL_PT_vWeightPanel,
                    PANEL_PT_vWeightPanel_QuickWeights,
                    PANEL_PT_vWeightPanel_SelectByWeight,
                    PANEL_PT_vWeightPanel_CopyPaste,
                    PANEL_PT_vWeightPanel_Debug,
                    vWeight_Preferences,
                    ]
def register():
    for clas in classes:
        bpy.utils.register_class(clas)
    bpy.types.Scene.gradCollection = bpy.props.CollectionProperty(type=SceneItems)
    bpy.types.Scene.gradOps = GradOps
    bpy.types.Scene.buttInt = IntProperty(name='Denomenator',description='Denomenator of fraction',default=2, min=1)
    bpy.types.Scene.copy_vweight = CopyPasteVWeight()
    bpy.types.Scene.debug_holder = DebugHolder()
    bpy.types.Scene.vweight_tools = PointerProperty(type=VWeightSettings)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)
    del bpy.types.Scene.gradCollection
    del bpy.types.Scene.copy_vweight
    del bpy.types.Scene.debug_holder
    del bpy.types.Scene.vweight_tools
    del bpy.types.Scene.gradOps
    del bpy.types.Scene.buttInt

if __name__ == "__main__":
    register()
