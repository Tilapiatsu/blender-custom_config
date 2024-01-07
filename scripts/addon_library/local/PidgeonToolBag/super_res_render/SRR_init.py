from . import (
    SRR_Panel,
    SRR_Operators,
    SRR_Settings,
)
def register_function():
    SRR_Settings.register_function()
    SRR_Operators.register_function()
    SRR_Panel.register_function()


def unregister_function():
    SRR_Panel.unregister_function()
    SRR_Operators.unregister_function()
    SRR_Settings.unregister_function()
