from pack_utils import PackScenario
from uvpm_core import (PackParams,
                     PackTask,
                     StageParams,
                     StdStageTarget)


class Scenario(PackScenario):

    def run(self):

        task = PackTask(0, self.pack_params)

        stage_params = StageParams()
        stage_target = StdStageTarget()

        for box in self.target_boxes:
            stage_target.append(box)

        task.add_stage(stage_params, stage_target, self.islands_to_pack, self.static_islands)
        self.pack_manager.add_task(task)

        return self.pack_manager.pack()
