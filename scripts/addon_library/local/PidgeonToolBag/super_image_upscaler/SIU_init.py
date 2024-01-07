from . import (
    SIU_Operators,
    SIU_Settings,
    SIU_Panel,
)
def register_function():
    SIU_Settings.register_function()
    SIU_Operators.register_function()
    SIU_Panel.register_function()


def unregister_function():
    SIU_Panel.unregister_function()
    SIU_Operators.unregister_function()
    SIU_Settings.unregister_function()
