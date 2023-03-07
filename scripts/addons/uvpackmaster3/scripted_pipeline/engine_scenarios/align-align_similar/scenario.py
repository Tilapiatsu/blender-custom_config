from similarity_utils import SimilarityScenario
from uvpm_core import packer, RetCode, LogType, IslandSet


class Scenario(SimilarityScenario):

    def run(self):

        packer.send_log(LogType.STATUS, "Similar islands aligning...")

        if self.stack_group_iparam_desc:
            (aligned_groups, non_aligned_islands) = self.align_similar_by_stack_group(self.cx.selected_islands)
        else:
            (aligned_groups, non_aligned_islands) = self.align_similar(self.cx.selected_islands)

        aligned_islands = IslandSet()
        for group in aligned_groups:
            aligned_islands += group

        send_kwargs = {'send_vertices' if self.simi_params.correct_vertices else 'send_transform' : True}
        packer.send_out_islands(aligned_islands, **send_kwargs)
        packer.send_log(LogType.STATUS, "Done. Islands aligned: {}".format(len(aligned_islands)))
        return RetCode.SUCCESS
