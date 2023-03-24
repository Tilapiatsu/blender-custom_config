from scripted_pipeline import GenericScenario
from uvpm_core import IslandSet, packer, RetCode, LogType
from utils import area_to_string

import math


class Scenario(GenericScenario):

    def run(self):
        # area = self.cx.selected_islands.area()

        eps = 1.0e-9
        avg_scale_ratio = 0.0

        valid_count = 0

        for island in self.cx.unselected_islands:
            area = island.faces_area()
            area_3d = island.faces_3d_area()

            if area < eps or area_3d < eps:
                continue

            ratio = area_3d / area
            avg_scale_ratio += ratio

            valid_count += 1

        if valid_count == 0:
            packer.send_log(LogType.STATUS, 'No valid unselected island found - adjustment could not be made')
            return RetCode.WARNING

        avg_scale_ratio /= valid_count
        out_islands = IslandSet()

        for island in self.cx.selected_islands:
            area = island.faces_area()
            area_3d = island.faces_3d_area()

            if area < eps or area_3d < eps:
                continue

            scale = math.sqrt(area_3d / avg_scale_ratio / area)
            out_islands.append(island.scale(scale, scale, island.bbox().center()))

        packer.send_out_islands(out_islands, send_transform=True)
        packer.send_log(LogType.STATUS, "Done")
        return RetCode.SUCCESS
