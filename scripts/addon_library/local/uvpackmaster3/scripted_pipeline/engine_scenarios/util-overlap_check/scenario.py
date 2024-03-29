from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode, LogType, IslandFlag
from utils import flag_islands


class Scenario(GenericScenario):

    def run(self):

        packer.send_log(LogType.STATUS, "Looking for overlapping islands...")

        islands_to_check = self.cx.selected_islands
        overlapping = islands_to_check.overlapping_islands(islands_to_check)[0]
        overlapping.set_flags(IslandFlag.OVERLAPS)

        flag_islands(islands_to_check, overlapping)

        ret_code = RetCode.NOT_SET

        if len(overlapping) > 0:
            ret_code = RetCode.WARNING
            log_msg = 'Overlapping islands detected (check selected islands)'
        else:
            ret_code = RetCode.SUCCESS
            log_msg = 'No overlapping islands detected'

        packer.send_log(LogType.STATUS, log_msg)
        return ret_code
