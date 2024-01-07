from . import (
    SID_Settings,
    SID_Operators,
    SID_Panel,
)
def register_function():
    SID_Settings.register_function()
    SID_Operators.register_function()
    SID_Panel.register_function()


def unregister_function():
    SID_Panel.unregister_function()
    SID_Operators.unregister_function()
    SID_Settings.unregister_function()
