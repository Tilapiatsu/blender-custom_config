from . import (
    SEA_Settings,
    SEA_Operators,
    SEA_Panel,
)
def register_function():
    SEA_Settings.register_function()
    SEA_Operators.register_function()
    SEA_Panel.register_function()


def unregister_function():
    SEA_Panel.unregister_function()
    SEA_Operators.unregister_function()
    SEA_Settings.unregister_function()
