import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from .utils import parse_json_file, in_debug_mode, encode_string
from .enums import RunScenario

import os
import json


SCRIPTED_PIPELINE_DIRNAME = "scripted_pipeline"
ENGINE_PACKAGES_DIRNAME = "engine_packages"
SCENARIOS_DIRNAME = "engine_scenarios"
SCENARIO_FILENAME = "scenario.json"
SCENARIO_SCRIPT_FILENAME = "scenario.py"


def load_scripted_pipeline(root=None):
    if root is None:
        root = os.path.dirname(__file__)

    run_scenarios_dir = os.path.join(root, SCRIPTED_PIPELINE_DIRNAME, SCENARIOS_DIRNAME)
    if not os.path.exists(run_scenarios_dir):
        print("UVPM3: Missing scenarios root directory")
        return

    run_scenarios_subdirs = [os.path.join(run_scenarios_dir, d) for d in os.listdir(run_scenarios_dir)
                             if os.path.isdir(os.path.join(run_scenarios_dir, d))]
    run_scenarios_subdirs.sort()
    scenarios = []
    for subdir in run_scenarios_subdirs:
        scenario_path = os.path.join(subdir, SCENARIO_FILENAME)
        if not os.path.exists(scenario_path):
            print("UVPM3: Missing scenario \"{}\"".format(scenario_path))
            continue
        scenario = parse_json_file(scenario_path)
        if scenario is not None:
            scenario['file_path'] = os.path.relpath(scenario_path, root)
            scenario['script_path'] = os.path.abspath(os.path.join(subdir, SCENARIO_SCRIPT_FILENAME))
            scenarios.append(scenario)
        else:
            print("UVPM3: Cannot parse '{}'".format(scenario_path))

    return True, scenarios


def _has_whitespace(string):
    return any(True for s in string if s in ' \t\n\r\x0b\x0c')


def _validate_string(name, args_dict_or_value, empty=True, whitespaces=True):
    value = args_dict_or_value.get(name) if isinstance(args_dict_or_value, dict) else args_dict_or_value
    if not isinstance(value, str):
        return "Type mismatch for '{}' field, str expected, got {}".format(name, type(value))
    if not empty and not value:
        return "An empty '{}' field".format(name)
    if not whitespaces and _has_whitespace(value):
        return "The '{}' field contain whitespaces".format(name)


def _validate_scenario(scenario, processed_scenarios_metadata, processed_props_metadata):
    scenario_errors = []

    scenario_id = scenario.get("id")
    scenario_id_error = _validate_string("id", scenario_id, empty=False, whitespaces=False)
    if scenario_id_error:
        scenario_errors.append(scenario_id_error)
    else:
        if scenario_id in processed_scenarios_metadata.keys():
            scenario_errors.append("Scenario with id '{}' already exists({})".format(scenario_id,
                                                                                     processed_scenarios_metadata[scenario_id]))

    return scenario_errors


def add_dynamic_property(cls, prop_id, prop_func, prop_args):
    cls.__annotations__[prop_id] = prop_func(**prop_args)


def scripted_pipeline_property_group(collection_name, parent, builtins):
    result_ok, scenarios = load_scripted_pipeline()
    if not result_ok and not in_debug_mode():
        print("UVPM3: Initialization error, run Blender with -d parameter to debug")

    processed_props_metadata = {collection_name: "Builtin property in '{}'".format(parent.__name__)}
    for builtin in builtins:
        if hasattr(builtin, '__annotations__'):
            keys = builtin.__annotations__.keys()
            processed_props_metadata.update(zip(keys, ("Builtin property in '{}'".format(builtin.__name__),)*len(keys)))

    def decorator(cls):
        validate_errors = []

        if not hasattr(cls, "__annotations__"):
            cls.__annotations__ = {}

        processed_scenarios_metadata = {}
        for scenario in scenarios:
            scenario_id = scenario.get("id")
            scenario_errors = _validate_scenario(scenario, processed_scenarios_metadata, processed_props_metadata)
            if scenario_errors:
                validate_errors.append(' ')
                validate_errors.append("UVPM3: Scenario '{}' not created ({})".format(scenario_id, scenario["file_path"]))
                validate_errors.extend(scenario_errors)
                validate_errors.append('-'*80)
            else:
                RunScenario.add_scenario(scenario)
                processed_scenarios_metadata[scenario_id] = scenario["file_path"]

        if validate_errors and not in_debug_mode():
            print("UVPM3: Dynamic properties initialization error for '{}', run Blender with -d parameter to debug".format(cls.__name__))
        elif validate_errors and in_debug_mode():
            if in_debug_mode():
                for err in validate_errors:
                    print(err)

        add_dynamic_property(parent, collection_name, PointerProperty, {"type": cls})
        return cls

    return decorator


class ScriptParams:

    DEVICE_SETTINGS_PARAM_NAME = '__device_settings'
    SYS_PATH_PARAM_NAME = '__sys_path'
    GROUPING_SCHEME_PARAM_NAME = '__grouping_scheme'

    def __init__(self):
        self.param_dict = dict()

    def add_param(self, id, value):
        self.param_dict[id] = value

    def add_device_settings(self, dev_array):
        settings_params = []

        for dev in dev_array:
            settings = dev.settings
            settings_params.append({'id': dev.id, 'enabled': settings.enabled})

        self.param_dict[self.DEVICE_SETTINGS_PARAM_NAME] = settings_params

    def add_sys_path(self, sys_path):
        sys_path_param = self.param_dict.setdefault(self.SYS_PATH_PARAM_NAME, [])
        sys_path_param.append(sys_path)

    def add_grouping_scheme(self, g_scheme):

        out_groups = []
        for group in g_scheme.groups:

            out_target_boxes = []
            for box in group.target_boxes:
                out_target_boxes.append(box.coords_tuple())

            out_groups.append(
                {
                    'name': group.name,
                    'num': group.num,
                    'tdensity_cluster': group.tdensity_cluster,
                    'target_boxes': out_target_boxes
                })

        out_g_scheme =\
        {
            'iparam_name': g_scheme.get_iparam_info().script_name,
            'group_compactness': g_scheme.options.base.group_compactness,
            'groups': out_groups
        }

        self.param_dict[self.GROUPING_SCHEME_PARAM_NAME] = out_g_scheme

    def serialize(self):
        return encode_string(json.dumps(self.param_dict))
