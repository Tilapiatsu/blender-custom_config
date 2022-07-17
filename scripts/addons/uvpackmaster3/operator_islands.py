# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


from .grouping_scheme import GroupingSchemeAccess, UVPM3_GroupingScheme
from .utils import *
from .pack_context import *
# from .prefs import *
from .island_params import *
from .operator import UVPM3_OT_Engine, UVPM3_OT_Help
from .overlay import TextOverlay
from .event import key_release_event

# import bmesh
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty, PointerProperty
# import bgl
# import blf





class UVPM3_OT_IParamGeneric(UVPM3_OT_Engine):

    SCENARIO_ID = 'aux.get_iparam_values'

    def __init__(self):
        super().__init__()
        
        self.iparam_info = None
        self.iparam_value = None
        self.overlay_count = 0

    def skip_topology_parsing(self):
        return True

    def pre_operation(self):
        self.iparam_info = self.get_iparam_info()
        self.p_context.register_iparam(self.iparam_info)
        self.iparam_value = self.get_iparam_value()

    def operation_done_finish_condition(self, event):
        return key_release_event(event)

    def operation_done_hint(self):

        return "press any key to hide '{}' values".format(self.iparam_info.label)

    def get_iparam_serializers(self):
        return [VColorIParamSerializer(self.iparam_info)]

    def iparam_to_text(self, iparam_value):
        return self.iparam_info.param_to_text(iparam_value)

    def iparam_to_color(self, iparam_value):
        return self.iparam_info.param_to_color(iparam_value)

    def create_param_overlay(self, p_island):
        self.overlay_count += 1
        iparam_value = p_island.iparam_value(self.iparam_info)
        return TextOverlay(self.iparam_to_text(iparam_value), self.iparam_to_color(iparam_value))

    def get_iparam_value(self):

        return getattr(self.scene_props, self.iparam_info.VALUE_PROP_NAME)

    def post_operation(self):

        for p_island in self.p_context.p_islands:

            if p_island.iparam_values is None:
                continue

            if self.process_island(p_island):
                p_island.register_overlay(self.create_param_overlay(p_island))

        if self.overlay_count > 0:
            self.update_context_meshes()

        self.log_manager.log(UvpmLogType.STATUS, 'Done')


class UVPM3_OT_ShowIParam(UVPM3_OT_IParamGeneric):

    def process_island(self, p_island):

        return True


class UVPM3_OT_SelectIParam(UVPM3_OT_IParamGeneric):

    def pre_operation(self):
        super().pre_operation()

    def require_selection(self):

        return False
        
    def send_unselected_islands(self):

        return True

    def process_island(self, p_island):

        if p_island.iparam_value(self.iparam_info) != self.iparam_value:
            return False

        p_island.select(bool(self.select))
        return True


class UVPM3_OT_SelectNonDefaultIParam(UVPM3_OT_IParamGeneric):

    def require_selection(self):

        return False
        
    def send_unselected_islands(self):

        return True

    def process_island(self, p_island):
        
        if p_island.iparam_value(self.iparam_info) == self.iparam_info.default_value:
            return False

        p_island.select(bool(self.select))
        return True


class UVPM3_OT_SetIParam(UVPM3_OT_ShowIParam):

    bl_options = {'UNDO'}

    def pre_operation(self):
        super().pre_operation()

        self.p_context.save_iparam(
            self.iparam_info,
            self.iparam_value)
        
        self.update_context_meshes()


class UVPM3_OT_SetFreeIParam(UVPM3_OT_ShowIParam):

    bl_options = {'UNDO'}

    def pre_operation(self):
        super().pre_operation()

        self.p_context.save_iparam(
            self.iparam_info,
            self.iparam_value)
        
        self.update_context_meshes()

    def get_iparam_value(self):

        param_values = self.p_context.load_all_iparam_values(self.iparam_info)
        param_values.sort()

        def assign_new_value(new_value):
            return new_value if new_value != self.iparam_info.DEFAULT_VALUE else new_value + 1

        free_value = assign_new_value(self.iparam_info.min_value)

        for iparam_value in param_values:

            if free_value == iparam_value:
                free_value = assign_new_value(free_value + 1)

            elif free_value < iparam_value:
                break

        if free_value > self.iparam_info.max_value:
            raise RuntimeError('Free value not found')

        return free_value


class UVPM3_OT_ResetIParam(UVPM3_OT_SetIParam):

    def get_iparam_value(self):

        return self.iparam_info.default_value



# ROTATION STEP

class UVPM3_OT_RotStepIParamGeneric:

    def get_iparam_info(self):
        return RotStepIParamInfo()


class UVPM3_OT_RotStepShowIParam(UVPM3_OT_RotStepIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.show_rot_step_iparam'
    bl_label = 'Show Rotation Step Setting'
    bl_description = "Show rotation step values assigned to the selected islands"


class UVPM3_OT_RotStepSetIParam(UVPM3_OT_RotStepIParamGeneric, UVPM3_OT_SetIParam):

    bl_idname = 'uvpackmaster3.set_island_rot_step'
    bl_label = 'Set Rotation Step'
    bl_description = "Set rotation step value for the selected islands. The value to be set is defined by the '{}' parameter".format(Labels.ISLAND_ROT_STEP_NAME)


class UVPM3_OT_RotStepResetIParam(UVPM3_OT_RotStepIParamGeneric, UVPM3_OT_ResetIParam):

    bl_idname = 'uvpackmaster3.reset_island_rot_step'
    bl_label = 'Reset Rotation Step'
    bl_description = "Reset rotation step value for the selected islands. After reset a special 'G' value will be assigned to the islands, which means they will use the global 'Rotation Step' parameter when generating orientations"


# SCALE LIMIT

class UVPM3_OT_ScaleLimitIParamGeneric:

    def get_iparam_info(self):
        return ScaleLimitIParamInfo()


class UVPM3_OT_ScaleLimitShowIParam(UVPM3_OT_ScaleLimitIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.show_scale_limit_iparam'
    bl_label = 'Show Scale Limit Setting'
    bl_description = "Show scale limit values assigned to the selected islands"


class UVPM3_OT_ScaleLimitSetIParam(UVPM3_OT_ScaleLimitIParamGeneric, UVPM3_OT_SetIParam):

    bl_idname = 'uvpackmaster3.set_island_scale_limit'
    bl_label = 'Set Scale Limit'
    bl_description = "Set scale limit value for the selected islands. The value to be set is defined by the '{}' parameter".format(Labels.ISLAND_SCALE_LIMIT_NAME)


class UVPM3_OT_ScaleLimitResetIParam(UVPM3_OT_ScaleLimitIParamGeneric, UVPM3_OT_ResetIParam):

    bl_idname = 'uvpackmaster3.reset_island_scale_limit'
    bl_label = 'Reset Scale Limit'
    bl_description = "Reset scale limit value for the selected islands"


# MANUAL GROUP

class UVPM3_OT_ManualGroupIParamGeneric(GroupingSchemeAccess):

    def execute_internal(self, context):
        self.init_access(context)
        return super().execute_internal(context)

    def get_iparam_info(self):
        
        if self.active_g_scheme is None or self.active_group is None:
            raise RuntimeError('No active grouping scheme or group')

        return self.active_g_scheme.get_iparam_info()

    def get_iparam_value(self):
        return self.active_group.num

    def iparam_to_text(self, iparam_value):
        return self.active_g_scheme.group_to_text(iparam_value)

    def iparam_to_color(self, iparam_value):
        return rgb_to_rgba(self.active_g_scheme.group_to_color(iparam_value))

    def grouping_enabled(self):
        return True

    def get_group_method(self):
        return GroupingMethod.MANUAL.code

    def get_iparam_serializers(self):
        return []



class UVPM3_OT_ShowManualGroupIParam(UVPM3_OT_ManualGroupIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.uv_show_manual_group_iparam'
    bl_label = 'Show Group Assignment'
    bl_description = "Show the names of all groups the selected islands are assigned to"


class UVPM3_OT_SetManualGroupIParam(UVPM3_OT_ManualGroupIParamGeneric, UVPM3_OT_SetIParam):

    bl_idname = 'uvpackmaster3.set_island_manual_group'
    bl_label = 'Assign Islands To The Group'
    bl_description = "Assign the selected islands to the active group"

class UVPM3_OT_ResetManualGroupIParam(UVPM3_OT_ManualGroupIParamGeneric, UVPM3_OT_ResetIParam):

    bl_idname = 'uvpackmaster3.reset_island_manual_group'
    bl_label = 'Reset Groups'
    bl_description = "Reset the group assignment for the selected islands"


class UVPM3_OT_SelectManualGroupIParam(UVPM3_OT_ManualGroupIParamGeneric, UVPM3_OT_SelectIParam):

    select : BoolProperty(name='', default=True)
    
    bl_idname = 'uvpackmaster3.select_island_manual_group'
    bl_label = 'Select Islands Assigned To Group'
    bl_description = "Select / deselect all islands which are assigned to the active group"


class UVPM3_OT_ApplyGroupingToScheme(UVPM3_OT_ManualGroupIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.apply_grouping_to_scheme'
    bl_label = 'Apply Grouping To Scheme'
    bl_description = "Create or extend a manual grouping scheme using the currently selected automatic grouping method"

    apply_action : EnumProperty(name="Action", items=[("NEW", "Create A New Scheme", "Create A New Scheme", 0),
                                                      ("EXTEND", "Apply To An Existing Scheme", "Apply To An Existing Scheme", 1)])
    name : StringProperty(name="Name", default=UVPM3_GroupingScheme.DEFAULT_GROUPING_SCHEME_NAME)
    scheme : EnumProperty(name="Grouping Schemes", items=GroupingSchemeAccess.get_grouping_schemes_enum_items_callback)

    def pre_operation(self):
        create_new_grouping_scheme = self.apply_action == "NEW"

        if not create_new_grouping_scheme and len(self.get_grouping_schemes()) == 0:
            raise RuntimeError('No grouping scheme in the blend file found')

        generated_grouping_scheme = self.init_grouping_scheme(self.scene_props.group_method)

        if create_new_grouping_scheme:
            self.create_grouping_scheme()
        else:
            self.set_active_grouping_scheme_idx(int(self.scheme))

        target_grouping_scheme = self.active_g_scheme

        if create_new_grouping_scheme:
            target_grouping_scheme.copy_from(generated_grouping_scheme)
            target_grouping_scheme.name = self.name
            target_group_map = generated_grouping_scheme.group_map
        else:
            target_group_map = self.extend_grouping_scheme(target_grouping_scheme, generated_grouping_scheme)

        target_iparam_info = target_grouping_scheme.get_iparam_info()

        for target_group in target_grouping_scheme.groups:
            for p_obj in self.p_context.p_objects:
                p_obj_faces = [f for f in p_obj.selected_faces_stored if target_group_map.get_map(p_obj, f.index) == target_group.num]
                p_obj.save_iparam(target_iparam_info, target_group.num, p_obj_faces)

        self.scene_props.group_method = GroupingMethod.MANUAL.code
        super().pre_operation()

    def extend_grouping_scheme(self, target_grouping_scheme, generated_grouping_scheme):
        groups_num_map = {}
        target_grouping_scheme.init_defaults()
        target_grouping_scheme.init_group_map(self.p_context, GroupingMethod.MANUAL.code)

        for generated_group in generated_grouping_scheme.groups:
            target_group = target_grouping_scheme.get_group_by_name(generated_group.name)
            groups_num_map[generated_group.num] = target_group.num

        generated_group_map = generated_grouping_scheme.group_map
        target_group_map = target_grouping_scheme.group_map
        for face_idx, generated_group_num in enumerate(generated_group_map.map):
            if generated_group_num in groups_num_map:
                target_group_map.map[face_idx] = groups_num_map[generated_group_num]
                
        return target_group_map

    def invoke(self, context, event):
        scene_props = context.scene.uvpm3_props
        group_method_label = scene_props.bl_rna.properties['group_method'].enum_items[scene_props.group_method].name
        self.name = "Scheme '{}'".format(group_method_label)

        return super().invoke(context, event)

    def draw(self, context):
        self.init_access(context, ui_drawing=True)
        create_new_grouping_scheme = self.apply_action == "NEW"

        layout = self.layout
        layout.prop(self, "apply_action", text="")

        row = layout.row(align=True)

        if create_new_grouping_scheme:
            split = row.split(factor=0.4, align=True)
            split.label(text="New Scheme Name:")
            row = split.row(align=True)
            row.prop(self, "name", text="")
        else:
            if len(self.get_grouping_schemes()) == 0:
                row.label(text='WARNING: no grouping scheme in the blend file found.')
            else:
                split = row.split(factor=0.4, align=True)
                split.label(text="Apply To Scheme:")
                row = split.row(align=True)
                row.prop(self, "scheme", text="")
                

# LOCK GROUP

class UVPM3_OT_LockGroupIParamGeneric:

    def get_iparam_info(self):
        return LockGroupIParamInfo()


class UVPM3_OT_ShowLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.uv_show_lock_group_iparam'
    bl_label = 'Show Lock Group Assignment'
    bl_description = "Show lock group numbers the selected islands are assigned to"


class UVPM3_OT_SetLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_SetIParam):

    bl_idname = 'uvpackmaster3.set_island_lock_group'
    bl_label = 'Assign Islands To Lock Group'
    bl_description = "Assign the selected islands to a lock group determined by the 'Lock Group Number' parameter"


class UVPM3_OT_SetFreeLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_SetFreeIParam):

    bl_idname = 'uvpackmaster3.set_free_island_lock_group'
    bl_label = 'Assign Islands To Free Lock Group'
    bl_description = "Assign the selected islands to the first free lock group (the lowest lock group not currently used by faces in the UV map)"


class UVPM3_OT_ResetLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_ResetIParam):

    bl_idname = 'uvpackmaster3.reset_island_lock_group'
    bl_label = 'Unset Lock Groups'
    bl_description = "Unset the lock group assignment for the selected islands (the islands will not belong to any group)"


class UVPM3_OT_SelectLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_SelectIParam):

    select : BoolProperty(name='', default=True)
    
    bl_idname = 'uvpackmaster3.select_island_lock_group'
    bl_label = 'Select Islands Assigned To Lock Group'
    bl_description = "Select / deselect all islands which are assigned to the lock group determined by the '{}' parameter".format(Labels.LOCK_GROUP_NUM_NAME)


class UVPM3_OT_SelectNonDefaultLockGroupIParam(UVPM3_OT_LockGroupIParamGeneric, UVPM3_OT_SelectNonDefaultIParam):

    select : BoolProperty(name='', default=True)
    
    bl_idname = 'uvpackmaster3.select_non_default_island_lock_group'
    bl_label = 'Select All Lock Groups'
    bl_description = "Select all islands which are assigned to any lock group"
 

# ALIGN PRIORITY

class UVPM3_OT_AlignPriorityIParamGeneric:

    def get_iparam_info(self):
        return AlignPriorityIParamInfo()


class UVPM3_OT_AlignPriorityShowIParam(UVPM3_OT_AlignPriorityIParamGeneric, UVPM3_OT_ShowIParam):

    bl_idname = 'uvpackmaster3.align_priority_show_iparam'
    bl_label = 'Show Align Priority'
    bl_description = "Show align priority values assigned to the selected islands"


class UVPM3_OT_AlignPrioritySetIParam(UVPM3_OT_AlignPriorityIParamGeneric, UVPM3_OT_SetIParam):

    bl_idname = 'uvpackmaster3.align_priority_set_iparam'
    bl_label = 'Set Align Priority'
    bl_description = "Set align priority value for the selected islands. The value to be set is defined by the '{}' parameter".format(Labels.ALIGN_PRIORITY_NAME)


class UVPM3_OT_AlignPriorityResetIParam(UVPM3_OT_AlignPriorityIParamGeneric, UVPM3_OT_ResetIParam):

    bl_idname = 'uvpackmaster3.align_priority_reset_iparam'
    bl_label = 'Reset Align Priority'
    bl_description = "Reset align priority for the selected islands (assign priority 0 to the islands)"





class IParamEditUI:

    # List of the variables the derived class must provide:
    # OPERATOR_PREFIX
    # ENABLED_PROP_NAME

    # List of the optional variables:
    HELP_URL_SUFFIX = None

    def __init__(self, context, scene_props):

        self.context = context
        self.scene_props = scene_props

    def impl_enabled(self):

        return True, ''

    def operator_class_str(self, type):

        return "UVPM3_OT_{}{}".format(self.OPERATOR_PREFIX, type)

    def operator_class(self, type):

        return globals()[self.operator_class_str(type)]

    def impl_set_iparam_operator(self):

        return self.operator_class('SetIParam')

    def impl_reset_iparam_operator(self):

        return self.operator_class('ResetIParam')

    def impl_show_iparam_operator(self):

        return self.operator_class('ShowIParam')

    def impl_iparam_value_prop_name(self):

        return self.operator_class('IParamGeneric')().get_iparam_info().VALUE_PROP_NAME

    def draw(self, layout):

        col = layout.column(align=True)
        col.enabled = True

        row = col.row(align=True)
        row.prop(self.scene_props, self.impl_iparam_value_prop_name())

        if self.HELP_URL_SUFFIX is not None:
            help_op = row.operator(UVPM3_OT_Help.bl_idname, icon='HELP', text='')
            help_op.url_suffix = self.HELP_URL_SUFFIX

        row = col.row(align=True)
        row.operator(self.impl_set_iparam_operator().bl_idname)

        col.separator()
        row = col.row(align=True)
        row.operator(self.impl_reset_iparam_operator().bl_idname)

        row = col.row(align=True)
        row.operator(self.impl_show_iparam_operator().bl_idname)
