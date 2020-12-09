import bpy, sys, subprocess, os, re, time, datetime
import logging, ast
# from . import def_rentask_covert_log


def bfile_open_and_run():
	print("")
	print("_____________  Render Setup  _____________")
	print("")

	# 受け取った辞書を得る
	sys_argv = sys.argv
	ag_dic = sys_argv[sys_argv.index("__rentask_split__")+1:]
	dic = ast.literal_eval(ag_dic[0])
	app_path = sys.argv[0]


	# コマンドリストを作成
	bfile_path = dic[list(dic.keys())[0]]["blendfile"]
	cmd_l = [app_path, '-b', bfile_path]
	script = "import bpy; bpy.ops.rentask.rentask_run('INVOKE_DEFAULT',run_from_script_text=str(%s))" % dic[list(dic.keys())[0]]
	cmd_l += ["--python-expr",script]


	# Blenderを起動してレンダリング実行
	# subprocess.Popen(cmd_l)
	popen_lines = subprocess.Popen(cmd_l, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,text=True)
	log_dir_path = os.path.dirname(os.path.dirname(__file__))
	log_path = os.path.join(log_dir_path,"scripts","render_log.log")
	logging.basicConfig(filename=log_path, level=logging.DEBUG)

	# ファイルにログを書き込む
	for line in iter(popen_lines.stdout.readline, b''):
		if line:
			print(line)
			if line == "Blender quit":
				sys.exit(0)

			# logging.info(line)

			# ログを必要な情報だけ抽出、変換
			main_text_cycles = convert_log_cycles(line)
			main_text_eevee = convert_log_eevee(line)
			finished_text_ = convert_log_finished(line)
			endtime_text = convert_log_endtime(line)
			saved_text = convert_log_saved(line)
			append_text = convert_log_append_mp4(line)
			compo_par_text = convert_log_composite(line)

			base_dict = {}
			now_time = datetime.datetime.fromtimestamp(time.time())
			time_text = {"wtime":str(now_time)}

			# ログファイルに書き込み
			with open(log_path, mode='a') as f:
				# f.write(line)

				# 書き込み時間
				# eevee
				if not main_text_eevee == None: # ログが空白でない場合
					base_dict.update(**time_text,**main_text_eevee)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)


				# Cycles
				if not main_text_cycles == None: # ログが空白でない場合
					base_dict.update(**time_text,**main_text_cycles)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)

				# finished
				if not finished_text_ == None: # ログが空白でない場合
					base_dict.update(**time_text,**finished_text_)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)


				# endtime
				if not endtime_text == None: # ログが空白でない場合
					base_dict.update(**time_text,**endtime_text)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)


				# saved
				if not saved_text == None: # ログが空白でない場合
					base_dict.update(**time_text,**saved_text)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)

				# append
				if not append_text == None: # ログが空白でない場合
					base_dict.update(**time_text,**append_text)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)


				if not compo_par_text == None: # ログが空白でない場合
					base_dict.update(**time_text,**compo_par_text)
					log_text_line = str(base_dict)
					f.write("\n" + log_text_line)


#

def convert_log_finished(out):
	re_compile = re.compile('\| Finished')     # Finished
	matches = re_compile.findall(out)

	if matches:
		return {'par' : "100"}
	else:
		return None


def convert_log_cycles(out):
	# {'wtime': '2020-05-17 14:44:15.342858', 'par': '100.0', 'frame': '0', 'mem': '151.45M', 'elapsed': '00:01.96', 'samples_done': '64', 'samples_todo': '64'}
	# Fra:1 Mem:82.04M (0.00M, Peak 117.83M) | Time:00:01.18 | Mem:44.84M, Peak:80.62M | sc_name, MAIN | Rendered 9/9 Tiles
	# Fra:1 Mem:82.04M (0.00M, Peak 117.83M) | Time:00:01.20 | Mem:44.83M, Peak:80.62M | sc_name, MAIN | Finished
	re_compile = re.compile('Fra:(\d+)\s'                       # Frame
						   'Mem:(\w+.\w+)\s\(.+?\)\W\|\W'      # RAM usage
						   'Time:([0-9a-zA-Z_:.]+)\W\|\W'      # Elapsed
						   'Remaining:([0-9a-zA-Z_:.]+)\s.+?'  # Remaining
						   'Rendered\s(\d+)/(\d+)\sTiles')     # Tile no.

	matches = re_compile.findall(out)

	if matches:
		return {'par' : str((int(matches[0][4]) / int(matches[0][5])) * 100),
					'frame': matches[0][0],
					'mem': matches[0][1],
					'elapsed': matches[0][2],
					'remaining': matches[0][3],
					'tiles_done': matches[0][4],
					'tiles_todo': matches[0][5],
				}
	else:
		return None


def convert_log_eevee(out):
	re_compile = re.compile('Fra:(\d+)\s'                           # Frame
						  'Mem:(\w+.\w+)\s\(.+?\)\W\|\W'          # RAM
						  'Time:([0-9a-zA-Z_:.]+)\W\|\W'          # Elapsed
						  'Rendering\s(\d+)\s/\s(\d+)\ssamples')  # Samples

	matches = re_compile.findall(out)

	if matches:
		return {'par' : str((int(matches[0][3]) / int(matches[0][4])) * 100),
					'frame': matches[0][0],
					'mem': matches[0][1],
					'elapsed': matches[0][2],
					'samples_done': matches[0][3],
					'samples_todo': matches[0][4],
				}
	else:
		return None




def convert_log_endtime(out):
	# Time: 00:04.16 (Saving: 00:00.84)
	re_compile = re.compile("Time: (\d\d\:\d\d\.\d\d)")                           # Frame
	matches = re_compile.findall(out)

	if matches:
		return {"endtime" : matches[0]}
	else:
		return None


def convert_log_saved(out):
	# b"Saved: 'C:\\Users\\sdt\\Desktop\\moge\\ren_0032.png'"
	# b' Time: 00:00.85 (Saving: 00:00.08)'
	# Saved: 'C:\\Users\\sdt\\Desktop\\moge\\act_c_ren_0011.png'
	re_compile = re.compile("Saved:(.*)")                           # Saved
	matches = re_compile.findall(out)

	if matches:
		return {"saved" : matches[0]}
	else:
		return None

def convert_log_append_mp4(out):
	# Append frame 6
	re_compile = re.compile("Append\sframe(.*)")
	matches = re_compile.findall(out)

	if matches:
		return {"append_frame" : matches[0]}
	else:
		return None

def convert_log_composite(out):
	# Compositing | Tile 4-4
	re_compile = re.compile("Compositing\s\|\sTile\s(\d)\-(\d)")
	matches = re_compile.findall(out)

	if matches:
		return {'compo_par' : str((int(matches[0][0]) / int(matches[0][1])) * 100)}
	else:
		return None

if __name__ == "__main__":
	bfile_open_and_run()
