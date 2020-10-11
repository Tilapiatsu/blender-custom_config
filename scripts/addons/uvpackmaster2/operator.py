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
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import subprocess
import queue
import threading
import signal
import webbrowser

from .utils import *
from .pack_context import *
from .connection import *
from .prefs import *
from .os_iface import *
from .island_params import *
from .labels import UvpLabels
from .register import check_uvp, unregister_uvp

import bmesh
import bpy
import mathutils
import tempfile



class InvalidIslandsError(Exception):
    pass

class NoUvFaceError(Exception):
    pass

class UVP2_OT_PackOperatorGeneric(bpy.types.Operator):

    bl_options = {'UNDO'}

    MODAL_INTERVAL_S = 0.1
    interactive = False

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.uvp_initialized and context.active_object is not None and context.active_object.mode == 'EDIT'

    def check_uvp_retcode(self, retcode):
        self.prefs.uvp_retcode = retcode

        if retcode in {UvPackerErrorCode.SUCCESS,
                       UvPackerErrorCode.INVALID_ISLANDS,
                       UvPackerErrorCode.NO_SPACE,
                       UvPackerErrorCode.PRE_VALIDATION_FAILED}:
            return

        if retcode == UvPackerErrorCode.CANCELLED:
            raise OpCancelledException()

        if retcode == UvPackerErrorCode.NO_VALID_STATIC_ISLAND:
            raise RuntimeError("'Pack To Others' option enabled, but no unselected island found in the packing box")

        if retcode == UvPackerErrorCode.MAX_GROUP_COUNT_EXCEEDED:
            raise RuntimeError("Maximal group count exceeded")

        if retcode == UvPackerErrorCode.DEVICE_NOT_SUPPORTED:
            raise RuntimeError("Selected device is not supported")

        if retcode == UvPackerErrorCode.DEVICE_DOESNT_SUPPORT_GROUPS_TOGETHER:
            raise RuntimeError("Selected device doesn't support packing groups together")

        raise RuntimeError('Pack process returned an error')

    def raiseUnexpectedOutputError(self):
        raise RuntimeError('Unexpected output from the pack process')

    def set_status(self, status_type, status):

        self.op_status_type = status_type
        self.op_status = status

    def add_warning(self, warn_msg):

        self.op_warnings.append(warn_msg)

    def report_status(self):

        if self.op_status is not None:
            self.prefs['op_status'] = self.op_status

            op_status_type = self.op_status_type if self.op_status_type is not None else 'INFO'
            op_status = self.op_status

            if len(self.op_warnings) > 0:

                if op_status_type == 'INFO':
                    op_status_type = 'WARNING'

                op_status += '. (WARNINGS were reported - check the UVP tab for details)'

            self.report({op_status_type}, op_status)

        self.prefs['op_warnings'] = self.op_warnings
            # self.prefs.stats_op_warnings.add(warning_msg)

    def exit_common(self):

        if self.interactive:
            wm = self.p_context.context.window_manager
            wm.event_timer_remove(self._timer)

        self.p_context.update_meshes()
        self.report_status()

        if in_debug_mode():
            print('UVP operation time: ' + str(time.time() - self.start_time))

    def read_islands(self, islands_msg):
        islands = []
        island_cnt = force_read_int(islands_msg)
        selected_cnt = force_read_int(islands_msg)

        for i in range(island_cnt):
            islands.append(read_int_array(islands_msg))

        self.p_context.set_islands(selected_cnt, islands)

    def process_invalid_islands(self):
        if self.uvp_proc.returncode != UvPackerErrorCode.INVALID_ISLANDS:
            return

        if self.invalid_islands_msg is None:
            self.raiseUnexpectedOutputError()

        code = force_read_int(self.invalid_islands_msg)
        subcode = force_read_int(self.invalid_islands_msg)

        invalid_islands = read_int_array(self.invalid_islands_msg)

        if len(invalid_islands) == 0:
            self.raiseUnexpectedOutputError()

        self.p_context.handle_invalid_islands(invalid_islands)

        if code == UvInvalidIslandCode.TOPOLOGY:
            error_msg = "Invalid topology encountered in the selected islands. Check the Help panel to learn more"
        elif code == UvInvalidIslandCode.INT_PARAM:
            param_array = IslandParamInfo.get_param_info_array()
            error_msg = "Faces with inconsistent {} values found in the selected islands".format(param_array[subcode].NAME)
        else:
            self.raiseUnexpectedOutputError()

        raise InvalidIslandsError(error_msg)

    def require_selection(self):
        return True 

    def finish_after_op_done(self):
        return True
        
    def op_done(self):
        return self.curr_phase == UvPackingPhaseCode.DONE

    def handle_op_done(self):
        self.connection_thread.join()

        try:
            self.uvp_proc.wait(5)
        except:
            raise RuntimeError('The UVP process wait timeout reached')

        self.check_uvp_retcode(self.uvp_proc.returncode)

        if not self.p_context.islands_received():
            self.raiseUnexpectedOutputError()

        self.process_invalid_islands()
        self.process_result()

        if self.finish_after_op_done():
            raise OpFinishedException()

    def finish(self, context):

        self.exit_common()
        return {'FINISHED', 'PASS_THROUGH'}

    def cancel(self, context):
        self.uvp_proc.terminate()
        # self.progress_thread.terminate()

        self.exit_common()
        return {'FINISHED'}

    def get_progress_msg_spec(self):
        return False

    def get_progress_msg(self):

        if self.hang_detected:
            return 'Packer process not responding for a longer time (press ESC to abort)'

        if self.curr_phase is None:
            return False

        progress_msg_spec = self.get_progress_msg_spec()

        if progress_msg_spec:
            return progress_msg_spec

        if self.curr_phase == UvPackingPhaseCode.INITIALIZATION:
            return 'Initialization (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.TOPOLOGY_ANALYSIS:
            return "Topology analysis: {:3}% (press ESC to cancel)".format(self.progress_array[0])

        if self.curr_phase == UvPackingPhaseCode.OVERLAP_CHECK:
            return 'Overlap check in progress (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.AREA_MEASUREMENT:
            return 'Area measurement in progress (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.SIMILAR_SELECTION:
            return 'Searching for similar islands (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.SIMILAR_ALIGNING:
            return 'Similar islands aligning (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.RENDER_PRESENTATION:
            return 'Close the demo window to finish'

        if self.curr_phase == UvPackingPhaseCode.TOPOLOGY_VALIDATION:
            return "Topology validation: {:3}% (press ESC to cancel)".format(self.progress_array[0])

        if self.curr_phase == UvPackingPhaseCode.VALIDATION:
            return "Per-face overlap check: {:3}% (press ESC to cancel)".format(self.progress_array[0])

        raise RuntimeError('Unexpected packing phase encountered')

    def handle_uvp_msg_spec(self, msg_code, msg):
        return False

    def handle_event_spec(self, event):
        return False

    def handle_progress_msg(self):

        if self.op_done():
            return

        msg_refresh_interval = 2.0
        new_progress_msg = self.get_progress_msg()

        if not new_progress_msg:
            return

        now = time.time()
        if now - self.progress_last_update_time > msg_refresh_interval or new_progress_msg != self.progress_msg:
            self.progress_last_update_time = now
            self.progress_msg = new_progress_msg
            self.report({'INFO'}, self.progress_msg)

    def handle_uvp_msg(self, msg):

        msg_code = force_read_int(msg)

        if self.handle_uvp_msg_spec(msg_code, msg):
            return

        if msg_code == UvPackMessageCode.PROGRESS_REPORT:
            self.curr_phase = force_read_int(msg)
            progress_size = force_read_int(msg)
            
            if progress_size > len(self.progress_array):
                self.progress_array = [0] * (progress_size)

            for i in range(progress_size):
                self.progress_array[i] = force_read_int(msg)

            self.progress_sec_left = force_read_int(msg)
            self.progress_iter_done = force_read_int(msg)

            # Inform the upper layer wheter it should finish
            if self.curr_phase == UvPackingPhaseCode.DONE:
                self.handle_op_done()

        elif msg_code == UvPackMessageCode.INVALID_ISLANDS:
            if self.invalid_islands_msg is not None:
                self.raiseUnexpectedOutputError()

            self.invalid_islands_msg = msg

        elif msg_code == UvPackMessageCode.ISLAND_FLAGS:
            if self.island_flags_msg is not None:
                self.raiseUnexpectedOutputError()

            self.island_flags_msg = msg

        elif msg_code == UvPackMessageCode.PACK_SOLUTION:
            if self.pack_solution_msg is not None:
                self.raiseUnexpectedOutputError()

            self.pack_solution_msg = msg

        elif msg_code == UvPackMessageCode.AREA:
            if self.area_msg is not None:
                self.raiseUnexpectedOutputError()

            self.area_msg = msg

        elif msg_code == UvPackMessageCode.INVALID_FACES:
            if self.invalid_faces_msg is not None:
                self.raiseUnexpectedOutputError()

            self.invalid_faces_msg = msg

        elif msg_code == UvPackMessageCode.SIMILAR_ISLANDS:
            if self.similar_islands_msg is not None:
                self.raiseUnexpectedOutputError()

            self.similar_islands_msg = msg

        elif msg_code == UvPackMessageCode.ISLANDS:

            self.read_islands(msg)

        elif msg_code == UvPackMessageCode.ISLANDS_METADATA:
            if self.islands_metadata_msg is not None:
                self.raiseUnexpectedOutputError()

            self.islands_metadata_msg = msg

        else:
            self.raiseUnexpectedOutputError()

    def handle_communication(self):

        if self.op_done():
            return

        msg_received = 0
        while True:
            try:
                item = self.progress_queue.get_nowait()
            except queue.Empty as ex:
                break

            if isinstance(item, str):
                raise RuntimeError(item)
            elif isinstance(item, io.BytesIO):
                self.handle_uvp_msg(item)
            else:
                raise RuntimeError('Unexpected output from the connection thread')
            
            msg_received += 1

        curr_time = time.time()
        if msg_received > 0:
            self.last_msg_time = curr_time
            self.hang_detected = False
        else:
            if self.curr_phase != UvPackingPhaseCode.RENDER_PRESENTATION and curr_time - self.last_msg_time > self.hang_timeout:
                self.hang_detected = True

    def handle_event(self, event):
        # Kill the UVP process unconditionally if a hang was detected
        if self.hang_detected and event.type == 'ESC':
            raise OpAbortedException()

        if self.handle_event_spec(event):
            return

        # Generic event processing code
        if event.type == 'ESC':
            raise OpCancelledException()
        elif event.type == 'TIMER':
            self.handle_communication()

    def modal(self, context, event):
        cancel = False
        finish = False

        try:
            try:
                self.handle_event(event)

                # Check whether the uvp process is alive
                if not self.op_done() and self.uvp_proc.poll() is not None:
                    # In order to avoid race condition we must check for a done message once more
                    self.handle_communication()

                    if not self.op_done():
                        # Special value indicating a crash
                        self.prefs.uvp_retcode = -1
                        raise RuntimeError('Packer process died unexpectedly')

                self.handle_progress_msg()

            except OpFinishedException:
                finish = True
            except:
                raise

            if finish:
                return self.finish(context)

        except OpAbortedException:
            self.set_status('INFO', 'Packer process killed')
            cancel = True

        except OpCancelledException:
            self.set_status('INFO', 'Operation cancelled by the user')
            cancel = True

        except InvalidIslandsError as err:
            self.set_status('ERROR', str(err))
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_status('ERROR', str(ex))
            cancel = True

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_status('ERROR', 'Unexpected error')

            cancel = True

        if cancel:
            return self.cancel(context)

        return {'RUNNING_MODAL'} if not self.op_done() else {'PASS_THROUGH'}

    def pre_op_initialize(self):
        pass

    def execute(self, context):
        
        cancel = False
        self.uvp_proc = None

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvp2_props

        self.p_context = None
        self.pack_ratio = 1.0
        self.target_box = None

        self.op_status_type = None
        self.op_status = None
        self.op_warnings = []

        try:
            if not check_uvp():
                unregister_uvp()
                redraw_ui(context)
                raise RuntimeError("UVP engine broken")

            reset_stats(self.prefs)
            self.p_context = PackContext(context)

            self.pre_op_initialize()

            send_unselected = self.send_unselected_islands()
            send_rot_step = self.send_rot_step()
            send_groups = self.grouping_enabled() and (to_uvp_group_method(self.get_group_method()) == UvGroupingMethodUvp.EXTERNAL)
            send_lock_groups = self.lock_groups_enabled()
            send_verts_3d = self.send_verts_3d()

            selected_cnt, unselected_cnt = self.p_context.serialize_uv_maps(send_unselected, send_groups, send_rot_step, send_lock_groups, send_verts_3d, self.get_group_method() if send_groups else None)

            if self.require_selection():
                if selected_cnt == 0:
                    raise NoUvFaceError('No UV face selected')
            
            else:
                if selected_cnt + unselected_cnt == 0:
                    raise NoUvFaceError('No UV face visible')


            self.validate_pack_params()

            if self.prefs.write_to_file:
                out_filepath = os.path.join(tempfile.gettempdir(), 'uv_islands.data')
                out_file = open(out_filepath, 'wb')
                out_file.write(self.p_context.serialized_maps)
                out_file.close()

            uvp_args_final = [get_uvp_execpath(), '-E', '-e', str(UvTopoAnalysisLevel.FORCE_EXTENDED), '-t', str(self.prefs.thread_count)] + self.get_uvp_args()

            if send_unselected:
                uvp_args_final.append('-s')

            if self.grouping_enabled():
                uvp_args_final += ['-a', str(to_uvp_group_method(self.get_group_method()))]

            if self.send_rot_step():
                uvp_args_final += ['-R']

            if self.lock_groups_enabled():
                uvp_args_final += ['-Q']

            if in_debug_mode():
                if self.prefs.seed > 0:
                    uvp_args_final += ['-S', str(self.prefs.seed)]

                if self.prefs.simplify_disable:
                    uvp_args_final.append('-y')

                if self.prefs.wait_for_debugger:
                    uvp_args_final.append('-G')

                uvp_args_final += ['-T', str(self.prefs.test_param)]
                print('Pakcer args: ' + ' '.join(x for x in uvp_args_final))


            creation_flags = os_uvp_creation_flags()
            popen_args = dict()

            if creation_flags is not None:
                popen_args['creationflags'] = creation_flags

            self.uvp_proc = subprocess.Popen(uvp_args_final,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             **popen_args)

            out_stream = self.uvp_proc.stdin
            out_stream.write(self.p_context.serialized_maps)
            out_stream.flush()

            self.start_time = time.time()

            self.last_msg_time = self.start_time
            self.hang_detected = False
            self.hang_timeout = 10.0

            # Start progress monitor thread
            self.progress_queue = queue.Queue()
            self.connection_thread = threading.Thread(target=connection_thread_func,
                                                      args=(self.uvp_proc.stdout, self.progress_queue))
            self.connection_thread.daemon = True
            self.connection_thread.start()
            self.progress_array = [0]
            self.progress_msg = ''
            self.progress_sec_left = -1
            self.progress_iter_done = -1
            self.progress_last_update_time = 0.0
            self.curr_phase = UvPackingPhaseCode.INITIALIZATION

            self.invalid_islands_msg = None
            self.island_flags_msg = None
            self.pack_solution_msg = None
            self.area_msg = None
            self.invalid_faces_msg = None
            self.similar_islands_msg = None
            self.islands_metadata_msg = None

        except NoUvFaceError as ex:
            self.set_status('WARNING', str(ex))
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_status('ERROR', str(ex))
            cancel = True
            
        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_status('ERROR', 'Unexpected error')
            cancel = True

        if self.p_context is not None:
            self.p_context.update_meshes()

        if cancel:
            if self.uvp_proc is not None:
                self.uvp_proc.terminate()

            self.report_status()
            return {'FINISHED'}

        if self.interactive:
            wm = context.window_manager
            self._timer = wm.event_timer_add(self.MODAL_INTERVAL_S, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        class FakeTimerEvent:
            def __init__(self):
                self.type = 'TIMER'
                self.value = 'NOTHING'
                self.ctrl = False

        while True:
            event = FakeTimerEvent()

            ret = self.modal(context, event)
            if ret.intersection({'FINISHED', 'CANCELLED'}):
                return ret

            time.sleep(self.MODAL_INTERVAL_S)


    def invoke(self, context, event):

        self.interactive = True

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvp2_props

        self.confirmation_msg = self.get_confirmation_msg()

        wm = context.window_manager
        if self.confirmation_msg != '':
            pix_per_char = 5
            dialog_width = pix_per_char * len(self.confirmation_msg) + 50
            return wm.invoke_props_dialog(self, width=dialog_width)

        return self.execute(context)
        

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.confirmation_msg)

    def get_confirmation_msg(self):
        return ''

    def send_unselected_islands(self):
        return False

    def grouping_enabled(self):
        return False

    def get_group_method(self):
        raise RuntimeError('Unexpected grouping requested')

    def send_rot_step(self):
        return False

    def lock_groups_enabled(self):
        return False

    def send_verts_3d(self):
        return False

    def read_area(self, area_msg):
        return round(force_read_float(area_msg) / self.pack_ratio, 3)


class UVP2_OT_PackOperator(UVP2_OT_PackOperatorGeneric):
    bl_idname = 'uvpackmaster2.uv_pack'
    bl_label = 'Pack'
    bl_description = 'Pack selected UV islands'

    def __init__(self):
        self.cancel_sig_sent = False
        self.area = None

    def get_confirmation_msg(self):

        if platform.system() == 'Darwin':
            active_dev = self.prefs.dev_array[self.prefs.sel_dev_idx] if self.prefs.sel_dev_idx < len(self.prefs.dev_array) else None
            if active_dev is not None and active_dev.id.startswith('cuda'):
                return UvpLabels.CUDA_MACOS_CONFIRM_MSG

        if self.prefs.pack_groups_together(self.scene_props) and not self.prefs.heuristic_enabled(self.scene_props):
            return UvpLabels.GROUPS_TOGETHER_CONFIRM_MSG

        return ''

    def send_unselected_islands(self):
        return self.prefs.pack_to_others_enabled(self.scene_props)

    def grouping_enabled(self):
        return self.prefs.grouping_enabled(self.scene_props)

    def get_group_method(self):
        return self.scene_props.group_method

    def send_rot_step(self):
        return self.prefs.FEATURE_island_rotation_step and self.scene_props.rot_enable and self.scene_props.island_rot_step_enable

    def lock_groups_enabled(self):
        return self.prefs.FEATURE_lock_overlapping and self.scene_props.lock_groups_enable

    def send_verts_3d(self):
        return self.scene_props.normalize_islands

    def get_progress_msg_spec(self):

        if self.curr_phase in { UvPackingPhaseCode.PACKING, UvPackingPhaseCode.PIXEL_MARGIN_ADJUSTMENT }:

            if self.curr_phase == UvPackingPhaseCode.PIXEL_MARGIN_ADJUSTMENT:
                header_str = 'Pixel margin adjustment. '
            elif self.prefs.heuristic_enabled(self.scene_props):
                header_str = 'Current area: {}. '.format(self.area if self.area is not None else 'none')
            else:
                header_str = ''

            if self.progress_iter_done >= 0:
                iter_str = 'Iter. done: {}. '.format(self.progress_iter_done)
            else:
                iter_str = ''

            if self.progress_sec_left >= 0:
                time_left_str = "Time left: {} sec. ".format(self.progress_sec_left)
            else:
                time_left_str = ''

            percent_progress_str = ''       
            for prog in self.progress_array:
                percent_progress_str += str(prog).rjust(3, ' ') + '%, '
            percent_progress_str = percent_progress_str[:-2]

            progress_str = 'Pack progress: {} '.format(percent_progress_str)

            if self.area is not None:
                end_str = '(press ESC to apply result) '
            else:
                end_str = '(press ESC to cancel) '

            return header_str + iter_str + time_left_str + progress_str + end_str

        return False

    def handle_uvp_msg_spec(self, msg_code, msg):

        if msg_code == UvPackMessageCode.AREA:

            self.area = self.read_area(msg)
            return True

        elif msg_code == UvPackMessageCode.PACK_SOLUTION:
            
            pack_solution = read_pack_solution(msg)
            self.p_context.apply_pack_solution(self.pack_ratio, pack_solution)
            return True

        elif msg_code == UvPackMessageCode.BENCHMARK:

            stats = self.prefs.stats_array.add()

            dev_name_len = force_read_int(msg)
            stats.dev_name = msg.read(dev_name_len).decode('ascii')

            stats.iter_count = force_read_int(msg)
            stats.total_time = force_read_int(msg)
            stats.avg_time = force_read_int(msg)
            
            return True

        return False

    def handle_event_spec(self, event):
        if event.type == 'ESC':
            if not self.cancel_sig_sent:
                self.uvp_proc.send_signal(os_cancel_sig())
                self.cancel_sig_sent = True

            return True

        return False

    def process_result(self):
        overlap_detected = False
        outside_detected = False

        if self.invalid_faces_msg is not None:
            invalid_face_count = force_read_int(self.invalid_faces_msg)
            invalid_faces = read_int_array(self.invalid_faces_msg)

            if not self.prefs.FEATURE_demo:
                if len(invalid_faces) != invalid_face_count:
                    self.raiseUnexpectedOutputError()

                if invalid_face_count > 0:
                    # Switch to the face selection mode
                    if self.p_context.context.tool_settings.use_uv_select_sync:
                        self.p_context.context.tool_settings.mesh_select_mode = (False, False, True)
                    else:
                        self.p_context.context.tool_settings.uv_select_mode = 'FACE'

                    self.p_context.select_all_faces(False)
                    self.p_context.select_faces(list(invalid_faces), True)

            if invalid_face_count > 0:
                self.set_status('WARNING', 'Pre-validation failed. Number of invalid faces found: ' + str(invalid_face_count) + '. Packing aborted')
                return


        if not self.prefs.FEATURE_demo:
            if self.island_flags_msg is None:
                self.raiseUnexpectedOutputError()

            island_flags = read_int_array(self.island_flags_msg)
            overlap_detected, outside_detected = self.p_context.handle_island_flags(island_flags)

        if self.area is not None:
            self.prefs.stats_area = self.area

        if self.uvp_proc.returncode == UvPackerErrorCode.NO_SPACE:
            op_status = 'Packing stopped - no space to pack all islands'
            self.add_warning("Overlap check was performed only on the islands which were packed")
        else:
            op_status = 'Packing done'
            if self.area is not None:
                op_status += ', packed islands area: ' + str(self.area)

        self.set_status('INFO', op_status)

        if overlap_detected:
            self.add_warning("Overlapping islands were detected after packing (check the selected islands). Consider increasing the 'Precision' parameter. Sometimes increasing the 'Adjustment Time' may solve the problem (if used in the operation).")
        if outside_detected:
            self.add_warning("Some islands are outside their packing box after packing (check the selected islands). This usually happens when 'Pixel Padding' is set to a small value and the 'Adjustment Time' is not long enough.")
        

    def validate_pack_params(self):
        active_dev = self.prefs.dev_array[self.prefs.sel_dev_idx] if self.prefs.sel_dev_idx < len(self.prefs.dev_array) else None

        if active_dev is None:
            raise RuntimeError('Could not find a packing device')

        if not active_dev.supported:
            raise RuntimeError('Selected packing device is not supported in this engine edition')

        # Validate pack mode
        pack_mode = UvPackingMode.get_mode(self.scene_props.pack_mode)

        if pack_mode.req_feature != '' and not getattr(self.prefs, 'FEATURE_' + pack_mode.req_feature):
            raise RuntimeError('Selected packing mode is not supported in this engine edition')

        if self.grouping_enabled():

            if self.get_group_method() == UvGroupingMethod.SIMILARITY.code:
                if self.prefs.pack_to_others_enabled(self.scene_props):
                    raise RuntimeError("'Pack To Others' is not supported with grouping by similarity")

                if not self.scene_props.rot_enable:
                    raise RuntimeError("Island rotations must be enabled in order to group by similarity")

                if self.scene_props.prerot_disable:
                    raise RuntimeError("'Pre-Rotation Disable' option must be off in order to group by similarity")

        if self.prefs.FEATURE_target_box and self.prefs.target_box_enable:
            validate_target_box(self.scene_props)

    def get_target_box_string(self, target_box):

        prec = 4
        return "{}:{}:{}:{}".format(
            round(target_box[0].x, prec),
            round(target_box[0].y, prec),
            round(target_box[1].x, prec),
            round(target_box[1].y, prec))

    def get_uvp_args(self):

        uvp_args = ['-o', str(UvPackerOpcode.PACK), '-i', str(self.scene_props.precision), '-m',
                       str(self.scene_props.margin)]

        uvp_args += ['-d', self.prefs.dev_array[self.prefs.sel_dev_idx].id]

        # Overlap check
        uvp_args.append('-c')
        # Area measure
        uvp_args.append('-A')

        if self.prefs.pixel_margin_enabled(self.scene_props):
            pixel_margin = get_pixel_margin(self.p_context.context)
            uvp_args += ['-M', str(pixel_margin)]

            if self.prefs.pixel_padding_enabled(self.scene_props):
                pixel_padding = get_pixel_padding(self.p_context.context)
                uvp_args += ['-N', str(pixel_padding)]

            uvp_args += ['-W', self.scene_props.pixel_margin_method]
            uvp_args += ['-Y', str(self.scene_props.pixel_margin_adjust_time)]

        if self.prefs.fixed_scale_enabled(self.scene_props):
            uvp_args += ['-O']
            uvp_args += ['-F', self.scene_props.fixed_scale_strategy]

        if self.prefs.FEATURE_island_rotation and self.scene_props.rot_enable:
            uvp_args += ['-r', str(self.scene_props.rot_step)]

            if self.scene_props.prerot_disable:
                uvp_args += ['-w']

        if self.prefs.FEATURE_packing_depth:
            uvp_args += ['-p', str(self.prefs.packing_depth)]

        if self.prefs.heuristic_enabled(self.scene_props):
            uvp_args += ['-h', str(self.scene_props.heuristic_search_time), '-j', str(self.scene_props.heuristic_max_wait_time)]

            if self.prefs.FEATURE_advanced_heuristic and self.scene_props.advanced_heuristic:
                uvp_args.append('-H')

        uvp_args += ['-g', self.scene_props.pack_mode]

        tile_count, tiles_in_row = self.prefs.tile_grid_config(self.scene_props, self.p_context.context)

        if self.prefs.pack_to_tiles(self.scene_props):
            uvp_args += ['-V', str(tile_count)]

        if self.prefs.tiles_enabled(self.scene_props):
            uvp_args += ['-C', str(tiles_in_row)]

        if self.grouping_enabled():
            if to_uvp_group_method(self.get_group_method()) == UvGroupingMethodUvp.SIMILARITY:
                uvp_args += ['-I', str(self.scene_props.similarity_threshold)]

            if self.prefs.pack_groups_together(self.scene_props):
                uvp_args += ['-U', str(self.scene_props.group_compactness)]

        if self.prefs.multi_device_enabled(self.scene_props):
            uvp_args.append('-u')

        if self.prefs.lock_overlap_enabled(self.scene_props):
            uvp_args += ['-l', self.scene_props.lock_overlapping_mode]

        if self.prefs.pack_to_others_enabled(self.scene_props):
            uvp_args += ['-x']

        if self.prefs.FEATURE_validation and self.scene_props.pre_validate:
            uvp_args.append('-v')

        if self.prefs.normalize_islands_enabled(self.scene_props):
            uvp_args.append('-L')

        if self.prefs.FEATURE_target_box and self.prefs.target_box_enable:
            self.target_box = self.prefs.target_box(self.scene_props)
        
        if self.prefs.pack_ratio_enabled(self.scene_props):
            self.pack_ratio = get_active_image_ratio(self.p_context.context)

            if self.pack_ratio != 1.0:
                uvp_args += ['-q', str(self.pack_ratio)]

                if self.target_box is not None:
                    self.target_box[0].x *= self.pack_ratio
                    self.target_box[1].x *= self.pack_ratio
                else:
                    self.target_box = (Vector((0.0, 0.0)),
                                    Vector((self.pack_ratio, 1.0)))

        if self.target_box is not None:
            uvp_args += ['-B', self.get_target_box_string(self.target_box)]

        uvp_args.append('-b')

        return uvp_args


class UVP2_OT_OverlapCheckOperator(UVP2_OT_PackOperatorGeneric):
    bl_idname = 'uvpackmaster2.uv_overlap_check'
    bl_label = 'Overlap Check'
    bl_description = 'Check wheter selected UV islands overlap each other'

    def process_result(self):

        if self.island_flags_msg is None:
            self.raiseUnexpectedOutputError()

        island_flags = read_int_array(self.island_flags_msg)
        overlap_detected, outside_detected = self.p_context.handle_island_flags(island_flags)

        if overlap_detected:
            self.set_status('WARNING', 'Overlapping islands detected')
        else:
            self.set_status('INFO', 'No overlapping islands detected')

    def validate_pack_params(self):
        pass

    def get_uvp_args(self):

        uvp_args = ['-o', str(UvPackerOpcode.OVERLAP_CHECK)]
        return uvp_args



class UVP2_OT_MeasureAreaOperator(UVP2_OT_PackOperatorGeneric):
    bl_idname = 'uvpackmaster2.uv_measure_area'
    bl_label = 'Measure Area'
    bl_description = 'Measure area of selected UV islands'

    def process_result(self):

        if self.area_msg is None:
            self.raiseUnexpectedOutputError()

        area = self.read_area(self.area_msg)
        self.prefs.stats_area = area
        self.set_status('INFO', 'Islands area: ' + str(area))

    def validate_pack_params(self):
        pass

    def get_uvp_args(self):

        uvp_args = ['-o', str(UvPackerOpcode.MEASURE_AREA)]
        return uvp_args



class UVP2_OT_ValidateOperator(UVP2_OT_PackOperatorGeneric):
    bl_idname = 'uvpackmaster2.uv_validate'
    bl_label = 'Validate UVs'
    bl_description = 'Validate selected UV faces. The validation procedure looks for invalid UV faces i.e. faces with area close to 0, self-intersecting faces, faces overlapping each other'

    def get_confirmation_msg(self):

        if self.prefs.FEATURE_demo:
            return 'WARNING: in the demo mode only the number of invalid faces found is reported, invalid faces will not be selected. Click OK to continue'

        return ''

    def process_result(self):
        if self.invalid_faces_msg is None:
            self.raiseUnexpectedOutputError()

        invalid_face_count = force_read_int(self.invalid_faces_msg)
        invalid_faces = read_int_array(self.invalid_faces_msg)

        if not self.prefs.FEATURE_demo:
            if len(invalid_faces) != invalid_face_count:
                self.raiseUnexpectedOutputError()

            if invalid_face_count > 0:
                # Switch to the face selection mode
                if self.p_context.context.tool_settings.use_uv_select_sync:
                    self.p_context.context.tool_settings.mesh_select_mode = (False, False, True)
                else:
                    self.p_context.context.tool_settings.uv_select_mode = 'FACE'

                self.p_context.select_all_faces(False)
                self.p_context.select_faces(list(invalid_faces), True)
        else:
            if len(invalid_faces) > 0:
                self.raiseUnexpectedOutputError()

        if invalid_face_count > 0:
            self.set_status('WARNING', 'Number of invalid faces found: ' + str(invalid_face_count))
        else:
            self.set_status('INFO', 'No invalid faces found')

    def validate_pack_params(self):
        pass

    def get_uvp_args(self):

        uvp_args = ['-o', str(UvPackerOpcode.VALIDATE_UVS)]
        return uvp_args


class UVP2_OT_ProcessSimilar(UVP2_OT_PackOperatorGeneric):

    def validate_pack_params(self):
        pass

    def get_uvp_args(self):

        uvp_args = ['-o', str(self.get_uvp_opcode()), '-I', str(self.scene_props.similarity_threshold)]
        uvp_args += ['-i', str(self.scene_props.precision)]
        uvp_args += ['-r', str(90)]

        if self.prefs.pack_ratio_enabled(self.scene_props):
            self.pack_ratio = get_active_image_ratio(self.p_context.context)
            uvp_args += ['-q', str(self.pack_ratio)]

        return uvp_args



class UVP2_OT_SelectSimilar(UVP2_OT_ProcessSimilar):
    bl_idname = 'uvpackmaster2.uv_select_similar'
    bl_label = 'Select Similar'
    bl_description = "Selects all islands which have similar shape to islands which are already selected. For more info regarding similarity detection click the help button"

    def get_confirmation_msg(self):

        if self.prefs.FEATURE_demo:
            return 'WARNING: in the demo mode only the number of similar islands found is reported, islands will not be selected. Click OK to continue'

        return ''

    def send_unselected_islands(self):

        return True

    def get_uvp_opcode(self):

        return UvPackerOpcode.SELECT_SIMILAR

    def process_result(self):

        if self.similar_islands_msg is None:
            self.raiseUnexpectedOutputError()

        similar_island_count = force_read_int(self.similar_islands_msg)
        similar_islands = read_int_array(self.similar_islands_msg)

        if not self.prefs.FEATURE_demo:
            if len(similar_islands) != similar_island_count:
                self.raiseUnexpectedOutputError()

            for island_idx in similar_islands:
                self.p_context.select_island_faces(island_idx, self.p_context.uv_island_faces_list[island_idx], True)
        else:
            if len(similar_islands) > 0:
                self.raiseUnexpectedOutputError()

        self.set_status('INFO', 'Similar islands found: ' + str(similar_island_count))



class UVP2_OT_AlignSimilar(UVP2_OT_ProcessSimilar):
    bl_idname = 'uvpackmaster2.uv_align_similar'
    bl_label = 'Align Similar'
    bl_description = "Align selected islands, so islands which are similar are placed on top of each other. For more info regarding similarity detection click the help button"


    def get_uvp_opcode(self):

        return UvPackerOpcode.ALIGN_SIMILAR

    def process_result(self):

        if self.prefs.FEATURE_demo:
            return

        if self.pack_solution_msg is None:
            self.raiseUnexpectedOutputError()

        pack_solution = read_pack_solution(self.pack_solution_msg)
        self.p_context.apply_pack_solution(self.pack_ratio, pack_solution)

        self.set_status('INFO', 'Islands aligned')



class UVP2_OT_ScaleIslands(bpy.types.Operator):

    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def execute(self, context):

        try:
            self.p_context = PackContext(context)
            ratio = get_active_image_ratio(self.p_context.context)
            self.p_context.scale_selected_faces(self.get_scale_factors())

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')


        self.p_context.update_meshes()
        return {'FINISHED'}

    def get_scale_factors(self):
        return (1.0, 1.0)

class UVP2_OT_AdjustIslandsToTexture(UVP2_OT_ScaleIslands):

    bl_idname = 'uvpackmaster2.uv_adjust_islands_to_texture'
    bl_label = 'Adjust Islands To Texture'
    bl_description = "Adjust scale of selected islands so they are suitable for packing into the active texture. CAUTION: this operator should be used only when packing to a non-square texture. For for info regarding non-square packing click the help icon"

    def get_scale_factors(self):
        ratio = get_active_image_ratio(self.p_context.context)
        return (1.0 / ratio, 1.0)

class UVP2_OT_UndoIslandsAdjustemntToTexture(UVP2_OT_ScaleIslands):

    bl_idname = 'uvpackmaster2.uv_undo_islands_adjustment_to_texture'
    bl_label = 'Undo Islands Adjustment'
    bl_description = "Undo adjustment performed by the 'Adjust Islands To Texture' operator so islands are again suitable for packing into a square texture. For for info regarding non-square packing read the documentation"

    def get_scale_factors(self):
        ratio = get_active_image_ratio(self.p_context.context)
        return (ratio, 1.0)


class UVP2_OT_Help(bpy.types.Operator):
    bl_label = 'Help'

    def execute(self, context):

        webbrowser.open(UvpLabels.HELP_BASEURL + self.URL_SUFFIX)
        return {'FINISHED'}


class UVP2_OT_UvpSetupHelp(UVP2_OT_Help):
    bl_label = 'UVP Setup Help'
    bl_idname = 'uvpackmaster2.uv_uvp_setup_help'
    bl_description = "Show help for UVP setup"

    URL_SUFFIX = "uvp-setup"


class UVP2_OT_HeuristicSearchHelp(UVP2_OT_Help):
    bl_label = 'Non-Square Packing Help'
    bl_idname = 'uvpackmaster2.uv_heuristic_search_help'
    bl_description = "Show help for heuristic search"

    URL_SUFFIX = "heuristic-search"


class UVP2_OT_NonSquarePackingHelp(UVP2_OT_Help):
    bl_label = 'Non-Square Packing Help'
    bl_idname = 'uvpackmaster2.uv_nonsquare_packing_help'
    bl_description = "Show help for non-square packing"

    URL_SUFFIX = "non-square-packing"


class UVP2_OT_SimilarityDetectionHelp(UVP2_OT_Help):
    bl_label = 'Similarity Detection Help'
    bl_idname = 'uvpackmaster2.uv_similarity_detection_help'
    bl_description = "Show help for similarity detection"

    URL_SUFFIX = "similarity-detection"


class UVP2_OT_InvalidTopologyHelp(UVP2_OT_Help):
    bl_label = 'Invalid Topology Help'
    bl_idname = 'uvpackmaster2.uv_invalid_topology_help'
    bl_description = "Show help for handling invalid topology errors"

    URL_SUFFIX = "invalid-topology-issues"


class UVP2_OT_PixelMarginHelp(UVP2_OT_Help):
    bl_label = 'Pixel Margin Help'
    bl_idname = 'uvpackmaster2.uv_pixel_margin_help'
    bl_description = "Show help for setting margin in pixels"

    URL_SUFFIX = "pixel-margin"


class UVP2_OT_IslandRotStepHelp(UVP2_OT_Help):
    bl_label = 'Island Rotation Step Help'
    bl_idname = 'uvpackmaster2.uv_island_rot_step_help'
    bl_description = "Show help for setting rotation step on per-island level"

    URL_SUFFIX = "island-rotation-step"


class UVP2_OT_UdimSupportHelp(UVP2_OT_Help):
    bl_label = 'UDIM Support Help'
    bl_idname = 'uvpackmaster2.uv_udim_support_help'
    bl_description = "Show help for UDIM support"

    URL_SUFFIX = "udim-support"


class UVP2_OT_ManualGroupingHelp(UVP2_OT_Help):
    bl_label = 'Manual Grouping Help'
    bl_idname = 'uvpackmaster2.uv_manual_grouping_help'
    bl_description = "Show help for manual grouping"

    URL_SUFFIX = "udim-support#manual-grouping"
