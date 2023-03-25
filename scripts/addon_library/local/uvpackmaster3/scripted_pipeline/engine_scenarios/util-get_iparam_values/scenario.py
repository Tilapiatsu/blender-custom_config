from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode


class Scenario(GenericScenario):

    def run(self):
        packer.send_out_islands(self.cx.input_islands, send_iparams=True)
        return RetCode.SUCCESS
