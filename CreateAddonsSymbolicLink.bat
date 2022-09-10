PUSHD %~dp0
echo OFF
set "currdir=%cd%"

CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\SimpleAssetManager" "%currdir%\scripts\GIT\simple-asset-manager\SimpleAssetManager" 
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\fspy" "%currdir%\scripts\GIT\fSpy-Blender\fspy_blender"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\mesh_mesh_align_plus" "%currdir%\scripts\GIT\mesh_align_plus\mesh_mesh_align_plus"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\screencast_keys" "%currdir%\scripts\GIT\ScreenCast-Keys\src\screencast_keys"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\mira_tools" "%currdir%\scripts\GIT\mifthtools\blender\addons\2.8\mira_tools"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\PolyQuilt" "%currdir%\scripts\GIT\PolyQuilt\Addons\PolyQuilt"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\vertex_color_master" "%currdir%\scripts\GIT\vertex_color_master\vertex_color_master"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\MathsExpressionLiteBlender" "%currdir%\scripts\GIT\Blender-Addons\MathsExpressionLiteBlender28"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\MapsModelsImporter" "%currdir%\scripts\GIT\MapsModelsImporter\blender\MapsModelsImporter"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\Polycount" "%currdir%\scripts\GIT\Polycount\polycount"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\Texel_Density" "%currdir%\scripts\GIT\Texel-Density-Checker\Texel_Density_3_3_291"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\uv-packer" "%currdir%\scripts\GIT\uvpacker\uv-packer"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\uvpacker_exe" "%currdir%\scripts\GIT\uvpacker_exe"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\asset_bridge" "%currdir%\scripts\GIT\asset_bridge\asset_bridge"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\Asset_Creation_Toolset" "%currdir%\scripts\GIT\Asset-Creation-Toolset\Asset_Creation_Toolset_3_1_281"
@REM mklink /d "%currdir%\scripts\addons\io_mesh_fast_obj" "%currdir%\scripts\GIT\bpy_photogrametry\io_mesh_fast_obj"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\math_formula" "%currdir%\scripts\GIT\WM_Blender-addons\math_formula"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\photogrammetry_importer" "%currdir%\scripts\GIT\Blender-Addon-Photogrammetry-Importer\photogrammetry_importer"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\shotmanager" "%currdir%\scripts\GIT\shotmanager\shotmanager"
mkdir "%currdir%\scripts\startup\bl_app_templates_user\"
CALL :MakeSymbolicLink "d" "%currdir%\datafiles\colormanagement" "%currdir%\scripts\GIT\AgX"

CALL :MakeSymbolicLink "d" "%currdir%\scripts\startup\bl_app_templates_user\blender_media_viewer" "%currdir%\scripts\GIT\Blender_Studio_Tools\blender-media-viewer\blender_media_viewer"

"%PYTHONPATH%\python.exe" ".\GIT\BEER\scripts\package_blender_addon.py"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\BlenderMalt" "%currdir%\scripts\GIT\BEER\BlenderMalt"
CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\BlenderMalt\MaltPath\Malt" "%currdir%\scripts\GIT\BEER\Malt"

CALL :MakeSymbolicLink "d" "%currdir%\scripts\addons\hairNet" "%currdir%\scripts\GIT\HairNet\hairNet"
powershell -Command "(gc addons\hairNet\hairNet.py) -replace 'DEBUG = 1', 'DEBUG = 0' | Out-File -encoding ASCII addons\hairNet\hairNet.py"

CALL :MakeSymbolicLink "h" "%currdir%\scripts\presets\interface_theme\blender_pro.xml" "%currdir%\scripts\GIT\ProTheme\blender_pro.xml"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\RenderBurst.py" "%currdir%\scripts\GIT\RenderBurst\RenderBurst.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\Object_Shake.py" "%currdir%\scripts\GIT\object-shake\Object_Shake.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\TiNA.py" "%currdir%\scripts\GIT\TiNA\TiNA.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\blenderbezierutils.py" "%currdir%\scripts\GIT\bezierutils\blenderbezierutils.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\Lodify.py" "%currdir%\scripts\GIT\Lodify\Lodify.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\carbon_tools.py" "%currdir%\scripts\GIT\bpy_photogrametry\carbon_tools.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\io_import_photoscan_cameras.py" "%currdir%\scripts\GIT\bpy_photogrametry\io_import_photoscan_cameras.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\system_time_tracker.py" "%currdir%\scripts\GIT\bpy_photogrametry\system_time_tracker.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\space_view3d_point_cloud_visualizer.py" "%currdir%\scripts\GIT\bpy_photogrametry\space_view3d_point_cloud_visualizer.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\advanced_transform.py" "%currdir%\scripts\GIT\advanced_transform\advanced_transform_2_8.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\oscurart_edit_split_normals.py" "%currdir%\scripts\GIT\oscuart\oscurart_edit_split_normals.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\oscurart_bake_pbr.py" "%currdir%\scripts\GIT\oscuart\oscurart_bake_pbr.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\object_convert_to_armature.py" "%currdir%\scripts\GIT\Export-Paper-Model\object_convert_to_armature.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\optiloops.py" "%currdir%\scripts\GIT\optiloops\optiloops_v1_2_0.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\addons\mesh_restoresymmetry.py" "%currdir%\scripts\GIT\RestoreSymmetry\RestoreSymmetry\mesh_restoresymmetry.py"

CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_OPERATORS.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_OPERATORS.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_pie_rotate_90.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_rotate_90.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_pie_areas.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_areas.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_pie_symmetry.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_symmetry.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_pie_add.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_add.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_pie_boolean.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_pie_boolean.py"
@REM CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\HEAVYPOLY_select_through_border.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\HEAVYPOLY_select_through_border.py"
CALL :MakeSymbolicLink "h" "%currdir%\scripts\startup\jmQuickPipe.py" "%currdir%\scripts\GIT\HEAVYPOLY\scripts\startup\jmQuickPipe.py"

pause

:MakeSymbolicLink
@REM echo param = %~1
@REM echo target = %~2
@REM echo source = %~3
IF %~1 == d ( rmdir /s /q "%~2" ) ELSE ( del "%~2" )
mklink /%~1 "%~2" "%~3"
EXIT /B 0
