
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
