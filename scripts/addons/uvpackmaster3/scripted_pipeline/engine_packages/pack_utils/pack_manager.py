
import time

from uvpm_core import (\
    packer,
    LogType,
    RetCode,
    IslandSet,
    append_ret_codes,
    solution_available)
from utils import area_to_string, eprint


def pack_manager_result_handler(self, task, result):
    global packer
    new_result = False

    if self.result_array[task.id] is None:
        self.result_count += 1
        new_result = True

    self.result_array[task.id] = result
    # self.scenario.send_out_islands([result.islands, result.non_packed_islands])

    if self.result_count < len(self.tasks):
        return

    assert(self.result_count == len(self.tasks))
    if new_result:
        self.scenario.send_out_islands([result.islands for result in self.result_array] + [result.non_packed_islands for result in self.result_array], send_transform=True)
    else:
        self.scenario.send_out_islands([result.islands, result.non_packed_islands], send_transform=True)

    if self.log_result_area:
        area_sum = 0.0
        for result in self.result_array:
            area_sum += result.islands.area()
        packer.send_log(LogType.INFO, "New result area: {}".format(area_to_string(area_sum)))


class PackManager:

    HEURISTIC_HINT = 'press ESC to stop'

    def __init__(self, scenario, runconfig):
        self.scenario = scenario
        self.runconfig = runconfig
        self.tasks = []
        self.packed_islands = None
        self.invalid_islands = None
        self.log_result_area = False

    def add_task(self, task):
        task.id = len(self.tasks)
        self.tasks.append(task)

    def standard_log(self):
        return 'Packing in progress', -1

    def heuristic_search_log(self):
        return 'Heuristic search in progress', -1

    def heuristic_search_time_log(self):
        now = time.time()
        run_time = now - self.start_time
        time_left = max(0, int(round(float(self.runconfig.heuristic_search_time) - run_time)))
        return "{} (time left: {} s.)".format(self.heuristic_search_log()[0], time_left), 1000

    def init_log_method(self):
        heuristic_search_time = self.runconfig.heuristic_search_time
        hint_str = None
        
        if heuristic_search_time >= 0:
            self.log_result_area = True
            hint_str = self.HEURISTIC_HINT

            if heuristic_search_time > 0:
                self.start_time = time.time()
                # self.time_left = float(heuristic_search_time)
                self.log_method = self.heuristic_search_time_log
            else:
                self.log_method = self.heuristic_search_log
        else:
            self.log_method = self.standard_log

        if hint_str is not None:
            packer.send_log(LogType.HINT, hint_str)

    def pack(self):
        self.result_array = [None] * len(self.tasks)
        self.result_count = 0

        self.runconfig.asyn = True
        self.runconfig.realtime_solution = True
        self.runconfig.set_result_handler(pack_manager_result_handler, self)

        self.init_log_method()

        for task in self.tasks:
            packer.run_task(task, self.runconfig)

        all_tasks_completed = False
        while not all_tasks_completed:
            log_str, time_to_wait = self.log_method()
            packer.send_log(LogType.STATUS, log_str)
            all_tasks_completed = packer.wait_for_all_tasks(time_to_wait)

        ret_code = RetCode.NOT_SET
        self.packed_islands = IslandSet()
        self.invalid_islands = IslandSet()

        for task in self.tasks:
            assert(task.result is not None)
            result = task.result

            ret_code = append_ret_codes(ret_code, result.ret_code)

            if result.ret_code == RetCode.INVALID_ISLANDS:
                self.invalid_islands += result.invalid_islands

            if solution_available(result.ret_code):
                self.packed_islands += result.islands

        return ret_code
