import bpy
import mathutils
from .qobject import *

Pverts = [[-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0], [0, 0, 2]]
Pfaces = [[0,1,2,3],[0,1,4],[1,2,4],[2,3,4],[3,0,4]]
PvertsM = [[-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0], [0, 0, 1], [0,0,-1]]
PfacesM = [[0,1,4],[1,2,4],[2,3,4],[3,0,4], [0,1,5],[1,2,5],[2,3,5],[3,0,5]]

class Qpyramid(Qobject):
    basetype = 1

    def copyData(self, _op):
        newQ = Qpyramid(_op)
        return newQ

    def UpdateMesh(self):
        transformS = GetTransformOffset(self.isCentered)
        bvertList = []
        bmeshNew = bmesh.new()
        if not self.isCentered:
            for newvert in Pverts:
                actVert = bmeshNew.verts.new(newvert)
                bvertList.append(actVert)
            for newface in Pfaces:
                bvseq = []
                for vi in newface:
                    bvseq.append(bvertList[vi])
                bmeshNew.faces.new(bvseq) 
        else:
            for newvert in PvertsM:
                actVert = bmeshNew.verts.new(newvert)
                bvertList.append(actVert)
            for newface in PfacesM:
                bvseq = []
                for vi in newface:
                    bvseq.append(bvertList[vi])
                bmeshNew.faces.new(bvseq) 
        
        bmeshNew.to_mesh(self.bMesh)
        # self.bMesh.transform(transformS)
        self.bMesh.update()
        bpy.context.view_layer.update()
