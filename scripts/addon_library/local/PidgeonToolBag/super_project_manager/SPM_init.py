from . import (
    SPM_Settings,
    SPM_Operators,
    SPM_Panel,
    SPM_Functions,
)
def register_function():
    SPM_Functions.setup_addons_data()
    
    SPM_Settings.register_function()
    SPM_Operators.register_function()
    SPM_Panel.register_function()

    SPM_Functions.register_properties()


def unregister_function():
    SPM_Panel.unregister_function()
    SPM_Operators.unregister_function()
    SPM_Settings.unregister_function()
