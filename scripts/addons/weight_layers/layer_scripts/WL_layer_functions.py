"""This is a collection of functions that are intended
to be used by custom drawing scripts for nodes.

The system is designed to allow each node to have a script that can draw anything to the panel,
which is useful for nodes that use color ramps or rgb curves for example.

However, the system doesn't do any checks on the code, so if you got it from a third party (not the developer)
make sure that you trust them before using the custom nodes."""

from ..WL_functions import get_wl_node, get_wl_obj, get_wl_mod_group, get_wl_socket, get_layer_info, get_wl_prefs
from ..WL_constants import SOCKETS, GROUP_TYPES, TEMP_NAME
from ..extra_props import GetSetProperty
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty, IntProperty
import bpy


class CustomSettingsBase(PropertyGroup):
    "Contains methods that are used by both layers and adjustments"

    # Drawing
    def draw_mix_settings(self, layout):
        """Draw the blend type and factor for this layer"""
        mix_node = get_wl_node(self.node.node_tree, "mix")
        if mix_node:
            row = layout.row(align=True)
            row.prop(mix_node, "blend_type", text="")
            row.prop(mix_node.inputs[0], "default_value", text="fac")
            return row
        else:
            return None

    def draw_node_inputs(self, context, layout, node=None):
        """Draw the node inputs for this layer"""
        node = node if node else self.node
        for socket in node.inputs:
            if all([
                    not socket.links, socket.enabled, not socket.hide_value,
                    hasattr(socket, 'draw'), socket.name != SOCKETS["input"]
            ]):
                if socket.type == "BOOLEAN":
                    self.draw_aligned_boolean(layout, socket)
                    continue
                socket.draw(context, layout, node, socket.name)
        return layout

    def draw_color_ramp(self, layout, node):
        layout.template_color_ramp(
            node,
            "color_ramp",
            expand=True,
        )

    def draw_math_node_operation(self, layout, node):
        layout.prop(node, "operation", text="")

    def draw_texture(self, layout):
        layout.template_ID(
            self.node,
            "texture",
            new="texture.new",
        )

    def draw_aligned_boolean(self, layout, socket):
        row = layout.row()
        add = "" if socket.name.endswith(":") else ":"
        row.label(text=socket.name + add)
        row.prop(socket, "default_value", text="")


def _get_layer(self):
    layers = self.id_data.wl.layers
    for layer in layers:
        if layer.layer_settings == self:
            return layer


def _get_layer_node(self):
    layer = _get_layer(self)
    stack_group = self.id_data
    for node in stack_group.nodes:
        if node.type == "GROUP" and node.node_tree == layer.layer_group:
            return node


def _get_layer_stack(self):
    obj = get_wl_obj(bpy.context)
    for stack in obj.weight_layers.layer_stacks:
        group = stack.stack_group
        for layer in group.wl.layers:
            if layer == self.layer:
                return stack


class CustomLayerSettingsBase(CustomSettingsBase):
    """Class that contains methods to be used by layers"""

    layer_stack = GetSetProperty(get=_get_layer_stack)

    layer = GetSetProperty(get=_get_layer)
    
    node = GetSetProperty(get=_get_layer_node)

    def on_creation(self, context):
        """Called after a layer of this type has been created"""
        pass

    def on_removal(self, context):
        """Called before this layer is removed"""
        pass

    def on_new_stack_instance(self, context):
        """Called when the stack group that this layer is in is selected from a new layer stack slot"""
        pass

    def on_remove_stack_instance(self, context):
        """Called when the stack group that this layer is in is removed from a layer stack slot"""
        pass

    def draw_layer(self, context, layout):
        """This is the basic function that is called when there is no custom drawing script detected"""
        self.draw_mix_settings(layout)
        self.draw_node_inputs(context, layout)
        self.draw_adjustments_stack(context, layout)

    def draw_adjustments_header(self, layout):
        layout.separator(factor=0.6)
        layer_group = self.node.node_tree
        layer_info = get_layer_info(layer_group)
        adjustments = self.layer.adjustments

        if layer_info["dont_use_mix"]:
            # cannot use adjustment layers
            return

        row = layout.row(align=True)
        row.prop(
            self.layer,
            "show_adjustments",
            text="",
            emboss=False,
            icon="DISCLOSURE_TRI_DOWN" if self.layer.show_adjustments else "DISCLOSURE_TRI_RIGHT",
        )
        row.label(text="Adjustments")
        row.emboss = "NONE"
        row.operator("weight_layer.adjustment_add_menu", text="", icon="ADD").layer_index = self.layer.index
        row = row.row(align=True)
        row.scale_x = 0.9

        if self.layer.a_index != 0:
            op = row.operator("weight_layer.adjustment_actions", text="", icon="TRIA_UP", emboss=False)
            op.action = "MOVE_UP"
            op.layer_index = self.layer.index

        if self.layer.a_index != len(adjustments) - 1 and adjustments:
            op = row.operator("weight_layer.adjustment_actions", text="", icon="TRIA_DOWN", emboss=False)
            op.action = "MOVE_DOWN"
            op.layer_index = self.layer.index

        if adjustments:
            op = row.operator("weight_layer.adjustment_actions", text="", icon="REMOVE", emboss=False)
            op.action = "REMOVE"
            op.layer_index = self.layer.index

    def draw_adjustments_stack(self, context, layout):
        adjustments = self.layer.adjustments

        self.draw_adjustments_header(layout)

        if not self.layer.show_adjustments:
            return

        adj_col = layout.column(align=True)
        for adj in adjustments:
            box = adj_col.box()
            col = box.column()
            col.scale_y = 0.9
            row = col.row(align=True)
            row.prop(adj,
                     "active",
                     text="",
                     icon="RESTRICT_SELECT_OFF" if adj.active else "RESTRICT_SELECT_ON",
                     emboss=False)
            col = row.column()
            col = col.column(align=True)

            adj.adjustment_settings.draw_adjustment(context, col)


class CustomLayerSettings(CustomLayerSettingsBase):
    pass


def _get_adjustment_layer(self):
    layers = self.id_data.wl.layers
    if self.is_layer:
        return _get_layer(self)
    for layer in layers:
        for adj in layer.adjustments:
            if adj.adjustment_settings == self:
                return layer


def _get_adjustment(self):
    for adj in self.layer.adjustments:
        if adj.adjustment_settings == self:
            return adj


def _get_adjustment_node(self):
    if self.is_layer:
        return _get_layer_node(self)
    for node in self.layer.layer_group.nodes:
        if node.type == "GROUP" and node.node_tree == self.adjustment.adjustment_group:
            return node


class CustomAdjustmentSettingsBase(CustomLayerSettingsBase):
    """Class that contains methods to be used by layers"""

    is_layer = GetSetProperty(get=lambda self: self in [l.layer_settings for l in self.id_data.wl.layers])

    layer = GetSetProperty(get=_get_adjustment_layer)

    adjustment = GetSetProperty(get=_get_adjustment)

    node = GetSetProperty(get=_get_adjustment_node)

    def draw_adjustment(self, context, layout, node=None):
        node = node if node else self.node
        self.draw_node_inputs(context, layout, node)


class CustomAdjustmentSettings(CustomAdjustmentSettingsBase):
    pass


class InputOutputParent(CustomLayerSettingsBase):
    """Used to store shared methods and properties for the input and output nodes"""

    is_output = True

    def vgroup_enum_items(self, context):
        items = [("NONE", "None", "None")]
        for vg in get_wl_obj(context).vertex_groups:
            items.append((vg.name, vg.name, vg.name))

        for i in range(max(20 - len(items), 0)):
            items.append(("FILLER_" + str(i), "", "filler"))
        return items

    update_name: bpy.props.BoolProperty(
        default=True,
        description="Used to know whether name is updated by enum or user",
    )

    def vgroup_enum_set(self, value):
        vgroup_name = self.vgroup_enum_items(bpy.context)[value][0]
        if vgroup_name.startswith("FILLER_"):
            return
        self.update_name = False
        self.vgroup_name = vgroup_name
        self["_vgroup_enum"] = value

    def vgroup_name_set(self, value):
        orig_name = self.vgroup_name
        value = "" if value == "NONE" else value
        for obj in bpy.data.objects:
            if value and self.update_name:
                for vg in obj.vertex_groups:
                    if vg.name == orig_name:
                        vg.name = value

            for modifier in obj.modifiers:
                if modifier.type == "NODES":
                    if not len(modifier.keys()):
                        continue
                    mod_group_sockets = [
                        k for k in modifier.keys() if self.s_name.capitalize()[:-1] in k and "attribute_name" in k
                    ]
                    idx = self.get_mod_socket_index(get_wl_mod_group(bpy.context, get_modifier=True))
                    prop_name = mod_group_sockets[idx]
                    stack_slot = [s for s in obj.weight_layers.layer_stacks if s.stack_group == self.layer_stack.stack_group]
                    suffix = TEMP_NAME if stack_slot[0].manual_refresh and self.is_output else ""
                    modifier[prop_name] = value + suffix
                    if not self.is_output:
                        modifier[prop_name.replace("attribute_name", "use_attribute")] = True

        if value and self.update_name:
            for mesh in bpy.data.meshes:
                for vc in mesh.vertex_colors:
                    if vc.name == orig_name:
                        vc.name = value
        self.update_name = True
        self["_vgroup_name"] = value
        pass

    vgroup_enum: EnumProperty(
        items=vgroup_enum_items,
        name="Vertex Group",
        description="The vertex group to output to",
        get=lambda self: self.get("_vgroup_enum", 0),
        set=vgroup_enum_set,
    )

    vgroup_name: StringProperty(
        name="Vertex group name",
        description="The name of the selected vertex groups.\
        When updated it will update all objects that have this vertex group",
        get=lambda self: self.get("_vgroup_name", ""),
        set=vgroup_name_set,
    )

    def get_socket_index(self):
        sockets = getattr(self.node, self.s_name)
        node_socket = sockets[SOCKETS[f"ext_{self.s_name[:-1]}"]]
        in_out_socket = getattr(node_socket.links[0], f"{'to' if self.is_output else 'from'}_socket")
        in_out_node = self.id_data.nodes.get(f"Group {'Output' if self.is_output else 'Input'}")
        return list(getattr(in_out_node, self.s_name_inv)).index(in_out_socket)

    socket_index: IntProperty(description="Internal property that stores the index of this output in the node modifier",
                              get=get_socket_index)

    # sockets name
    s_name = property(lambda self: "outputs" if self.is_output else "inputs")
    s_name_inv = property(fget=lambda self: "inputs" if self.is_output else "outputs")

    def get_mod_socket_index(self, modifier):
        mod_group = modifier.node_group
        for node in mod_group.nodes:
            if node.type == "GROUP" and node.node_tree == self.id_data:
                mod_socket = getattr(node, self.s_name)[self.socket_index].links[0].to_socket
                mod_socket = getattr(mod_socket.links[0], f"{'to' if self.is_output else 'from'}_socket")
                in_out_node = mod_group.nodes.get(f"Group {'Output' if self.is_output else 'Input'}")
                idx = list(getattr(in_out_node, self.s_name_inv)).index(mod_socket) - 1
                return idx

    def add_modifier_sockets(self):
        stack_group = self.layer.id_data
        name = self.s_name
        name_inv = self.s_name_inv
        name_cap = name.capitalize()
        for ng in bpy.data.node_groups:
            if ng.type == "GEOMETRY" and ng.wl.type == GROUP_TYPES["stack_list"]:
                for node in ng.nodes:
                    if node.type == "GROUP" and node.node_tree == stack_group:
                        for socket in getattr(node, name)[1:]:
                            if not socket.links:
                                ng_sockets = getattr(ng, name)
                                ng_sockets.new(socket.bl_idname, socket.name)
                                in_out_node = ng.nodes.get(f"Group {name_cap[:-1]}")
                                ng_socket = getattr(in_out_node, name_inv)[-2]
                                ng.links.new(socket, ng_socket)

    def on_creation(self, context):
        """Adds new attribute input/output to the stack group and modifier group"""
        stack_group = self.layer.id_data
        layer_node = self.node
        name = self.s_name
        name_cap = name.capitalize()
        name_inv = self.s_name_inv
        sockets = getattr(stack_group, name)
        sockets.new("NodeSocketFloat", f"_{self.s_name[:-1]}_{layer_node.name}")
        output_node = stack_group.nodes.get(f"Group {name_cap[:-1]}")
        stack_group.links.new(get_wl_socket(getattr(layer_node, name), "ext_" + name[:-1]),
                              getattr(output_node, name_inv)[-2])
        self.add_modifier_sockets()

    def remove_modifier_sockets(self):
        stack_group = self.layer.id_data

        for ng in bpy.data.node_groups:
            if ng.type == "GEOMETRY" and ng.wl.type == GROUP_TYPES["stack_list"]:
                for node in ng.nodes:
                    if node.type == "GROUP" and node.node_tree == stack_group:
                        node_in_out = getattr(node, self.s_name)[self.socket_index].links[0]
                        ng_in_out = getattr(node_in_out, f"{'to' if self.is_output else 'from'}_socket")
                        out_node = ng.nodes.get(f"Group {self.s_name.capitalize()[:-1]}")
                        idx = list(getattr(out_node, self.s_name_inv)).index(ng_in_out)
                        sockets = getattr(ng, self.s_name)
                        sockets.remove(sockets[idx])

    def on_removal(self, context):
        """Removes this nodes attribute input/output from the stack group and modifier group"""
        self.remove_modifier_sockets()
        stack_group = self.layer.id_data
        sockets = getattr(stack_group, self.s_name)
        sockets.remove(sockets[self.socket_index])

    def on_new_stack_instance(self, context):
        self.add_modifier_sockets()
        self.vgroup_name = self.vgroup_name  # update modifiers

    def on_remove_stack_instance(self, context):
        self.remove_modifier_sockets()

    def draw_layer(self, context, layout):
        self.draw_mix_settings(layout)
        obj = get_wl_obj(context)
        try:
            _ = obj.vertex_groups[self.vgroup_name]
            vgroup_exists = True
        except KeyError:
            vgroup_exists = False
        row = layout.row(align=True)
        row.prop(self, "vgroup_enum", text="", icon="MESH_DATA", icon_only=True)
        if self.vgroup_enum != "NONE":
            row.prop(self, "vgroup_name", text="")

        op = row.operator(
            "weight_layer.output_add_menu",
            text="" if self.vgroup_enum != "NONE" else "Add vertex group",
            icon="ADD",
        )
        op.layer_index = self.layer.index
        op.menu = False
        op.add_to_all = True

        if self.vgroup_enum != "NONE":
            row.prop(self.node.inputs["Invert"], "default_value", text="", icon="ARROW_LEFTRIGHT")

        if self.vgroup_name and not vgroup_exists:
            row = layout.row(align=True)
            row.label(text="No vgroup with that name on this object. Do you want to add one?")
            row.operator_context = "EXEC_DEFAULT"  # so that the dialogue doesn't appear
            op = row.operator(
                "weight_layer.output_add_menu",
                text="" if self.vgroup_enum != "NONE" else "Add vertex group",
                icon="ADD",
            )
            op.name = self.vgroup_name
            op.layer_index = self.layer.index
            op.menu = False

        self.draw_adjustments_header(layout)
