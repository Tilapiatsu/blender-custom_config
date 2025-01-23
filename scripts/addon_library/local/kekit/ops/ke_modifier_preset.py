import json
import os
import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator, Panel
from mathutils import Vector

from .._ui import pcoll
from .._utils import get_prefs, refresh_ui


class UIOMPModule(Panel):
    bl_idname = "UI_PT_M_OMP"
    bl_label = "Modifier Presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_BOOKMARKS"
    bl_options = {'DEFAULT_CLOSED'}

    info_omp = ("Store/Restore all the active object's modifiers as a preset\n"
                "Note: Entries are automatically sorted alphabetically\n"
                "See Wiki for full documentation")

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_omp

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        k = get_prefs()
        entries = sorted([i for i in k.omp_presets.split("\x1f") if i], key=str.casefold)

        row = col.row(align=True)
        row.prop(context.scene.kekit_temp, "omp_name")
        new = row.operator('view3d.ke_modifier_preset', text="", icon="ADD")
        new.op = "SAVE"
        new.preset_id = ""

        row = col.row(align=True)
        row.prop(k, "modp_add")
        col.separator(factor=0.25)

        if entries:
            for i, name in enumerate(entries, 1):
                row = col.row(align=True)

                fname = "\u001f" + name
                if "\x1e" in name:
                    icon = 161  # "CURVE_DATA"
                else:
                    icon_idx = str(i)[-1]
                    icon = pcoll['kekit']['ke_mod' + icon_idx].icon_id

                loading = row.operator('view3d.ke_modifier_preset', text=name, icon_value=icon)
                loading.op = "LOAD"
                loading.preset_id = fname
                row.separator()

                saving = row.operator('view3d.ke_modifier_preset', text="", icon="IMPORT")
                saving.op = "SAVE"
                saving.preset_id = fname
                row.separator()

                removing = row.operator('view3d.ke_modifier_preset', text="", icon="X")
                removing.op = "DELETE"
                removing.preset_id = fname


def json_serializable(attr):
    if isinstance(attr, Vector):
        attr = attr[:]
    # elif isinstance(attr, bpy.types.object):  # nah...
    #     attr = attr.name
    try:
        json.dumps(attr)
        return attr
    except (TypeError, OverflowError, RuntimeError):
        print("Attr. failed JSON converison: ", type(attr), attr)
        return None


class KeOMP(Operator):
    bl_idname = "view3d.ke_modifier_preset"
    bl_label = "Modifier Preset"
    bl_description = "LOAD / SAVE / DELETE the Active Object's modifiers as a preset"
    bl_options = {'REGISTER', 'UNDO'}

    op: EnumProperty(
        items=[("SAVE", "", ""), ("LOAD", "", ""), ("DELETE", "", "")],
        default="LOAD", options={"HIDDEN"})

    preset_id : StringProperty(name="Preset", default="", options={"HIDDEN"})
    path = ""

    @classmethod
    def description(cls, context, properties):
        if properties.op == "LOAD":
            return "LOAD stored modifier preset for the Active Object"
        elif properties.op == "SAVE":
            return "SAVE the Active Object's modifiers as a preset"
        else:
            return "DELETE the modifier preset"

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == "OBJECT"

    def update_json(self, preset):
        try:
            jsondata = json.dumps(preset, indent=1, ensure_ascii=True)
        except Exception as e:
            print(f"JSON dumps fail: ", e)
            self.report({"ERROR"}, "Failed to convert to JSON")
            return {"CANCELLED"}
        with open(self.path, "w") as text_file:
            text_file.write(jsondata)
        text_file.close()

    def read_json(self):
        try:
            with open(self.path, "r") as jf:
                extant = json.load(jf)
                jf.close()
                return extant
        except (OSError, IOError):
            print("No previous JSON file found")
            return {}

    def execute(self, context):
        self.path = os.path.join(bpy.utils.user_resource('CONFIG'), "ke_modifier_presets.json")
        preset = self.read_json()
        kt = context.scene.kekit_temp
        kprop = get_prefs()

        if not self.preset_id:
            # New w/o name string:
            nr = str(len(preset) + 1).zfill(2)
            self.preset_id = "\u001fMod Preset " + nr if not kt.omp_name else "\x1f" + kt.omp_name

        preset_names = kprop.omp_presets
        # Note: ASCII Control Character \x1f (\u001f) ('Unit Separator') used for string separation:
        pref_names = [i for i in preset_names.split("\x1f") if i]
        preset_id = self.preset_id.split("\x1f")[-1]
        add_mode = bool(kprop.modp_add)
        sel_obj = context.selected_objects[:]

        curve_props = [
            'bevel_depth', 'bevel_factor_end', 'bevel_factor_mapping_end', 'bevel_factor_mapping_start',
            'bevel_factor_start', 'bevel_mode', 'bevel_resolution', 'extrude', 'fill_mode', 'offset',
            'path_duration', 'name', 'render_resolution_u', 'render_resolution_v', 'resolution_u', 'resolution_v',
            'taper_radius_mode', 'twist_mode', 'twist_smooth', 'use_auto_texspace', 'use_deform_bounds',
            'use_fill_caps', 'use_map_taper', 'use_path', 'use_path_clamp', 'use_path_follow', 'use_radius',
            'use_stretch']  # skipping 'bevel_profile' etc.

        #
        # Storing preset
        #
        if self.op == "SAVE":
            # clear old:
            if self.preset_id in preset:
                preset.pop(self.preset_id)

            ignored_props = [
                "bl_rna", "rna_type", "is_active", "is_override_data", "execution_time", "type", "persistent_uid",
                "panels", "open_bake_data_blocks_panel", "open_bake_panel", "open_manage_panel",
                "open_named_attributes_panel", "open_output_attributes_panel", "custom_profile"
            ]

            physics_mods = [
                "COLLISION", "CLOTH", "DYNAMIC_PAINT", "FLUID", "SOFT_BODY", "PARTICLE_SYSTEM", "PARTICLE_INSTANCE",
                "EXPLODE", "OCEAN",
            ]  # TBD: maybe separately...

            panel_props = [
                "show_expanded", "show_in_editmode", "show_on_cage", "show_render", "show_viewport", "use_pin_to_last"
            ]

            ao = context.active_object
            obj = ao if ao in sel_obj else sel_obj[0]

            mods = {}

            if obj.type == "CURVE":
                entry = {"type": "CURVE"}
                for prop in curve_props:
                    attr = json_serializable(getattr(obj.data, prop))
                    entry[prop] = attr
                mods["curve_data"] = entry
                # Note: ASCII Control Character \x1e (\u001e) ('Record Separator') used as 'curve tag' in str:
                if "\x1e" not in self.preset_id:
                    self.preset_id += "\x1e"
                # entry["bevel_profile_preset"] = ""  # TBD
                # if obj.data.bevel_mode == "PROFILE":
                #     entry["bevel_profile_preset"] = obj.data.bevel_profile.preset

            for i, m in enumerate(obj.modifiers):
                if m.type in physics_mods:
                    continue

                entry = {"type": m.type}

                if m.type == "NODES":
                    # node specific props
                    name = m.name
                    if "Auto Smooth" in name:
                        print("Deprecated 'Auto Smooth' GN stored as 'Smooth by Angle")
                        name = "Smooth by Angle"

                    entry["name"] = name
                    entry["node_group"] = m.node_group.name

                    for k in m.keys():
                        attr = json_serializable(m[k])
                        if attr:
                            entry[k] = attr

                    attr = json_serializable(getattr(m, "show_group_selector"))
                    if attr is not None:
                        entry["show_group_selector"] = attr
                else:
                    for k in dir(m):
                        if "__" not in k and k not in ignored_props:
                            attr = json_serializable(getattr(m, k))
                            if attr:
                                entry[k] = attr
                            # custom profile special case - only storing preset (name)
                            if k == "profile_type" and attr == "CUSTOM":
                                cpf = getattr(m, "custom_profile")
                                entry["custom_profile_preset"] = cpf.preset

                # + panel props
                for k in panel_props:
                    attr = json_serializable(getattr(m, k))
                    if attr is not None:
                        entry[k] = attr

                mods[i] = entry

            # Write preset(s)
            preset[self.preset_id] = mods
            self.update_json(preset)

            # Update name string listing for add-on prefs & panel UI:
            if preset_id not in pref_names:
                preset_names = preset_names + self.preset_id

            kprop.omp_presets = preset_names

            bpy.ops.wm.save_userpref()
            refresh_ui()
            print(f"Stored Preset {self.preset_id}:", [mods[i]["name"] for i in mods])

            return {"FINISHED"}

        elif self.op == "DELETE":
            preset.pop(self.preset_id)
            self.update_json(preset)
            new_prefs_names = "".join(["\x1f" + i for i in pref_names if i != preset_id])
            kprop.omp_presets = new_prefs_names
            bpy.ops.wm.save_userpref()
            refresh_ui()
            return {"FINISHED"}

        #
        # Checking preset
        #
        stored_presets = self.read_json()
        try:
            preset = stored_presets[self.preset_id]
        except KeyError:
            self.report({"INFO"}, f"Modifier Preset not found/stored > nr: {self.preset_id}")
            return {"CANCELLED"}

        #
        # Loading/restoring preset
        #
        if not add_mode:
            for obj in sel_obj:
                for m in obj.modifiers:
                    obj.modifiers.remove(m)

        mods = [idx for idx in preset]
        if not mods:
            if not add_mode:
                print("Clean: No modifiers stored - removing all modifiers on active object!")
            print("No modifiers stored in preset?")
            return {"FINISHED"}

        if add_mode:
            # no pin-2-last if just adding
            for mod in preset.keys():
                if preset[mod].get("use_pin_to_last", None) is not None:
                    preset[mod].pop("use_pin_to_last", None)

        # node_assets = ["smooth_by_angle.blend", "procedural_hair_node_assets.blend"]  # that's all for now I guess?
        # --> automatic listing for future additions:  e.g: /usr/share/blender/4.2/datafiles/assets/geometry_nodes/
        blend_dir = os.path.split(bpy.utils.script_paths(use_user=False)[0])[0]
        gn_essentials_path = os.path.abspath(os.path.join(blend_dir, "datafiles/assets/geometry_nodes/"))
        node_assets = os.listdir(gn_essentials_path)
        gn_custom_paths = context.preferences.filepaths.asset_libraries

        custom_node_assets = {}
        for lib in gn_custom_paths:
            libpath = os.path.abspath(lib.path)
            if os.path.isdir(libpath):
                custom_node_assets[lib.name] = [file for file in os.listdir(libpath) if file[-6:] == ".blend"]
        for obj in sel_obj:
            obj.select_set(False)

        for obj in sel_obj:
            obj.select_set(True)
            context.view_layer.objects.active = obj

            for mod_idx in preset:
                found = False
                mod = preset[mod_idx]
                modname = mod["name"]

                if mod["type"] == "CURVE":
                    if obj.type == "CURVE":
                        for prop in curve_props:
                            if prop not in ["name", "type"]:
                                try:
                                    setattr(obj.data, prop, mod[prop])
                                except Exception as e:
                                    print(f"Setting {obj.name} {prop} failed:", e)
                            # if prop == "bevel_profile_preset" and mod[prop]:  # does not work
                            #     obj.data["bevel_profile"].preset = mod[prop]

                elif mod["type"] == "NODES":
                    new_mod = None
                    node_group = mod["node_group"]
                    # check if exists 1st to re-use
                    has_ng = bpy.data.node_groups.get(node_group)
                    if has_ng:
                        new_mod = obj.modifiers.new(mod["name"], mod["type"])
                        new_mod.node_group = has_ng
                        found = True
                    else:
                        # this method S U C K S
                        n = node_group.replace(" ", "_").lower()
                        for ast in node_assets:
                            if n in ast:
                                rai = os.path.join("geometry_nodes/", ast, "NodeTree/", node_group)
                                bpy.ops.object.modifier_add_node_group(
                                    asset_library_type='ESSENTIALS', asset_library_identifier="",
                                    relative_asset_identifier=rai)
                                found = True

                        if not found and custom_node_assets:
                            for key in custom_node_assets:
                                for ast in custom_node_assets[key]:
                                    if ast and n in ast:
                                        rai = os.path.join(ast, "NodeTree/", node_group)
                                        bpy.ops.object.modifier_add_node_group(
                                            asset_library_type='CUSTOM', asset_library_identifier=key,
                                            relative_asset_identifier=rai)
                                        found = True
                        if found:
                            # Find the new modifier (sigh)
                            new_mod = []
                            for m in obj.modifiers:
                                if m.type == "NODES" and m.node_group.name == node_group:
                                    new_mod.append(m)
                            if new_mod:
                                new_mod = new_mod[-1]
                            else:
                                print("Could not find new modifier")
                                found = False

                    if found and new_mod is not None:
                        # Apply node mod props
                        for prop in mod:
                            if prop not in ["name", "type", "node_group"]:
                                try:
                                    new_mod[prop] = mod[prop]
                                except Exception as e:
                                    print(f"Setting {modname} {prop} failed:", e)
                                # and panel props:
                                if hasattr(new_mod, prop):
                                    try:
                                        setattr(new_mod, prop, mod[prop])
                                    except Exception as e:
                                        print(f"Setting {modname} {prop} failed:", e)

                else:
                    # All the standard modifiers
                    new_mod = obj.modifiers.new(mod["name"], mod["type"])
                    for prop in mod:
                        if prop not in ["name", "type"]:
                            try:
                                setattr(new_mod, prop, mod[prop])
                            except Exception as e:
                                print(f"Setting {modname} {prop} failed:", e)

                if mod.get("use_pin_to_last") is not None:
                    # to make sure the pin-order is correct
                    bpy.ops.object.modifier_move_to_index(modifier=mod["name"], index=int(mod_idx))

            obj.select_set(False)

        for obj in sel_obj:
            obj.select_set(True)

        return {'FINISHED'}
