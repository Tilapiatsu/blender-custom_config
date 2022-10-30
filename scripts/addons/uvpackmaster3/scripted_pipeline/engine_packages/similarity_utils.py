from scripted_pipeline import GenericScenario, TO_ENUM
from uvpm_core import packer, SimilarityParams, SimilarityMode, LogType, Axis


class SimilarityScenario(GenericScenario):

    TOPOLOGY_MODE_VERT_COUNT_WARNING_THRESHOLD = 10 * 1000
    TOPOLOGY_MODE_VERT_COUNT_WARNING_MSG = 'The Topology mode may be slow when used with islands with a huge number of vertices (>{})'.format(TOPOLOGY_MODE_VERT_COUNT_WARNING_THRESHOLD)

    def pre_run(self):
        mode = TO_ENUM(SimilarityMode, self.cx.params['mode'])

        if mode == SimilarityMode.TOPOLOGY:
            for island in self.cx.input_islands:
                if island.vert_count() >= self.TOPOLOGY_MODE_VERT_COUNT_WARNING_THRESHOLD:
                    packer.send_log(LogType.WARNING, self.TOPOLOGY_MODE_VERT_COUNT_WARNING_MSG)
                    break

        self.simi_params = SimilarityParams()
        self.simi_params.mode = mode
        self.simi_params.precision = self.cx.params['precision']
        self.simi_params.threshold = self.cx.params['threshold']
        self.simi_params.flipping_enable = self.cx.params['flipping_enable']
        self.simi_params.adjust_scale = self.cx.params['adjust_scale']
        self.simi_params.match_3d_axis = TO_ENUM(Axis, self.cx.params['match_3d_axis'])
        self.simi_params.correct_vertices = self.cx.params['correct_vertices']
        self.simi_params.vertex_threshold = self.cx.params['vertex_threshold']

        align_priority_iparam_name = self.cx.params['align_priority_iparam_name']
        if align_priority_iparam_name is not None:
            self.simi_params.align_priority_iparam_desc = self.iparams_manager.iparam_desc(align_priority_iparam_name)
