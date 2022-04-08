# from scripted_pipeline import 
from pack_utils import PackScenario
from uvpm_core import (PackParams,
                     PackTask,
                     StageParams,
                     StdStageTarget,
                     InputError,
                     solution_available)
from utils import eprint


class Scenario(PackScenario):

    def run(self):

        stage_params = StageParams()
        stage_target = StdStageTarget()

        for box in self.target_boxes:
            stage_target.append(box)

        for group in self.g_scheme.groups:
            if group.islands is None:
                continue

            task = PackTask(0, self.pack_params)

            task.add_stage(stage_params, stage_target, group.islands, self.static_islands)
            self.pack_manager.add_task(task)

        return self.pack_manager.pack()


    def post_run_island_sets(self):

        packed_islands_array = []

        for task in self.pack_manager.tasks:
            assert(task.result is not None)
            result = task.result

            if solution_available(result.ret_code):
                packed_islands_array.append(result.islands)

        return packed_islands_array, self.pack_manager.invalid_islands
