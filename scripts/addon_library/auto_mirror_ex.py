# b2.80~ update by Bookyakuno
####################################################################
# Quickly set up mirror modifiers and assist mirror modifiers
# Detailed authorship:
#  Bookyakuno(Current support b2.80~)
#  Lapineige(AutoMirror ~b2.79),
#  Robert Fornof & MX(MirrorMirror ~b2.79),
####################################################################


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
	"name": "Auto Mirror EX",
	"description": "Super fast cutting and mirroring for mesh",
	"author": "Lapineige, Robert Fornof & MX, Bookyakuno(Blender2.8 Update)",
	"version": (2, 9, 4),
	"blender": (2, 93, 0),
	"location": "View 3D > Sidebar > Tools tab > AutoMirror (panel)",
	"warning": "",
	"wiki_url": "https://bookyakuno.com/auto-mirror/",
	"category": "Mesh"}


import bpy
import rna_keymap_ui # Required for displaying keymap list Menu
from mathutils import Vector
from bpy.props import *
from bpy.types import (
		Operator,
		Menu,
		Panel,
		PropertyGroup,
		AddonPreferences,
		)


mod_items = [
	("DATA_TRANSFER", "Data Transfer","","MOD_DATA_TRANSFER",0),
	("MESH_CACHE", "Mesh Cache","","MOD_MESH_CACHE",1),
	("MESH_SEQUENCE_CACHE", "Mesh Sequence Cache","","MOD_MESH_SEQUENCE_CACHE",2),
	("NORMAL_EDIT", "Normal Edit","","MOD_NORMALEDIT",3),
	("WEIGHTED_NORMAL", "Weighted Normal","","MOD_NORMALEDIT",4),
	("UV_PROJECT", "UV Project","","MOD_UVPROJECT",5),
	("UV_WARP", "UV Warp","","MOD_UVPROJECT",6),
	("VERTEX_WEIGHT_EDIT", "Vertex Weight Edit","","MOD_VERTEX_WEIGHT",7),
	("VERTEX_WEIGHT_MIX", "Vertex Weight Mix","","MOD_VERTEX_WEIGHT",8),
	("VERTEX_WEIGHT_PROXIMITY", "Vertex Weight Proximity","","MOD_VERTEX_WEIGHT",9),
	("____", "____","","BLANK1",10),
	("ARRAY", "Array","","MOD_ARRAY",11),
	("BEVEL", "Bevel","","MOD_BEVEL",12),
	("BOOLEAN", "Boolean","","MOD_BOOLEAN",13),
	("BUILD", "Build","","MOD_BUILD",14),
	("DECIMATE", "Decimate","","MOD_DECIM",15),
	("EDGE_SPLIT", "Edge Split","","MOD_EDGESPLIT",16),
	("MASK", "Mask","","MOD_MASK",17),
	("MIRROR", "Mirror","","MOD_MIRROR",18),
	("MULTIRES", "Multiresolution","","MOD_MULTIRES",19),
	("REMESH", "Remesh","","MOD_REMESH",20),
	("SCREW", "Screw","","MOD_SCREW",21),
	("SKIN", "Skin","","MOD_SKIN",22),
	("SOLIDIFY", "Solidify","","MOD_SOLIDIFY",23),
	("SUBSURF", "Subdivision Surface","","MOD_SUBSURF",24),
	("TRIANGULATE", "Triangulate","","MOD_TRIANGULATE",25),
	("WIREFRAME", "Wireframe","","MOD_WIREFRAME",26),
	("____", "____","","BLANK1",27),
	("WELD", "Weld","","MOD_WELD",28),
	("ARMATURE", "Armature","","MOD_ARMATURE",29),
	("CAST", "Cast","","MOD_CAST",30),
	("CURVE", "Curve","","MOD_CURVE",31),
	("DISPLACE", "Displace","","MOD_DISPLACE",32),
	("HOOK", "Hook","","HOOK",33),
	("LAPLACIANDEFORM", "Laplacian Deform","","MOD_LAPLACIANDEFORM",34),
	("LATTICE", "Lattice","","MOD_LATTICE",35),
	("MESH_DEFORM", "Mesh Deform","","MOD_MESH_DEFORM",36),
	("SHRINKWRAP", "Shrinkwrap","","MOD_SHRINKWRAP",37),
	("SIMPLE_DEFORM", "Simple Deform","","MOD_SIMPLEDEFORM",38),
	("SMOOTH", "Smooth","","MOD_SMOOTH",39),
	("CORRECTIVE_SMOOTH", "Smooth Corrective","","MOD_SMOOTH",40),
	("LAPLACIANSMOOTH", "Smooth Laplacian","","MOD_SMOOTH",41),
	("SURFACE_DEFORM", "Surface Deform","","MOD_MESHDEFORM",42),
	("WARP", "Warp","","MOD_WARP",43),
	("WAVE", "Wave","","MOD_WAVE",44),
	("____", "____","","BLANK1",45),
	("CLOTH", "Cloth","","MOD_CLOTH",46),
	("COLLISION", "Collision","","MOD_COLLISION",47),
	("DYNAMIC_PAINT", "Dynamic Paint","","MOD_DYNAMIC_PAINT",48),
	("EXPLODE", "Explode","","MOD_EXPLODE",49),
	("OCEAN", "Ocean","","MOD_OCEAN",50),
	("PARTICLE_INSTANCE", "Particle Instance","","MOD_PARTICLE_INSTANCE",51),
	("PARTICLE_SYSTEM", "Particle System","","PARTICLES",52),
	("FLUID", "Fluid Simulation","","MOD_FLUID",53),
	("SOFT_BODY", "Soft Body","","MOD_SOFT",54),
	("SURFACE", "Surface","","MOD_SURFACE",55),
	]


def get_mode_name(mod_type):
	if mod_type == "DATA_TRANSFER": return "Data Transfer"
	if mod_type == "MESH_CACHE": return "Mesh Cache"
	if mod_type == "MESH_SEQUENCE_CACHE": return "Mesh Sequence Cache"
	if mod_type == "NORMAL_EDIT": return "Normal Edit"
	if mod_type == "WEIGHTED_NORMAL": return "Weighted Normal"
	if mod_type == "UV_PROJECT": return "UV Project"
	if mod_type == "UV_WARP": return "UV Warp"
	if mod_type == "VERTEX_WEIGHT_EDIT": return "Vertex Weight Edit"
	if mod_type == "VERTEX_WEIGHT_MIX": return "Vertex Weight Mix"
	if mod_type == "VERTEX_WEIGHT_PROXIMITY": return "Vertex Weight Proximity"
	if mod_type == "____": return "____"
	if mod_type == "ARRAY": return "Array"
	if mod_type == "BEVEL": return "Bevel"
	if mod_type == "BOOLEAN": return "Boolean"
	if mod_type == "BUILD": return "Build"
	if mod_type == "DECIMATE": return "Decimate"
	if mod_type == "EDGE_SPLIT": return "Edge Split"
	if mod_type == "MASK": return "Mask"
	if mod_type == "MIRROR": return "Mirror"
	if mod_type == "MULTIRES": return "Multiresolution"
	if mod_type == "REMESH": return "Remesh"
	if mod_type == "SCREW": return "Screw"
	if mod_type == "SKIN": return "Skin"
	if mod_type == "SOLIDIFY": return "Solidify"
	if mod_type == "SUBSURF": return "Subdivision Surface"
	if mod_type == "TRIANGULATE": return "Triangulate"
	if mod_type == "WIREFRAME": return "Wireframe"
	if mod_type == "____": return "____"
	if mod_type == "WELD": return "Weld"
	if mod_type == "ARMATURE": return "Armature"
	if mod_type == "CAST": return "Cast"
	if mod_type == "CURVE": return "Curve"
	if mod_type == "DISPLACE": return "Displace"
	if mod_type == "HOOK": return "Hook"
	if mod_type == "LAPLACIANDEFORM": return "Laplacian Deform"
	if mod_type == "LATTICE": return "Lattice"
	if mod_type == "MESH_DEFORM": return "Mesh Deform"
	if mod_type == "SHRINKWRAP": return "Shrinkwrap"
	if mod_type == "SIMPLE_DEFORM": return "Simple Deform"
	if mod_type == "SMOOTH": return "Smooth"
	if mod_type == "CORRECTIVE_SMOOTH": return "Smooth Corrective"
	if mod_type == "LAPLACIANSMOOTH": return "Smooth Laplacian"
	if mod_type == "SURFACE_DEFORM": return "Surface Deform"
	if mod_type == "WARP": return "Warp"
	if mod_type == "WAVE": return "Wave"
	if mod_type == "____": return "____"
	if mod_type == "CLOTH": return "Cloth"
	if mod_type == "COLLISION": return "Collision"
	if mod_type == "DYNAMIC_PAINT": return "Dynamic Paint"
	if mod_type == "EXPLODE": return "Explode"
	if mod_type == "OCEAN": return "Ocean"
	if mod_type == "PARTICLE_INSTANCE": return "Particle Instance"
	if mod_type == "PARTICLE_SYSTEM": return "Particle System"
	if mod_type == "FLUID": return "Fluid Simulation"
	if mod_type == "SOFT_BODY": return "Soft Body"
	if mod_type == "SURFACE": return "Surface"

# Changing the category in which the panel menu is displayed
# Executed when Blender starts or when a checkbox is changed
def update_panel(self, context):
	message = ": Updating Panel locations has failed"
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


# Add / Remove keymap
# Executed when Blender starts or when a checkbox is changed
def update_keymap(self, context):
	try:
		addon_prefs = bpy.context.preferences.addons[__name__].preferences
		if addon_prefs.keymap_automirror:
			add_keymap_automirror()
		else:
			remove_keymap_automirror()
	except:
		pass


class AUTOMIRROR_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__

	category          : StringProperty(name="Tab Category", description="Choose a name for the category of the panel", default="Edit", update=update_panel)
	keymap_automirror : BoolProperty(name = "Add Keymap (X/Y/Z/F + Shift + alt)", update = update_keymap)
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[('Option', "Option", "","DOT",0),('Keymap', "Keymap", "","KEYINGSET",1), ('Link', "Link", "","URL",2)], default='Option')

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "tab_addon_menu",expand=True)
		if self.tab_addon_menu=="Option":
			box = layout.box()

			row = box.row()
			col = row.column()
			col.label(text="Tab Category:")
			col.prop(self, "category", text="")

		# Keymap
		# Search the keymap that matches the operator name and the property status of the keymap registered with the add-on from the Blender keymap setting and display it in the menu
		if self.tab_addon_menu=="Keymap":
			box = layout.box()
			box.prop(self, "keymap_automirror")
			if self.keymap_automirror:
				col = box.column()
				col.label(text="Keymap List:",icon="KEYINGSET")


				wm = bpy.context.window_manager
				kc = wm.keyconfigs.user
				old_km_name = ""
				get_kmi_l = []
				for km_add, kmi_add in addon_keymaps:
					for km_con in kc.keymaps:
						if km_add.name == km_con.name:
							km = km_con
							break

					for kmi_con in km.keymap_items:
						if kmi_add.idname == kmi_con.idname:
							if kmi_add.name == kmi_con.name:
								get_kmi_l.append((km,kmi_con))

				get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

				for km, kmi in get_kmi_l:
					if not km.name == old_km_name:
						col.label(text=str(km.name),icon="DOT")
					col.context_pointer_set("keymap", km)
					rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
					col.separator()
					old_km_name = km.name


		if self.tab_addon_menu=="Link":
			box = layout.box()
			col = box.column(align=True)
			col.label(text="Store Site")
			row = col.row()
			row.operator("wm.url_open", text="gumroad", icon="URL").url = "https://bookyakuno.com/auto-mirror/"
			col.separator()
			col.label(text="Description")
			row = col.row()
			row.operator("wm.url_open", text="Blender Artists", icon="URL").url = "https://blenderartists.org/t/auto-mirror-blender2-8-ver/1151539"
			row.operator("wm.url_open", text="Japanese - bookyakuno.com", icon="URL").url = "https://bookyakuno.com/auto-mirror/"
			col.separator()
			col.label(text="Old version")
			row = col.row()
			row.operator("wm.url_open", text="Old version 2.7x - github", icon="URL").url = "https://github.com/lapineige/Blender_add-ons/blob/master/AutoMirror/AutoMirror_V2-4.py"
			# row.operator("wm.url_open", text="MirrorMirror - github", icon="URL").url = "https://github.com/fornof/BlenderAddons/blob/master/MirrorMirrorTool.py"

		#


class AUTOMIRROR_OT_MirrorMirror(Operator):
	"""Mirror to the selected object"""
	bl_idname = "automirror.mirror_mirror"
	bl_label = "MirrorMirror"
	bl_description = "Mirror another object to an axis.\n First select the objects you want to mirror,\n Second select the objects you want to be axis and then execute.\n Set up a regular mirror if there is only one selected object"
	bl_options = {'REGISTER', 'UNDO'}

	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)
	use_existing_mod : BoolProperty(name="Use existing mirror modifier",description="Use existing mirror modifier")
	axis_x           : BoolProperty(default=True,name="Axis X")
	axis_y           : BoolProperty(name="Axis Y")
	axis_z           : BoolProperty(name="Axis Z")
	use_bisect_axis           : BoolProperty(name="Bisect")
	use_bisect_flip_axis           : BoolProperty(name="Bisect Flip")
	apply_mirror : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")

	def invoke(self, context, event):
		props = bpy.context.scene.automirror
		props.mm_target_obj = bpy.context.view_layer.objects.active
		return self.execute(context)

	@classmethod
	def poll(cls, context):
		return len(bpy.context.selected_objects)

	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self,"axis_x",text="X",icon="BLANK1",emboss=True)
		row.prop(self,"axis_y",text="Y",icon="BLANK1",emboss=True)
		row.prop(self,"axis_z",text="Z",icon="BLANK1",emboss=True)

		layout.prop(self,"sort_top_mod")
		layout.prop(self,"use_bisect_axis")
		layout.prop(self,"use_bisect_flip_axis")


		row = layout.row(align=True)
		row.label(text="",icon="CHECKBOX_HLT")
		row.prop(self, "apply_mirror", text="Apply Modifier")



	def run_mirror_mirror_mesh(self, context, obj, tgt_obj):
		mod = obj.modifiers.new("mirror_mirror","MIRROR")
		mod.use_axis[0] = False
		mod.use_axis[1] = False
		mod.use_axis[2] = False
		if self.axis_x:
			mod.use_axis[0] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[0] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[0] = True

		if self.axis_y:
			mod.use_axis[1] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[1] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[1] = True

		if self.axis_z:
			mod.use_axis[2] = True
			if self.use_bisect_axis:
				mod.use_bisect_axis[2] = True
				if self.use_bisect_flip_axis:
					mod.use_bisect_flip_axis[2] = True
		if tgt_obj:
			mod.mirror_object = tgt_obj

		sort_top_mod(self,context,obj,mod,1)

		if self.apply_mirror:
			current_mode = obj.mode
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.modifier_apply(modifier= mod.name)
			bpy.ops.object.mode_set(mode=current_mode)
		return mod


	def run_mirror_mirror_gp(self, context, obj, tgt_obj):
		mod = obj.grease_pencil_modifiers.new("mirror_mirror","GP_MIRROR")
		x = False
		y = False
		z = False
		if self.axis_x:
			x = True
		if self.axis_y:
			y = True
		if self.axis_z:
			z = True
		mod.use_axis_x = x
		mod.use_axis_y = y
		mod.use_axis_z = z
		if tgt_obj:
			mod.object = tgt_obj

		sort_top_mod(self,context,obj,mod,1)

		if self.apply_mirror:
			current_mode = obj.mode
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.gpencil_modifier_apply(modifier= mod.name)
			bpy.ops.object.mode_set(mode=current_mode)
		return mod

	def execute(self, context):
		props = bpy.context.scene.automirror


		# info text
		info_text = "Add"
		X = "*"
		Y = "*"
		Z = "*"
		if self.axis_x:
			X = "X"
		if self.axis_y:
			Y = "Y"
		if self.axis_z:
			Z = "Z"
		if self.apply_mirror:
			info_text = "Apply"


		# main run
		if len(bpy.context.selected_objects) == 1:
			obj = bpy.context.object
			if obj.type=="GPENCIL":
				self.run_mirror_mirror_gp(context, obj, None)
			else:
				self.run_mirror_mirror_mesh(context, obj, None)

			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s]" % (info_text, X, Y, Z))
			return{'FINISHED'}
		else:
			# Multi selected object
			tgt_obj = bpy.context.view_layer.objects.active
			tgt_obj.select_set(False)

			for obj in bpy.context.selected_objects:
				bpy.context.view_layer.objects.active = obj
				if obj.type=="GPENCIL":
					self.run_mirror_mirror_gp(context, obj, tgt_obj)
				else:
					self.run_mirror_mirror_mesh(context, obj, tgt_obj)

			sel_obj = str(len(bpy.context.selected_objects))
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s] to %s object" % (info_text, X, Y, Z, sel_obj))


		return {'FINISHED'}


class AUTOMIRROR_OT_mirror_toggle(Operator):
	'''Switch on / off the Mirror Modifier'''
	bl_idname = "automirror.toggle_mirror"
	bl_label = "Toggle Mirror"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Switch on / off the Mirror Modifier"


	show_viewport     : BoolProperty(name="Viewport",default=True)
	show_render     : BoolProperty(name="Render")
	show_in_editmode     : BoolProperty(name="In edit mode")
	show_on_cage     : BoolProperty(name="On cage")

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mod_items
	mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")
		# row = col.row(align=True)
		# row.prop(self, "move_count")

		row = layout.row(align=True)
		row.prop(self, "show_render",text="",icon="RESTRICT_RENDER_OFF" if self.show_render else "RESTRICT_RENDER_ON")
		row.prop(self, "show_viewport",text="",icon="RESTRICT_VIEW_OFF" if self.show_viewport else "RESTRICT_VIEW_ON")
		row.prop(self, "show_in_editmode",text="",icon="EDITMODE_HLT")
		row.prop(self, "show_on_cage",text="",icon="OUTLINER_DATA_MESH")



	def toggle_status(self, context,mod):
		if self.show_viewport:
			if mod.show_viewport == True:
				mod.show_viewport = False
			else:
				mod.show_viewport = True

		if self.show_render:
			if mod.show_render == True:
				mod.show_render = False
			else:
				mod.show_render = True

		if self.show_in_editmode:
			if mod.show_in_editmode == True:
				mod.show_in_editmode = False
			else:
				mod.show_in_editmode = True

		if self.show_on_cage:
			if mod.show_on_cage == True:
				mod.show_on_cage = False
			else:
				mod.show_on_cage = True


	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if not len(obj.modifiers):
				continue
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						self.toggle_status(context,mod)
				else:
					if mod.type == self.mod_type:
						self.toggle_status(context,mod)


		bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}


class AUTOMIRROR_OT_mirror_target_set(Operator):
	'''Set the Active object as the 'mirror target object' of the mirror modifier'''
	bl_idname = "automirror.target_set"
	bl_label = "Target Set"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Set the Active object as the 'mirror target object' of the mirror modifier"

	clear : BoolProperty(name="Clear")
	only : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="mirror_mirror",name="Modifier Name")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self, "clear")

		col = layout.column(align=True)
		col.prop(self, "only")
		row = col.row(align=True)
		if not self.only:
			row.active=False
		row.prop(self, "mod_name")

	def execute(self, context):
		if self.clear:
			try:
				for obj in bpy.context.selected_objects:
					for mod in obj.modifiers:
						if mod.type == "MIRROR":
							if self.only:
								if mod.name == self.mod_name:
									mod.mirror_object = None
							else:
								mod.mirror_object = None
			except: pass
			return {'FINISHED'}


		act_obj = bpy.context.object
		try:
			for obj in bpy.context.selected_objects:
				if obj == act_obj:
					continue
				for mod in obj.modifiers:
					if mod.type == "MIRROR":
						if self.only:
							if mod.name == self.mod_name:
								mod.mirror_object = act_obj
						else:
							mod.mirror_object = act_obj
		except: pass

		return {'FINISHED'}


class AUTOMIRROR_OT_modifier_add(Operator):
	bl_idname = "automirror.modifier_add"
	bl_label = "Add Modifier"
	bl_description = "Add a specific modifier on the selected object"
	bl_options = {'REGISTER', 'UNDO'}

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="",name="Modifier Name")

	global mod_items
	mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")

	def execute(self, context):
		# old_act = bpy.context.view_layer.objects.active
		if self.mod_name:
			mod_name = self.mod_name
		else:
			mod_name = get_mode_name(self.mod_type)

		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			mod = obj.modifiers.new(mod_name,self.mod_type)

		# bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}

class AUTOMIRROR_OT_mirror_apply(Operator):
	'''Apply a specific modifier on the selected object'''
	bl_idname = "automirror.apply"
	bl_label = "Apply Modifier"
	bl_description = "Apply a specific modifier on the selected object"
	bl_options = {'REGISTER', 'UNDO'}

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mod_items
	mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")

	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						bpy.ops.object.modifier_apply(modifier=mod.name)
				else:
					if mod.type == self.mod_type:
						bpy.ops.object.modifier_apply(modifier=mod.name)

		bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}


class AUTOMIRROR_OT_mirror_remove(Operator):
	'''Remove a specific modifier on the selected object'''
	bl_idname = "automirror.remove"
	bl_label = "Remove Modifier"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Remove a specific modifier on the selected object"

	only_same_name : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mod_items
	mod_type         : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")

	def execute(self, context):
		for obj in bpy.context.selected_objects:
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						obj.modifiers.remove(modifier=mod)
				else:
					if mod.type == self.mod_type:
						obj.modifiers.remove(modifier=mod)


		return {'FINISHED'}


class AUTOMIRROR_OT_modifier_sort(Operator):
	bl_idname = "automirror.modifier_sort"
	bl_label = "Modifier Sort"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}


	is_down     : BoolProperty(name="Down")
	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")
	move_count : IntProperty(default=0,name="Move Count",min=0)

	global mod_items
	mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")
		col.separator()
		row = col.row(align=True)
		row.label(text="",icon="SORT_ASC")
		row.prop(self, "is_down")
		row = col.row(align=True)
		row.label(text="",icon="BLANK1")
		row.prop(self, "move_count")

	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if not len(obj.modifiers) > 1:
				continue
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						self.mod_sort_fanc(context,obj,mod)

				else:
					if mod.type == self.mod_type:
						self.mod_sort_fanc(context,obj,mod)


		bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}


	def mod_sort_fanc(self, context, obj, mod):
			if self.move_count == 0:
				modindex = len(obj.modifiers) - self.move_count
			else:
				modindex = self.move_count

			for i in range(modindex):
				if self.is_down:
					bpy.ops.object.modifier_move_down(modifier=mod.name)
				else:
					bpy.ops.object.modifier_move_up(modifier=mod.name)




		# モディファイアの数だけ繰り返して一番最初に移動する
		# modindex = len(obj.modifiers)
		#
		# # if self.move_count < 0:
		# # 	modindex = len(obj.modifiers) - self.move_count
		# # else:
		# # 	modindex = len(obj.modifiers) - self.move_count
		# #
		# #
		# for i in range(modindex):
		# 	# 順番が同じなら終了
		# 	tgt_mod_index = obj.modifiers.find(mod.name)
		# 	if tgt_mod_index == len(obj.modifiers):
		# 		return
		# 	if self.move_count < 0:
		#
		#
		# 		bpy.ops.object.modifier_move_down(modifier=mod.name)
		# 	else:
		# 		if tgt_mod_index == 0:
		# 			return
		# 		bpy.ops.object.modifier_move_up(modifier=mod.name)


class AUTOMIRROR_OT_main(Operator):
	""" Automatically cut an object along an axis """
	bl_idname = "automirror.automirror"
	bl_label = "AutoMirror"
	bl_options = {'REGISTER', 'UNDO'}

	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)

	apply_mirror : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")
	cut          : BoolProperty(default= True, description="If enabeled, cut the mesh in two parts and mirror it. If not, just make a loopcut")
	show_on_cage : BoolProperty(description="Enable to edit the cage (it's the classical modifier's option)")
	threshold    : FloatProperty(default= 0.001, min= 0, description="Vertices closer than this distance are merged on the loopcut")
	toggle_edit  : BoolProperty(default= False, description="If not in edit mode, change mode to edit")
	use_clip     : BoolProperty(default=True, description="Use clipping for the mirror modifier")

	axis_x : BoolProperty(name="Axis X",default=True)
	axis_y : BoolProperty(name="Axis Y")
	axis_z : BoolProperty(name="Axis Z")


	axis_quick_override : BoolProperty(name="axis_quick_override", description="Axis used by the mirror modifier")

	orientation  : EnumProperty(description="Choose the side along the axis of the editable part (+/- coordinates)",items = [
	("positive", "Positive", "", "ADD", 0),
	("negative", "Negative","", "REMOVE", 1)])



	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == "MESH"

	def invoke(self, context, event):
		props = bpy.context.scene.automirror
		self.apply_mirror = props.apply_mirror
		self.cut = props.cut
		self.show_on_cage = props.show_on_cage
		self.threshold = props.threshold
		self.toggle_edit = props.toggle_edit
		self.use_clip = props.use_clip
		self.orientation = props.orientation

		if not self.axis_quick_override:
			self.axis_x = props.axis_x
			self.axis_y = props.axis_y
			self.axis_z = props.axis_z

		return self.execute(context)


	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self,"axis_x",text="X",toggle=True)
		row.prop(self,"axis_y",text="Y",toggle=True)
		row.prop(self,"axis_z",text="Z",toggle=True)

		row = layout.row(align=True)
		row.prop(self, "orientation", text="Orientation", expand=True)
		layout.prop(self, "threshold", text="Threshold")
		layout.prop(self, "toggle_edit", text="Toggle Edit")
		layout.prop(self, "cut", text="Cut and Mirror")
		if self.cut:
			layout.label(text="Mirror Modifier:")
			row = layout.row(align=True)
			row.label(text="",icon="AUTOMERGE_ON")
			row.prop(self, "use_clip", text="Use Clip")
			row = layout.row(align=True)
			row.label(text="",icon="OUTLINER_DATA_MESH")
			row.prop(self, "show_on_cage", text="Editable")
			row = layout.row(align=True)
			row.label(text="",icon="SORT_DESC")
			row.prop(self, "sort_top_mod")
			row = layout.row(align=True)
			row.label(text="",icon="CHECKBOX_HLT")
			row.prop(self, "apply_mirror", text="Apply Modifier")
		else:
			layout.label(text="Only Bisect")

	def get_local_axis_vector(self, context, X, Y, Z, orientation,obj):
		loc = obj.location
		bpy.ops.object.mode_set(mode="OBJECT") # Needed to avoid to translate vertices

		v1 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(X*orientation, Y*orientation, Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')
		v2 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(-X*orientation, -Y*orientation, -Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')

		bpy.ops.object.mode_set(mode="EDIT")

		return v2-v1

	def bisect_main(self, context, X, Y, Z, orientation,obj):
		cut_normal = self.get_local_axis_vector(context, X, Y, Z, orientation,obj)
		# plane_no=[X*orientation,Y*orientation,Z*orientation],

		# Cut the mesh
		bpy.ops.mesh.bisect(
				plane_co=(
				obj.location[0],
				obj.location[1],
				obj.location[2]
				),
				plane_no=cut_normal,
				use_fill= False,
				clear_inner= self.cut,
				clear_outer= 0,
				threshold= self.threshold)


	def execute(self, context):
		props = bpy.context.scene.automirror
		sc = bpy.context.scene
		if not (self.axis_x or self.axis_y or self.axis_z):
			self.report({'WARNING'}, "No axis")
			return {'FINISHED'}


		# info text
		info_text = "Add"
		text_X = "*"
		text_Y = "*"
		text_Z = "*"
		if self.axis_x:
			text_X = "X"
		if self.axis_y:
			text_Y = "Y"
		if self.axis_z:
			text_Z = "Z"
		if self.apply_mirror:
			info_text = "Apply"

		if self.orientation == 'positive':
			orientation = 1
		else:
			orientation = -1

		# 選択オブジェクトを回す
		old_obj = bpy.context.view_layer.objects.active
		old_sel = bpy.context.selected_objects
		for obj in bpy.context.selected_objects:
			obj.select_set(False)

		for obj in old_sel:
			if obj.type == "MESH":
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				X,Y,Z = 0,0,0
				current_mode = obj.mode # Save the current mode

				if obj.mode != "EDIT":
					bpy.ops.object.mode_set(mode="EDIT") # Go to edit mode

				##############################################
				# 反対側を削除
				if self.axis_x:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 1
					Y = 0
					Z = 0
					self.bisect_main(context, X, Y, Z, orientation,obj)

				if self.axis_y:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 0
					Y = 1
					Z = 0
					self.bisect_main(context, X, Y, Z, orientation,obj)

				if self.axis_z:
					bpy.ops.mesh.select_all(action='SELECT')
					X = 0
					Y = 0
					Z = 1
					self.bisect_main(context, X, Y, Z, orientation,obj)


				##############################################
				# Modifier
				if self.cut:
					mod = obj.modifiers.new("Mirror","MIRROR")
					mod.use_axis[0] = self.axis_x # Choose the axis to use, based on the cut's axis
					mod.use_axis[1] = self.axis_y
					mod.use_axis[2] = self.axis_z
					mod.use_clip = self.use_clip
					mod.show_on_cage = self.show_on_cage

					sort_top_mod(self,context,obj,mod,1)

					if self.apply_mirror:
						bpy.ops.object.mode_set(mode='OBJECT')
						bpy.ops.object.modifier_apply(modifier= mod.name)
						if self.toggle_edit:
							bpy.ops.object.mode_set(mode='EDIT')
						else:
							bpy.ops.object.mode_set(mode=current_mode)


				if not self.toggle_edit:
					bpy.ops.object.mode_set(mode=current_mode) # Reload previous mode
				obj.select_set(False)


		for obj in old_sel:
			obj.select_set(True)
		bpy.context.view_layer.objects.active = old_obj



		# 変更した設定をシーン設定に反映
		props.apply_mirror = self.apply_mirror
		props.cut = self.cut
		props.show_on_cage = self.show_on_cage
		props.threshold = self.threshold
		props.toggle_edit = self.toggle_edit
		props.use_clip = self.use_clip
		props.orientation = self.orientation

		if not self.axis_quick_override:
			props.axis_x = self.axis_x
			props.axis_y = self.axis_y
			props.axis_z = self.axis_z
		else:
			self.axis_quick_override = False

		if len(bpy.context.selected_objects) == 1:
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s]" % (info_text, text_X, text_Y, text_Z))
		else:
			sel_obj = str(len(bpy.context.selected_objects))
			self.report({'INFO'}, "%s Mirror Modifier [%s,%s,%s] to %s object" % (info_text, text_X, text_Y, text_Z, sel_obj))

		return {'FINISHED'}


def sort_top_mod(self,context,obj,mod,move_count):
	old_act = bpy.context.view_layer.objects.active

	bpy.context.view_layer.objects.active = obj

	if not self.sort_top_mod:
		return

	if not len(obj.modifiers) > 1:
		return

	modindex = len(obj.modifiers) - move_count
	for i in range(modindex):
		bpy.ops.object.modifier_move_up(modifier=mod.name)


	bpy.context.view_layer.objects.active = old_act


class AUTOMIRROR_PT_panel(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tools'
	bl_label = "Auto Mirror"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		obj = bpy.context.object
		return obj is not None


	def draw(self, context):
		layout = self.layout
		props = bpy.context.scene.automirror

		box = layout.box()
		row = box.row(align=True)
		row.scale_y = 1.2
		row.operator("automirror.automirror")
		row.separator()
		rows = row.row(align=True)
		row.scale_x = 1.5
		rows.operator("automirror.toggle_mirror",text="",icon="RESTRICT_VIEW_OFF")
		rows.operator("automirror.target_set",text="",icon="OBJECT_DATAMODE")

		sp = box.split(align=True,factor=0.3)
		sp.label(text="Quick Axis")
		row = sp.row()
		row.scale_y = 1.2
		am = row.operator("automirror.automirror",text="X")
		am.axis_quick_override = True
		am.axis_x = True
		am.axis_y = False
		am.axis_z = False
		am = row.operator("automirror.automirror",text="Y")
		am.axis_quick_override = True
		am.axis_x = False
		am.axis_y = True
		am.axis_z = False
		am = row.operator("automirror.automirror",text="Z")
		am.axis_quick_override = True
		am.axis_x = False
		am.axis_y = False
		am.axis_z = True

		row = box.row(align=True)
		row.alignment="LEFT"
		row.prop(props, "toggle_option", text="Option", icon="TRIA_DOWN" if props.toggle_option else "TRIA_RIGHT", emboss=False)

		if props.toggle_option:
			# draw_main_fanc_option(self,context,layout)

			box = box.box()
			col = box.column()
			row = col.row(align=True)
			row.prop(props,"axis_x",text="X",toggle=True)
			row.prop(props,"axis_y",text="Y",toggle=True)
			row.prop(props,"axis_z",text="Z",toggle=True)
			# row.prop(props, "axis", text="Mirror Axis", expand=True)
			row = col.row(align=True)
			row.prop(props, "orientation", text="Orientation", expand=True)
			col.prop(props, "threshold", text="Threshold")
			col.prop(props, "toggle_edit", text="Toggle Edit")
			col.prop(props, "cut", text="Cut and Mirror")
			if props.cut:
				col = box.column(align=True)
				col.label(text="Mirror Modifier:")
				row = col.row(align=True)
				row.label(text="",icon="AUTOMERGE_ON")
				row.prop(props, "use_clip", text="Use Clip")
				row = col.row(align=True)
				row.label(text="",icon="OUTLINER_DATA_MESH")
				row.prop(props, "show_on_cage", text="Editable")
				row = col.row(align=True)
				row.label(text="",icon="SORT_DESC")
				row.prop(props, "sort_top_mod")
				row = col.row(align=True)
				row.label(text="",icon="CHECKBOX_HLT")
				row.prop(props, "apply_mirror", text="Apply Mirror")
			else:
				box.label(text="Only Bisect")

		# mirror mirror
		box = layout.box()
		sp = box.split(align=True,factor=0.3)
		sp.label(text="Mirror Mirror")
		row = sp.row()
		row.scale_y = 1.2
		mm = row.operator("automirror.mirror_mirror",text="X")
		mm.axis_x = True
		mm.axis_y = False
		mm.axis_z = False
		mm = row.operator("automirror.mirror_mirror",text="Y")
		mm.axis_x = False
		mm.axis_y = True
		mm.axis_z = False
		mm = row.operator("automirror.mirror_mirror",text="Z")
		mm.axis_x = False
		mm.axis_y = True
		mm.axis_z = False


		row = layout.row(align=True)
		row.scale_x = 1.2
		row.menu("AUTOMIRROR_MT_modifier_add",text="",icon="ADD")
		row.separator()
		row.operator("automirror.apply",text="Apply",icon="FILE_TICK")
		row.operator("automirror.remove",text="Remove",icon="X")
		row.separator()
		row.operator("automirror.modifier_sort",text="",icon="SORT_DESC")



class AUTOMIRROR_MT_modifier_add(Menu):
	bl_label = "Add"

	def draw(self, context):
		layout = self.layout
		global mod_items
		for i in mod_items:
			op = layout.operator("automirror.modifier_add",text=i[1],icon="ADD")
			op.mod_type = i[0]




class AUTOMIRROR_Props(PropertyGroup):
	sort_top_mod      : BoolProperty(name="Sort first Modifier",default=True)
	toggle_option : BoolProperty(name="Toggle Option")
	apply_mirror  : BoolProperty(description="Apply the mirror modifier (useful to symmetrise the mesh)")
	cut           : BoolProperty(default= True, description="If enabeled, cut the mesh in two parts and mirror it. If not, just make a loopcut")
	show_on_cage  : BoolProperty(description="Enable to edit the cage (it's the classical modifier's option)")
	threshold     : FloatProperty(default= 0.001, min= 0.001, description="Vertices closer than this distance are merged on the loopcut")
	toggle_edit   : BoolProperty(description="If not in edit mode, change mode to edit")
	use_clip      : BoolProperty(default=True, description="Use clipping for the mirror modifier")
	axis_x : BoolProperty(name="Axis X",default=True)
	axis_y : BoolProperty(name="Axis Y")
	axis_z : BoolProperty(name="Axis Z")
	axis          : EnumProperty(name="Axis", description="Axis used by the mirror modifier",items = [
	("x", "X", "", 1),
	("y", "Y", "", 2),
	("z", "Z", "", 3)])
	orientation   : EnumProperty(description="Choose the side along the axis of the editable part (+/- coordinates)",items = [
	("positive", "Positive", "", "ADD", 1),
	("negative", "Negative","", "REMOVE", 2)])

	mm_target_obj       : PointerProperty(name="Target Object", type=bpy.types.Object)

# Add-ons Preferences Update Panel. Define Panel classes for updating
panels = (
		AUTOMIRROR_PT_panel,
		)

# define classes for registration
classes = (
	AUTOMIRROR_MT_AddonPreferences,
	AUTOMIRROR_MT_modifier_add,
	AUTOMIRROR_OT_main,
	AUTOMIRROR_OT_mirror_apply,
	AUTOMIRROR_OT_mirror_remove,
	AUTOMIRROR_OT_mirror_target_set,
	AUTOMIRROR_OT_mirror_toggle,
	AUTOMIRROR_OT_MirrorMirror,
	AUTOMIRROR_OT_modifier_add,
	AUTOMIRROR_OT_modifier_sort,
	AUTOMIRROR_Props,
	AUTOMIRROR_PT_panel,
	)

addon_keymaps = []

# Keymap List
def add_keymap_automirror():
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')

	kmi = km.keymap_items.new("automirror.automirror", 'X', 'PRESS', alt=True, shift=True, ctrl=True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'X', 'PRESS',alt=True, shift = True)
	kmi.properties.axis_x = True
	kmi.properties.axis_y = False
	kmi.properties.axis_z = False
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'Y', 'PRESS', alt=True, shift = True)
	kmi.properties.axis_x = False
	kmi.properties.axis_y = True
	kmi.properties.axis_z = False
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'Z', 'PRESS', alt=True, shift = True)
	kmi.properties.axis_x = False
	kmi.properties.axis_y = False
	kmi.properties.axis_z = True
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.toggle_mirror", 'F', 'PRESS', alt=True, shift = True)
	addon_keymaps.append((km, kmi))


def remove_keymap_automirror():
	for l in addon_keymaps:
		for km, kmi in l:
			km.keymap_items.remove(kmi)

		l.clear()
		del l[:]


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	update_panel(None, bpy.context)
	update_keymap(None, bpy.context)

	bpy.types.Scene.automirror = PointerProperty(type=AUTOMIRROR_Props)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()
