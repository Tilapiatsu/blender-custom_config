from scripted_pipeline import GenericScenario
from utils import box_from_coords
from geom_utils import islands_inside_box
from uvpm_core import packer, RetCode, IslandSet


class Scenario(GenericScenario):

    def run(self):
        fully_inside = self.cx.params['fully_inside']
        orig_box = box_from_coords(self.cx.params['orig_box'])
        modified_box = box_from_coords(self.cx.params['modified_box'])

        islands_inside = islands_inside_box(self.cx.selected_islands, orig_box, fully_inside)
        box_offset = modified_box.min_corner - orig_box.min_corner

        transformed_islands = IslandSet()

        for island in islands_inside:
            tr_island = island.offset(box_offset.x, box_offset.y)
            transformed_islands.append(tr_island)

        packer.send_out_islands(transformed_islands, send_transform=True)
        return RetCode.SUCCESS
