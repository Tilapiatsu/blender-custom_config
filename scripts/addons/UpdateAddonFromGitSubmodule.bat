
set param=/e /purge /r:10 /w:1 /bytes /fp

robocopy "..\GIT\Capsule\Capsule" "Capsule" %param%
robocopy "..\GIT\simple-asset-manager\SimpleAssetManager" "SimpleAssetManager" %param%
robocopy "..\GIT\fSpy-Blender\fspy_blender" "fspy_blender" %param%
robocopy "..\GIT\glTF_Blender-IO\addons\io_sketchfab_plugin" "glTF_Blender-IO" %param%
robocopy "..\GIT\mesh_align_plus\mesh_mesh_align_plus" "mesh_mesh_align_plus" %param%
robocopy "..\GIT\ScreenCast-Keys\src\screencastkeys" "screencastkeys" %param%
robocopy "..\GIT\mifthtools\blender\addons\2.8\mira_tools" "mira_tools" %param%
robocopy "..\GIT\PolyQuilt\Addons\PolyQuilt" "PolyQuilt" %param%
@REM robocopy "addon_common" "retopoflow\addon_common" %param%
robocopy "..\GIT\vertex_color_master\vertex_color_master" "vertex_color_master" %param%
robocopy "..\GIT\Blender-Addons\MathsExpressionLiteBlender28" "MathsExpressionLiteBlender28" %param%
robocopy "..\GIT\MapsModelsImporter\blender\MapsModelsImporter" "MapsModelsImporter" %param%
robocopy "..\GIT\Polycount\polycount" "Polycount" %param%
robocopy "..\GIT\Texel-Density-Checker\Texel_Density_3_1_281" "Texel_Density" %param%

"%PYTHONPATH%\python.exe" "..\GIT\BEER\Malt\scripts\package_blender_addon.py"
robocopy "..\GIT\BEER\Malt\BlenderMalt" "BlenderMalt" %param%
robocopy "..\GIT\BEER\Malt\Malt" "BlenderMalt\MaltPath\Malt" %param%

robocopy "..\GIT\HairNet\hairNet" "hairNet" %param%
powershell -Command "(gc hairNet\hairNet.py) -replace 'DEBUG = 1', 'DEBUG = 0' | Out-File -encoding ASCII hairNet\hairNet.py"


@REM robocopy "..\GIT\OpenColorIO\aces_1.2" "..\..\datafiles\colormanagement" %param%
@REM powershell -Command "(gc ..\..\datafiles\colormanagement\config.ocio) -replace 'texture_paint: ACES - ACEScc', 'texture_paint: Utility - Rec.2020 - Display' | Out-File -encoding ASCII ..\..\datafiles\colormanagement\config.ocio"

copy "..\GIT\ProTheme\blender_pro.xml" "..\presets\interface_theme"

copy "..\GIT\flexi-bezier\blenderbezierutils.py" .
copy "..\GIT\RenderBurst\RenderBurst.py" .
copy "..\GIT\object-shake\Object_Shake.py" .
copy "..\GIT\TiNA\TiNA.py" .
copy "..\GIT\bezierutils\blenderbezierutils.py" .
copy "..\GIT\Lodify\Lodify.py" .

copy "..\GIT\bpy_photogrametry\carbon_tools.py" .
copy "..\GIT\bpy_photogrametry\io_import_photoscan_cameras.py" .
copy "..\GIT\bpy_photogrametry\system_time_tracker.py" .
copy "..\GIT\bpy_photogrametry\uv_tube_unwrap.py" .
copy "..\GIT\bpy_photogrametry\space_view3d_point_cloud_visualizer.py" .
copy "..\GIT\advanced_transform\advanced_transform_2_8.py" .
copy "..\GIT\Asset-Creation-Toolset\Asset_Creation_Toolset_2_6_1_281.py" .
copy "..\GIT\oscuart\oscurart_edit_split_normals.py" .
copy "..\GIT\oscuart\oscurart_bake_pbr.py" .
copy "..\GIT\Export-Paper-Model\object_convert_to_armature.py" .
robocopy "..\GIT\bpy_photogrametry\io_mesh_fast_obj" "io_mesh_fast_obj" %param%

copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_OPERATORS.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_rotate_90.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_areas.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_symmetry.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_add.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_boolean.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_select_through_border.py" "..\startup\"
copy "..\GIT\HEAVYPOLY\scripts\startup\jmQuickPipe.py" "..\startup\"

pause