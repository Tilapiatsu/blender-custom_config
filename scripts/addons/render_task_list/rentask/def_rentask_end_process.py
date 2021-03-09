import bpy, platform

def end_processing_type(self,context):
	props = bpy.context.scene.rentask
	p_rtask = props.rentask_main
	end_cmd_l = []

	if p_rtask.end_processing_type == "NONE":
		return

	pf = platform.system()

	# シャットダウンするためのコマンド
	if p_rtask.end_processing_type == "SHUTDOWN":
		if pf == 'Windows':
			end_cmd_l += ["shutdown", "-s", "-f", "-t", "0"]
		elif pf == 'Darwin': # Mac
			end_cmd_l += ["scudo", "shutdown", "-h", "now"]
		elif pt == 'Linux':
			end_cmd_l += ["shutdown", "-h", "now"]

	# 再起動するためのコマンド
	elif p_rtask.end_processing_type == "REBOOT":
		if pf == 'Windows':
			end_cmd_l += ["shutdown", "-r", "-f", "-t", "0"]
			# end_cmd_l += ["shutdown.exe", "-r", "-f", "-t", "0"]
		elif pf == 'Darwin': # Mac
			end_cmd_l += ["sudo", "shutdown", "-r", "now"]
		elif pt == 'Linux':
			end_cmd_l += ["shutdown", "-r", "now"]

	# スリープ（スタンバイ）状態にするためのコマンド
	elif p_rtask.end_processing_type == "SLEEP":
		if pf == 'Windows':
			end_cmd_l += ["C:\Windows\System32\rundll32.exe", "PowrProf.dll,SetSuspendState"]
		elif pf == 'Darwin': # Mac
			end_cmd_l += ["pmset", "sleepnow"]
		elif pt == 'Linux':
			end_cmd_l += ["systemctl", "suspend", "-i"]


	# Blenderを終了
	elif p_rtask.end_processing_type == "QUIT_BLENDER":
		end_cmd_l.append("QUIT_BLENDER")

	if end_cmd_l:
		return end_cmd_l
