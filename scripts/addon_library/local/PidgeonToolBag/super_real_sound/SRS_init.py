from . import (
    SRS_Operators,
    SRS_Settings,
    SRS_Panel,
)
def register_function():
    SRS_Settings.register_function()
    SRS_Operators.register_function()
    SRS_Panel.register_function()


def unregister_function():
    SRS_Panel.unregister_function()
    SRS_Operators.unregister_function()
    SRS_Settings.unregister_function()
