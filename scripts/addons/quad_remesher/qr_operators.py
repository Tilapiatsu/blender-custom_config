# "Quad-Remesher Bridge for Blender"
# Author : Maxime Rouca
#
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
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy

import os
import stat # for mac fix chmod
import subprocess
import sys
import platform
import shutil
import tempfile
import time

# --- global variables ---
verboseDebug = False



# ----- misc functions -----
# print() fait un print dans la console windows (terminal)
# console_print() fait un print dans la Python console si elle est ouverte !   (+ print in windows terminal)
def console_print(*args, clear=False):
	s = " ".join([str(arg) for arg in args])
	print(s)
	for a in bpy.context.screen.areas:
		if a.type == 'CONSOLE':
			c = {}
			c['area'] = a
			c['space_data'] = a.spaces.active
			c['region'] = a.regions[-1]
			c['window'] = bpy.context.window
			c['screen'] = bpy.context.screen

			if clear:
				bpy.ops.console.clear(c)

			for line in s.split("\n"):
				bpy.ops.console.scrollback_append(c, text=line)
				if (verboseDebug): print(line)

def unixifyPath(path):
	path = path.replace('\\', '/')
	return path

def getQREngineFolder():
    isMacOS = (platform.system()=="Darwin") or (platform.system()=="macosx")
    if (isMacOS):
        engineFolder = "/Users/Shared/Exoside/QuadRemesher/Datas_Blender/QuadRemesherEngine_1.0"
    else:
        #appData = os.getenv('APPDATA')  windows ... UserName/../Roaming... 
        appData = os.getenv('ALLUSERSPROFILE')  # on windows : C:\Users\All Users == C:\ProgramData\
        engineFolder = os.path.join(appData, "Exoside/QuadRemesher/Datas_Blender/QuadRemesherEngine_1.0")
    return engineFolder
	

def export_selected_mesh_fbx(filepath):
	bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)

# NB: the imported objects are automatically selected.
def import_mesh_fbx(filepath):
	# https://docs.blender.org/api/blender2.8/bpy.ops.import_scene.html
	bpy.ops.import_scene.fbx(filepath=filepath)

	sel_objects = bpy.context.selected_objects
	if len(sel_objects) >= 1:
		retopo_object = sel_objects[0]
		#2.79 : bpy.context.scene.objects.active = retopo_object
		bpy.context.view_layer.objects.active = retopo_object
		#bpy.context.render_layer.objects.active = retopo_object


# return (ProgressValue, ProgressText)      (specific values : -10="no progress file")
def update_progress_bar(theOp):

	ProgressText = ""
	
	# read progress file:
	progressLines=[]
	try:
		pf = open(theOp.progressFilename, "r")
		progressLines = pf.read().splitlines()
		pf.close()
	except Exception:
		return -10, ""
	
	if len(progressLines)>=1:
		#console_print(progressLines[0])
		try:
			ProgressValueFloat = float(progressLines[0]) # value in [0,1] or <0 : error
		except Exception:
			console_print(' error in progressbar...')
		
		if ProgressValueFloat != None:
			if (ProgressValueFloat < 0):
				if len(progressLines)>=2:
					ProgressText = progressLines[1]
				return ProgressValueFloat, ProgressText
			
			# Succeded ?
			if ProgressValueFloat == 2:
				return ProgressValueFloat, ""

			newPBarValue = int( (99.0 * ProgressValueFloat + 1.0) )
			
			# update Blender progress
			#wm = bpy.context.window_manager
			#wm.progress_update(newPBarValue)
			
			# update my own slider
			#props = bpy.context.scene.qremesher
			#props.progress_value = newPBarValue
			
			# INFO:
			theOp.report({'INFO'}, "Remeshing progress:"+str(newPBarValue)+"% (ESC=Abort)")

			# force redraw
			#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

			#console_print("Update PROGRESS: " + str(newPBarValue) + "\n")
			
			return ProgressValueFloat, ProgressText
	
	# check process is running:
	if (theOp.remeshProcess.poll() != None):
		ProgressValueFloat = -3    # this means that the remesher crashed
		ProgressText = "Remeshing Failed! (-3)"
		return ProgressValueFloat, ProgressText
	
	ProgressValueFloat = -11
	ProgressText = "Remeshing Failed! (Bad ProgressFile Data)"
	return ProgressValueFloat, ProgressText

def fixExecutableMode(path):
	st = os.stat(path)
	# NB:S_IEXEC=executeByUser    S_IXUSR=executeByUser    S_IXGRP=executeByGroup    S_IXOTH=executeByOther
	newMode = st.st_mode | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
	if (st.st_mode != newMode):
		os.chmod(path, newMode)


#def IsQuadRemesherEngineInstalled(enginePath):
#return os.path.exists(enginePath)

# return values:
# 0 : nothing done
# 1 : if the QuadRemesher has been installed
# 2,3 : if the QuadRemesher has not been downloaded/installed : error!
# NB: enginePath can be either xremesh or xrLicenseManager
def InstallQuadRemesherEngineIfNeeded(op, context, enginePath):
	if not os.path.exists(enginePath):
		console_print("Engine not found: downloading and installing...("+enginePath+")")
		
		op.report({'WARNING'}, "Downloading QuadRemesher Engine...")
		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)

		# test invoke
		#context.window_manager.invoke_confirm(self, event)
		
		#if (op.ReCallFromTimer_DownloadMsgDone != True):
		#	op.report({'INFO'}, "Downloading QuadRemesher Engine...")
		#	bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		
		#engineFolder = os.path.join(script_folder, "QuadRemesherEngine")
		engineFolder = getQREngineFolder()
		if not os.path.exists(engineFolder):
			os.makedirs(engineFolder)
			
		# download first  (NB: python version = 3.7 in Blender 2.8)
		isMacOSX = (platform.system()=="Darwin") or (platform.system()=="macosx")
		try:
			#zip_file_name = os.path.join(script_folder, "install_engine.zip")
			zip_file_name = os.path.join(engineFolder, "../install_engine.zip")
			import urllib.request
			if isMacOSX:
				urllib.request.urlretrieve("http://exoside.com/quadremesherdata/quad_remesher_engine_1.0_macOS.zip", zip_file_name)
			else:
				urllib.request.urlretrieve("https://exoside.com/quadremesherdata/quad_remesher_engine_1.0_win.zip", zip_file_name)
			if not os.path.exists(zip_file_name):
				op.report({'ERROR'}, "Failed to download Quad Remesher Engine.")
				return 2
		except Exception:
			import traceback
			console_print("Install remesher Engine ERROR: Download Failed" + str(traceback.format_exc()) + "\n")
			op.report({'ERROR'}, "Failed to download Quad Remesher Engine.")
			return 2
			
		# then unzip
		op.report({'WARNING'}, "unzipping QuadRemesher Engine...")
		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		try:
			from zipfile import ZipFile
			with ZipFile(zip_file_name, 'r') as zip: 
				zip.extractall(engineFolder) 
				#return 1
			
			#return 1
		except Exception:
			import traceback
			console_print("Install remesher Engine ERROR: Unzip Failed" + str(traceback.format_exc()) + "\n")
			op.report({'ERROR'}, "Failed to unzip Quad Remesher Engine.")
			return 3
			
		#delete zip
		os.remove(zip_file_name)
		
		# fix executable mode:
		if isMacOSX:
			fixExecutableMode(os.path.join(engineFolder, 'xremesh'))
			fixExecutableMode(os.path.join(engineFolder, 'xrLicenseManager.app/Contents/MacOS/xrLicenseManager'))

		return 1
			
	return 0

def setSelectedObjectShadeFlat(context):
	try:
		sel_objects = context.selected_objects
		if len(sel_objects) != 1:
			return 
		obj = sel_objects[0]
		for f in obj.data.polygons:
			f.use_smooth = False
	except Exception:
		import traceback
		console_print("setSelectedObjectShadeFlat exception" + str(traceback.format_exc()) + "\n")


def doRemeshing_Start(theOp, context) :
	#print("------- name = ------")
	#print(__name__)  # -> "quad_remesher.qr_operators"
	#console_print(__name__)
	#print("------ Script/addons ------")
	#print(bpy.utils.user_resource('SCRIPTS', "addons")) # OK can use it!
	#print("------__file__------")
	#print(__file__)  # -> the real path !!!
	
	#addon_name = __name__.split(".")[0]
	#prefs = bpy.context.preferences.addons[addon_name].preferences
	#args = generate_command_line_args(theOp, prefs)
	
	# reset data:
	theOp.the_input_object = None
	theOp.retopoFilename = None
	theOp.progressFilename = None
	theOp.IsRemeshing = False
		
	props = bpy.context.scene.qremesher

	# check selection		
	sel_objects = context.selected_objects
	if len(sel_objects) != 1:
		theOp.report({'ERROR'}, "You must select one and only one object.")
		return 
	theOp.the_input_object = sel_objects[0]
	if theOp.the_input_object.type != 'MESH':
		theOp.report({'ERROR'}, "You must select one MESH object !")
		return 
		
	
	# ------------ 0 - set folders and path ----------------
	isMacOSX = (platform.system()=="Darwin") or (platform.system()=="macosx")
	if isMacOSX :
		QRTempFolder = "/var/tmp/Exoside"
	else :
		QRTempFolder = os.path.join(tempfile.gettempdir(), "Exoside")
	#console_print("TempFolder = "+ QRTempFolder + "\n")

	if not os.path.exists(QRTempFolder):
		os.makedirs(QRTempFolder)

	export_path = os.path.join(QRTempFolder, "QuadRemesher/Blender")
	export_path = unixifyPath(export_path)

	if not os.path.exists(export_path):
		os.makedirs(export_path)

	settingsFilename = os.path.join(export_path, 'RetopoSettings.txt')
	inputFilename = os.path.join(export_path, 'inputMesh.fbx')
	theOp.retopoFilename = os.path.join(export_path, 'retopo.fbx')
	theOp.progressFilename = os.path.join(export_path, 'progress.txt')

	engineFolder = getQREngineFolder()
	#script_folder = os.path.dirname(os.path.realpath(__file__))
	if isMacOSX :
		enginePath = os.path.join(engineFolder, "xremesh")
	else:
		enginePath = os.path.join(engineFolder, "xremesh.exe")

	# unixify path
	inputFilename = unixifyPath(inputFilename)
	theOp.retopoFilename = unixifyPath(theOp.retopoFilename)
	settingsFilename = unixifyPath(settingsFilename)
	enginePath = unixifyPath(enginePath)
	
	# --------------- install QuadRemesher Engine if needed -------------------
	installRes = InstallQuadRemesherEngineIfNeeded(theOp, context, enginePath)
	if installRes == 1:  # 1 = Installed 
		theOp.report({'WARNING'}, "QuadRemesher Engine has been downloaded and installed, please click <<Remesh It>> again...")
		#theOp.NeedReCallStartFromTimer = True
		#return
	if installRes >= 2:  # 2 or 3 or 4
		return
	
	
	# -------------- 1 - Export mesh + settings ---------------
	# 1.1 - Write settings file
	settings_file = open(settingsFilename, "w")
	settings_file.write('HostApp=Blender\n')
	settings_file.write('FileIn="%s"\n' % inputFilename)
	settings_file.write('FileOut="%s"\n' % theOp.retopoFilename)
	settings_file.write('ProgressFile="%s"\n' % theOp.progressFilename)

	settings_file.write("TargetQuadCount=%s\n" % str(getattr(props, 'target_count')))
	settings_file.write("CurvatureAdaptivness=%s\n" % str(getattr(props, 'adaptive_size')))
	settings_file.write("ExactQuadCount=%d\n" % (not getattr(props, 'adapt_quad_count')))

	settings_file.write("UseVertexColorMap=%s\n" % str(getattr(props, 'use_vertex_color')))
	
	settings_file.write("UseMaterialIds=%d\n" % getattr(props, 'use_materials'))
	settings_file.write("UseIndexedNormals=%d\n" % getattr(props, 'use_normals'))
	settings_file.write("AutoDetectHardEdges=%d\n" % getattr(props, 'autodetect_hard_edges'))

	symAxisText = ''
	if getattr(props, 'symmetry_x') : symAxisText = symAxisText + 'X'
	if getattr(props, 'symmetry_y') : symAxisText = symAxisText + 'Y'
	if getattr(props, 'symmetry_z') : symAxisText = symAxisText + 'Z'
	if symAxisText != '':
		settings_file.write('SymAxis=%s\n' % symAxisText) 
		settings_file.write("SymLocal=1\n")
	
	settings_file.close()
	if (verboseDebug): print(" ----------- settingsFile exported!")

	# 1.2 - Export Selected Mesh
	export_selected_mesh_fbx(inputFilename)
	if (verboseDebug): print(" inputFile exported!")
	

	
	

	# --------------- 2 - Start Remeshing ------------
	try:
		if (os.path.isfile(theOp.retopoFilename)):
			os.remove(theOp.retopoFilename)
		if (os.path.isfile(theOp.progressFilename)):
			os.remove(theOp.progressFilename)
			
		# using subprocess
		if (verboseDebug): print("Launch : path=" + enginePath + "\n")
		if (verboseDebug): print("    settings_path=" + settingsFilename + "\n")
		theOp.remeshProcess = subprocess.Popen([enginePath, "-s", settingsFilename])   #NB: Popen automatically add quotes around parameters when there are SPACES inside
		if (verboseDebug): print("  -> theOp.remeshProcess = " + str(theOp.remeshProcess) + "\n")

	except Exception:
		import traceback
		print("Execute remesher ERROR: " + str(traceback.format_exc()) + "\n")
		theOp.report({'ERROR'}, "Cannot execute the remesher engine....")
		return 
	
	theOp.IsRemeshing = True
	theOp.StartRemeshingTime = time.time()
		
	if (verboseDebug): console_print("theOp.remeshProcess: " + str(theOp.remeshProcess) + "\n")
	
	return
		
		


def doRemeshing_Finish(theOp, context) :
	# ----------------- 3 - Import Remeshing result -------------------------
	# mode is changed by fbx-import: need to save and restore it
	current_mode = bpy.context.object.mode 
	
	# first hide the selected object
	theOp.the_input_object.hide_set(state=True)   # NB: 2.8 only, 2.7 must use 'hide'
	
	# get the Smooth/Flat shading value of the input object (assuming constant all over the mesh...)
	inputUseSmoothShading = True
	try:
		if len(theOp.the_input_object.data.polygons) >= 1:
			inputUseSmoothShading = theOp.the_input_object.data.polygons[0].use_smooth
			# add warning for "Use Normals Splitting":
			if inputUseSmoothShading == False:
				props = bpy.context.scene.qremesher
				if getattr(props, 'use_normals'):
					theOp.report({'WARNING'}, "QuadRemesher Engine has been downloaded and installed, please click <<Remesh It>> again...")
			if (verboseDebug): print ("poly[0] : use_smooth = %d" % (inputUseSmoothShading))
	except Exception:
		#import traceback
		#print("EXCEPTION: " + str(traceback.format_exc()) + "\n")
		print("warning: exception with shade flat/smooth...")
	
		
	# then import result (and automatically select it)
	import_mesh_fbx(theOp.retopoFilename)

	# set the shade flat/smooth... (NB: by default, the output retopo.fbx has no normals -> Blender imports it as Shade Smooth (tested with 2.80))
	if inputUseSmoothShading == False:
		setSelectedObjectShadeFlat(context)
	
	# restore previous mode
	bpy.ops.object.mode_set(mode=current_mode)


# -------------- Download QuadRemesher Operator ----------------
'''
class QREMESHER_OT_downloadEngine(bpy.types.Operator):
	bl_idname = "qremesher.download_engine"
	bl_label = "Download and install QuadRemesher Engine ?"
	bl_description = "Download and install QuadRemesher Engine ..."
	bl_options = {'REGISTER'}

	@classmethod
	def poll(self, context):
		return True

	def execute(self, context):
		engineFolder = getQREngineFolder()
		if isMacOSX :
			enginePath = os.path.join(engineFolder, "xremesh")
		else:
			enginePath = os.path.join(engineFolder, "xremesh.exe")
		InstallQuadRemesherEngineIfNeeded(self, context, enginePath)
		return {'FINISHED'}

	def invoke(self, context, event):
		#console_print("invoke called!!!")
		self.execute(context)
		return {'RUNNING_MODAL'}
'''


# --------------- Main Operator called when <<Remesh It>> is pressed! -------
class QREMESHER_OT_remesh(bpy.types.Operator):
	bl_idname = "qremesher.remesh"
	bl_label = "<<  REMESH IT  >> "
	bl_description = "Remesh the selected mesh.\n It also downloads and installs the RemesherEngine the 1st time, if needed."
	bl_options = {'REGISTER', 'UNDO'}

	# class variables
	remeshProcess = None
	IsRemeshing = False
	retopoFilename = ""
	progressFilename = ""
	Aborted = False
	StartRemeshingTime = 0
	
	@classmethod
	def poll(self, context):
		return True

	def execute(self, context):
		#console_print("execute called!!!")
		
		doRemeshing_Start(self, context)
		
		if (self.IsRemeshing):
			wm = context.window_manager  
			# add timer
			self.timer = wm.event_timer_add(0.3, window=context.window)  
			wm.modal_handler_add(self)  
			return {'RUNNING_MODAL'}  
		else:
			return {'FINISHED'}
	
	# reset things (for FINISHED or CANCELLED)
	def onEndingOperator(self, context, isSuccess):
		wm = context.window_manager  
		if self.timer != None:
			wm.event_timer_remove(self.timer)  
			self.timer = None
		self.IsRemeshing = False
		self.remeshProcess = None
		self.retopoFilename = ""
		self.progressFilename = ""
		self.Aborted = False
		self.StartRemeshingTime = 0


	def modal(self, context, event):  
		#console_print("modal called.   event.type="+str(event.type))
		if event.type in {'ESC'}:
			self.report({'INFO'}, "Remeshing CANCELLED !")
			self.onEndingOperator(context, False)
			return {'CANCELLED'}
			
		if event.type == 'TIMER':  
			# update progress bar
			ProgressValueFloat, ProgressText = update_progress_bar(self) 
			
			# Choose: RUNNING/FINISHED/CANCELLED
			CurTimeFromStart = time.time() - self.StartRemeshingTime
			if ProgressValueFloat == -10:   # no progress file found
				if CurTimeFromStart > 2 :   # after 2 seconds without progressFile..
					console_print(' WARNING : no progressFile....')
				if CurTimeFromStart > 40 :   # after 40 seconds without progressFile..
					console_print(' ERROR : no progressFile after 40s....')
					self.report({'ERROR'}, "Remeshing FAILED !")
					self.onEndingOperator(context, False)
					return {'FINISHED'}
					
			elif ProgressValueFloat == -11:   # BadSyntax in ProgressFile
				return {'RUNNING_MODAL'}
				
			elif ProgressValueFloat == -2:   # in EULA or Activation: User will have to click Remesh It again !
				return {'FINISHED'}
				
			elif ProgressValueFloat < 0:	# error returned
				console_print(' RETURNING ERROR.... ProgressValueFloat='+str(ProgressValueFloat))
				self.onEndingOperator(context, False)
				self.report({'ERROR'}, "Remeshing FAILED !")
				return {'FINISHED'}
				
			elif ProgressValueFloat == 2:   # SUCCESS -> import the result
				doRemeshing_Finish(self, context)
				
				self.onEndingOperator(context, True)
				self.report({'INFO'}, "Remeshing Succeded !")
				
				return {'FINISHED'}
				
			return {'RUNNING_MODAL'}  
		return {'RUNNING_MODAL'}
		#return {'PASS_THROUGH'}

	def invoke(self, context, event):
		#console_print("invoke called!!!")
		
		self.execute(context)
		
		if self.IsRemeshing:
			return {'RUNNING_MODAL'}
		else:
			return {'FINISHED'}

	def cancel(self, context):
		console_print("cancel called!!!")
		self.onEndingOperator(context, False)
		return {'CANCELLED'}



# -------------- License Manager button Operator ----------------
class QREMESHER_OT_license_manager(bpy.types.Operator):
	bl_idname = "qremesher.license_manager"
	bl_label = "License Manager"
	bl_description = "Launches the License manager"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(self, context):
		return True

	def execute(self, context):
		# 1 - get license manager path
		try:
			engineFolder = getQREngineFolder()
			#script_folder = os.path.dirname(os.path.realpath(__file__))
			isMacOSX = (platform.system()=="Darwin") or (platform.system()=="macosx")
			if isMacOSX :
				licenseManagerPath = os.path.join(engineFolder, "xrLicenseManager.app/Contents/MacOS/xrLicenseManager")
			else:
				licenseManagerPath = os.path.join(engineFolder, "xrLicenseManager.exe")
			licenseManagerPath = unixifyPath(licenseManagerPath)
		except Exception:
			self.report({'ERROR'}, "Error while settings LicenseManager path!")
			return {'CANCELLED'}
		
		# 2 - launch licenseManager
		InstallQuadRemesherEngineIfNeeded(self, context, licenseManagerPath)

		#console_print("Launching LicenseManager : " + str(licenseManagerPath))
		try:
			subprocess.Popen([licenseManagerPath, "-hostApp", "Blender"])
		except Exception:
			#console_print("ERROR : " + str(licenseManagerPath))
			self.report({'ERROR'}, "Exception: while launching LicenseManager.... (" + str(licenseManagerPath) + ")")
			return {'CANCELLED'}

		#console_print("OK : " + str(licenseManagerPath))
		return {'FINISHED'}


# -------------- Reset Setting button Operator ----------------
class QREMESHER_OT_reset_settings(bpy.types.Operator):
	bl_idname = "qremesher.reset_scene_prefs"
	bl_label = "Reset Settings"
	bl_description = "Reset settings to default values"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return True

	def execute(self, context):
		#ne marche pas .... bpy.ops.qremesher.custom_confirm_dialog.('INVOKE_DEFAULT')
		
		props = bpy.context.scene.qremesher
		props.target_count = 5000
		props.adaptive_size = 50
		props.adapt_quad_count = True
		props.use_vertex_color = False
		
		props.use_materials = False
		props.use_normals = False
		props.autodetect_hard_edges = True

		props.symmetry_x = False
		props.symmetry_y = False
		props.symmetry_z = False

		return {'FINISHED'}


# -------------- FaceMap -> Material  button Operator ----------------
class QREMESHER_OT_facemap_to_materials(bpy.types.Operator):
	bl_idname = "qremesher.facemap_to_materials"
	bl_label = "Face Maps 2 Materials"
	bl_description = "Assign new Materials to each FaceMap (using random colors) so that:\n- FaceMaps can be used with 'Use Materials' option.\n- FaceMaps can be easily visualized."
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return True

	def execute(self, context):
		# NB: FOUND NOT ACCESS TO FaceMaps (neither from mesh nor from mesh) -> need to select them and read selection...
		
		import random
	
		sel_objects = context.selected_objects
		if len(sel_objects) != 1:
			theOp.report({'ERROR'}, "You must select one and only one object.")
			return {'FINISHED'}
		
		o = sel_objects[0]
		#print ("%d face maps!" % len(o.face_maps))
		
		# reset all materialIds:
		for f in o.data.polygons:
			f.material_index = 0

		matIndex = 0
		mapCount = len(o.face_maps)
		for fm in o.face_maps:
			matIndex += 1
			
			# create the material (assign random color)
			matName = ("FaceMapMat%d" % matIndex)
			mat = bpy.data.materials.new(matName)
			r = random.randint(0, 255) / 255.0
			g = random.randint(0, 255) / 255.0
			b = random.randint(0, 255) / 255.0
			#print ("face map [%d] : (%f %f %f)" % (matIndex-1, r, g, b))
			#r = (matIndex-1.0) / mapCount
			mat.diffuse_color = (r, g, b, 1)
			if o.data.materials:
				if matIndex < len(o.data.materials):
					o.data.materials[matIndex] = mat
				else:
					o.data.materials.append(mat)
			else:
				o.data.materials.append(mat)
				
			# select this face map	
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')		
			o.face_maps.active_index = matIndex-1
			
			# select all faces of this face map
			bpy.ops.object.face_map_select()
			
			# set materialId for selected faces:
			# NB: in Edit Mode ".select" returns the selected status when entering the EditMode !!! ????!!!!!
			bpy.ops.object.mode_set(mode='OBJECT')
			for f in o.data.polygons:
				#print("test select polygon %d -> %d" % (f.index, f.select))
				if f.select:
					#print("face[%d] set material = %d" % (f.index, matIndex))
					f.material_index = matIndex
			
			
		# CHECKING:
		for f in o.data.polygons: print(str(f.material_index))
		
		return {'FINISHED'}
		

