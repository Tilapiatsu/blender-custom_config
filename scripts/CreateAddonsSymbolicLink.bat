PUSHD %~dp0
echo OFF
set "currdir=%cd%"

CALL :MakeSymbolicLink "d" "%currdir%\addons\SimpleAssetManager" "%currdir%\GIT\simple-asset-manager\SimpleAssetManager" 
CALL :MakeSymbolicLink "d" "%currdir%\addons\fspy" "%currdir%\GIT\fSpy-Blender\fspy_blender"
CALL :MakeSymbolicLink "d" "%currdir%\addons\mesh_mesh_align_plus" "%currdir%\GIT\mesh_align_plus\mesh_mesh_align_plus"
CALL :MakeSymbolicLink "d" "%currdir%\addons\screencast_keys" "%currdir%\GIT\ScreenCast-Keys\src\screencast_keys"
CALL :MakeSymbolicLink "d" "%currdir%\addons\mira_tools" "%currdir%\GIT\mifthtools\blender\addons\2.8\mira_tools"
CALL :MakeSymbolicLink "d" "%currdir%\addons\PolyQuilt" "%currdir%\GIT\PolyQuilt\Addons\PolyQuilt"
CALL :MakeSymbolicLink "d" "%currdir%\addons\vertex_color_master" "%currdir%\GIT\vertex_color_master\vertex_color_master"
CALL :MakeSymbolicLink "d" "%currdir%\addons\MathsExpressionLiteBlender" "%currdir%\GIT\Blender-Addons\MathsExpressionLiteBlender28"
CALL :MakeSymbolicLink "d" "%currdir%\addons\MapsModelsImporter" "%currdir%\GIT\MapsModelsImporter\blender\MapsModelsImporter"
CALL :MakeSymbolicLink "d" "%currdir%\addons\Polycount" "%currdir%\GIT\Polycount\polycount"
CALL :MakeSymbolicLink "d" "%currdir%\addons\Texel_Density" "%currdir%\GIT\Texel-Density-Checker\Texel_Density_3_1_281"
CALL :MakeSymbolicLink "d" "%currdir%\addons\uv-packer" "%currdir%\GIT\uvpacker\uv-packer"
CALL :MakeSymbolicLink "d" "%currdir%\addons\uvpacker_exe" "%currdir%\GIT\uvpacker_exe"
CALL :MakeSymbolicLink "d" "%currdir%\addons\Asset_Creation_Toolset" "%currdir%\GIT\Asset-Creation-Toolset\Asset_Creation_Toolset_3_1_281"
@REM mklink /d "%currdir%\addons\io_mesh_fast_obj" "%currdir%\GIT\bpy_photogrametry\io_mesh_fast_obj"
CALL :MakeSymbolicLink "d" "%currdir%\addons\math_formula" "%currdir%\GIT\WM_Blender-addons\math_formula"
CALL :MakeSymbolicLink "d" "%currdir%\addons\photogrammetry_importer" "%currdir%\GIT\Blender-Addon-Photogrammetry-Importer\photogrammetry_importer"
mkdir "%currdir%\startup\bl_app_templates_user\"
CALL :MakeSymbolicLink "d" "%currdir%\startup\bl_app_templates_user\blender_media_viewer" "%currdir%\GIT\Blender_Studio_Tools\blender-media-viewer\blender_media_viewer"

"%PYTHONPATH%\python.exe" ".\GIT\BEER\scripts\package_blender_addon.py"
CALL :MakeSymbolicLink "d" "%currdir%\addons\BlenderMalt" "%currdir%\GIT\BEER\BlenderMalt"
CALL :MakeSymbolicLink "d" "%currdir%\addons\BlenderMalt\MaltPath\Malt" "%currdir%\GIT\BEER\Malt"

CALL :MakeSymbolicLink "d" "%currdir%\addons\hairNet" "%currdir%\GIT\HairNet\hairNet"
powershell -Command "(gc addons\hairNet\hairNet.py) -replace 'DEBUG = 1', 'DEBUG = 0' | Out-File -encoding ASCII addons\hairNet\hairNet.py"

CALL :MakeSymbolicLink "h" "%currdir%\presets\interface_theme\blender_pro.xml" "%currdir%\GIT\ProTheme\blender_pro.xml"
CALL :MakeSymbolicLink "h" "%currdir%\addons\RenderBurst.py" "%currdir%\GIT\RenderBurst\RenderBurst.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\Object_Shake.py" "%currdir%\GIT\object-shake\Object_Shake.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\TiNA.py" "%currdir%\GIT\TiNA\TiNA.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\blenderbezierutils.py" "%currdir%\GIT\bezierutils\blenderbezierutils.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\Lodify.py" "%currdir%\GIT\Lodify\Lodify.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\carbon_tools.py" "%currdir%\GIT\bpy_photogrametry\carbon_tools.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\io_import_photoscan_cameras.py" "%currdir%\GIT\bpy_photogrametry\io_import_photoscan_cameras.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\system_time_tracker.py" "%currdir%\GIT\bpy_photogrametry\system_time_tracker.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\space_view3d_point_cloud_visualizer.py" "%currdir%\GIT\bpy_photogrametry\space_view3d_point_cloud_visualizer.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\advanced_transform.py" "%currdir%\GIT\advanced_transform\advanced_transform_2_8.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\oscurart_edit_split_normals.py" "%currdir%\GIT\oscuart\oscurart_edit_split_normals.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\oscurart_bake_pbr.py" "%currdir%\GIT\oscuart\oscurart_bake_pbr.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\object_convert_to_armature.py" "%currdir%\GIT\Export-Paper-Model\object_convert_to_armature.py"
CALL :MakeSymbolicLink "h" "%currdir%\addons\optiloops.py" "%currdir%\GIT\optiloops\optiloops_v1_2_0.py"

CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_OPERATORS.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_OPERATORS.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_pie_rotate_90.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_rotate_90.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_pie_areas.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_areas.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_pie_symmetry.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_symmetry.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_pie_add.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_add.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_pie_boolean.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_boolean.py"
@REM CALL :MakeSymbolicLink "h" "%currdir%\startup\HEAVYPOLY_select_through_border.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_select_through_border.py"
CALL :MakeSymbolicLink "h" "%currdir%\startup\jmQuickPipe.py" "%currdir%\GIT\HEAVYPOLY\scripts\startup\jmQuickPipe.py"

pause

:MakeSymbolicLink
@REM echo param = %~1
@REM echo target = %~2
@REM echo source = %~3
IF %~1 == d ( rmdir /s /q "%~2" ) ELSE ( del "%~2" )
mklink /%~1 "%~2" "%~3"
EXIT /B 0
