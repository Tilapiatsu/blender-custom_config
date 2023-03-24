from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode, LogType
from utils import area_to_string


class Scenario(GenericScenario):

    def run(self):
        area = self.cx.selected_islands.area()
        packer.send_log(LogType.STATUS, "Selected islands area: {}".format(area_to_string(area)))
        return RetCode.SUCCESS
