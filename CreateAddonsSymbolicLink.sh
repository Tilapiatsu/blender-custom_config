#!/bin/sh
MakeSymbolicLink () {
    target=$1
    source=$2

    echo "Make Symbolic Link $source to $target"
    unlink $target
    ln -sf $source $target

}

curr_dir=${PWD}

MakeSymbolicLink "$curr_dir/scripts/addons/SimpleAssetManager" "$curr_dir/scripts/GIT/simple-asset-manager/SimpleAssetManager"
MakeSymbolicLink "$curr_dir/scripts/addons/fspy" "$curr_dir/scripts/GIT/fSpy-Blender/fspy_blender"
MakeSymbolicLink "$curr_dir/scripts/addons/mesh_mesh_align_plus" "$curr_dir/scripts/GIT/mesh_align_plus/mesh_mesh_align_plus"
MakeSymbolicLink "$curr_dir/scripts/addons/screencast_keys" "$curr_dir/scripts/GIT/ScreenCast-Keys/src/screencast_keys"
MakeSymbolicLink "$curr_dir/scripts/addons/mira_tools" "$curr_dir/scripts/GIT/mifthtools/blender/addons/2.8/mira_tools"
MakeSymbolicLink "$curr_dir/scripts/addons/PolyQuilt" "$curr_dir/scripts/GIT/PolyQuilt/Addons/PolyQuilt"
MakeSymbolicLink "$curr_dir/scripts/addons/vertex_color_master" "$curr_dir/scripts/GIT/vertex_color_master/vertex_color_master"
MakeSymbolicLink "$curr_dir/scripts/addons/MathsExpressionLiteBlender" "$curr_dir/scripts/GIT/Blender-Addons/MathsExpressionLiteBlender28"
MakeSymbolicLink "$curr_dir/scripts/addons/MapsModelsImporter" "$curr_dir/scripts/GIT/MapsModelsImporter/blender/MapsModelsImporter"
MakeSymbolicLink "$curr_dir/scripts/addons/Polycount" "$curr_dir/scripts/GIT/Polycount/polycount"
MakeSymbolicLink "$curr_dir/scripts/addons/Texel_Density" "$curr_dir/scripts/GIT/Texel-Density-Checker/Texel_Density_3_3_291"
MakeSymbolicLink "$curr_dir/scripts/addons/uv-packer" "$curr_dir/scripts/GIT/uvpacker/uv-packer"
MakeSymbolicLink "$curr_dir/scripts/addons/Asset_Creation_Toolset" "$curr_dir/scripts/GIT/Asset-Creation-Toolset/Asset_Creation_Toolset_3_2_310"
# mklink /d "$curr_dir/scripts/addons/io_mesh_fast_obj" "$curr_dir/scripts/GIT/bpy_photogrametry/io_mesh_fast_obj"
MakeSymbolicLink "$curr_dir/scripts/addons/math_formula" "$curr_dir/scripts/GIT/WM_Blender-Addons/math_formula"
MakeSymbolicLink "$curr_dir/scripts/addons/photogrammetry_importer" "$curr_dir/scripts/GIT/Blender-Addon-Photogrammetry-Importer/photogrammetry_importer"

mkdir "$curr_dir/scripts/startup/bl_app_templates_user"
MakeSymbolicLink "$curr_dir/scripts/startup/bl_app_templates_user/blender_media_viewer" "$curr_dir/scripts/GIT/Blender_Studio_Tools/blender-media-viewer/blender_media_viewer"

python "$curr_dir/scripts/GIT/BEER/scripts/package_blender_addon.py"
MakeSymbolicLink "$curr_dir/scripts/addons/BlenderMalt" "$curr_dir/scripts/GIT/BEER/BlenderMalt"
MakeSymbolicLink "$curr_dir/scripts/addons/BlenderMalt/MaltPath/Malt" "$curr_dir/scripts/GIT/BEER/Malt"
MakeSymbolicLink "$curr_dir/scripts/addons/hairNet" "$curr_dir/scripts/GIT/HairNet/hairNet"
# powershell -Command "(gc addons/hairNet/hairNet.py) -replace 'DEBUG = 1', 'DEBUG = 0' | Out-File -encoding ASCII addons/hairNet/hairNet.py"

MakeSymbolicLink "$curr_dir/scripts/presets/interface_theme/blender_pro.xml" "$curr_dir/scripts/GIT/ProTheme/blender_pro.xml"
MakeSymbolicLink "$curr_dir/scripts/addons/RenderBurst.py" "$curr_dir/scripts/GIT/RenderBurst/RenderBurst.py"
MakeSymbolicLink "$curr_dir/scripts/addons/Object_Shake.py" "$curr_dir/scripts/GIT/object-shake/Object_Shake.py"
MakeSymbolicLink "$curr_dir/scripts/addons/TiNA.py" "$curr_dir/scripts/GIT/TiNA/TiNA.py"
MakeSymbolicLink "$curr_dir/scripts/addons/blenderbezierutils.py" "$curr_dir/scripts/GIT/bezierutils/blenderbezierutils.py"
MakeSymbolicLink "$curr_dir/scripts/addons/Lodify.py" "$curr_dir/scripts/GIT/Lodify/Lodify.py"
MakeSymbolicLink "$curr_dir/scripts/addons/carbon_tools.py" "$curr_dir/scripts/GIT/bpy_photogrametry/carbon_tools.py"
MakeSymbolicLink "$curr_dir/scripts/addons/io_import_photoscan_cameras.py" "$curr_dir/scripts/GIT/bpy_photogrametry/io_import_photoscan_cameras.py"
MakeSymbolicLink "$curr_dir/scripts/addons/system_time_tracker.py" "$curr_dir/scripts/GIT/bpy_photogrametry/system_time_tracker.py"
MakeSymbolicLink "$curr_dir/scripts/addons/space_view3d_point_cloud_visualizer.py" "$curr_dir/scripts/GIT/bpy_photogrametry/space_view3d_point_cloud_visualizer.py"
MakeSymbolicLink "$curr_dir/scripts/addons/advanced_transform.py" "$curr_dir/scripts/GIT/advanced_transform/advanced_transform_2_8.py"
MakeSymbolicLink "$curr_dir/scripts/addons/oscurart_edit_split_normals.py" "$curr_dir/scripts/GIT/oscuart/oscurart_edit_split_normals.py"
MakeSymbolicLink "$curr_dir/scripts/addons/oscurart_bake_pbr.py" "$curr_dir/scripts/GIT/oscuart/oscurart_bake_pbr.py"
MakeSymbolicLink "$curr_dir/scripts/addons/object_convert_to_armature.py" "$curr_dir/scripts/GIT/Export-Paper-Model/object_convert_to_armature.py"
MakeSymbolicLink "$curr_dir/scripts/addons/optiloops.py" "$curr_dir/scripts/GIT/optiloops/optiloops_v1_2_0.py"
MakeSymbolicLink "$curr_dir/scripts/addons/mesh_restoresymmetry.py" "$curr_dir/scripts/GIT/RestoreSymmetry/RestoreSymmetry/mesh_restoresymmetry.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_OPERATORS.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_OPERATORS.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_pie_rotate_90.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_pie_rotate_90.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_pie_areas.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_pie_areas.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_pie_symmetry.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_pie_symmetry.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_pie_add.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_pie_add.py"
MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_pie_boolean.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_pie_boolean.py"
# MakeSymbolicLink "$curr_dir/scripts/startup/HEAVYPOLY_select_through_border.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/HEAVYPOLY_select_through_border.py"
MakeSymbolicLink "$curr_dir/scripts/startup/jmQuickPipe.py" "$curr_dir/scripts/GIT/HEAVYPOLY/scripts/startup/jmQuickPipe.py"