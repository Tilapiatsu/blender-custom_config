import bpy

from .WL_constants import GROUP_TYPES, ADJUSTMENT_NAME
from . import WL_functions
from . import WL_callbacks
from .WL_functions import get_wl_mod_group, get_wl_obj, get_wl_vars, get_wl_group_nodes, get_random_rgb_from_hsv


class WEIGHTLAYER_OT_layer_stack_list_actions(bpy.types.Operator):
    """Manipulate list items, either: move up, move down, add or remove"""
    bl_label = "List actions"
    bl_idname = "weight_layer.layer_stacks_actions"
    bl_description = "Manipulate list items, either: move up, move down, add or remove"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    action: bpy.props.EnumProperty(
        items=(
            ("ADD", "Add", "Add item"),
            ("REMOVE", "Remove", "Remove item"),
            ("UP", "Up", "Move item up"),
            ("DOWN", "Down", "Move item down"),
        ),
        options={"HIDDEN"},
    )

    def execute(self, context):
        wl = get_wl_obj(context).weight_layers
        g_index = wl.g_index

        if self.action == "ADD":
            wl.new_layer_stack_slot()

        elif self.action == "REMOVE":
            wl.remove_layer_stack_slot(context, g_index)

        elif self.action == "UP" or "DOWN":
            up = (self.action == "UP")
            new_index = g_index + (-1 if up else 1)
            wl.move_layer_stack_slot(context, g_index, new_index)

        return {"FINISHED"}


class WEIGHTLAYER_OT_new_layer_stack(bpy.types.Operator):
    """Add new layer stack"""
    bl_label = "New layer stack"
    bl_idname = "weight_layer.new_layer_stack"
    bl_description = "Add new layer stack"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wl = get_wl_obj(context).weight_layers
        slot = wl.layer_stacks[wl.g_index]
        slot.new_layer_stack(context)
        return {"FINISHED"}


class WEIGHTLAYER_OT_copy_layer_stack(bpy.types.Operator):
    """Copy the current layer stack"""
    bl_label = "Copy layer stack"
    bl_idname = "weight_layer.copy_layer_stack"
    bl_description = "copy the current layer stack"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    stack_index: bpy.props.IntProperty()

    def execute(self, context):
        mod_group = get_wl_mod_group(context)
        stack_node = mod_group.nodes.get(str(self.stack_index))

        def rename_group(group, orig_name):
            # do simple check to see if name ends with an int separated by one of the separators listed
            for separator in [" ", "_", "-", "."]:
                try:
                    index = int(orig_name.split(separator)[-1])
                    orig_name = orig_name[:-len(str(index))]
                    break
                except ValueError:
                    continue
            else:
                index = 0
                orig_name = orig_name + " " if not orig_name.endswith(" ") else orig_name

            # get unique name
            i = index
            while True:
                i += 1
                name = orig_name + str(i)
                try:
                    _ = bpy.data.node_groups[WL_functions.get_stack_group(name, only_name=True)]
                except KeyError:
                    break
            if group.wl.type == "STACK":
                _ = group.wl.name
                group.wl.name = name
            else:
                group.name = name

        # copy all node groups in the hierarchy
        path = [stack_node]
        done = []
        i = 0
        while path:
            if i > 1000:
                print("fuck")
                break
            i += 1

            group_node = path[-1]
            if group_node not in done:
                orig_name = group_node.node_tree.wl.name if group_node.node_tree.wl.type == "STACK"\
                    else group_node.node_tree.name
                new_group = group_node.node_tree.copy()
                group_node.node_tree = new_group
                rename_group(new_group, orig_name)

            nodes = list(group_node.node_tree.nodes)
            for node in nodes:
                if node.type == "GROUP" and node.node_tree:
                    if node not in done:
                        path.append(node)
                        break
            else:
                path.pop()

            done.append(group_node)

        _, stack, _, = get_wl_vars(context)

        # update internal references
        stack.stack_group = stack_node.node_tree
        for layer in stack.stack_group.wl.layers:
            layer.layer_group = stack.stack_group.nodes.get(str(layer.index)).node_tree
            for adj in layer.adjustments:
                adj.adjustment_group = layer.layer_group.nodes.get(str(adj.index)).node_tree

        return {"FINISHED"}


class WEIGHTLAYER_OT_bake_layer_stack(bpy.types.Operator):
    """Bake the current layer stack to a vertex group"""
    bl_label = "Bake layer stack"
    bl_idname = "weight_layer.bake_layer_stack"
    bl_description = "Bake the current layer stack to a vertex group"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    stack_index: bpy.props.IntProperty(options={"HIDDEN"},)

    def execute(self, context):
        wl, _, _ = get_wl_vars(context)
        stack = wl.layer_stacks[self.stack_index]
        if not stack.manual_refresh:
            stack.bake_layer_stack()
            stack.layer_stacks_enum = "NONE"
        else:
            stack.bake_layer_stack()

        # stack.
        return {"FINISHED"}


class WEIGHTLAYER_OT_remove_layer_stack(bpy.types.Operator):
    """Remove the current layer stack"""
    bl_label = "Remove layer stack"
    bl_idname = "weight_layer.remove_layer_stack"
    bl_description = "Remove the current layer stack"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wl = get_wl_obj(context).weight_layers
        slot = wl.layer_stacks[wl.g_index]
        slot.remove_layer_stack(context, wl.g_index)
        return {"FINISHED"}


class WEIGHTLAYER_OT_layer_add(bpy.types.Operator):
    """Add a new layer to the stack"""
    bl_label = "Add layer"
    bl_idname = "weight_layer.layer_add"
    bl_description = "Add a new layer to the stack"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(items=WL_callbacks.layer_types_items)

    def execute(self, context):
        wl = get_wl_obj(context).weight_layers
        stack = wl.layer_stacks[wl.g_index]
        stack_group = stack.stack_group
        stack_group.wl.new_layer(context, self.type)

        return {"FINISHED"}


class WEIGHTLAYER_OT_layer_actions(bpy.types.Operator):
    """move/remove this layer"""
    bl_label = "Layer actions"
    bl_idname = "weight_layer.layer_actions"
    bl_description = "move/remove this layer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    action: bpy.props.EnumProperty(
        items=(
            ("REMOVE", "Remove", "Remove"),
            ("MOVE_UP", "Move up", "Move up"),
            ("MOVE_DOWN", "Move down", "Move down"),
            ("MOVE_TO_INDEX", "Move to index", "Move to index"),
        ),
        options={"HIDDEN"},
    )

    index: bpy.props.IntProperty(options={"HIDDEN"})

    to_index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        index = self.index
        _, stack, layers = get_wl_vars(context)
        stack_group = stack.stack_group

        if self.action == "REMOVE":
            stack_group.wl.remove_layer(context, self.index)

        elif self.action in ["MOVE_UP", "MOVE_DOWN", "MOVE_TO_INDEX"]:
            up = self.action == "MOVE_UP"
            if index < 0:
                index = len(layers) + index  # convert negative indices to positive ones

            new_index = index + (-1 if up else 1) if self.action != "MOVE_TO_INDEX" else self.to_index
            layers.move(new_index, index)

            for node in stack_group.nodes:
                try:
                    replaced_index = int(node.name)
                except ValueError:
                    continue
                if replaced_index == new_index:
                    replaced_node = node
                elif replaced_index == index:
                    old_node = node

            replaced_node.name = "temp"
            old_node.name = str(new_index)
            replaced_node.name = str(index)

        stack_group.wl.relink_stack_group()
        stack_group.wl.organise_stack_group()
        return {"FINISHED"}


class WEIGHTLAYER_OT_adjustment_add_menu(bpy.types.Operator):
    """Show the adjustment add menu"""
    bl_label = "Adjustment add menu"
    bl_idname = "weight_layer.adjustment_add_menu"
    bl_description = "Show the adjustment add menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER"}

    layer_index: bpy.props.IntProperty()

    def draw_menu(self, popup, context):
        layout = popup.layout
        adjustments = WL_functions.get_layer_cache()

        for adjust_name in adjustments:
            adjust = adjustments[adjust_name]
            if adjust["type"] == ADJUSTMENT_NAME:
                op = layout.operator("weight_layer.adjustment_add", text=adjust["name"], icon=adjust["icon"])
                op.type = adjust["name"].upper()
                op.layer_index = self.layer_index

    def execute(self, context):
        context.window_manager.popup_menu(self.draw_menu, title="", icon='NONE')
        return {"FINISHED"}


class WEIGHTLAYER_OT_adjustment_add(bpy.types.Operator):
    """Add a new adjustment to the stack"""
    bl_label = "Add adjustment"
    bl_idname = "weight_layer.adjustment_add"
    bl_description = "Add a new adjustment to the stack"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    layer_index: bpy.props.IntProperty()

    type: bpy.props.EnumProperty(items=WL_callbacks.adjustment_types_items)

    def execute(self, context):
        _, _, layers = get_wl_vars(context)
        layer = layers[self.layer_index]
        layer_group = layer.layer_group
        type = self.type.capitalize()

        nodes = layer_group.nodes

        adjust_group = WL_functions.append_node_group(self.type, new_instance=True)
        adjust_group.wl.type = GROUP_TYPES["adjustment"]
        adjust_node = nodes.new("GeometryNodeGroup")
        adjust_node.node_tree = adjust_group
        adjust_node.name = str(len(layer.adjustments))
        adjust_node.use_custom_color = True
        adjust_node.color = get_random_rgb_from_hsv((0, 0.75, 0.8), h=0.01, s=0.05, v=0.2)  # strawberry

        i = 0
        while True:
            i += 1
            name = ADJUSTMENT_NAME + "_" + type + "_" + str(i)
            try:
                _ = bpy.data.node_groups[name]
            except KeyError:
                break
        adjust_group.name = name

        adjust = layer.adjustments.add()
        adjust.adjustment_group = adjust_group
        adjust.type = type
        adjust.active = True

        layer.show_adjustments = True
        layer.relink_layer_group()
        layer.organise_layer_group()
        return {"FINISHED"}


class WEIGHTLAYER_OT_adjustment_actions(bpy.types.Operator):
    """move/remove this adjustment"""
    bl_label = "adjustment actions"
    bl_idname = "weight_layer.adjustment_actions"
    bl_description = "move/remove this adjustment"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    layer_index: bpy.props.IntProperty(options={"HIDDEN"})

    action: bpy.props.EnumProperty(
        items=(
            ("REMOVE", "Remove", "Remove"),
            ("MOVE_UP", "Move up", "Move up"),
            ("MOVE_DOWN", "Move down", "Move down"),
            ("MOVE_TO_INDEX", "Move to index", "Move to index"),
        ),
        options={"HIDDEN"},
    )

    to_index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        layer_index = self.layer_index
        _, _, layers = get_wl_vars(context)
        layer = layers[layer_index]
        layer_group = layer.layer_group
        adjustments = layer.adjustments
        index = layer.a_index

        if self.action == "REMOVE":
            group = layer.adjustments[index].adjustment_group
            adjustments.remove(index)
            WL_functions.remove_node_group_references(group)

            bpy.data.node_groups.remove(group)

            # rename all nodes that came after
            adj_nodes = get_wl_group_nodes(layer_group, GROUP_TYPES["adjustment"])
            adj_nodes.sort(key=lambda node: int(node.name))

            for node in adj_nodes:
                if int(node.name) > index:
                    node.name = str(int(node.name) - 1)

            if adjustments:
                adjustments[-1].active = True
            else:
                layer.show_adjustments = False
            layer.relink_layer_group()

        elif self.action in ["MOVE_UP", "MOVE_DOWN", "MOVE_TO_INDEX"]:
            up = self.action == "MOVE_UP"
            if index < 0:
                index = len(layers) + index  # convert negative indices to positive ones

            new_index = index + (-1 if up else 1) if self.action != "MOVE_TO_INDEX" else self.to_index
            adjustments.move(new_index, index)

            for node in layer_group.nodes:
                try:
                    replaced_index = int(node.name)
                except ValueError:
                    continue
                if replaced_index == new_index:
                    replaced_node = node
                elif replaced_index == index:
                    old_node = node

            replaced_node.name = "temp"
            old_node.name = str(new_index)
            replaced_node.name = str(index)

            layer.a_index = new_index
            layer.relink_layer_group()

        layer.organise_layer_group()
        return {"FINISHED"}


class WEIGHTLAYER_OT_output_add_menu(bpy.types.Operator):
    """Show the output add menu"""
    bl_label = "Output add"
    bl_idname = "weight_layer.output_add_menu"
    bl_description = "Show the output add menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    layer_index: bpy.props.IntProperty(options={"HIDDEN"},)

    menu: bpy.props.BoolProperty(options={"HIDDEN"},)

    add_to_all: bpy.props.BoolProperty(options={"HIDDEN"},)

    enum_items = (("VERTEX_WEIGHT", "New vertex group", "Add a new vertex group"),)
    # ("VERTEX_COLOR", "New vertex color layer", "Add a new vertex color layer"),

    type: bpy.props.EnumProperty(
        items=enum_items,
        options={"HIDDEN"},
    )

    name: bpy.props.StringProperty(
        name="Name",
        default="",
        options={"HIDDEN"},
    )

    def draw(self, context):
        if not self.menu:
            self.layout.activate_init = True
            self.layout.prop(self, "name")

    def invoke(self, context, event):
        if not self.menu:
            self.name = "WL_" + self.type.lower() if not self.name else self.name
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw_menu(self, popup, context):
        layout = popup.layout
        icons = ["MOD_VERTEX_WEIGHT", "COLOR"]
        # this is necessary for the invoke method to be called for some reason
        layout.operator_context = "INVOKE_DEFAULT"

        for type, icon in zip(self.enum_items, icons):
            op = layout.operator("weight_layer.output_add_menu", text=type[1], icon=icon)
            op.menu = False
            op.layer_index = self.layer_index
            op.type = type[0]

    def execute(self, context):
        if self.menu:
            context.window_manager.popup_menu(self.draw_menu, title="", icon='NONE')
            return {"FINISHED"}

        _, layer_stack, layers = get_wl_vars(context)

        objs = []
        if self.add_to_all:
            for obj in bpy.data.objects:
                if obj.weight_layers.layer_stacks:
                    layer_stacks = obj.weight_layers.layer_stacks
                    for ls in layer_stacks:
                        if ls.stack_group == layer_stack.stack_group:
                            objs.append(obj)
                            break
        else:
            objs.append(get_wl_obj(context))

        for obj in objs:
            name = self.name if self.name else "WL_" + self.type.lower()
            if self.type == "VERTEX_WEIGHT":
                group = obj.vertex_groups.new(name=name)
            elif self.type == "VERTEX_COLOR":
                group = obj.data.vertex_colors.new(name=name)

        layers[self.layer_index].layer_settings.vgroup_enum = group.name
        obj.update_tag()

        return {"FINISHED"}


class WEIGHTLAYER_OT_output_rename(bpy.types.Operator):
    """Rename this attribute"""
    bl_label = "Rename"
    bl_idname = "weight_layer.output_rename"
    bl_description = "Rename this attribute"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    orig_name: bpy.props.StringProperty(options={"HIDDEN"},)

    new_name: bpy.props.StringProperty(name="New name",)

    def draw(self, context):
        layout = self.layout
        layout.activate_init = True
        layout.prop(
            self,
            "new_name",
        )

    def invoke(self, context, event):
        self.new_name = self.orig_name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for ng in bpy.data.node_groups:
            for node in ng.nodes:
                for socket in node.inputs:
                    if hasattr(socket, "default_value") and socket.default_value == self.orig_name:
                        socket.default_value = self.new_name

        for obj in bpy.data.objects:
            for vg in obj.vertex_groups:
                if vg.name == self.orig_name:
                    vg.name = self.new_name

        for mesh in bpy.data.meshes:
            for vc in mesh.vertex_colors:
                if vc.name == self.orig_name:
                    vc.name = self.new_name
        return {"FINISHED"}


classes = [
    WEIGHTLAYER_OT_layer_stack_list_actions,
    WEIGHTLAYER_OT_new_layer_stack,
    WEIGHTLAYER_OT_copy_layer_stack,
    WEIGHTLAYER_OT_bake_layer_stack,
    WEIGHTLAYER_OT_remove_layer_stack,
    WEIGHTLAYER_OT_layer_add,
    WEIGHTLAYER_OT_layer_actions,
    WEIGHTLAYER_OT_adjustment_add,
    WEIGHTLAYER_OT_adjustment_add_menu,
    WEIGHTLAYER_OT_adjustment_actions,
    WEIGHTLAYER_OT_output_add_menu,
    WEIGHTLAYER_OT_output_rename,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
