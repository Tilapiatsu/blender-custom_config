# Copyright (C) 2023 CG GALAXY
# cggalaxy@hotmail.com

# Created by CG GALAXY

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Pro Aligner",
    "author" : "CG GALAXY", 
    "description" : "Align and restore object's rotation",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "View 3D > Sidebar > Pro Aligner",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "3D View" 
}


import bpy
import bpy.utils.previews
from bpy.app.handlers import persistent
import mathutils


addon_keymaps = {}
_icons = None
align_button = {'sna_x_trigger_checker': False, 'sna_y_trigger_checker': False, 'sna_z_trigger_checker': False, 'sna_active_object': None, }
depsgraph_update = {'sna_depsgraph_update': False, }
operator = {'sna_z_trigger': False, 'sna_x_trigger': False, 'sna_y_trigger': False, 'sna_if_x_true': False, 'sna_if_y_true': False, 'sna_z_empty_rot_x': 0.0, 'sna_z_empty_rot_y': 0.0, 'sna_z_empty_rot_z': 0.0, 'sna_x_empty_rot_x': 0.0, 'sna_x_empty_rot_y': 0.0, 'sna_x_empty_rot_z': 0.0, 'sna_y_empty_rot_x': 0.0, 'sna_y_empty_rot_y': 0.0, 'sna_y_empty_rot_z': 0.0, 'sna_in_which_mode': '', }
save_cursor_location__rotation = {'sna_cursor_loc_x': 0.0, 'sna_cursor_loc_y': 0.0, 'sna_cursor_loc_z': 0.0, 'sna_cursor_rot_x': 0.0, 'sna_cursor_rot_y': 0.0, 'sna_cursor_rot_z': 0.0, }
save_object_location = {'sna_object_x': 0.0, 'sna_object_y': 0.0, 'sna_object_z': 0.0, }


def sna_select__set_active_object_07AE7_1E5C9(Object):
    bpy.ops.object.select_all('INVOKE_DEFAULT', action='DESELECT')
    bpy.context.view_layer.objects.active = Object
    Object.select_set(state=True, )
    return


def sna_select__set_active_object_07AE7_22791(Object):
    bpy.ops.object.select_all('INVOKE_DEFAULT', action='DESELECT')
    bpy.context.view_layer.objects.active = Object
    Object.select_set(state=True, )
    return


def sna_select__set_active_object_07AE7_9BC93(Object):
    bpy.ops.object.select_all('INVOKE_DEFAULT', action='DESELECT')
    bpy.context.view_layer.objects.active = Object
    Object.select_set(state=True, )
    return


def sna_select__set_active_object_07AE7_09F3E(Object):
    bpy.ops.object.select_all('INVOKE_DEFAULT', action='DESELECT')
    bpy.context.view_layer.objects.active = Object
    Object.select_set(state=True, )
    return


def sna_func_DCD00_F4AF8():
    return round(1.5707963705062866, abs(50))


def sna_func_877A4_5DFD6():
    return round(-1.5707963705062866, abs(50))


def sna_func_A7BA5_9B2F4():
    return round(4.71238899230957, abs(50))


def sna_func_5071F_57B3A():
    return round(-4.71238899230957, abs(50))


def sna_func_7052F_3E8B4():
    return round(3.1415927410125732, abs(50))


def sna_func_DCD00_9E38D():
    return round(1.5707963705062866, abs(50))


def sna_func_877A4_12739():
    return round(-1.5707963705062866, abs(50))


def sna_func_A7BA5_647D5():
    return round(4.71238899230957, abs(50))


def sna_func_5071F_9A29E():
    return round(-4.71238899230957, abs(50))


def sna_func_7052F_14F7D():
    return round(3.1415927410125732, abs(50))


def sna_func_7052F_2FA03():
    return round(3.1415927410125732, abs(50))


def sna_func_DCD00_F01DE():
    return round(1.5707963705062866, abs(50))


def sna_func_8476F_93E92():
    return round(-3.1415927410125732, abs(50))


def sna_func_A7BA5_9888E():
    return round(4.71238899230957, abs(50))


def sna_func_A7BA5_9F639():
    return round(4.71238899230957, abs(50))


def sna_func_DCD00_DCE29():
    return round(1.5707963705062866, abs(50))


def sna_func_877A4_3A20F():
    return round(-1.5707963705062866, abs(50))


def sna_func_A7BA5_ECFF1():
    return round(4.71238899230957, abs(50))


def sna_func_5071F_DF393():
    return round(-4.71238899230957, abs(50))


def sna_func_7052F_EEF5F():
    return round(3.1415927410125732, abs(50))


def sna_func_DCD00_7DA53():
    return round(1.5707963705062866, abs(50))


def sna_func_877A4_84D43():
    return round(-1.5707963705062866, abs(50))


def sna_func_A7BA5_D1D26():
    return round(4.71238899230957, abs(50))


def sna_func_5071F_A9192():
    return round(-4.71238899230957, abs(50))


def sna_func_7052F_5148E():
    return round(3.1415927410125732, abs(50))


def sna_func_DCD00_0D193():
    return round(1.5707963705062866, abs(50))


def sna_func_877A4_4699E():
    return round(-1.5707963705062866, abs(50))


def sna_func_A7BA5_1CB8B():
    return round(4.71238899230957, abs(50))


def sna_func_5071F_CD117():
    return round(-4.71238899230957, abs(50))


def sna_func_7052F_91394():
    return round(3.1415927410125732, abs(50))


def sna_func_7052F_270D3():
    return round(3.1415927410125732, abs(50))


def property_exists(prop_path, glob, loc):
    try:
        eval(prop_path, glob, loc)
        return True
    except:
        return False


def sna_add_empty_8A33C(Object_Name):
    Empty_Object = Object_Name
    # Create an empty object
    empty = bpy.data.objects.new(Empty_Object, None)
    # Get the 3D cursor rotation
    cursor_rot = bpy.context.scene.cursor.rotation_euler
    # Set the empty object's rotation to the 3D cursor rotation
    empty.rotation_euler = cursor_rot
    sna_link_empty_to_scene_077C5(Object_Name)


class SNA_OT_Align_3Ea9B(bpy.types.Operator):
    bl_idname = "sna.align_3ea9b"
    bl_label = "Align"
    bl_description = "Align the object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        align_button['sna_active_object'] = bpy.context.view_layer.objects.active
        sna_save_cursor_location__rotation_438BE()
        sna_save_object_location_3F045()
        if operator['sna_z_trigger']:
            align_button['sna_z_trigger_checker'] = True
        else:
            align_button['sna_z_trigger_checker'] = False
        if operator['sna_x_trigger']:
            align_button['sna_x_trigger_checker'] = True
        else:
            align_button['sna_x_trigger_checker'] = False
        if operator['sna_y_trigger']:
            align_button['sna_y_trigger_checker'] = True
        else:
            align_button['sna_y_trigger_checker'] = False
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Set origin to center of mass
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        sna_cursor_to_origin_C852E()
        if align_button['sna_z_trigger_checker']:
            sna_add_empty_8A33C('PA_Z_Axis_Store_Object')
            sna_object_rotation_combine_A460B('PA_Z_Axis_Store_Object', 'PA_Z_Axis_Store_Constraint', operator['sna_z_empty_rot_x'], operator['sna_z_empty_rot_y'], operator['sna_z_empty_rot_z'])
            if align_button['sna_x_trigger_checker']:
                sna_add_empty_8A33C('PA_X_Axis_Store_Object')
                bpy.data.objects['PA_X_Axis_Store_Object'].rotation_euler = (operator['sna_x_empty_rot_x'], operator['sna_x_empty_rot_y'], operator['sna_x_empty_rot_z'])
                sna_select__set_active_object_07AE7_1E5C9(bpy.data.objects['PA_Z_Axis_Store_Object'])
                bpy.data.objects['PA_X_Axis_Store_Object'].select_set(state=True, )
                bpy.ops.object.parent_set('INVOKE_DEFAULT', type='OBJECT', keep_transform=True)
                sna_align_z_D133A()
                bpy.ops.object.parent_clear('INVOKE_DEFAULT', type='CLEAR_KEEP_TRANSFORM')
                sna_select__set_active_object_07AE7_22791(align_button['sna_active_object'])
                Empty_Constraint_Apply = 'PA_Z_Axis_Store_Constraint'
                # Apply constraint
                bpy.ops.constraint.apply(constraint=Empty_Constraint_Apply,)
                sna_remove_object_ECF92('PA_Z_Axis_Store_Object')
                Empty_Object = 'PA_X_Axis_Store_Object'
                Empty_Constraint = 'PA_X_Axis_Store_Constraint'
                # Get the active object
                active_object = bpy.context.active_object
                # Create the constraint
                constraint = active_object.constraints.new(type='CHILD_OF')
                constraint.name = Empty_Constraint if 'Child Of' in active_object.constraints else Empty_Constraint
                # Set the target object for the constraint
                constraint.target = bpy.data.objects[Empty_Object]
                bpy.context.view_layer.update()
                sna_align_x_A0848()
                sna_combine_1__align_button_91DC0('PA_X_Axis_Store_Object', 'PA_X_Axis_Store_Constraint')
            else:
                if align_button['sna_y_trigger_checker']:
                    sna_add_empty_8A33C('PA_Y_Axis_Store_Object')
                    bpy.data.objects['PA_Y_Axis_Store_Object'].rotation_euler = (operator['sna_y_empty_rot_x'], operator['sna_y_empty_rot_y'], operator['sna_y_empty_rot_z'])
                    sna_select__set_active_object_07AE7_9BC93(bpy.data.objects['PA_Z_Axis_Store_Object'])
                    bpy.data.objects['PA_Y_Axis_Store_Object'].select_set(state=True, )
                    bpy.ops.object.parent_set('INVOKE_DEFAULT', type='OBJECT', keep_transform=True)
                    sna_align_z_D133A()
                    bpy.ops.object.parent_clear('INVOKE_DEFAULT', type='CLEAR_KEEP_TRANSFORM')
                    sna_select__set_active_object_07AE7_09F3E(align_button['sna_active_object'])
                    Empty_Constraint_Apply = 'PA_Z_Axis_Store_Constraint'
                    # Apply constraint
                    bpy.ops.constraint.apply(constraint=Empty_Constraint_Apply,)
                    sna_remove_object_ECF92('PA_Z_Axis_Store_Object')
                    Empty_Object = 'PA_Y_Axis_Store_Object'
                    Empty_Constraint = 'PA_Y_Axis_Store_Constraint'
                    # Get the active object
                    active_object = bpy.context.active_object
                    # Create the constraint
                    constraint = active_object.constraints.new(type='CHILD_OF')
                    constraint.name = Empty_Constraint if 'Child Of' in active_object.constraints else Empty_Constraint
                    # Set the target object for the constraint
                    constraint.target = bpy.data.objects[Empty_Object]
                    bpy.context.view_layer.update()
                    sna_align_y_1FE4D()
                    sna_combine_1__align_button_91DC0('PA_Y_Axis_Store_Object', 'PA_Y_Axis_Store_Constraint')
                else:
                    sna_align_z_D133A()
                    # Apply constraint
                    bpy.ops.constraint.apply(constraint='PA_Z_Axis_Store_Constraint',)
                    sna_remove_object_ECF92('PA_Z_Axis_Store_Object')
                    sna_cursor_to_object_saved_location_FA0D9()
                    # Origin to cursor
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                    sna_return_cursor_location__rotation_08E90()
                    bpy.context.view_layer.update()
                    # Switch to edit mode
                    bpy.ops.object.mode_set(mode='EDIT')
        else:
            if align_button['sna_x_trigger_checker']:
                sna_add_empty_8A33C('PA_X_Axis_Store_Object')
                sna_object_rotation_combine_A460B('PA_X_Axis_Store_Object', 'PA_X_Axis_Store_Constraint', operator['sna_x_empty_rot_x'], operator['sna_x_empty_rot_y'], operator['sna_x_empty_rot_z'])
                sna_align_x_A0848()
                sna_combine_1__align_button_91DC0('PA_X_Axis_Store_Object', 'PA_X_Axis_Store_Constraint')
            else:
                if align_button['sna_y_trigger_checker']:
                    sna_add_empty_8A33C('PA_Y_Axis_Store_Object')
                    sna_object_rotation_combine_A460B('PA_Y_Axis_Store_Object', 'PA_Y_Axis_Store_Constraint', operator['sna_y_empty_rot_x'], operator['sna_y_empty_rot_y'], operator['sna_y_empty_rot_z'])
                    sna_align_y_1FE4D()
                    sna_combine_1__align_button_91DC0('PA_Y_Axis_Store_Object', 'PA_Y_Axis_Store_Constraint')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_combine_1__align_button_91DC0(Object_Name, Constraint_Name):
    Empty_Constraint_Apply = Constraint_Name
    # Apply constraint
    bpy.ops.constraint.apply(constraint=Empty_Constraint_Apply,)
    sna_remove_object_ECF92(Object_Name)
    sna_cursor_to_object_saved_location_FA0D9()
    # Origin to cursor
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    sna_return_cursor_location__rotation_08E90()
    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')


def sna_align_x_A0848():
    if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_X_Axis_Store_Object')[2], sna_func_DCD00_F4AF8(), sna_func_877A4_5DFD6()):
        a_0_a3993, b_1_a3993, c_2_a3993, object_name_3_a3993 = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
        sna_align_empty_2_EABEF(a_0_a3993, b_1_a3993, 0.0, object_name_3_a3993)
    else:
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_X_Axis_Store_Object')[2], sna_func_A7BA5_9B2F4(), sna_func_5071F_57B3A()):
            a_0_b5f1e, b_1_b5f1e, c_2_b5f1e, object_name_3_b5f1e = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_b5f1e, b_1_b5f1e, sna_func_7052F_3E8B4(), object_name_3_b5f1e)
        else:
            a_0_1e765, b_1_1e765, c_2_1e765, object_name_3_1e765 = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_1e765, b_1_1e765, 0.0, object_name_3_1e765)
    if align_button['sna_z_trigger_checker']:
        pass
    else:
        bpy.context.view_layer.update()
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_X_Axis_Store_Object')[1], sna_func_DCD00_9E38D(), sna_func_877A4_12739()):
            a_0_30789, b_1_30789, c_2_30789, object_name_3_30789 = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_30789, 0.0, c_2_30789, object_name_3_30789)
        else:
            if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_X_Axis_Store_Object')[1], sna_func_A7BA5_647D5(), sna_func_5071F_9A29E()):
                a_0_b570e, b_1_b570e, c_2_b570e, object_name_3_b570e = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
                sna_align_empty_2_EABEF(a_0_b570e, sna_func_7052F_14F7D(), c_2_b570e, object_name_3_b570e)
            else:
                a_0_10b9d, b_1_10b9d, c_2_10b9d, object_name_3_10b9d = sna_align_empty_1_32E4D('PA_X_Axis_Store_Object')
                sna_align_empty_2_EABEF(a_0_10b9d, 0.0, c_2_10b9d, object_name_3_10b9d)


def sna_align_y_1FE4D():
    if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Y_Axis_Store_Object')[2], sna_func_7052F_2FA03(), 0.0):
        a_0_ee129, b_1_ee129, c_2_ee129, object_name_3_ee129 = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
        sna_align_empty_2_EABEF(a_0_ee129, b_1_ee129, sna_func_DCD00_F01DE(), object_name_3_ee129)
    else:
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Y_Axis_Store_Object')[2], 0.0, sna_func_8476F_93E92()):
            a_0_ee8ed, b_1_ee8ed, c_2_ee8ed, object_name_3_ee8ed = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_ee8ed, b_1_ee8ed, sna_func_A7BA5_9888E(), object_name_3_ee8ed)
        else:
            a_0_1c0a1, b_1_1c0a1, c_2_1c0a1, object_name_3_1c0a1 = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_1c0a1, b_1_1c0a1, sna_func_A7BA5_9F639(), object_name_3_1c0a1)
    if align_button['sna_z_trigger_checker']:
        pass
    else:
        bpy.context.view_layer.update()
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Y_Axis_Store_Object')[1], sna_func_DCD00_DCE29(), sna_func_877A4_3A20F()):
            a_0_c4af9, b_1_c4af9, c_2_c4af9, object_name_3_c4af9 = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_c4af9, 0.0, c_2_c4af9, object_name_3_c4af9)
        else:
            if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Y_Axis_Store_Object')[1], sna_func_A7BA5_ECFF1(), sna_func_5071F_DF393()):
                a_0_ed87e, b_1_ed87e, c_2_ed87e, object_name_3_ed87e = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
                sna_align_empty_2_EABEF(a_0_ed87e, sna_func_7052F_EEF5F(), c_2_ed87e, object_name_3_ed87e)
            else:
                a_0_6f86b, b_1_6f86b, c_2_6f86b, object_name_3_6f86b = sna_align_empty_1_32E4D('PA_Y_Axis_Store_Object')
                sna_align_empty_2_EABEF(a_0_6f86b, 0.0, c_2_6f86b, object_name_3_6f86b)


def sna_angle_compare_set_1_94E82(Object_Name):
    return [bpy.data.objects[Object_Name].rotation_euler[0], bpy.data.objects[Object_Name].rotation_euler[1], bpy.data.objects[Object_Name].rotation_euler[2]]


def sna_angle_compare_set_2_56D89(Axis, Plus, Minus):
    return ((Axis <= Plus) and (Axis >= Minus))


def sna_align_empty_2_EABEF(a, b, c, Object_Name):
    bpy.data.objects[Object_Name].rotation_euler = (a, b, c)


def sna_align_empty_1_32E4D(Object_Name):
    return [sna_object_rotation_split_vector_EBB56(Object_Name)[0], sna_object_rotation_split_vector_EBB56(Object_Name)[1], sna_object_rotation_split_vector_EBB56(Object_Name)[2], Object_Name]


def sna_align_z_D133A():
    if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Z_Axis_Store_Object')[0], sna_func_DCD00_7DA53(), sna_func_877A4_84D43()):
        a_0_ce304, b_1_ce304, c_2_ce304, object_name_3_ce304 = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
        sna_align_empty_2_EABEF(0.0, b_1_ce304, c_2_ce304, object_name_3_ce304)
    else:
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Z_Axis_Store_Object')[0], sna_func_A7BA5_D1D26(), sna_func_5071F_A9192()):
            a_0_4e0b1, b_1_4e0b1, c_2_4e0b1, object_name_3_4e0b1 = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
            sna_align_empty_2_EABEF(sna_func_7052F_5148E(), b_1_4e0b1, c_2_4e0b1, object_name_3_4e0b1)
        else:
            a_0_5e987, b_1_5e987, c_2_5e987, object_name_3_5e987 = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
            sna_align_empty_2_EABEF(0.0, b_1_5e987, c_2_5e987, object_name_3_5e987)
    bpy.context.view_layer.update()
    if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Z_Axis_Store_Object')[1], sna_func_DCD00_0D193(), sna_func_877A4_4699E()):
        a_0_6941f, b_1_6941f, c_2_6941f, object_name_3_6941f = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
        sna_align_empty_2_EABEF(a_0_6941f, 0.0, c_2_6941f, object_name_3_6941f)
    else:
        if sna_angle_compare_set_2_56D89(sna_angle_compare_set_1_94E82('PA_Z_Axis_Store_Object')[1], sna_func_A7BA5_1CB8B(), sna_func_5071F_CD117()):
            a_0_69a50, b_1_69a50, c_2_69a50, object_name_3_69a50 = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_69a50, sna_func_7052F_91394(), c_2_69a50, object_name_3_69a50)
        else:
            a_0_5ebaf, b_1_5ebaf, c_2_5ebaf, object_name_3_5ebaf = sna_align_empty_1_32E4D('PA_Z_Axis_Store_Object')
            sna_align_empty_2_EABEF(a_0_5ebaf, 0.0, c_2_5ebaf, object_name_3_5ebaf)


def sna_check_triggers_9CA3E():
    return [(operator['sna_z_trigger'] or operator['sna_x_trigger'] or operator['sna_y_trigger']), (not (operator['sna_z_trigger'] or operator['sna_x_trigger'] or operator['sna_y_trigger']))]


def sna_cursor_to_object_saved_location_FA0D9():
    bpy.context.scene.cursor.location = (save_object_location['sna_object_x'], save_object_location['sna_object_y'], save_object_location['sna_object_z'])


def sna_cursor_to_origin_C852E():
    bpy.context.scene.cursor.location = bpy.context.view_layer.objects.active.location


@persistent
def depsgraph_update_pre_handler_28632(dummy):
    if depsgraph_update['sna_depsgraph_update']:
        if (bpy.context.active_object.mode != 'EDIT'):
            sna_remove_object_and_constraint_2F139('PA_Z_Axis_Store_Object', 'PA_Z_Axis_Store_Constraint')
            sna_remove_object_and_constraint_2F139('PA_X_Axis_Store_Object', 'PA_X_Axis_Store_Constraint')
            sna_remove_object_and_constraint_2F139('PA_Y_Axis_Store_Object', 'PA_Y_Axis_Store_Constraint')
            depsgraph_update['sna_depsgraph_update'] = False
            operator['sna_z_trigger'] = False
            operator['sna_x_trigger'] = False
            operator['sna_y_trigger'] = False
            operator['sna_if_x_true'] = False
            operator['sna_if_y_true'] = False


def sna_in_mode_2C0C4():
    return ('EDIT_MESH'==bpy.context.mode != bpy.context.view_layer.objects.active.type == 'MESH')


def sna_is_face_selected_4D918():
    return ((not sna_in_mode_2C0C4()) or (not (bpy.context.view_layer.objects.active.data.total_vert_sel > 0)))


def sna_link_empty_to_scene_077C5(Object_Name):
    bpy.context.scene.collection.objects.link(object=bpy.data.objects[Object_Name], )
    bpy.data.objects[Object_Name].location = bpy.context.scene.cursor.location


def sna_object_rotation_combine_A460B(Object_Name, Constraint_Name, a, b, c):
    bpy.data.objects[Object_Name].rotation_euler = (a, b, c)
    Empty_Object = Object_Name
    Empty_Constraint = Constraint_Name
    # Get the active object
    active_object = bpy.context.active_object
    # Create the constraint
    constraint = active_object.constraints.new(type='CHILD_OF')
    constraint.name = Empty_Constraint if 'Child Of' in active_object.constraints else Empty_Constraint
    # Set the target object for the constraint
    constraint.target = bpy.data.objects[Empty_Object]
    bpy.context.view_layer.update()


def sna_invert_axis_35593(Axis):
    sna_save_cursor_location__rotation_438BE()
    sna_save_object_location_3F045()
    # Save the current mode
    saved_mode = bpy.context.object.mode
    # Switch to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # Set origin to center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    bpy.ops.transform.rotate(value=sna_func_7052F_270D3(), orient_axis=Axis, orient_type='GLOBAL')
    sna_cursor_to_object_saved_location_FA0D9()
    # Origin to cursor
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    sna_return_cursor_location__rotation_08E90()
    # Switch back to the saved mode
    bpy.ops.object.mode_set(mode=saved_mode)


def sna_object_rotation_split_vector_EBB56(Object_Name):
    return [bpy.data.objects[Object_Name].rotation_euler[0], bpy.data.objects[Object_Name].rotation_euler[1], bpy.data.objects[Object_Name].rotation_euler[2]]


def sna_combine_2__operator_64983(Object_Name):
    # Cursor rotation to face
    scene = bpy.context.scene
    bpy.ops.transform.create_orientation(use=False)
    slot = scene.transform_orientation_slots[0]

    def get_orientation_list(slot):
        try: slot.type = ""
        except Exception as inst:
            s = str(inst)
            s = s[50:]
            return eval(s)
    slots = get_orientation_list(slot)
    old_type = slot.type
    slot.type = slots[-1]
    mat4x4 = slot.custom_orientation.matrix.to_4x4()
    loc, rot, sca = mat4x4.decompose()
    print(loc)
    print(rot)
    cursor = scene.cursor
    old_mode = cursor.rotation_mode
    cursor.rotation_mode = 'QUATERNION'
    scene.cursor.rotation_quaternion = rot
    cursor.rotation_mode = old_mode
    bpy.ops.transform.delete_orientation()
    slot.type = old_type
    # Switch to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    sna_add_empty_8A33C(Object_Name)


def sna_combine_1__operator_24E3C():
    sna_save_cursor_location__rotation_438BE()
    depsgraph_update['sna_depsgraph_update'] = False


def sna_combine_3__operator_A5F95(Object_Name):
    sna_remove_object_ECF92(Object_Name)
    sna_return_cursor_location__rotation_08E90()
    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    depsgraph_update['sna_depsgraph_update'] = True


class SNA_OT_Z__Off_B57B8(bpy.types.Operator):
    bl_idname = "sna.z__off_b57b8"
    bl_label = "Z - OFF"
    bl_description = "Align selected face along the z-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        operator['sna_z_trigger'] = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_X__Off_501D5(bpy.types.Operator):
    bl_idname = "sna.x__off_501d5"
    bl_label = "X - OFF"
    bl_description = "Align selected face along the x-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        operator['sna_x_trigger'] = False
        operator['sna_if_x_true'] = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_X__On_5796E(bpy.types.Operator):
    bl_idname = "sna.x__on_5796e"
    bl_label = "X - ON"
    bl_description = "Align selected face along the x-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not sna_is_face_selected_4D918()

    def execute(self, context):
        sna_combine_1__operator_24E3C()
        operator['sna_x_trigger'] = True
        operator['sna_if_x_true'] = True
        sna_combine_2__operator_64983('PA_X_Axis_Store_Object')
        bpy.context.view_layer.update()
        Empty_Rotation = 'PA_X_Axis_Store_Object'
        import math
        # Get the object named "gabo"
        obj = bpy.data.objects.get(Empty_Rotation)
        if obj is not None:
            # Create a rotation matrix
            rotation_matrix = mathutils.Matrix.Rotation(math.radians(-90), 4, 'Y')
            # Rotate the object's local orientation
            obj.matrix_local = obj.matrix_local @ rotation_matrix
        operator['sna_x_empty_rot_x'] = sna_object_rotation_split_vector_EBB56('PA_X_Axis_Store_Object')[0]
        operator['sna_x_empty_rot_y'] = sna_object_rotation_split_vector_EBB56('PA_X_Axis_Store_Object')[1]
        operator['sna_x_empty_rot_z'] = sna_object_rotation_split_vector_EBB56('PA_X_Axis_Store_Object')[2]
        sna_combine_3__operator_A5F95('PA_X_Axis_Store_Object')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Y__Off_Af3C8(bpy.types.Operator):
    bl_idname = "sna.y__off_af3c8"
    bl_label = "Y - OFF"
    bl_description = "Align selected face along the y-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        operator['sna_y_trigger'] = False
        operator['sna_if_y_true'] = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Y__On_B9C47(bpy.types.Operator):
    bl_idname = "sna.y__on_b9c47"
    bl_label = "Y - ON"
    bl_description = "Align selected face along the y-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not sna_is_face_selected_4D918()

    def execute(self, context):
        sna_combine_1__operator_24E3C()
        operator['sna_y_trigger'] = True
        operator['sna_if_y_true'] = True
        sna_combine_2__operator_64983('PA_Y_Axis_Store_Object')
        bpy.context.view_layer.update()
        Empty_Rotation = 'PA_Y_Axis_Store_Object'
        import math
        # Get the object named "gabo"
        obj = bpy.data.objects.get(Empty_Rotation)
        if obj is not None:
            # Create a rotation matrix
            rotation_matrix = mathutils.Matrix.Rotation(math.radians(-90), 4, 'Y')
            # Rotate the object's local orientation
            obj.matrix_local = obj.matrix_local @ rotation_matrix
        operator['sna_y_empty_rot_x'] = sna_object_rotation_split_vector_EBB56('PA_Y_Axis_Store_Object')[0]
        operator['sna_y_empty_rot_y'] = sna_object_rotation_split_vector_EBB56('PA_Y_Axis_Store_Object')[1]
        operator['sna_y_empty_rot_z'] = sna_object_rotation_split_vector_EBB56('PA_Y_Axis_Store_Object')[2]
        sna_combine_3__operator_A5F95('PA_Y_Axis_Store_Object')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Z__On_E1233(bpy.types.Operator):
    bl_idname = "sna.z__on_e1233"
    bl_label = "Z - ON"
    bl_description = "Align selected face along the z-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not sna_is_face_selected_4D918()

    def execute(self, context):
        sna_combine_1__operator_24E3C()
        operator['sna_z_trigger'] = True
        sna_combine_2__operator_64983('PA_Z_Axis_Store_Object')
        operator['sna_z_empty_rot_x'] = sna_object_rotation_split_vector_EBB56('PA_Z_Axis_Store_Object')[0]
        operator['sna_z_empty_rot_y'] = sna_object_rotation_split_vector_EBB56('PA_Z_Axis_Store_Object')[1]
        operator['sna_z_empty_rot_z'] = sna_object_rotation_split_vector_EBB56('PA_Z_Axis_Store_Object')[2]
        sna_combine_3__operator_A5F95('PA_Z_Axis_Store_Object')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Invert_Z_2F7Af(bpy.types.Operator):
    bl_idname = "sna.invert_z_2f7af"
    bl_label = "Invert Z"
    bl_description = "Invert the object's rotation around the z-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_invert_axis_35593('X')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Invert_X_3B1Ab(bpy.types.Operator):
    bl_idname = "sna.invert_x_3b1ab"
    bl_label = "Invert X"
    bl_description = "Invert the object's rotation around the x-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_invert_axis_35593('Z')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Invert_Y_7255A(bpy.types.Operator):
    bl_idname = "sna.invert_y_7255a"
    bl_label = "Invert Y"
    bl_description = "Invert the object's rotation around the y-axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_invert_axis_35593('Z')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Apply_Origin_395Fc(bpy.types.Operator):
    bl_idname = "sna.apply_origin_395fc"
    bl_label = "Apply Origin"
    bl_description = "Set origin to center of mass"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_transforms_8D074(True, False, False)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Move_To_Center_76Ceb(bpy.types.Operator):
    bl_idname = "sna.move_to_center_76ceb"
    bl_label = "Move to Center"
    bl_description = "Move the object to the center of 3d space"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_transforms_8D074(False, False, True)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Apply_Rotation_B6323(bpy.types.Operator):
    bl_idname = "sna.apply_rotation_b6323"
    bl_label = "Apply Rotation"
    bl_description = "Apply rotation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active:
            sna_transforms_8D074(False, True, False)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_transforms_8D074(Apply_Origin, Apply_Rotation, Move_to_Center):
    Var1 = Apply_Origin
    Var2 = Apply_Rotation
    Var3 = Move_to_Center
    # Save the current mode
    saved_mode = bpy.context.object.mode
    # Switch to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # set up the variables
    Apply_Origin = Var1
    Apply_Rotation = Var2
    Move_to_Center = Var3
    # Set origin to center of mass
    if Apply_Origin:
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    # Apply rotation
    if Apply_Rotation:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    # Move the object to the center of 3d space
    if Move_to_Center:
        bpy.ops.object.location_clear()
    # Switch back to the saved mode
    bpy.ops.object.mode_set(mode=saved_mode)


class SNA_PT_PRO_ALIGNER_260B4(bpy.types.Panel):
    bl_label = 'Pro Aligner'
    bl_idname = 'SNA_PT_PRO_ALIGNER_260B4'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Pro Aligner'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        col_F9049 = layout.column(heading='', align=True)
        col_F9049.alert = False
        col_F9049.enabled = True
        col_F9049.active = True
        col_F9049.use_property_split = False
        col_F9049.use_property_decorate = False
        col_F9049.scale_x = 1.0
        col_F9049.scale_y = 1.0
        col_F9049.alignment = 'Expand'.upper()
        if not True: col_F9049.operator_context = "EXEC_DEFAULT"
        col_7DCE6 = col_F9049.column(heading='', align=True)
        col_7DCE6.alert = False
        col_7DCE6.enabled = sna_in_mode_2C0C4()
        col_7DCE6.active = sna_in_mode_2C0C4()
        col_7DCE6.use_property_split = False
        col_7DCE6.use_property_decorate = False
        col_7DCE6.scale_x = 1.0
        col_7DCE6.scale_y = 1.0
        col_7DCE6.alignment = 'Expand'.upper()
        if not True: col_7DCE6.operator_context = "EXEC_DEFAULT"
        row_A9CD3 = col_7DCE6.row(heading='', align=False)
        row_A9CD3.alert = False
        row_A9CD3.enabled = True
        row_A9CD3.active = True
        row_A9CD3.use_property_split = False
        row_A9CD3.use_property_decorate = False
        row_A9CD3.scale_x = 1.0
        row_A9CD3.scale_y = 1.0
        row_A9CD3.alignment = 'Center'.upper()
        if not True: row_A9CD3.operator_context = "EXEC_DEFAULT"
        row_A9CD3.label(text='Align', icon_value=0)
        col_7DCE6.separator(factor=1.0)
        col_D937B = col_7DCE6.column(heading='', align=True)
        col_D937B.alert = False
        col_D937B.enabled = True
        col_D937B.active = True
        col_D937B.use_property_split = False
        col_D937B.use_property_decorate = False
        col_D937B.scale_x = 1.0
        col_D937B.scale_y = 1.2000000476837158
        col_D937B.alignment = 'Expand'.upper()
        if not True: col_D937B.operator_context = "EXEC_DEFAULT"
        if operator['sna_z_trigger']:
            op = col_D937B.operator('sna.z__off_b57b8', text='Z', icon_value=0, emboss=True, depress=True)
        else:
            op = col_D937B.operator('sna.z__on_e1233', text='Z', icon_value=0, emboss=True, depress=False)
        row_015A3 = col_7DCE6.row(heading='', align=True)
        row_015A3.alert = False
        row_015A3.enabled = True
        row_015A3.active = True
        row_015A3.use_property_split = False
        row_015A3.use_property_decorate = False
        row_015A3.scale_x = 1.600000023841858
        row_015A3.scale_y = 1.0
        row_015A3.alignment = 'Center'.upper()
        if not False: row_015A3.operator_context = "EXEC_DEFAULT"
        row_F6C98 = row_015A3.row(heading='', align=True)
        row_F6C98.alert = False
        row_F6C98.enabled = (not operator['sna_if_y_true'])
        row_F6C98.active = (not operator['sna_if_y_true'])
        row_F6C98.use_property_split = False
        row_F6C98.use_property_decorate = False
        row_F6C98.scale_x = 2.0
        row_F6C98.scale_y = 1.2000000476837158
        row_F6C98.alignment = 'Center'.upper()
        if not False: row_F6C98.operator_context = "EXEC_DEFAULT"
        if operator['sna_x_trigger']:
            op = row_F6C98.operator('sna.x__off_501d5', text='X', icon_value=0, emboss=True, depress=True)
        else:
            op = row_F6C98.operator('sna.x__on_5796e', text='X', icon_value=0, emboss=True, depress=False)
        row_81F22 = row_015A3.row(heading='', align=True)
        row_81F22.alert = False
        row_81F22.enabled = (not operator['sna_if_x_true'])
        row_81F22.active = (not operator['sna_if_x_true'])
        row_81F22.use_property_split = False
        row_81F22.use_property_decorate = False
        row_81F22.scale_x = 2.0
        row_81F22.scale_y = 1.2000000476837158
        row_81F22.alignment = 'Center'.upper()
        if not False: row_81F22.operator_context = "EXEC_DEFAULT"
        if operator['sna_y_trigger']:
            op = row_81F22.operator('sna.y__off_af3c8', text='Y', icon_value=0, emboss=True, depress=True)
        else:
            op = row_81F22.operator('sna.y__on_b9c47', text='Y', icon_value=0, emboss=True, depress=False)
        col_300E9 = col_7DCE6.column(heading='', align=True)
        col_300E9.alert = False
        col_300E9.enabled = sna_check_triggers_9CA3E()[0]
        col_300E9.active = sna_check_triggers_9CA3E()[0]
        col_300E9.use_property_split = True
        col_300E9.use_property_decorate = True
        col_300E9.scale_x = 1.0
        col_300E9.scale_y = 2.5
        col_300E9.alignment = 'Expand'.upper()
        if not True: col_300E9.operator_context = "EXEC_DEFAULT"
        op = col_300E9.operator('sna.align_3ea9b', text='Align', icon_value=0, emboss=True, depress=False)
        col_F9049.separator(factor=1.0)
        row_C3033 = col_F9049.row(heading='', align=False)
        row_C3033.alert = False
        row_C3033.enabled = sna_check_triggers_9CA3E()[1]
        row_C3033.active = sna_check_triggers_9CA3E()[1]
        row_C3033.use_property_split = False
        row_C3033.use_property_decorate = False
        row_C3033.scale_x = 1.0
        row_C3033.scale_y = 1.0
        row_C3033.alignment = 'Center'.upper()
        if not True: row_C3033.operator_context = "EXEC_DEFAULT"
        row_C3033.label(text='Invert Axis', icon_value=0)
        col_F9049.separator(factor=1.0)
        col_88ACB = col_F9049.column(heading='', align=True)
        col_88ACB.alert = False
        col_88ACB.enabled = sna_check_triggers_9CA3E()[1]
        col_88ACB.active = sna_check_triggers_9CA3E()[1]
        col_88ACB.use_property_split = False
        col_88ACB.use_property_decorate = False
        col_88ACB.scale_x = 1.0
        col_88ACB.scale_y = 1.2000000476837158
        col_88ACB.alignment = 'Expand'.upper()
        if not True: col_88ACB.operator_context = "EXEC_DEFAULT"
        row_6D559 = col_88ACB.row(heading='', align=True)
        row_6D559.alert = False
        row_6D559.enabled = True
        row_6D559.active = True
        row_6D559.use_property_split = False
        row_6D559.use_property_decorate = False
        row_6D559.scale_x = 1.600000023841858
        row_6D559.scale_y = 1.0
        row_6D559.alignment = 'Center'.upper()
        if not False: row_6D559.operator_context = "EXEC_DEFAULT"
        op = row_6D559.operator('sna.invert_z_2f7af', text='Z', icon_value=0, emboss=True, depress=False)
        op = row_6D559.operator('sna.invert_x_3b1ab', text='X', icon_value=0, emboss=True, depress=False)
        op = row_6D559.operator('sna.invert_y_7255a', text='Y', icon_value=0, emboss=True, depress=False)
        col_F9049.separator(factor=1.0)
        row_51678 = col_F9049.row(heading='', align=False)
        row_51678.alert = False
        row_51678.enabled = sna_check_triggers_9CA3E()[1]
        row_51678.active = sna_check_triggers_9CA3E()[1]
        row_51678.use_property_split = False
        row_51678.use_property_decorate = False
        row_51678.scale_x = 1.0
        row_51678.scale_y = 1.0
        row_51678.alignment = 'Center'.upper()
        if not True: row_51678.operator_context = "EXEC_DEFAULT"
        row_51678.label(text='Transforms', icon_value=0)
        col_F9049.separator(factor=1.0)
        col_1AFD3 = col_F9049.column(heading='', align=True)
        col_1AFD3.alert = False
        col_1AFD3.enabled = sna_check_triggers_9CA3E()[1]
        col_1AFD3.active = sna_check_triggers_9CA3E()[1]
        col_1AFD3.use_property_split = False
        col_1AFD3.use_property_decorate = False
        col_1AFD3.scale_x = 1.0
        col_1AFD3.scale_y = 1.5
        col_1AFD3.alignment = 'Expand'.upper()
        if not True: col_1AFD3.operator_context = "EXEC_DEFAULT"
        op = col_1AFD3.operator('sna.apply_origin_395fc', text='Apply Origin', icon_value=0, emboss=True, depress=False)
        op = col_1AFD3.operator('sna.apply_rotation_b6323', text='Apply Rotation', icon_value=0, emboss=True, depress=False)
        op = col_1AFD3.operator('sna.move_to_center_76ceb', text='Move to Center', icon_value=0, emboss=True, depress=False)


def sna_remove_object_ECF92(Object_Name):
    bpy.data.objects.remove(object=bpy.data.objects[Object_Name], )


def sna_remove_object_and_constraint_2F139(Object_Name, Constraint_Name):
    if property_exists("bpy.data.objects[Object_Name]", globals(), locals()):
        sna_remove_object_ECF92(Object_Name)
    if property_exists("bpy.context.view_layer.objects.active.constraints[Constraint_Name]", globals(), locals()):
        bpy.context.view_layer.objects.active.constraints.remove(constraint=bpy.context.view_layer.objects.active.constraints[Constraint_Name], )


def sna_return_cursor_location__rotation_08E90():
    bpy.context.scene.cursor.location = (save_cursor_location__rotation['sna_cursor_loc_x'], save_cursor_location__rotation['sna_cursor_loc_y'], save_cursor_location__rotation['sna_cursor_loc_z'])
    bpy.context.scene.cursor.rotation_euler = (save_cursor_location__rotation['sna_cursor_rot_x'], save_cursor_location__rotation['sna_cursor_rot_y'], save_cursor_location__rotation['sna_cursor_rot_z'])


def sna_save_cursor_location__rotation_438BE():
    save_cursor_location__rotation['sna_cursor_loc_x'] = bpy.context.scene.cursor.location[0]
    save_cursor_location__rotation['sna_cursor_loc_y'] = bpy.context.scene.cursor.location[1]
    save_cursor_location__rotation['sna_cursor_loc_z'] = bpy.context.scene.cursor.location[2]
    save_cursor_location__rotation['sna_cursor_rot_x'] = bpy.context.scene.cursor.rotation_euler[0]
    save_cursor_location__rotation['sna_cursor_rot_y'] = bpy.context.scene.cursor.rotation_euler[1]
    save_cursor_location__rotation['sna_cursor_rot_z'] = bpy.context.scene.cursor.rotation_euler[2]


def sna_save_object_location_3F045():
    save_object_location['sna_object_x'] = bpy.context.view_layer.objects.active.location[0]
    save_object_location['sna_object_y'] = bpy.context.view_layer.objects.active.location[1]
    save_object_location['sna_object_z'] = bpy.context.view_layer.objects.active.location[2]


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(SNA_OT_Align_3Ea9B)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_28632)
    bpy.utils.register_class(SNA_OT_Z__Off_B57B8)
    bpy.utils.register_class(SNA_OT_X__Off_501D5)
    bpy.utils.register_class(SNA_OT_X__On_5796E)
    bpy.utils.register_class(SNA_OT_Y__Off_Af3C8)
    bpy.utils.register_class(SNA_OT_Y__On_B9C47)
    bpy.utils.register_class(SNA_OT_Z__On_E1233)
    bpy.utils.register_class(SNA_OT_Invert_Z_2F7Af)
    bpy.utils.register_class(SNA_OT_Invert_X_3B1Ab)
    bpy.utils.register_class(SNA_OT_Invert_Y_7255A)
    bpy.utils.register_class(SNA_OT_Apply_Origin_395Fc)
    bpy.utils.register_class(SNA_OT_Move_To_Center_76Ceb)
    bpy.utils.register_class(SNA_OT_Apply_Rotation_B6323)
    bpy.utils.register_class(SNA_PT_PRO_ALIGNER_260B4)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(SNA_OT_Align_3Ea9B)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_28632)
    bpy.utils.unregister_class(SNA_OT_Z__Off_B57B8)
    bpy.utils.unregister_class(SNA_OT_X__Off_501D5)
    bpy.utils.unregister_class(SNA_OT_X__On_5796E)
    bpy.utils.unregister_class(SNA_OT_Y__Off_Af3C8)
    bpy.utils.unregister_class(SNA_OT_Y__On_B9C47)
    bpy.utils.unregister_class(SNA_OT_Z__On_E1233)
    bpy.utils.unregister_class(SNA_OT_Invert_Z_2F7Af)
    bpy.utils.unregister_class(SNA_OT_Invert_X_3B1Ab)
    bpy.utils.unregister_class(SNA_OT_Invert_Y_7255A)
    bpy.utils.unregister_class(SNA_OT_Apply_Origin_395Fc)
    bpy.utils.unregister_class(SNA_OT_Move_To_Center_76Ceb)
    bpy.utils.unregister_class(SNA_OT_Apply_Rotation_B6323)
    bpy.utils.unregister_class(SNA_PT_PRO_ALIGNER_260B4)
