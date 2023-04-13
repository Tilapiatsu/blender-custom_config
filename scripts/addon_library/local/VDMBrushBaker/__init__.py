# Copyright (C) 2022 Robin Hohnsbeen

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

bl_info = {
	"name" : "VDM Brush Baker",
	"author" : "Robin Hohnsbeen",
	"description" : "Bake VDM Brushes from planes easily",
	"blender" : (3, 5, 0),
	"version" : (1, 0, 1),
	"location" : "Sculpt Mode: View3D > Sidebar > Tool Tab",
	"warning" : "",
	"category" : "Baking"
}

import math
import bpy
import os
from pathlib import Path
from datetime import datetime
from mathutils import Vector

class VDMBrushBakerAddonData(bpy.types.PropertyGroup):
	draft_brush_name : bpy.props.StringProperty(name='Name', default="NewVDMBrush", description="The name that will be used for the brush and texture.")
	current_edited_brush : bpy.props.IntProperty(name='Current edited brush index', description="", default=-1)
	create_preview_image : bpy.props.BoolProperty(name="Create brush preview image", default=True)
	use_map_range_zero_to_one : bpy.props.BoolProperty(name="Always use full value range", default=False, description="The resulting brush will behave the same way but the height map will look different. Using a full range means there is always pure white and pure black in the texture")
	limit_z_sample_start : bpy.props.BoolProperty(name="Limit Z sample start", default=False, description="The minimum Z location in world space that is captured inside the height map")
	limit_z_sample_end : bpy.props.BoolProperty(name="Limit Z sample end", default=False, description="The maximum Z location in world space that is captured inside the height map")
	min_z_sample : bpy.props.FloatProperty(name="Min Z location", description="The minimum Z location in world space that is captured inside the height map", default=0)
	max_z_sample : bpy.props.FloatProperty(name="Max Z location", description="The maximum Z location in world space that is captured inside the height map", default=1.0)
	render_resolution : bpy.props.EnumProperty(items={
			("128", "128 px", "Render with 128 x 128 pixels", 1), 
			("256", "256 px", "Render with 256 x 256 pixels", 2),
			("512", "512 px", "Render with 512 x 512 pixels", 3),
			("1024", "1024 px", "Render with 1024 x 1024 pixels", 4),
			("2048", "2048 px", "Render with 2048 x 2048 pixels", 5),
			},
		default="512", name=''
		)
	compression : bpy.props.EnumProperty(items={
			("none", "None", "", 1), 
			("zip", "ZIP (lossless)", "", 2),
			},
		default="zip", name=''
		)


def GetAddonData() -> VDMBrushBakerAddonData:
	return bpy.context.scene.VDMBrushBakerAddonData

def GetOutputPath(filename):
	save_path = bpy.path.abspath("/tmp")
	if bpy.data.is_saved:
		save_path = os.path.dirname(bpy.data.filepath)
	return os.path.join(save_path, "output_vdm", filename)

class EDITOR_PT_VDMBaker(bpy.types.Panel):
	bl_label = "VDM Brush Baker"
	bl_idname = "Editor_PT_LayoutPanel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Tool"

	def draw(self, context):
		layout = self.layout
		scene = context.scene

		layout.operator(CreateSculptPlane.bl_idname)

		addon_data = GetAddonData()

		is_occupied, brush_name = GetNewBrushName()
		layout.prop(addon_data, "draft_brush_name")
		resolution_layout = layout.row(align=True)
		resolution_layout.label(text="Map resolution: ")
		resolution_layout.prop(addon_data, "render_resolution")

		compression_layout = layout.row(align=True)
		compression_layout.label(text="Compression: ")
		compression_layout.prop(addon_data, "compression")
		button_text = "Render and create brush"

		if is_occupied:
			layout.label(text="Name is already occupied. Brush will be overwritten.", icon="ERROR")
			button_text = "Overwrite vdm brush"

		createvdmlayout = layout.row()
		createvdmlayout.enabled = context.active_object is not None and context.active_object.type == "MESH"
		createvdmlayout.operator(CreateVDMBrush.bl_idname, text=button_text, icon="META_DATA")

		layout.separator()


def GetNewBrushName():
	addon_data = GetAddonData()

	is_name_occupied = False
	for custom_brush in bpy.data.brushes:
		if custom_brush.name == addon_data.draft_brush_name:
			is_name_occupied = True
			break

	if addon_data.draft_brush_name != "":
		return is_name_occupied, addon_data.draft_brush_name
	else:
		date = datetime.now()
		dateformat = date.strftime("%b-%d-%Y-%H-%M-%S")
		return False, f"vdm-{dateformat}"
	

AddonDirectory = ""

def GetVDMBakeMaterial():
	if bpy.data.materials.find("VDM_baking_material") == -1:
		global AddonDirectory
		addondir = Path(AddonDirectory)

		bpy.ops.wm.append(
		filepath="VDM_baking_setup.blend",
		directory=str(Path.joinpath(addondir, "VDM_baking_setup.blend", "Material")),
		filename="VDM_baking_material"
		)

	bpy.data.materials["VDM_baking_material"].use_fake_user = True
	return bpy.data.materials["VDM_baking_material"]

class CreateSculptPlane(bpy.types.Operator):
	bl_idname = "sculptplane.create"
	bl_label = "Create sculpting plane"
	bl_description = "Creates a plane to sculpt on"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		bpy.ops.mesh.primitive_grid_add(x_subdivisions=128, y_subdivisions=128, size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
		new_grid = bpy.context.active_object
		multires = new_grid.modifiers.new("MultiresVDM", type="MULTIRES")
		multires.boundary_smooth = "PRESERVE_CORNERS"
		bpy.ops.object.multires_subdivide(modifier="MultiresVDM", mode='CATMULL_CLARK')
		bpy.ops.object.multires_subdivide(modifier="MultiresVDM", mode='CATMULL_CLARK') # 512 vertices per one side

		return {"FINISHED"}


class CreateVDMBrush(bpy.types.Operator):
	bl_idname = "vdmbrush.create"
	bl_label = "Create vdm brush from plane"
	bl_description = "Creates a vector displacement map from your sculpture and creates a brush with it"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == "MESH"

	def execute(self, context):
		if context.active_object is None or context.active_object.type != "MESH":
			return {"CANCELLED"}

		vdm_plane = context.active_object
		addon_data = GetAddonData()
		new_brush_name = addon_data.draft_brush_name
		reference_brush_name = addon_data.draft_brush_name
		
		is_occupied, brush_name = GetNewBrushName()
		if len(addon_data.draft_brush_name) == 0 or is_occupied:
			addon_data.draft_brush_name = brush_name
			
		bpy.ops.object.mode_set(mode="OBJECT")
		
		# Image
		scene = context.scene
		default_render_engine = scene.render.engine
		default_view_transform = scene.view_settings.view_transform
		default_display_device = scene.display_settings.display_device
		default_file_format = scene.render.image_settings.file_format
		default_color_mode = scene.render.image_settings.color_mode
		default_codec = scene.render.image_settings.exr_codec
		default_denoise = scene.cycles.use_denoising
		default_compute_device = scene.cycles.device
		default_scene_samples = scene.cycles.samples

		vdm_bake_material = GetVDMBakeMaterial()
		try:
			scene.render.engine = "CYCLES"
			scene.cycles.samples = 2
			scene.cycles.use_denoising = False
			scene.cycles.device = "GPU"
			
			old_image_name = f"{reference_brush_name}" 
			if old_image_name in bpy.data.images:
				bpy.data.images[old_image_name].name = "Old VDM texture"

				# Removing old image if changes were made.
				#bpy.data.images.remove(bpy.data.images[old_image_name]) # Removing it right away can cause a crash when sculpt mode is exited.

			vdm_plane.data.materials.clear()
			vdm_plane.data.materials.append(vdm_bake_material)
			vdm_plane.location = Vector([0,0,0])
			vdm_plane.rotation_euler = (0,0,0)
			
			vdm_texture_node = vdm_bake_material.node_tree.nodes["VDMTexture"]
			render_resolution = 128
			if addon_data.render_resolution == "256":
				render_resolution = 256
			elif addon_data.render_resolution == "512":
				render_resolution = 512
			elif addon_data.render_resolution == "1024":
				render_resolution = 1024
			elif addon_data.render_resolution == "2048":
				render_resolution = 2048
			elif addon_data.render_resolution == "4096":
				render_resolution = 4096
			
			#Bake
			bpy.ops.object.select_all(action='DESELECT')
			vdm_plane.select_set(True)
			output_path = GetOutputPath(f"{new_brush_name}.exr")
			vdm_texture_image = bpy.data.images.new(name=new_brush_name, width=render_resolution, height=render_resolution, alpha=False, float_buffer=True)
			vdm_bake_material.node_tree.nodes.active = vdm_texture_node

			vdm_texture_image.filepath_raw = bpy.path.relpath(output_path)
			vdm_texture_image.use_half_precision = False
			
			scene.render.image_settings.file_format = 'OPEN_EXR'
			scene.render.image_settings.color_mode = "RGB"
			scene.render.image_settings.exr_codec = "NONE"
			if addon_data.compression == "zip":
				scene.render.image_settings.exr_codec = "ZIP"

			vdm_texture_image.colorspace_settings.is_data = True
			vdm_texture_image.colorspace_settings.name = "Non-Color"
			

			vdm_texture_node.image = vdm_texture_image
			vdm_texture_node.select = True

			bpy.ops.object.bake(type="EMIT")
			vdm_texture_image.file_format = 'OPEN_EXR' # Needs to set this after bake. Otherwise the texture will be saved as PNG, but with .exr ending.
			
			vdm_texture_image.save()
			

		finally:
			scene.render.image_settings.file_format = default_file_format
			scene.render.image_settings.color_mode = default_color_mode
			scene.render.image_settings.exr_codec = default_codec
			scene.cycles.samples = default_scene_samples
			scene.display_settings.display_device = default_display_device
			scene.view_settings.view_transform = default_view_transform
			scene.cycles.use_denoising = default_denoise
			scene.cycles.device = default_compute_device
			scene.render.engine = default_render_engine

			vdm_plane.data.materials.clear()
			bpy.data.materials.remove(vdm_bake_material)

		bpy.ops.object.mode_set(mode="SCULPT")


		# Texture
		vdm_texture : bpy.types.Texture = None
		if bpy.data.textures.find(reference_brush_name) != -1:
			vdm_texture = bpy.data.textures[reference_brush_name]
		else:
			vdm_texture = bpy.data.textures.new(name=new_brush_name, type="IMAGE")
		vdm_texture.extension = "CLIP"
		vdm_texture.image = vdm_texture_image
		vdm_texture.use_clamp = False # Remain negative values
		vdm_texture.name = new_brush_name

		# Brush
		new_brush : bpy.types.Brush = None
		if bpy.data.brushes.find(reference_brush_name) != -1:
			new_brush = bpy.data.brushes[reference_brush_name]
		else:
			new_brush = bpy.data.brushes.new(name=new_brush_name, mode="SCULPT")
		new_brush.texture = vdm_texture
		new_brush.texture_slot.map_mode = 'AREA_PLANE'
		new_brush.stroke_method = 'ANCHORED'
		new_brush.name = new_brush_name
		new_brush.use_color_as_displacement = True
		new_brush.strength = 1.0
		new_brush.curve_preset = 'CONSTANT'
		new_brush.use_custom_icon = True


		context.tool_settings.sculpt.brush = new_brush

		return {"FINISHED"}


registered_classes = [
	EDITOR_PT_VDMBaker,
	VDMBrushBakerAddonData,
	CreateVDMBrush,
	CreateSculptPlane
]


def register():

	global AddonDirectory
	script_file = os.path.realpath(__file__)
	AddonDirectory = os.path.dirname(script_file)
		
	for registered_class in registered_classes:
		bpy.utils.register_class(registered_class)

	bpy.types.Scene.VDMBrushBakerAddonData = bpy.props.PointerProperty(type=VDMBrushBakerAddonData)
	

def unregister():
	for registered_class in registered_classes:
		bpy.utils.unregister_class(registered_class)

	del bpy.types.Scene.VDMBrushBakerAddonData
	