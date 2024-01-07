from . import (
    SRF_Settings,
    SRF_Panel,
    SRF_Operators
)
def register_function():
    SRF_Settings.register_function()
    SRF_Operators.register_function()
    SRF_Panel.register_function()


def unregister_function():
    SRF_Panel.unregister_function()
    SRF_Operators.unregister_function()
    SRF_Settings.unregister_function()
