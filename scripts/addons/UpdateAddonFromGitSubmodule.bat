
set param=/e /purge /r:10 /w:1 /bytes /fp

robocopy "..\GIT\Capsule\Capsule" "Capsule" %param%
robocopy "..\GIT\simple-asset-manager\SimpleAssetManager" "SimpleAssetManager" %param%
robocopy "..\GIT\fSpy-Blender\fspy_blender" "fspy_blender" %param%
robocopy "..\GIT\glTF_Blender-IO\addons\io_sketchfab_plugin" "glTF_Blender-IO" %param%
robocopy "..\GIT\mesh_align_plus\mesh_mesh_align_plus" "mesh_mesh_align_plus" %param%
robocopy "..\GIT\glTF-Blender-IO\addons\io_scene_gltf2" "glTF-Blender-IO" %param%
robocopy "..\GIT\ScreenCast-Keys\src\screencastkeys" "screencastkeys" %param%

copy "RenderBurst_GIT\RenderBurst.py" .
copy "object-shake\Object_Shake.py" .

pause