
import bmesh
import os
import bpy
import rna_keymap_ui
bl_info = {
	"name": "NGon Loop Select",
	"author": "Amandeep",
	"description": "NGon Edge Loop Selection",
	"blender": (2, 90, 0),
	"version": (1, 0, 0),
	"warning": "",
	"category": "Object",
}

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
kmaps_3dview=["ls.select"]
def draw_hotkeys(col,km_name):
	kc = bpy.context.window_manager.keyconfigs.user
	for kmi in kmaps_3dview:
		km2=kc.keymaps[km_name]
		kmi2=[]
		for a,b in km2.keymap_items.items():
			if a==kmi:
				kmi2.append(b)
		
		if kmi2:
			for a in kmi2:
				col.context_pointer_set("keymap", km2)
				rna_keymap_ui.draw_kmi([], kc, km2, a, col, 0)
class LSPrefs(bpy.types.AddonPreferences):
	bl_idname = __package__
	def draw(self,context):
		layout=self.layout
		draw_hotkeys(layout,'Mesh')
def deselect_all():
	if bpy.context.mode == 'OBJECT':
		bpy.ops.object.select_all(action='DESELECT')
	elif 'EDIT' in bpy.context.mode:
		bpy.ops.mesh.select_all(action='DESELECT')



def get_angle(e1,e2,vert):
	v1=e1.other_vert(vert)
	v3=e2.other_vert(vert)
	a1=vert.co-v1.co
	a2=v3.co-vert.co
	angle=a1.angle(a2)
	return angle
import math
# from collections import OrderedDict
# edges=OrderedDict()
#                     for a in sorted_edge:
#                         new_angle=get_angle(a,active_edge,vert)
#                         edges[str(round(new_angle,2))]=sorted(edges[str(round(new_angle,2))]+[a,],key =lambda x:True if x.index in new_selection else False) if str(round(new_angle,2)) in edges.keys() else [a,]
						
#                     sorted_edges=[]
#                     for key,value in edges.items():
#                         sorted_edges.extend(value)
class LS_OT_Select(bpy.types.Operator):
	bl_idname = "ls.select"
	bl_label = "Loop Select"
	bl_description = "Select Loop"
	bl_options = {"REGISTER", "UNDO"}
	edge_threshold: bpy.props.FloatProperty(default=math.radians(100),name="Edge Threshold",subtype ='ANGLE')
	face_threshold: bpy.props.FloatProperty(default=math.radians(60),name="Face Threshold",subtype ='ANGLE')
	deselect: bpy.props.BoolProperty(default=False, name="Deselect")
	
	def __init__(self):
		self.loc = None
  
	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def invoke(self, context, event):
		self.loc = event.mouse_region_x, event.mouse_region_y
		return self.execute(context)
	
	def execute(self, context):
		active = context.active_object
		bm=bmesh.from_edit_mesh(active.data)
		# re select element under cursor
		bpy.ops.view3d.select(extend=True, deselect=self.deselect, toggle=False, location=self.loc)
  
		if issubclass(type(bm.select_history.active),bmesh.types.BMEdge):
			active_edge=bm.select_history.active
			#print(active_edge)
			# bpy.ops.mesh.loop_multi_select(ring=False)
			# active.data.update()
			# bm=bmesh.from_edit_mesh(active.data)

			# new_selection=[a.index for a in bm.edges if a.select]
			# deselect_all()
			# active_edge=bm.edges[active_edge_index]
			# active_edge.select=True
			og_edge=active_edge
			if active_edge and len(active_edge.link_faces)==2:
				angle=active_edge.calc_face_angle_signed()
				vert=active_edge.other_vert(active_edge.verts[0])
				og_vert=vert
				other_vert=active_edge.verts[0]
				used=[]
				used.append(active_edge.verts[0])
				used.append(active_edge.verts[1])
				while vert:
					#sorted_edge=sorted([e for e in vert.link_edges],key =lambda x:True if [f for f in x.link_faces if f in active_edge.link_faces] else False)
					sorted_edge=sorted([e for e in vert.link_edges],key =lambda x:get_angle(x,active_edge,vert))
					
					l=filter(lambda x:get_angle(x,active_edge,vert)<self.edge_threshold,sorted_edge)
					
					for e in l:
						if e!=active_edge and len(e.link_faces)==2:
							
							if abs(e.calc_face_angle_signed()-angle)<self.face_threshold:
								e.select = not self.deselect
								active_edge=e
								vert=[v for v in e.verts if v!=vert and v not in used]
								if vert:
									vert=vert[0]
									used.append(vert)
								break
					else:
								vert=None
				vert=other_vert
				active_edge=og_edge
				while vert:
					sorted_edge=sorted([e for e in vert.link_edges],key =lambda x:get_angle(x,active_edge,vert))
					
					l=filter(lambda x:get_angle(x,active_edge,vert)<self.edge_threshold,sorted_edge)
					for e in l:
						if e!=active_edge  and len(e.link_faces)==2:
							if abs(e.calc_face_angle_signed()-angle)<self.face_threshold:
								e.select=not self.deselect
								active_edge=e
								vert=[v for v in e.verts if v!=vert and v not in used]
								if vert:
									vert=vert[0]
									used.append(vert)
								break
					else:
								vert=None
				selected_verts=[v for v in bm.verts if v.select]
				vert=other_vert
				active_edge=og_edge
				#print(vert)
				split_verts=get_split_vert(vert,active_edge)
				edges_to_deselect=[]
				if split_verts:

					for split_vert in split_verts:
						
						deselect=False
						
						for e in split_vert.link_edges:
							if e.select:
								(length,edges)=get_path_to_self(vert,e,split_vert)
								
								if length<99999:
									deselect=True
								else:
									edges_to_deselect.append((length,edges))
					edges_to_deselect=sorted(edges_to_deselect,key=lambda x : x[0])
					if deselect:
						for i,e in enumerate(edges_to_deselect):
								for edge in e[1]:
									edge.select=False
				vert=og_vert
				active_edge=og_edge
				#print(vert)
				split_verts=get_split_vert(vert,active_edge)
				edges_to_deselect=[]
				if split_verts:

					for split_vert in split_verts:
						
						deselect=False
						
						for e in split_vert.link_edges:
							if e.select:
								(length,edges)=get_path_to_self(vert,e,split_vert)
								
								if length<99999:
									deselect=True
								else:
									edges_to_deselect.append((length,edges))
					edges_to_deselect=sorted(edges_to_deselect,key=lambda x : x[0])
					if deselect:
						for i,e in enumerate(edges_to_deselect):
								for edge in e[1]:
									edge.select=False
				if self.deselect:
					bpy.ops.view3d.select(deselect=True, extend=False, location=self.loc)
     
				context.active_object.data.update()
			else:
				self.report({'WARNING'},'Edge has more than 2 adjacent faces')
		else:
			self.report({'WARNING'},'Active element must be an edge!')
		return {'FINISHED'}

def get_split_vert(vert,active_edge):
	used=[]
	split_verts=[]
	while vert:
		sorted_edge=[e for e in vert.link_edges if e.select]
		if sorted_edge:
				
			for e in sorted_edge:
				if e!=active_edge:
						active_edge=e
						vert=[v for v in e.verts if v!=vert and v not in used]
						if vert:
							vert=vert[0]
							used.append(vert)
							#print(vert)
							#print([e for e in vert.link_edges if e.select])
							if len([e for e in vert.link_edges if e.select])==3:
								split_verts.append(vert)
								break

						break
			else:
						vert=None
		else:
			vert=None
	return split_verts
def get_path_to_self(vert,active_edge,split_vert):
	og_vert=vert
   # print("Target",vert)
	vert=active_edge.other_vert(split_vert)
	#print("OG",vert)
	used=[]
	length=0
	edges=[active_edge,]
	visited_edges=[]
	if vert==og_vert:
		return (active_edge.calc_length(),[])
	while vert:
		sorted_edge=[e for e in vert.link_edges if e.select]
		if sorted_edge:
				
			for e in sorted_edge:
				if e!=active_edge and e not in visited_edges:
						length+=e.calc_length()
						active_edge=e
						edges.append(e)
						visited_edges.append(e)
						#print("Used",used)
						#print("All",[v for v in e.verts])
						vert=[v for v in e.verts if v!=vert and v not in used]
						#print("Verts",vert)
						if vert and vert[0]==og_vert:
							return (length,edges)
						if vert:
							vert=vert[0]
							used.append(vert)
						
						break
			else:
						vert=None
		else:
			vert=None
	return (9999999999,edges)

classes = (LS_OT_Select,LSPrefs
		   )
icon_collection = {}
addon_keymaps = []


def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	km = kc.keymaps.new(name="Mesh", space_type="EMPTY")
	if kc:
		

		kmi = km.keymap_items.new(
			"ls.select",
			type='D',
			value="PRESS",
		)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new(
			"ls.select",
			type='LEFTMOUSE',
			value="DOUBLE_CLICK",
		)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new(
			"ls.select",
			type='LEFTMOUSE',
			value="DOUBLE_CLICK",shift=True
		)
		addon_keymaps.append((km, kmi))



def unregister():

	from bpy.utils import unregister_class

	for cls in reversed(classes):
		unregister_class(cls)
	for (km, kmi) in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()


if __name__ == "__main__":
	register()
