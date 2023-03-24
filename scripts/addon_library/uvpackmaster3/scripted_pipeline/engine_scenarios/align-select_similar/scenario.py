from similarity_utils import SimilarityScenario
from uvpm_core import packer, RetCode, IslandFlag, LogType


class Scenario(SimilarityScenario):

    def run(self):

        packer.send_log(LogType.STATUS, "Looking for similar islands...")
        simi_islands = self.cx.selected_islands.find_similar(self.simi_params, self.cx.unselected_islands)

        for island in simi_islands:
            island.set_flags(IslandFlag.SELECTED)

        packer.send_out_islands(simi_islands, send_flags=True)
        packer.send_log(LogType.STATUS, "Done. Similar islands found: {}".format(len(simi_islands)))
        return RetCode.SUCCESS
