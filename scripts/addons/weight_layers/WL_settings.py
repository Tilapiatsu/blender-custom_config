import bpy
import importlib
import inspect
from .WL_callbacks import *
from .layer_scripts import WL_layer_functions  # this needs to be imported explicitly for some reason
# rather than importing individual classes, which don't register properly -_-
from . import WL_functions
from .extra_props import NonIDProperty, GetSetProperty
from pathlib import Path

from bpy.props import BoolProperty, FloatVectorProperty, IntProperty, StringProperty, EnumProperty, CollectionProperty,\
    PointerProperty


class WLSceneSettings(bpy.types.PropertyGroup):

    use_pinned_obj: BoolProperty(
        name="Pin object",
        description="Use the pinned object instead of the active object.\n\
            This means that the panel wont change when selecting another object",
        default=False,
        update=use_pinned_obj_update,
    )

    pinned_obj: PointerProperty(
        type=bpy.types.Object,
        name="Pinned object",
        description="The object to display if use_pinned_obj is True",
    )


class WLObjectSettings(bpy.types.PropertyGroup):

    g_index: IntProperty()

    new_layer_stack_slot = new_layer_stack_slot

    remove_layer_stack_slot = remove_layer_stack_slot

    def organise_stack_list(self):
        """Sets position and size of all layer stack nodes in the chain"""
        group = WL_functions.get_wl_mod_group(bpy.context, obj=self.id_data)
        organise_stack_list(group)

    def relink_stack_group(self):
        """Recalculates the links between all layer stack nodes in the chain"""
        group = WL_functions.get_wl_mod_group(bpy.context, obj=self.id_data)
        relink_stack_list_group(group, self.layer_stacks)


class WLStackListItem(bpy.types.PropertyGroup):

    stack_group: PointerProperty(
        type=bpy.types.GeometryNodeTree,
        name="Layer stack",
        description="The backend reference to the layer stack node group",
        update=stack_group_update,
    )

    layer_stacks_enum: EnumProperty(
        items=layer_stacks_enum_items,
        name="layer stack",
        description="The layer stack to use for this slot",
        update=layer_stacks_enum_update,
    )

    index: IntProperty(
        name="Index",
        description="The index of this stack in the list",
        get=stack_index_get,
    )

    manual_refresh: BoolProperty(
        name="Use manual refresh",
        description="""When true, the stack needs to be refreshed manually, which is useful for heavy objects,
        especially where the geometry nodes or the object are edited often""",
        default=False,
        update=manual_refresh_update)

    new_layer_stack = new_layer_stack

    remove_layer_stack = remove_layer_stack

    def bake_layer_stack(self):
        bake_layer_stack(bpy.context, self)


class WLNodeGroupsSettings(bpy.types.PropertyGroup):

    type: EnumProperty(items=node_group_type_items())

    full_type: StringProperty()

    name: StringProperty(
        name="Name",
        description="the name of this layer stack",
        default="Layer Stack ",
        get=stack_name_get,
        set=stack_name_set,
    )

    color: FloatVectorProperty(
        name="Color",
        description="The color of this node group",
    )

    # Alpha Trees props
    # used to track if this item was made by alpha trees, and what vgroup it is used for
    vgroup = NonIDProperty(
        name="vgroup",
        subtype="vertex_groups",
        name_update=vgroup_name_update,
    )

    # Functions

    new_layer = new_layer

    remove_layer = remove_layer

    def organise_stack_group(self):
        """Sets position and size of all layer nodes in the chain"""
        group = self.id_data
        organise_layer_list(group)

    def relink_stack_group(self):
        """Recalculates the links between all nodes in the chain. Takes the node group to relink,
        and the list (CollectionProperty) to take the length of."""
        group = self.id_data
        relink_layer_list_group(group, self.layers)


class WLCustomLayerSettings(bpy.types.PropertyGroup):
    """This gets populated with all of the custom layer drawing and settings property groups,
    as defined in /layer_scripts"""

    default_settings: PointerProperty(type=WL_layer_functions.CustomLayerSettings)

    pass


class WLLayer(bpy.types.PropertyGroup):

    # PropertyGroup containing all of the custom layer settings defined in /layer_scripts
    all_settings: PointerProperty(type=WLCustomLayerSettings)

    # acts as a shortcut to the custom layer settings/functions that are defined in /layer_script
    layer_settings = GetSetProperty(get=get_layer_adjustment_settings)

    index: IntProperty(
        name="Index",
        description="The index of this layer in the list",
        get=layer_index_get,
    )

    show_ui: BoolProperty(
        name="Show layer settings",
        description="Show the settings of this layer in the UI",
        default=True,
    )

    show_adjustments: BoolProperty(
        name="Show adjustments",
        description="Show the adjustments of this layer in the UI",
        default=False,
    )

    name: StringProperty(name="Name", description="The name of this layer", default="Layer")

    type: StringProperty(name="Type", description="The type of this layer")

    layer_group: PointerProperty(
        type=bpy.types.GeometryNodeTree,
        name="Layer group",
        description="The backend reference to the layer node group",
    )

    a_index: IntProperty()

    def relink_layer_group(self):
        """Recalculates the links between all nodes in the chain. Takes the node group to relink,
        and the list (CollectionProperty) to take the length of."""
        relink_layer_group(self.layer_group, self.adjustments)

    def organise_layer_group(self):
        """Sets position and size of all adjustment nodes in the chain"""
        organise_layer_group(self.layer_group)


class WLCustomAdjustmentSettings(bpy.types.PropertyGroup):
    """This gets populated with all of the custom adjustment drawing and settings property groups,
    as defined in /layer_scripts"""

    default_settings: PointerProperty(type=WL_layer_functions.CustomAdjustmentSettings)

    pass


class WLAdjustment(bpy.types.PropertyGroup):

    # PropertyGroup containing all of the custom layer settings defined in /layer_scripts
    all_settings: PointerProperty(type=WLCustomAdjustmentSettings)

    # acts as a shortcut to the custom layer settings/functions that are defined in /layer_script
    adjustment_settings = GetSetProperty(get=get_layer_adjustment_settings)

    active: BoolProperty(
        name="Set active",
        description="If True, this adjustment layer is the active one",
        default=False,
        update=active_adjustment_update,
    )

    type: StringProperty(
        name="Type",
        description="The type of this layer",
    )

    layer_index: IntProperty(
        name="Layer index",
        description="The index of the layer that this adjustment is clipped to",
        get=adjustment_layer_index_get,
    )

    index: IntProperty(
        name="Index",
        description="The index of this adjustment in the list",
        get=adjustment_index_get,
    )

    adjustment_group: PointerProperty(
        type=bpy.types.GeometryNodeTree,
        name="Adjustment group",
        description="The backend reference to the adjustment node group",
    )


classes = [
    WL_layer_functions.CustomLayerSettings,
    WL_layer_functions.CustomAdjustmentSettings,
    WLSceneSettings,
    WLObjectSettings,
    WLStackListItem,
    WLNodeGroupsSettings,
    WLCustomLayerSettings,
    WLLayer,
    WLCustomAdjustmentSettings,
    WLAdjustment,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.weight_layers = PointerProperty(type=WLSceneSettings)
    bpy.types.Object.weight_layers = PointerProperty(type=WLObjectSettings)
    WLObjectSettings.layer_stacks = CollectionProperty(type=WLStackListItem)
    bpy.types.GeometryNodeTree.wl = PointerProperty(type=WLNodeGroupsSettings)
    WLNodeGroupsSettings.layers = CollectionProperty(type=WLLayer)
    WLLayer.adjustments = CollectionProperty(type=WLAdjustment)

    # register the custom layer settings defined in /layer_scripts
    nodes_dir = Path(__file__).parent / "layer_scripts"
    files = [f for f in nodes_dir.glob("*") if "WLAYER_" in f.name or "WLADJUST_" in f.name]
    for file in files:
        mod = importlib.import_module(".layer_scripts." + file.name.replace(".py", ""), __package__)
        settings_class = None
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, WL_layer_functions.CustomSettingsBase) and cls not in [
                    WL_layer_functions.CustomLayerSettingsBase, WL_layer_functions.CustomAdjustmentSettingsBase
            ]:
                settings_class = cls
                break
        if settings_class:
            try:
                bpy.utils.register_class(settings_class)
            except ValueError as e:
                # print(e)
                pass
            name = file.name.replace("WLAYER_", "").replace("WLADJUST_", "")[:-3]
            settings_group = WLCustomLayerSettings
            setattr(settings_group, name, PointerProperty(type=settings_class))
            if "WLADJUST_" in file.name:
                setattr(WLCustomAdjustmentSettings, name, PointerProperty(type=settings_class))

        else:
            print(f"Custom layer script '{mod.__name__.split('.')[-1]}' must have PropertyGroup inheriting from\
    'CustomSettingsBase' containing all custom properties/functions")


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.weight_layers
    del bpy.types.Object.weight_layers
    del bpy.types.GeometryNodeTree.wl
