# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Transfer Vert Order",
    "author": "Jose Conseco based on UV Transfer from MagicUV Nutti",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "Sidebar (N) -> Tools panel",
    "description": "Transfer Verts IDs by verts proximity or by selected faces",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
    }

from collections import OrderedDict

import bpy
import bmesh
from bpy.props import BoolProperty,BoolProperty
from mathutils import kdtree


class CopyIDs():
    def __init__(self):
        self.transuv = ID_DATA()

class ID_DATA():
    topology_copied = []


class VOT_PT_CopyVertIds(bpy.types.Panel):
    bl_idname = "VOT_PT_copyvertids"
    bl_label = "Transfer vertex order"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        if context.mode == 'OBJECT':
            layout.label(text = 'Transfer IDs from object')
            layout.operator("object.vert_id_transfer_proximity")

        elif context.mode == 'EDIT_MESH':
            layout.separator()
            layout.label(text='Transfer IDs by faces')
            layout.operator("object.copy_vert_id")
            layout.operator("object.paste_vert_id")



class VOT_OT_TransferVertId(bpy.types.Operator):
    """Transfer vert ID by vert proximity"""
    bl_label = "Transfer IDs  by location"
    bl_idname = "object.vert_id_transfer_proximity"
    bl_description = "Transfer verts IDs by vert positions (for meshes with exactly same shape)\nTwo mesh objects have to be selected"
    bl_options = {'REGISTER', 'UNDO'}

    delta: bpy.props.FloatProperty(name="Delta", description="SearchDistance", default=0.1, min=0, max=1, precision = 4)
    def execute(self, context):
        sourceObj = context.active_object

        TargetObjs = [obj for obj in context.selected_objects if obj!=sourceObj and obj.type=='MESH']
        if not TargetObjs:
            self.report({'ERROR'}, 'You seed to select two mesh objects (source then target that will receive vert order)! Cancelling')
            return {'CANCELLED'}

        mesh = sourceObj.data
        size = len(mesh.vertices)
        kdSourceObj = kdtree.KDTree(size)

        for i, v in enumerate(mesh.vertices):
            kdSourceObj.insert(v.co, i)

        kdSourceObj.balance()
        preocessedVertsIdDict = {}
        for target in TargetObjs:
            copiedCount = 0
            preocessedVertsIdDict.clear()
            bm = bmesh.new()  # load mesh
            bm.from_mesh(target.data)
            for targetVert in bm.verts:
                co, index, dist = kdSourceObj.find(targetVert.co)
                if dist<self.delta:  #delta
                    copiedCount+=1
                    targetVert.index = index
                    preocessedVertsIdDict[targetVert]=index
            VOT_OT_PasteVertID.sortOtherVerts(preocessedVertsIdDict, bm.verts)
            bm.verts.sort()
            bm.to_mesh(target.data)
            bm.free()
            self.report({'INFO'}, 'Pasted '+str(copiedCount)+' vert id\'s ')
        return {"FINISHED"}


class VOT_OT_CopyVertID(bpy.types.Operator):
    bl_idname = "object.copy_vert_id"
    bl_label = "Copy Vert IDs"
    bl_description = "Copy verts IDs by topology (you need to selected two faces)\nMesh shape can be different, bu topology must be the same"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.copy_indices.transuv
        active_obj = context.active_object
        self.obj = active_obj
        bm = bmesh.from_edit_mesh(active_obj.data)
        bm.faces.ensure_lookup_table()

        props.topology_copied.clear()

        # get selected faces
        active_face = bm.faces.active
        sel_faces = [face for face in bm.faces if face.select]
        if len(sel_faces) != 2:
            self.report({'WARNING'}, "Two faces must be selected")
            return {'CANCELLED'}
        if not active_face or active_face not in sel_faces:
            self.report({'WARNING'}, "Two faces must be active")
            return {'CANCELLED'}

        # parse all faces according to selection
        active_face_nor = active_face.normal.copy()
        all_sorted_faces = main_parse(self, sel_faces, active_face, active_face_nor)
        if all_sorted_faces:
            for face_data in all_sorted_faces.values():
                # ipdb.set_trace()
                verts = face_data[0]
                vertIndices = [vert.index for vert in verts]
                props.topology_copied.append(vertIndices)

        bmesh.update_edit_mesh(active_obj.data)

        return {'FINISHED'}


class VOT_OT_PasteVertID(bpy.types.Operator):
    bl_idname = "object.paste_vert_id"
    bl_label = "Paste verts Ids"
    bl_description = "Paste verts ID by topology (you need selected two faces matching source obj topology)\nMesh shape can be different, bu topology must be the same"
    bl_options = {'REGISTER', 'UNDO'}

    invert_normals: BoolProperty(name="Invert Normals", description="Invert Normals", default=False)

    @staticmethod
    def sortOtherVerts(preocessedVertsIdDict, allVerts):
        """Prevet verts on other islands from being all shuffled"""
        processedVerts = [v for v in preocessedVertsIdDict.keys()]  # faster that for dict.keys()
        processedIDs = [id for id in preocessedVertsIdDict.values()]
        notProcessedVerts = [v for v in allVerts if v not in processedVerts]
        notProcessedVertsIds = [v.index for v in allVerts if
                                v not in processedVerts]  # it will have duplicated ids from processedIDs that have to be
        # fixed. The rest of numbers are good as ids.

        spareIDS = [i for i in range(len(allVerts)) if (i not in processedIDs and i not in notProcessedVertsIds)]
        for v in notProcessedVerts:
            if v.index in processedIDs:  # if duplicated id found if not processed verts
                v.index = spareIDS.pop(0)  # what if list is empty??

    def execute(self, context):
        props = context.scene.copy_indices.transuv
        active_obj = context.active_object
        bm = bmesh.from_edit_mesh(active_obj.data)
        bm.faces.ensure_lookup_table()

        # get selection history
        all_sel_faces = [
            e for e in bm.select_history
            if isinstance(e, bmesh.types.BMFace) and e.select]
        if len(all_sel_faces) % 2 != 0:
            self.report({'WARNING'}, "Two faces must be selected")
            return {'CANCELLED'}

        # parse selection history
        vertID_dict = {}
        for i, _ in enumerate(all_sel_faces):
            if (i == 0) or (i % 2 == 0):
                continue
            sel_faces = [all_sel_faces[i - 1], all_sel_faces[i]]
            active_face = all_sel_faces[i]

            # parse all faces according to selection history
            active_face_nor = active_face.normal.copy()
            if self.invert_normals:
                active_face_nor.negate()
            all_sorted_faces = main_parse(self, sel_faces, active_face, active_face_nor)
            # ipdb.set_trace()
            if all_sorted_faces:
                # check amount of copied/pasted faces
                if len(all_sorted_faces) != len(props.topology_copied):
                    self.report(
                        {'WARNING'},
                        "Mesh has different amount of faces"
                    )
                    return {'FINISHED'}

                for j, face_data in enumerate(all_sorted_faces.values()):
                    copied_data = props.topology_copied[j]

                    # check amount of copied/pasted verts
                    if len(copied_data) != len(face_data[0]):
                        bpy.ops.mesh.select_all(action='DESELECT')
                        # select problematic face
                        list(all_sorted_faces.keys())[j].select = True
                        self.report(
                            {'WARNING'},
                            "Face have different amount of vertices"
                        )
                        return {'FINISHED'}


                    for k, vert in enumerate(face_data[0]):
                        vert.index = copied_data[k]  #index
                        vertID_dict[vert]=vert.index
        self.sortOtherVerts(vertID_dict, bm.verts)
        bm.verts.sort()
        bmesh.update_edit_mesh(active_obj.data)

        return {'FINISHED'}


def main_parse(self, sel_faces, active_face, active_face_nor):
    all_sorted_faces = OrderedDict()  # This is the main stuff

    used_verts = set()
    used_edges = set()

    faces_to_parse = []

    # get shared edge of two faces
    cross_edges = []
    for edge in active_face.edges:
        if edge in sel_faces[0].edges and edge in sel_faces[1].edges:
            cross_edges.append(edge)

    # parse two selected faces
    if cross_edges and len(cross_edges) == 1:
        shared_edge = cross_edges[0]
        vert1 = None
        vert2 = None

        dot_n = active_face_nor.normalized()
        edge_vec_1 = (shared_edge.verts[1].co - shared_edge.verts[0].co)
        edge_vec_len = edge_vec_1.length
        edge_vec_1 = edge_vec_1.normalized()

        af_center = active_face.calc_center_median()
        af_vec = shared_edge.verts[0].co + (edge_vec_1 * (edge_vec_len * 0.5))
        af_vec = (af_vec - af_center).normalized()

        if af_vec.cross(edge_vec_1).dot(dot_n) > 0:
            vert1 = shared_edge.verts[0]
            vert2 = shared_edge.verts[1]
        else:
            vert1 = shared_edge.verts[1]
            vert2 = shared_edge.verts[0]

        # get active face stuff and uvs
        # ipdb.set_trace()
        face_stuff = get_other_verts_edges(active_face, vert1, vert2, shared_edge)
        all_sorted_faces[active_face] = face_stuff
        used_verts.update(active_face.verts)
        used_edges.update(active_face.edges)

        # get first selected face stuff and uvs as they share shared_edge
        second_face = sel_faces[0]
        if second_face is active_face:
            second_face = sel_faces[1]
        face_stuff = get_other_verts_edges(second_face, vert1, vert2, shared_edge)
        all_sorted_faces[second_face] = face_stuff
        used_verts.update(second_face.verts)
        used_edges.update(second_face.edges)

        # first Grow
        faces_to_parse.append(active_face)
        faces_to_parse.append(second_face)

    else:
        self.report({'WARNING'}, "Two faces should share one edge")
        return None

    # parse all faces
    while True:
        new_parsed_faces = []

        if not faces_to_parse:
            break
        for face in faces_to_parse:
            face_stuff = all_sorted_faces.get(face)
            new_faces = parse_faces(face, face_stuff, used_verts, used_edges, all_sorted_faces)
            if new_faces == 'CANCELLED':
                self.report({'WARNING'}, "More than 2 faces share edge")
                return None

            new_parsed_faces += new_faces
        faces_to_parse = new_parsed_faces

    return all_sorted_faces


def parse_faces(check_face, face_stuff, used_verts, used_edges, all_sorted_faces):
    """recurse faces around the new_grow only"""

    new_shared_faces = []
    for sorted_edge in face_stuff[1]:
        shared_faces = sorted_edge.link_faces
        if shared_faces:
            if len(shared_faces) > 2:
                bpy.ops.mesh.select_all(action='DESELECT')
                for face_sel in shared_faces:
                    face_sel.select = True
                shared_faces = []
                return 'CANCELLED'

            clear_shared_faces = get_new_shared_faces(check_face, sorted_edge, shared_faces, all_sorted_faces.keys())
            if clear_shared_faces:
                shared_face = clear_shared_faces[0]
                # get vertices of the edge
                vert1 = sorted_edge.verts[0]
                vert2 = sorted_edge.verts[1]

                if face_stuff[0].index(vert1) > face_stuff[0].index(vert2):
                    vert1 = sorted_edge.verts[1]
                    vert2 = sorted_edge.verts[0]

                new_face_stuff = get_other_verts_edges(shared_face, vert1, vert2, sorted_edge)
                all_sorted_faces[shared_face] = new_face_stuff
                used_verts.update(shared_face.verts)
                used_edges.update(shared_face.edges)

                new_shared_faces.append(shared_face)

    return new_shared_faces


def get_new_shared_faces(orig_face, shared_edge, check_faces, used_faces):
    shared_faces = []

    for face in check_faces:
        is_shared_edge = shared_edge in face.edges
        not_used = face not in used_faces
        not_orig = face is not orig_face
        not_hide = face.hide is False
        if is_shared_edge and not_used and not_orig and not_hide:
            shared_faces.append(face)

    return shared_faces


def get_other_verts_edges(face, vert1, vert2, first_edge):
    face_edges = [first_edge]
    face_verts = [vert1, vert2]

    other_edges = [edge for edge in face.edges if edge not in face_edges]

    for _ in range(len(other_edges)):
        found_edge = None
        # get sorted verts and edges
        for edge in other_edges:
            if face_verts[-1] in edge.verts:
                other_vert = edge.other_vert(face_verts[-1])

                if other_vert not in face_verts:
                    face_verts.append(other_vert)

                found_edge = edge
                if found_edge not in face_edges:
                    face_edges.append(edge)
                break

        other_edges.remove(found_edge)

    return [face_verts, face_edges]


panels = (
    VOT_PT_CopyVertIds,
)

def update_panel(self, context):
    message = "Vertex Order: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class WertOrderPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: bpy.props.StringProperty( name="Tab Category", description="Choose a name for the category of the panel", default="Tools", update=update_panel )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")
        
        
classes = (
    WertOrderPreferences,
    VOT_OT_TransferVertId,
    VOT_OT_CopyVertID,
    VOT_OT_PasteVertID,
    VOT_PT_CopyVertIds,
)

def register():
    bpy.types.Scene.copy_indices = CopyIDs()
    # bpy.ops.wm.addon_enable(module="space_view3d_copy_attributes")

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    update_panel(None, bpy.context)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.copy_indices

if __name__ == "__main__":
    register()
