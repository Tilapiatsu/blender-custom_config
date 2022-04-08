from scripted_pipeline import GenericScenario
from utils import box_from_coords, eprint
from geom_utils import islands_inside_box
from uvpm_core import packer, RetCode, IslandSet, IslandFlag



class Scenario(GenericScenario):

    def run(self):
        fully_inside = self.cx.params['fully_inside']
        active_box = box_from_coords(self.cx.params['active_box'])
        select = self.cx.params['select']

        target_islands = self.cx.unselected_islands if select else self.cx.selected_islands
        islands_inside = islands_inside_box(target_islands, active_box, fully_inside)

        if select:
            islands_inside.set_flags(IslandFlag.SELECTED)
        else:
            islands_inside.clear_flags(IslandFlag.SELECTED)

        packer.send_out_islands(islands_inside, send_flags=True)
        return RetCode.SUCCESS
