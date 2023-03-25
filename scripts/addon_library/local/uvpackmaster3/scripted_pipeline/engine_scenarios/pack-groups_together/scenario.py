from pack_utils import PackScenario
from uvpm_core import (
    packer,
    LogType,
    PackTask,
    StageParams,
    StdStageTarget)


class Scenario(PackScenario):

    HEURISTIC_WARNINGS = [
        "Packing groups together requires heuristic search enabled to produce the optimal result",
        "It is strongy recommended to enable heuristic search in this mode"
    ]

    def run(self):

        if not self.pack_manager.runconfig.heuristic_search_enabled():
            for warn in self.HEURISTIC_WARNINGS:
                packer.send_log(LogType.WARNING, warn)
        
        self.pack_params.grouping_compactness = self.g_scheme.group_compactness
        pack_task = PackTask(0, self.pack_params)

        stage_params = StageParams()

        box = self.target_boxes[0]
        stage_target = StdStageTarget()
        stage_target.append(box)

        group_islands = [group.islands for group in self.g_scheme.groups if group.islands is not None]
        stage_params.pack_groups_together = len(group_islands) > 1
        
        pack_task.add_stage(stage_params, stage_target, group_islands, self.static_islands)

        self.pack_manager.add_task(pack_task)
        return self.pack_manager.pack()
