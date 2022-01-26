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
from sys import flags
import threading
import signal
import webbrowser
import tempfile

from .utils import *
from .pack_context import *
from .connection import *
# from .prefs import *
from .os_iface import *
from .island_params import *
from .labels import Labels
from .register_utils import check_engine, unregister_engine
from .overlay import EngineOverlayManager
from .prefs_scripted_utils import ScriptParams, SCRIPTED_PIPELINE_DIRNAME, ENGINE_PACKAGES_DIRNAME
from .log import LogManager
from .grouping_scheme import GroupingSchemeAccess, UVPM3_GroupingScheme, GroupingSchemeSerializer
from .box_utils import disable_box_rendering
from .event import DefaultFinishConditionMixin
from .out_island import OutIslands


import bmesh
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty, PointerProperty
import mathutils


class NoUvFaceError(Exception):
    pass

class ModeIdAttributeMixin:

    mode_id : StringProperty(name='mode_id', default='')


class UVPM3_OT_Generic(bpy.types.Operator):
    
    pass


class UVPM3_OT_Engine(UVPM3_OT_Generic, DefaultFinishConditionMixin):

    bl_options = {'UNDO'}

    MODAL_INTERVAL_S = 0.1
    STATUS_INITIAL = 'Initialization'
    HINT_INITIAL = 'press ESC to cancel'

    interactive = False

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.engine_initialized and context.active_object is not None and context.active_object.mode == 'EDIT'

    def __init__(self):
        
        self.cancel_sig_sent = False
        self._timer = None

    def check_engine_retcode(self, retcode):
        self.prefs.engine_retcode = retcode

        if retcode in {UvpmRetCode.SUCCESS,
                       UvpmRetCode.INVALID_ISLANDS,
                       UvpmRetCode.NO_SPACE,
                       UvpmRetCode.NO_SIUTABLE_DEVICE,
                       UvpmRetCode.INVALID_INPUT}:
            return

        if retcode == UvpmRetCode.CANCELLED:
            self.log_manager.log(UvpmLogType.STATUS, 'Operation cancelled by the user')
            return

        raise RuntimeError('Pack process returned an error')

    def get_scenario_id(self):

        if hasattr(self, 'SCENARIO_ID'):
            return self.SCENARIO_ID

        if self.mode is not None and hasattr(self.mode, 'SCENARIO_ID'):
            return self.mode.SCENARIO_ID

        raise RuntimeError("Provide a 'senario_id' method")

    def get_scenario(self):

        return RunScenario.get_scenario(self.get_scenario_id())

    def mode_method_std_call(self, default_impl, method_name):

        if self.mode is not None and hasattr(self.mode, method_name):
            method = getattr(self.mode, method_name)
            return method()

        return default_impl()

    def raiseUnexpectedOutputError(self):

        raise RuntimeError('Unexpected output from the pack process')

    def set_report(self, report_type, report_str):

        self.report({report_type}, report_str)

    def add_warning(self, warn_msg):
        # MUSTDO: remove it
        pass

    def get_box_renderer(self):

        return self.mode_method_std_call(lambda: None, 'get_box_renderer')

    def get_iparam_serializers(self):

        return self.mode_method_std_call(lambda: [], 'get_iparam_serializers')

    def update_context_meshes(self):

        if self.p_context is not None:
            self.p_context.update_meshes()
            self.redraw_context_area()

    def exit_common(self):

        if self.p_context is not None:
            if self._timer is not None:
                wm = self.p_context.context.window_manager
                wm.event_timer_remove(self._timer)

        if self.ov_manager is not None:
            self.ov_manager.finish()

        if self.box_renderer is not None:
            self.box_renderer.finish()

        if self.show_region_hud_saved is not None:
            self.context.area.spaces.active.show_region_hud = self.show_region_hud_saved

        self.update_context_meshes()

    def read_islands(self, islands_msg):

        islands = []
        island_cnt = force_read_int(islands_msg)
        selected_cnt = force_read_int(islands_msg)

        for i in range(island_cnt):
            islands.append(read_int_array(islands_msg))

        self.p_context.set_islands(selected_cnt, islands)

    def redraw_context_area(self):

        if self.interactive:
            self.context.area.tag_redraw()

    def post_operation(self):
        pass

    def require_selection(self):
        return True

    def finish_after_operation_done(self):
        
        return not self.interactive

    def handle_operation_done(self):

        if in_debug_mode():
            print('UVPM operation time: ' + str(time.time() - self.start_time))

        self.operation_done = True

        send_finish_confirmation(self.engine_proc)

        try:
            self.engine_proc.wait(5)
        except:
            raise RuntimeError('The UVPM process wait timeout reached')

        self.connection_thread.join()
        self.check_engine_retcode(self.engine_proc.returncode)

        if not self.p_context.islands_received():
            self.raiseUnexpectedOutputError()

        self.post_operation()

        if self.log_manager.type_logged(UvpmLogType.ERROR):
            report_type = 'ERROR'
            report_msg = 'Errors were reported'
        elif self.log_manager.type_logged(UvpmLogType.WARNING):
            report_type = 'WARNING'
            report_msg = 'Warnings were reported'
        else:
            report_type = 'INFO'
            report_msg = 'Done'

        # self.set_report(report_type, report_msg)

        if self.finish_after_operation_done():
            raise OpFinishedException()

        if self.log_manager.last_log(UvpmLogType.STATUS) is None:
            self.log_manager.log(UvpmLogType.STATUS, report_msg)

        hint_str = self.operation_done_hint()
        if hint_str is not None:
            self.log_manager.log(UvpmLogType.HINT, hint_str)

        if self.ov_manager is not None:
            self.ov_manager.print_dev_progress = False
            self.redraw_context_area()

    def finish(self, context):

        self.exit_common()
        return {'FINISHED', 'PASS_THROUGH'}

    def cancel(self, context):
        if self.engine_proc is not None:
            self.engine_proc.terminate()
        # self.progress_thread.terminate()
        self.exit_common()
        return {'FINISHED'}

    def handle_engine_msg_spec(self, msg_code, msg):
        return False

    def handle_event_spec(self, event):
        return False

    def handle_out_islands_msg(self, out_islands_msg):

        out_islands = OutIslands(out_islands_msg)

        self.p_context.apply_out_islands(out_islands)
        self.update_context_meshes()

    def handle_benchmark_msg(self, benchmark_msg):

        entry_count = force_read_int(benchmark_msg)

        for i in range(entry_count):
            dev_id = decode_string(benchmark_msg)
            dev_found = False

            for dev in self.prefs.device_array():
                if dev.id == dev_id:
                    dev_found = True
                    bench_entry = dev.bench_entry
                    bench_entry.decode(benchmark_msg)
                    break

            if not dev_found:
                self.raiseUnexpectedOutputError()

        self.redraw_context_area()

    def handle_log_msg(self, log_msg):

        log_type = force_read_int(log_msg)
        log_string = decode_string(log_msg)

        self.log_manager.log(log_type, log_string)
        self.redraw_context_area()

    def handle_engine_msg(self, msg):

        msg_code = force_read_int(msg)

        if self.handle_engine_msg_spec(msg_code, msg):
            return

        if msg_code == UvpmMessageCode.PHASE:
            self.curr_phase = force_read_int(msg)

            # Inform the upper layer wheter it should finish
            if self.curr_phase == UvpmPhaseCode.DONE:
                self.handle_operation_done()

        elif msg_code == UvpmMessageCode.ISLANDS:

            self.read_islands(msg)

        elif msg_code == UvpmMessageCode.OUT_ISLANDS:

            self.handle_out_islands_msg(msg)

        elif msg_code == UvpmMessageCode.BENCHMARK:

            self.handle_benchmark_msg(msg)

        elif msg_code == UvpmMessageCode.LOG:

            self.handle_log_msg(msg)

        else:
            self.raiseUnexpectedOutputError()

    def enter_hang_mode(self):

        if self.hang_detected:
            return

        self.hang_detected = True
        self.hang_saved_logs = (self.log_manager.last_log(UvpmLogType.STATUS), self.log_manager.last_log(UvpmLogType.HINT))
        self.log_manager.log(UvpmLogType.STATUS, 'Packer process not responding for a longer time')
        self.log_manager.log(UvpmLogType.HINT, 'press ESC to abort')
        
    def quit_hang_mode(self):

        if not self.hang_detected:
            return

        self.hang_detected = False
        saved_status, saved_hint = self.hang_saved_logs

        self.log_manager.log(UvpmLogType.STATUS, saved_status)
        self.log_manager.log(UvpmLogType.HINT, saved_hint)

    def handle_communication(self):

        if self.operation_done:
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
                self.quit_hang_mode()
                self.handle_engine_msg(item)

            else:
                raise RuntimeError('Unexpected output from the connection thread')
            
            msg_received += 1

        curr_time = time.time()

        if msg_received > 0:
            self.last_msg_time = curr_time
        else:
            if self.curr_phase != UvpmPhaseCode.STOPPED and curr_time - self.last_msg_time > self.hang_timeout:
                self.enter_hang_mode()

    def handle_event(self, event):
        # Kill the UVPM process unconditionally if a hang was detected
        if self.hang_detected and event.type == 'ESC':
            raise OpAbortedException()

        if self.handle_event_spec(event):
            return

        if self.operation_done and (self.operation_num != self.prefs.operation_counter or self.operation_done_finish_condition(event)):
            raise OpFinishedException()

        if self.box_renderer is not None:
            try:
                if self.box_renderer.coords_update_needed(event):
                    self.box_renderer.update_coords()

            except Exception as ex:
                if in_debug_mode():
                    print_backtrace(ex)

                raise OpFinishedException()

        # Generic event processing code
        if event.type == 'ESC':
            if not self.cancel_sig_sent:
                self.engine_proc.send_signal(os_cancel_sig())
                self.cancel_sig_sent = True

        elif event.type == 'TIMER':
            self.handle_communication()

    def modal_ret_value(self, event):

        if self.operation_done:
            return {'PASS_THROUGH'}

        if event.type in {'MIDDLEMOUSE','WHEELDOWNMOUSE', 'WHEELUPMOUSE'}:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        cancel = False
        finish = False

        try:
            if self.context.mode != 'EDIT_MESH':
                if self.operation_done:
                    raise OpFinishedException()

                raise RuntimeError('Edit Mode exited - operation cancelled')
            # try:
            self.handle_event(event)

            # Check whether the uvpm process is alive
            if not self.operation_done and self.engine_proc.poll() is not None:
                # It should not be required to but check once again to be on the safe side
                self.handle_communication()

                if not self.operation_done:
                    # Special value indicating a crash
                    self.prefs.engine_retcode = -1
                    raise RuntimeError('Packer process died unexpectedly')

            # except OpFinishedException:
            #     finish = True
            # except:
            #     raise

            # if finish:
            #     return self.finish(context)

        except OpFinishedException:
            finish = True

        except OpAbortedException:
            self.set_report('INFO', 'Packer process killed')
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_report('ERROR', str(ex))
            cancel = True

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_report('ERROR', 'Unexpected error')

            cancel = True

        if cancel:
            return self.cancel(context)

        if finish:
            return self.finish(context)

        return self.modal_ret_value(event)

    def pre_operation(self):
        pass

    def execute(self, context):

        # MUSTOD: move it to __init__
        cancel = False

        self.mode = None
        self.operation_done = False
        self.engine_proc = None
        self.curr_phase = None

        self.context = context
        self.script_params = None

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvpm3_props

        self.p_context = None
        self.g_scheme = None

        self.ov_manager = None
        self.box_renderer = None

        self.show_region_hud_saved = None

        self.operation_num = self.prefs.operation_counter + 1
        self.prefs.operation_counter += 1

        # Disable any box rendering if active
        disable_box_rendering(None, context)

        if self.interactive and self.context.area.spaces.active.show_region_hud:
            self.show_region_hud_saved = self.context.area.spaces.active.show_region_hud
            self.context.area.spaces.active.show_region_hud = False

        try:
            if hasattr(self, 'mode_id') and self.mode_id != '':
                self.mode = self.prefs.get_mode(self.mode_id, self.context)
                self.mode.init_op(self)

            if not check_engine():
                unregister_engine()
                redraw_ui(context)
                raise RuntimeError("UVPM engine broken")


            def post_log_op(log_type, log_str):
                if in_debug_mode():
                    print_log(log_str)
                self.redraw_context_area()

            self.log_manager = LogManager(post_log_op)
            self.log_manager.log(UvpmLogType.STATUS, self.STATUS_INITIAL)
            self.log_manager.log(UvpmLogType.HINT, self.HINT_INITIAL)


            self.prefs.reset_stats()
            self.p_context = PackContext(self.context)
            self.run_scenario = self.get_scenario()

            if self.run_scenario is None:
                raise RuntimeError('Invalid scenario provided')

            self.pre_operation()

            send_unselected = self.send_unselected_islands()
            send_groups = self.grouping_enabled()
            send_verts_3d = self.send_verts_3d()

            iparam_serializers = self.get_iparam_serializers()

            if send_groups:
                self.g_scheme = self.init_grouping_scheme()
                iparam_serializers.append(GroupingSchemeSerializer(self.g_scheme))

            serialized_maps, selected_cnt, unselected_cnt =\
                self.p_context.serialize_uv_maps(send_unselected, send_verts_3d, iparam_serializers)

            if self.require_selection():
                if selected_cnt == 0:
                    raise NoUvFaceError('No UV face selected')
            
            else:
                if selected_cnt + unselected_cnt == 0:
                    raise NoUvFaceError('No UV face visible')

            engine_args_final = [get_engine_execpath(), '-E']
            engine_args_final += ['-o', str(UvpmOpcode.EXECUTE_SCENARIO)]
            engine_args_final += ['-t', str(self.prefs.thread_count)]

            if send_unselected:
                engine_args_final.append('-s')

            if self.packing_operation():
                engine_args_final.append('-p')

            if in_debug_mode():
                if self.prefs.seed > 0:
                    engine_args_final += ['-S', str(self.prefs.seed)]

                if self.prefs.wait_for_debugger:
                    engine_args_final.append('-G')

                engine_args_final += ['-T', str(self.prefs.test_param)]
                print('Pakcer args: ' + ' '.join(x for x in engine_args_final))
            

            # --- Setup script params ---
            self.script_params = self.setup_script_params()
            self.script_params.add_device_settings(self.prefs.device_array())

            if self.skip_topology_parsing():
                self.script_params.add_param('__skip_topology_parsing', True)
            
            packages_dirpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), SCRIPTED_PIPELINE_DIRNAME, ENGINE_PACKAGES_DIRNAME)
            scenario_dirpath = os.path.abspath(os.path.dirname(self.run_scenario['script_path']))
            self.script_params.add_sys_path(packages_dirpath)
            self.script_params.add_sys_path(scenario_dirpath)

            if self.g_scheme is not None:
                self.script_params.add_grouping_scheme(self.g_scheme)
            # ------

            out_data = self.script_params.serialize()
            out_data += serialized_maps

            if self.prefs.write_to_file:
                out_filepath = os.path.join(tempfile.gettempdir(), 'uv_islands.data')
                out_file = open(out_filepath, 'wb')
                out_file.write(out_data)
                out_file.close()


            creation_flags = os_engine_creation_flags()
            popen_args = dict()

            if creation_flags is not None:
                popen_args['creationflags'] = creation_flags

            self.engine_proc = subprocess.Popen(engine_args_final,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             **popen_args)

            out_stream = self.engine_proc.stdin
            out_stream.write(out_data)
            out_stream.flush()

            self.start_time = time.time()

            self.last_msg_time = self.start_time
            self.hang_detected = False
            self.hang_timeout = 10.0

            # Start progress monitor thread
            self.progress_queue = queue.Queue()
            self.connection_thread = threading.Thread(target=connection_thread_func,
                                                      args=(self.engine_proc.stdout, self.progress_queue))
            self.connection_thread.daemon = True
            self.connection_thread.start()
            self.progress_array = [0]
            self.progress_msg = ''
            self.progress_sec_left = -1
            self.progress_iter_done = -1
            self.progress_last_update_time = 0.0

            if self.interactive:
                ov_dev_array = self.prefs.dev_array if self.packing_operation() else None
                self.ov_manager = EngineOverlayManager(self, ov_dev_array)
                self.box_renderer = self.get_box_renderer()

        except NoUvFaceError as ex:
            self.set_report('WARNING', str(ex))
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_report('ERROR', str(ex))
            cancel = True
            
        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.set_report('ERROR', 'Unexpected error')
            cancel = True

        # MUSTDO: is it needed?
        self.update_context_meshes()

        if cancel:
            return self.cancel(context)

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
        # self.scene_props = context.scene.uvpm3_props
        return self.execute(context)

    def send_unselected_islands(self):

        return self.mode_method_std_call(lambda: False, 'send_unselected_islands')

    def grouping_enabled(self):

        return self.mode_method_std_call(lambda: False, 'grouping_enabled')

    def skip_topology_parsing(self):

        return self.mode_method_std_call(lambda: False, 'skip_topology_parsing')

    def setup_script_params(self):

        return self.mode_method_std_call(lambda: ScriptParams(), 'setup_script_params')

    def get_group_method(self):

        def raise_unexpected_grouping():
            raise RuntimeError('Unexpected grouping requested')

        return self.mode_method_std_call(raise_unexpected_grouping, 'get_group_method')

    def packing_operation(self):

        return self.mode_method_std_call(lambda: False, 'packing_operation')

    def send_verts_3d(self):

        return self.mode_method_std_call(lambda: False, 'send_verts_3d')

    def init_grouping_scheme(self):

        g_method = self.get_group_method()
        g_scheme = UVPM3_GroupingScheme()

        if GroupingMethod.auto_grouping_enabled(g_method):
            g_scheme.options.copy_from(self.scene_props.auto_group_options)

        else:
            g_scheme_access = GroupingSchemeAccess()
            g_scheme_access.init_access(self.context)

            if g_scheme_access.active_g_scheme is None:
                raise RuntimeError('Manaul grouping requested but no grouping scheme was found - add a grouping scheme in the Grouping panel')

            g_scheme.copy_from(g_scheme_access.active_g_scheme)

        g_scheme.init_group_map(self.p_context, g_method)
        g_scheme.apply_tdensity_policy()
        g_scheme.apply_group_layout()

        return g_scheme


class UVPM3_OT_ScaleIslands(bpy.types.Operator):

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

class UVPM3_OT_AdjustIslandsToTexture(UVPM3_OT_ScaleIslands):

    bl_idname = 'uvpackmaster3.uv_adjust_islands_to_texture'
    bl_label = 'Adjust Islands To Texture'
    bl_description = "Adjust scale of selected islands so they are suitable for packing into the active texture. CAUTION: this operator should be used only when packing to a non-square texture. For for info regarding non-square packing click the help icon"

    def get_scale_factors(self):
        ratio = get_active_image_ratio(self.p_context.context)
        return (1.0 / ratio, 1.0)

class UVPM3_OT_UndoIslandsAdjustemntToTexture(UVPM3_OT_ScaleIslands):

    bl_idname = 'uvpackmaster3.uv_undo_islands_adjustment_to_texture'
    bl_label = 'Undo Islands Adjustment'
    bl_description = "Undo adjustment performed by the 'Adjust Islands To Texture' operator so islands are again suitable for packing into a square texture. For for info regarding non-square packing read the documentation"

    def get_scale_factors(self):
        ratio = get_active_image_ratio(self.p_context.context)
        return (ratio, 1.0)



class UrlSuffixMixin:

    url_suffix : StringProperty(default='', name='')


class UVPM3_OT_HelpGeneric(UVPM3_OT_Generic):

    from .version import UvpmVersionInfo

    HELP_BASEURL = "https://uvpackmaster.com/doc3/blender/{}/".format(UvpmVersionInfo.addon_version_string())
    ATTRS_TO_CHECK = ['URL_SUFFIX', 'url_suffix']
    
    def execute(self, context):

        url_suffix = None

        for attr in self.ATTRS_TO_CHECK:
            if hasattr(self, attr):
                url_suffix = getattr(self, attr)
                break

        if not url_suffix:
            return {'CANCELLED'}

        webbrowser.open(self.HELP_BASEURL + url_suffix)
        return {'FINISHED'}


class UVPM3_OT_Help(UVPM3_OT_HelpGeneric, UrlSuffixMixin):

    bl_label = 'Show Help'
    bl_idname = 'uvpackmaster3.help'
    bl_description = "Show help for the given functionality"


class UVPM3_OT_MainModeHelp(UVPM3_OT_HelpGeneric, UrlSuffixMixin):

    bl_label = 'Show Mode Help'
    bl_idname = 'uvpackmaster3.main_mode_help'
    bl_description = "Show help for the currently selected mode"


class UVPM3_OT_SetupHelp(UVPM3_OT_HelpGeneric):

    bl_label = 'UVPackmaster Setup Help'
    bl_idname = 'uvpackmaster3.uvpm_setup_help'
    bl_description = "Show help for UVPackmaster setup"

    URL_SUFFIX = "10-uvpackmaster-setup"
