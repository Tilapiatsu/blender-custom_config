# Copyright (C) 2023 Elias V.
# SPDX-License-Identifier: GPL-3.0-only

import bpy
import bmesh
from bpy_extras import mesh_utils

import numpy as np
import itertools
import functools
import random
import math
from heapq import heappush, heappop, heapify

print("-------------------")

#### A* ####

class Node():
    __slots__ = ('bmVert',
                 'cost',
                 'parentNode',
                 'travelledDistance',
                 'bmEdge')

    def __init__(self,
                 bmVert,
                 cost = 0,
                 parentNode = None,
                 travelledDistance = 0,
                 bmEdge = None):
        self.cost = cost
        self.parentNode = parentNode
        self.bmVert = bmVert
        self.bmEdge = bmEdge
        self.travelledDistance = travelledDistance

    def __lt__(self, other):
        return self.cost < other.cost

def getShortestPath(startVert, endVert, bmEdges, precalcs):
    fringes = [Node(startVert)]
    visited = set()
    pathEdges = []

    while fringes:
        currentNode = heappop(fringes)

        if(currentNode.bmVert == endVert):
            while(currentNode.parentNode):
                pathEdges.append(currentNode.bmEdge)
                currentNode = currentNode.parentNode

            return pathEdges

        edges = [edge for edge in currentNode.bmVert.link_edges
                 if edge in bmEdges]

        if(not edges):
            return None

        edgeLengths = np.array([precalcs.edgeLengths[edge.index] for edge in edges])

        finalDistances = np.array([edge.other_vert(currentNode.bmVert).co
                                   for edge in edges])
        finalDistances = np.array(endVert.co) - finalDistances
        finalDistances = np.sqrt(np.sum(finalDistances * finalDistances, axis = 1))

        costs = currentNode.travelledDistance + edgeLengths + finalDistances
        nodes = [Node(edges[c].other_vert(currentNode.bmVert),
                      costs[c],
                      currentNode,
                      currentNode.travelledDistance + edgeLengths[c],
                      edges[c])
                 for c in range(len(costs))]

        for n in nodes:
            if(n.bmEdge.index not in visited):
                heappush(fringes, n)
                visited.add(n.bmEdge.index)

    return None

############

class Precalcs():
    __slots__ = ("faceAreas",
                 "centroids",
                 "edgeLengths")

    def __init__(self):
        self.faceAreas = []
        self.centroids = []
        self.edgeLengths = []

@functools.cache
def getAdjacentFaces(bmFace):
    adjacent = set(face for edge in bmFace.edges if not edge.seam
                   for face in edge.link_faces if face != bmFace)

    return adjacent

def initBlenderState():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

def getActiveMesh():
    obj = bpy.context.edit_object
    mesh = obj.data

    return mesh

def getBMesh(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    return bm
    
def opMergeCharts(mesh, bm):
    selectedFaces = iter(f for f in bm.faces if f.select)
    facesToGrow = (next(selectedFaces), next(selectedFaces))

    queue = set()
    queue.add(facesToGrow[0])
    chart1 = set()

    while queue:
        adjacent = getAdjacentFaces(queue.pop())

        for f in adjacent:
            if(f not in chart1):
                chart1.add(f)
                queue.add(f)

    queue = set()
    queue.add(facesToGrow[1])
    chart2 = set()

    while queue:
        adjacent = getAdjacentFaces(queue.pop())

        for f in adjacent:
            if(f not in chart2):
                chart2.add(f)
                queue.add(f)

    if(chart1.intersection(chart2)):
        return

    chart1 = set(edge for face in chart1
                 for edge in face.edges)
    chart2 = set(edge for face in chart2
                 for edge in face.edges)
    edges = chart1.intersection(chart2)

    for e in edges:
        e.seam = False

    bpy.ops.object.mode_set(mode='OBJECT')
    bm.to_mesh(mesh)
    bpy.ops.object.mode_set(mode='EDIT')

def opStraightenSeams(mesh, bm):
    selectedEdges = set(e for e in bm.edges
                        if e.select == True)

    seams = set(e for e in selectedEdges
                if e.seam == True)

    cutoffPoints = set()
    for e in seams:
        for v in e.verts:
            count = len([le for le in v.link_edges
                         if le in seams])

            if(count == 1):
                cutoffPoints.add(v)

    precalcs = Precalcs()
    precalcs.edgeLengths = [e.calc_length() for e in bm.edges]
    path = getShortestPath(cutoffPoints.pop(), cutoffPoints.pop(), selectedEdges, precalcs)

    if(path):
        for e in seams:
            e.seam = False
        
        for e in path:
            e.seam = True

    bpy.ops.object.mode_set(mode='OBJECT')
    bm.to_mesh(mesh)
    bpy.ops.object.mode_set(mode='EDIT')
