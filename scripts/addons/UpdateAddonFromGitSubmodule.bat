
set param=/e /purge /r:10 /w:1 /bytes /fp

robocopy "Capsule_GIT\Capsule" "Capsule" %param%
robocopy "simple-asset-manager_GIT\SimpleAssetManager" "SimpleAssetManager" %param%
robocopy "fSpy-Blender_GIT\fspy_blender" "fspy_blender" %param%
robocopy "glTF_Blender-IO_GIT\addons\io_sketchfab_plugin" "glTF_Blender-IO" %param%
robocopy "mesh_align_plus_GIT\mesh_mesh_align_plus" "mesh_align_plus" %param%

copy "RenderBurst_GIT\RenderBurst.py" .
copy "object-shake\Object_Shake.py" .

pause