# from scripted_pipeline import 
from pack_utils import PackScenario
from uvpm_core import (PackParams,
                     PackTask,
                     StageParams,
                     StdStageTarget,
                     InputError)
from utils import eprint

from collections import defaultdict


class TexelDensityCluster:

    def __init__(self):

        self.groups = []

    def add_group(self, group):

        if len(group.target_boxes) == 0:
            raise InputError("Group with no target box encountered. Group name: {}".format(group.name))

        stage_target = StdStageTarget()

        for box in group.target_boxes:
            stage_target.append(box)

        group.stage_target = stage_target
        self.groups.append(group)

    def validate(self, other):

        for group in self.groups:
            for other_group in other.groups:

                if group.stage_target.intersects(other_group.stage_target):
                    raise InputError("Target boxes of groups packed with independent texel density must not intersect. Group names: {}, {}".format(group.name, other_group.name))


class Scenario(PackScenario):

    def run(self):

        tdensity_clusters = defaultdict(TexelDensityCluster)

        for group in self.g_scheme.groups:

            if group.islands is None:
                continue

            tdensity_clusters[group.tdensity_cluster].add_group(group)

        tdensity_clusters = list(tdensity_clusters.values())

        if len(tdensity_clusters) == 0:
            raise InputError("No group found on input")

        for idx1 in range(len(tdensity_clusters)):
            for idx2 in range(idx1+1, len(tdensity_clusters)):
                tdensity_clusters[idx1].validate(tdensity_clusters[idx2])

        for td_cluster in tdensity_clusters:

            task = PackTask(0, self.pack_params)

            for group in td_cluster.groups:
                stage_params = StageParams()

                if group.rotation_enable is not None:
                    stage_params.rotation_enable = group.rotation_enable
                if group.pre_rotation_disable is not None:
                    stage_params.pre_rotation_disable = group.pre_rotation_disable
                if group.rotation_step is not None:
                    stage_params.rotation_step = group.rotation_step
                if group.pixel_margin is not None:
                    stage_params.pixel_margin = group.pixel_margin
                if group.pixel_padding is not None:
                    stage_params.pixel_padding = group.pixel_padding
                if group.extra_pixel_margin_to_others is not None:
                    stage_params.extra_pixel_margin_to_others = group.extra_pixel_margin_to_others
                if group.pixel_margin_tex_size is not None:
                    stage_params.pixel_margin_tex_size = group.pixel_margin_tex_size

                task.add_stage(stage_params, group.stage_target, group.islands, self.static_islands)

            self.pack_manager.add_task(task)

        return self.pack_manager.pack()
