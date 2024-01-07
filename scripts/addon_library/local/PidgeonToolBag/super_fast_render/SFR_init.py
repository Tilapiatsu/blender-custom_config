from . import (
    SFR_Settings,
    SFR_Panel,
    SFR_Operators
)
def register_function():
    SFR_Settings.register_function()
    SFR_Operators.register_function()
    SFR_Panel.register_function()


def unregister_function():
    SFR_Panel.unregister_function()
    SFR_Operators.unregister_function()
    SFR_Settings.unregister_function()
