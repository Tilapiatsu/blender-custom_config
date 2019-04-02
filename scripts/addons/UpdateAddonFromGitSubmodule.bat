
set param=/e /purge /r:10 /w:1 /bytes /fp

robocopy "..\GIT\Capsule\Capsule" "Capsule" %param%
robocopy "..\GIT\simple-asset-manager\SimpleAssetManager" "SimpleAssetManager" %param%
robocopy "..\GIT\fSpy-Blender\fspy_blender" "fspy_blender" %param%
robocopy "..\GIT\glTF_Blender-IO\addons\io_sketchfab_plugin" "glTF_Blender-IO" %param%
robocopy "..\GIT\mesh_align_plus\mesh_mesh_align_plus" "mesh_mesh_align_plus" %param%
robocopy "..\GIT\glTF-Blender-IO\addons\io_scene_gltf2" "glTF-Blender-IO" %param%
robocopy "..\GIT\ScreenCast-Keys\src\screencastkeys" "screencastkeys" %param%

copy "..\GIT\RenderBurst\RenderBurst.py" .
copy "..\GIT\object-shake\Object_Shake.py" .
copy "..\GIT\TiNA\TiNA.py" .

copy "..\GIT\bpy_photogrametry\carbon_tools.py" .
copy "..\GIT\bpy_photogrametry\io_import_photoscan_cameras.py" .
copy "..\GIT\bpy_photogrametry\system_time_tracker.py" .
copy "..\GIT\bpy_photogrametry\uv_tube_unwrap.py" .
copy "..\GIT\bpy_photogrametry\view3d_point_cloud_visualizer.py" .
copy "..\GIT\advanced_transform\advanced_transform_2_8.py" .
robocopy "..\GIT\bpy_photogrametry\io_mesh_fast_obj" "io_mesh_fast_obj" %param%

pause