from similarity_utils import SimilarityScenario
from uvpm_core import packer, RetCode, LogType


class Scenario(SimilarityScenario):

    def run(self):

        packer.send_log(LogType.STATUS, "Similar islands aligning...")
        aligned_islands = self.cx.selected_islands.align_similar(self.simi_params)

        send_kwargs = {'send_vertices' if self.simi_params.correct_vertices else 'send_transform' : True}
        packer.send_out_islands(aligned_islands, **send_kwargs)
        packer.send_log(LogType.STATUS, "Done. Islands aligned: {}".format(len(aligned_islands)))
        return RetCode.SUCCESS
