from scripted_pipeline import GenericScenario
from uvpm_core import SimilarityParams


class SimilarityScenario(GenericScenario):

    def pre_run(self):

        self.simi_params = SimilarityParams()
        self.simi_params.precision = self.cx.params['precision']
        self.simi_params.threshold = self.cx.params['threshold']
        self.simi_params.adjust_scale = self.cx.params['adjust_scale']
        self.simi_params.check_vertices = self.cx.params['check_vertices']
        self.simi_params.correct_vertices = self.cx.params['correct_vertices']
        self.simi_params.vertex_threshold = self.cx.params['vertex_threshold']

        align_priority_iparam_name = self.cx.params['align_priority_iparam_name']
        if align_priority_iparam_name is not None:
            self.simi_params.align_priority_iparam_desc = self.iparams_manager.iparam_desc(align_priority_iparam_name)
