from .WL_layer_functions import InputOutputParent


class CustomLayerSettings(InputOutputParent):
    """Note that this is a special node that inherits from a custom class,
    so probably isn't the best to use as a reference for learning"""

    is_output = True
