# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import bmesh
from . import common
import os
import sys
sys.setrecursionlimit(99999)


class CheckTool():

    def ob_state(self,ob):
        if ob.type == "MESH" and not ob.hide_viewport and not ob.hide_get():
            return True
        return False

    def sel_active(self,ob,mod,sel_all=False):
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode=mod)
        if sel_all:
            bpy.ops.mesh.select_all(action="SELECT")

    def sel_des(self,ob,mod,sel_all=False):
        if sel_all:
            bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode=mod)
        ob.select_set(False)

    def set_sel_mode(self,mode,sel_des=False):
        bpy.ops.mesh.select_mode(type=mode)
        if sel_des:
            bpy.ops.mesh.select_all(action="DESELECT")

    def create_mesh(self,ob):
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        return bm

    def free_mesh(self,ob,bm,apply=False):
        if apply:
            bm.to_mesh(ob.data)
        bm.free()

    def sel_ver_cot(self,ob):
        return ob.data.total_vert_sel

    def loose_cot(self,ob,mode):
        bpy.ops.mesh.select_loose()
        if mode == "VERT":
            cot = ob.data.total_vert_sel
        elif mode == "EDGE":
            cot = ob.data.total_edge_sel
        elif mode == "FACE":
            cot = ob.data.total_face_sel
        return cot

    def find_doubles_cot(self,bm,dist,keep_verts=[]):
        # {"targetmap":{}}
        mutl_ver = bmesh.ops.find_doubles(bm, verts=bm.verts, keep_verts=keep_verts, dist=dist)
        return len(mutl_ver["targetmap"])

    def active_uv_syn(self):
        cur_syn = bpy.context.tool_settings.use_uv_select_sync
        bpy.context.tool_settings.use_uv_select_sync = True
        return cur_syn

    def set_uv_syn(self,state):
        bpy.context.tool_settings.use_uv_select_sync = state

    def action_uv(self,bm):
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.verify()
        return uv_layer

    def uv_cot(self,ob):
        uvw_area = 0.0
        island_info = []
        x_size = 0
        y_size = 0

        x_max_ver = 0
        y_max_ver = 0
        x_min_ver = 0
        y_min_ver = 0
        uv_ex = False

        try:
            island_info = common.get_island_info(ob)
            # print(island_info)
            for i in range(len(island_info)):
                x_size += island_info[i]["size"].x
                y_size += island_info[i]["size"].y

                x_max_ver = island_info[i]["max"].x
                y_max_ver = island_info[i]["max"].y
                x_min_ver = island_info[i]["min"].x
                y_min_ver = island_info[i]["min"].y
                if x_max_ver > 1 or x_max_ver < 0:
                    uv_ex = True
                elif y_max_ver > 1 or y_max_ver < 0:
                    uv_ex = True
                elif x_min_ver < 0 or y_min_ver < 0:
                    uv_ex = True

            if len(island_info) != 0:
                uvw_area = (x_size * y_size) / len(island_info)

            return round(uvw_area,3),uv_ex

        except Exception as e:
            return -1

    def ob_gnon_cot(self,ob):
        '''Start with here'''
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")        
        number = 0
        if bpy.context.scene.check.ngons:
            number = bpy.context.scene.check.ngons_verts_count-1
            
        else:
            number = bpy.context.scene.ui_prop.ngons_count-1
        '''End with here'''
        bpy.ops.mesh.select_face_by_sides(number=number, type='GREATER')
        count = ob.data.total_face_sel
        return count

class CheckModelTool():

    def init(self,mutl_ver_dist=0.0,
            open_ob=True,
            open_loose=True,
            open_mutl=True,
            open_gnons=True,
            open_uv=False,
            open_img=True):

        sc_all_info = []
        ob_info_all_lst = []
        ob_info_err_lst = []

        sc = bpy.context.scene
        self.op_collections_lay()
        dst = self.op_collections()


        sc_obj_cot = 0
        sc_mesh_cot = 0
        sc_mesh_face_cot = 0
        sc_mesh_ver_cot = 0

        sc_mesh_loose_ver_ob_cot = 0
        sc_mesh_loose_ver_cot = 0
        sc_mesh_loose_edg_ob_cot = 0
        sc_mesh_loose_edg_cot = 0
        sc_mesh_loose_fac_ob_cot = 0
        sc_mesh_loose_fac_cot = 0


        sc_mesh_ver_mutl_ob_cot = 0
        sc_mesh_ver_mutl_cot = 0

        sc_mesh_gnon_ob_cot = 0
        sc_mesh_gnon_cot = 0


        # sc_mesh_normal_ob_cot = 0
        # sc_mesh_normal_cot = 0

        sc_mesh_uvw_mutl_ob_cot = 0
        sc_mesh_uvw_mutl_cot = 0
        sc_mesh_uvw_ex_grid_ob_cot = 0

        sc_img_cot = 0
        sc_img_loose_cot = 0
        sc_img_loose_ob_cot = 0

        state = False

        if open_ob == True:
            sc_obj_cot = self.sc_ob_cot(sc)

        for ob in sc.objects:
            if open_ob == True:
                sc_mesh_cot += self.ob_is_mesh(ob)
                sc_mesh_face_cot += self.mesh_faces_cot(ob)
                sc_mesh_ver_cot += self.mesh_ver_cot(ob)

            # --------------------------------------------------

            mesh_loose_ver = "_"
            mesh_loose_edg = "_"
            mesh_loose_fac = "_"
            if open_loose == True:
                mesh_loose_ver = 0
                mesh_loose_edg = 0
                mesh_loose_fac = 0

                mesh_loose = self.mesh_loose_cot(ob)
                mesh_loose_ver = mesh_loose[0]
                if mesh_loose_ver > 0:
                    sc_mesh_loose_ver_ob_cot += 1
                    state = True
                sc_mesh_loose_ver_cot += mesh_loose_ver

                mesh_loose_edg = mesh_loose[1]
                if mesh_loose_edg > 0:
                    sc_mesh_loose_edg_ob_cot += 1
                    state = True
                sc_mesh_loose_edg_cot += mesh_loose_edg

                mesh_loose_fac = mesh_loose[2]
                if mesh_loose_fac > 0:
                    sc_mesh_loose_fac_ob_cot += 1
                    state = True
                sc_mesh_loose_fac_cot += mesh_loose_fac

            # --------------------------------------------------

            mesh_mutl_ver = "_"
            if open_mutl == True:
                mesh_mutl_ver = 0
                mesh_mutl_ver = self.mesh_mutl_ver_cot(ob,mutl_ver_dist)
                if mesh_mutl_ver > 0:
                    sc_mesh_ver_mutl_ob_cot += 1
                    state = True
                sc_mesh_ver_mutl_cot += mesh_mutl_ver

            # --------------------------------------------------

            mesh_non = "_"
            if open_gnons == True:
                mesh_non = 0
                mesh_non = self.check_ob_non(ob)
                if mesh_non > 0:
                    sc_mesh_gnon_ob_cot += 1
                    state = True
                sc_mesh_gnon_cot += mesh_non

            # -------------------------------------------------- 

            mesh_uvw_mutl = "_"
            mesh_uvw_area = "_"
            mesh_uvw_ex_grid = "_"

            if open_uv == True:
                mesh_uvw_mutl = "0"
                mesh_uvw_area = "0"
                mesh_uvw_ex_grid = "0"

                mesh_uvw_mutl = self.check_uvw_mutl_cot(ob)
                if mesh_uvw_mutl > 0:
                    sc_mesh_uvw_mutl_ob_cot += 1
                    sc_mesh_uvw_mutl_cot += mesh_uvw_mutl
                    state = True
                elif mesh_uvw_mutl == -1:
                    state = True
                    mesh_uvw_mutl = "/"


                mesh_uvw_area = self.check_uv_area(ob)
                if mesh_uvw_area == -1:
                    mesh_uvw_area = "/"
                    state = True

                mesh_uvw_ex_grid = self.check_uv_ex_grid(ob)
                if mesh_uvw_ex_grid == True:
                    mesh_uvw_ex_grid = "Overflow"
                    sc_mesh_uvw_ex_grid_ob_cot += 1
                    state = True
                elif mesh_uvw_ex_grid == -1:
                    mesh_uvw_ex_grid = "/"
                    state = True
                else:
                    mesh_uvw_ex_grid = "-"

            # --------------------------------------------------

            image_loose = "_"
            if open_img == True:
                image_loose = 0
                image_loose = self.check_img_loose(ob)
                if image_loose > 0:
                    state = True
                sc_img_loose_ob_cot += image_loose

            # --------------------------------------------------

            ob_name = self.ob_name(ob)
            ob_location = self.ob_location(ob)
            ob_rotation = self.ob_rotation(ob)
            ob_scale = self.ob_scale(ob)
            if state == True:
                ob_info_err_lst.append([
                                        ob_name,
                                        ob_location,
                                        ob_rotation,
                                        ob_scale,
                                        mesh_loose_ver,
                                        mesh_loose_edg,
                                        mesh_loose_fac,
                                        mesh_mutl_ver,
                                        mesh_non,
                                        mesh_uvw_mutl,
                                        mesh_uvw_area,
                                        mesh_uvw_ex_grid,
                                        image_loose,
                                        ])

            ob_info_all_lst.append([
                                    ob_name,
                                    ob_location,
                                    ob_rotation,
                                    ob_scale,
                                    mesh_loose_ver,
                                    mesh_loose_edg,
                                    mesh_loose_fac,
                                    mesh_mutl_ver,
                                    mesh_non,
                                    mesh_uvw_mutl,
                                    mesh_uvw_area,
                                    mesh_uvw_ex_grid,
                                    image_loose,
                                  ])

            state = False


        if open_img == True:
            sc_img_cot = self.img_cot()
            sc_img_loose_cot = self.img_loose_cot()


        sc_all_info = [
                        sc_obj_cot,
                        sc_mesh_cot,
                        sc_mesh_face_cot,
                        sc_mesh_ver_cot,
                        sc_mesh_loose_ver_ob_cot,
                        sc_mesh_loose_ver_cot,
                        sc_mesh_loose_edg_ob_cot,
                        sc_mesh_loose_edg_cot,
                        sc_mesh_loose_fac_ob_cot,
                        sc_mesh_loose_fac_cot,
                        sc_mesh_ver_mutl_ob_cot,
                        sc_mesh_ver_mutl_cot,
                        sc_mesh_gnon_ob_cot,
                        sc_mesh_gnon_cot,
                        sc_mesh_uvw_mutl_ob_cot,
                        sc_mesh_uvw_mutl_cot,
                        sc_mesh_uvw_ex_grid_ob_cot,
                        sc_img_cot,
                        sc_img_loose_cot,
                        sc_img_loose_ob_cot,
                      ]
        self.colse_collections(dst)
        return sc_all_info,ob_info_all_lst,ob_info_err_lst

    def sc_ob_cot(self,sc):
        return len(sc.objects)

    def ob_is_mesh(self,ob):
        if ob.type == "MESH":
            return 1
        return 0

    def mesh_faces_cot(self,ob):
        if ob.type == "MESH":
            return len(ob.data.polygons)
        return 0

    def mesh_ver_cot(self,ob):
        if ob.type == "MESH":
            return len(ob.data.vertices)
        return 0

    def mesh_loose_cot(self,ob,sel_mode=['VERT', 'EDGE', 'FACE']):
        tool = CheckTool()
        cot_ver = 0
        cot_edg = 0
        cot_fac = 0
        if tool.ob_state(ob):
            for i in sel_mode:
                tool.sel_active(ob,"EDIT")
                tool.set_sel_mode(i)

                if i == "VERT":
                    cot_ver += tool.loose_cot(ob,"VERT")
                elif i == "EDGE":
                    cot_edg += tool.loose_cot(ob,"EDGE")
                elif i == "FACE":
                    cot_fac += tool.loose_cot(ob,"FACE")

                tool.sel_des(ob,"OBJECT")

        return cot_ver,cot_edg,cot_fac


    def mesh_mutl_ver_cot(self,ob,dist=0.0):
        tool = CheckTool()
        count = 0
        if tool.ob_state(ob):
            tool.sel_active(ob,"OBJECT")
            bm = tool.create_mesh(ob)

            count = tool.find_doubles_cot(bm,dist)

            tool.free_mesh(ob,bm,True)
            tool.sel_des(ob,"OBJECT")
        return count

    def img_cot(self):
        count = 0
        for img in bpy.data.images:
            if not img.name == "Render Result" and not img.name == "Viewer Node":
                count += 1
        return count

    def img_loose_cot(self):
        count = 0
        for img in bpy.data.images:
            if not img.name == "Render Result" and not img.name == "Viewer Node":
                if not os.path.exists(img.filepath_from_user()):
                    count += 1
        return count

    def check_img_loose(self,ob):
        tool = CheckTool()
        count = 0
        if tool.ob_state(ob):
            for mat in ob.data.materials:
                try:
                    for node in mat.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            try:
                                if not os.path.exists(node.image.filepath_from_user()):
                                    count += 1
                            except Exception as e:
                                count += 1
                except Exception as e:
                    pass
        return count

    def check_uvw_mutl_cot(self,ob):
        tool = CheckTool()
        if tool.ob_state(ob):
            cur_syn = tool.active_uv_syn()
            bm = tool.create_mesh(ob)

            uv_layer = tool.action_uv(bm)

            if bpy.context.tool_settings.use_uv_select_sync:
                sel_faces = [f for f in bm.faces]
            else:
                sel_faces = [f for f in bm.faces if f.select]

            try:
                overlapped_info = common.get_overlapped_uv_info(bm, sel_faces, uv_layer, "FACE")
            except Exception as e:
                return -1

            tool.free_mesh(ob,bm,True)
            tool.set_uv_syn(cur_syn)
            return len(overlapped_info)

        return 0

    def check_uv_area(self,ob):
        tool = CheckTool()
        if tool.ob_state(ob):
            tool.sel_active(ob,"EDIT",True)
            uv_cot = 0
            try:
                uv_cot = tool.uv_cot(ob)[0]
            except Exception:
                tool.sel_des(ob,"OBJECT",True)
                return -1
            tool.sel_des(ob,"OBJECT",True)
            return uv_cot
        return 0

    def check_uv_ex_grid(self,ob):
        tool = CheckTool()
        if tool.ob_state(ob):
            tool.sel_active(ob,"EDIT",True)
            uv_cot = False
            try:
                uv_cot = tool.uv_cot(ob)[1]
            except Exception:
                tool.sel_des(ob,"OBJECT",True)
                return -1
            tool.sel_des(ob,"OBJECT",True)
            return uv_cot
        return False

    def ob_name(self,ob):
        return ob.name

    def ob_location(self,ob):
        return [round(i) for i in ob.location]

    def ob_rotation(self,ob):
        return [round(i) for i in ob.rotation_euler]

    def ob_scale(self,ob):
        return [round(i) for i in ob.scale]

    def check_ob_non(self,ob):
        tool = CheckTool()
        count = 0
        if tool.ob_state(ob):
            tool.sel_active(ob,"EDIT",True)
            tool.set_sel_mode('VERT',True)

            count = tool.ob_gnon_cot(ob)

            tool.sel_des(ob,"OBJECT",True)
        return count

    def op_collections_lay(self):
        bpy.context.view_layer.active_layer_collection.exclude = True
        bpy.context.view_layer.active_layer_collection.exclude = True
        bpy.context.view_layer.active_layer_collection.exclude = True

    def op_collections(self):
        dst=[]
        for i in bpy.data.collections:
            dst.append({i.name_full:i.hide_viewport})
            i.hide_viewport=False
        return dst

    def colse_collections(self,dst):
        for i in range(len(dst)):
            for j in dst[i]:
                bpy.data.collections[j].hide_viewport = dst[i][j]
