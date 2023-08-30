import bpy
import bmesh
from bpy.types import Panel, Operator
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty
from math import degrees, radians
from mathutils import Vector, Matrix
from ._utils import set_active_collection, flattened
from . import ke_cursor_fit, ke_frame_view, ke_quick_origin_move, ke_mouse_side_of_active, ke_view_align
from ._prefs import pcoll
# from bpy.app.handlers import persistent


#
# MODULE UI
#
class UISelectionModule(Panel):
    bl_idname = "UI_PT_M_SELECTION"
    bl_label = "Select & Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        split = row.split(factor=0.78, align=True)
        # subrow1 = split.row(align=True)
        split.operator("view3d.cursor_fit_selected_and_orient", text="Cursor Fit & Align")
        # subrow2 = split.row(align=True)
        if k.cursorfit:
            split.prop(k, "cursorfit", text="", icon="CHECKMARK", toggle=True)
        else:
            split.prop(k, "cursorfit", text="", icon_value=pcoll['kekit']['ke_uncheck'].icon_id, toggle=True)

        row = col.row(align=True)
        row.operator("view3d.ke_vp_step_rotate", text="StepRotate 90").rot = 90
        row.operator("view3d.ke_vp_step_rotate", text="StepRotate -90").rot = -90

        col.label(text="Align View To")
        row = col.row(align=True)
        row.operator('view3d.ke_view_align_toggle', text="Cursor").mode = 'CURSOR'
        row.operator('view3d.ke_view_align_toggle', text="Selected").mode = 'SELECTION'
        row.operator('view3d.ke_view_align_snap', text="OrthoSnap").contextual = False

        row = col.row(align=True)
        row.operator("screen.ke_frame_view", text="Frame All or Selected")
        split = row.row(align=True)
        split.alignment = "RIGHT"
        if k.frame_mo:
            split.prop(k, "frame_mo", text="", icon="CHECKMARK", toggle=True)
        else:
            split.prop(k, "frame_mo", text="", icon_value=pcoll['kekit']['ke_uncheck'].icon_id, toggle=True)

        col.label(text="Align Origin(s) To")
        row = col.row(align=True)
        row.operator('view3d.ke_origin_to_cursor', text="Cursor")
        row.operator('view3d.align_origin_to_selected', text="Selection")
        row.operator('view3d.origin_to_selected', text="Sel.Loc")
        row = col.row(align=True)

        row.operator("view3d.ke_quick_origin_move", icon="TRANSFORM_ORIGINS").mode = "MOVE"
        split = row.row(align=True)
        split.alignment = "RIGHT"
        split.operator("view3d.ke_quick_origin_move", icon="TRANSFORM_ORIGINS", text="AutoAxis").mode = "AUTOAXIS"

        col.label(text="Align Object(s) To")
        row = col.row(align=True)
        row.operator('view3d.ke_object_to_cursor', text="Cursor")
        row.operator('view3d.ke_align_object_to_active', text="Active Object").align = "BOTH"
        row.operator('view3d.selected_to_origin', text="Origin")
        col.operator('object.ke_bbmatch')

        col.separator(factor=0.5)
        col.operator('object.ke_straighten', icon="CON_ROTLIMIT")
        col.operator('view3d.ke_swap', text="Swap Places", icon="CON_TRANSLIKE")

        col.label(text="Select")
        row = col.row(align=True)
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_ON", text="Lock").mode = "LOCK"
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_ON", text="Lock Unselected").mode = "LOCK_UNSELECTED"
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_OFF", text="Unlock").mode = "UNLOCK"

        col.operator("mesh.ke_select_boundary", text="Select Boundary (+Active)")
        col.operator('view3d.ke_select_invert_linked')
        col.operator('mesh.ke_mouse_side_of_active', icon="MOUSE_MOVE")
        col.operator('view3d.ke_show_in_outliner')
        col.operator('view3d.ke_set_active_collection')
        col.operator('object.ke_select_objects_by_vertselection')


class UISelectByDisplayType(Panel):
    bl_idname = "UI_PT_ke_select_by_display_type"
    bl_label = "Select by Display Type"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_SELECTION"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout = layout.column(align=True)
        layout.prop(context.preferences.addons[__package__].preferences, "sel_type_coll", toggle=True)
        layout.label(text="Select Objects with Display Type:")
        layout.operator('object.ke_select_by_displaytype', text="Textured").dt = "TEXTURED"
        layout.operator('object.ke_select_by_displaytype', text="Solid").dt = "SOLID"
        layout.operator('object.ke_select_by_displaytype', text="Wire").dt = "WIRE"
        layout.operator('object.ke_select_by_displaytype', text="Bounds").dt = "BOUNDS"
        layout.separator(factor=0.5)
        layout.label(text="Specific Bounds Display Type:")
        layout.operator('object.ke_select_by_displaytype', text="Capsule").dt = "CAPSULE"
        layout.operator('object.ke_select_by_displaytype', text="Cone").dt = "CONE"
        layout.operator('object.ke_select_by_displaytype', text="Cylinder").dt = "CYLINDER"
        layout.operator('object.ke_select_by_displaytype', text="Sphere").dt = "SPHERE"
        layout.operator('object.ke_select_by_displaytype', text="Box").dt = "BOX"


#
# MODULE OPERATORS (MISC)
#
class KeCursorClearRot(Operator):
    bl_idname = "view3d.ke_cursor_clear_rot"
    bl_label = "Clear Cursor Rotation"
    bl_description = "Clear the cursor's rotation (only)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        c = context.scene.cursor
        if c.rotation_mode == "QUATERNION":
            c.rotation_quaternion = 1, 0, 0, 0
        elif c.rotation_mode == "AXIS_ANGLE":
            c.rotation_axis_angle = 0, 0, 1, 0
        else:
            c.rotation_euler = 0, 0, 0

        return {'FINISHED'}


class KeOriginToCursor(Operator):
    bl_idname = "view3d.ke_origin_to_cursor"
    bl_label = "Align Origin To Cursor"
    bl_description = "Aligns selected object(s) origin(s) to Cursor (Rotation,Location or both)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    align: EnumProperty(
        items=[("LOCATION", "Location Only", "", 1),
               ("ROTATION", "Rotation Only", "", 2),
               ("BOTH", "Location & Rotation", "", 3)
               ],
        name="Align",
        default="BOTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "align", expand=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):

        if len(context.selected_objects) == 0:
            return {"CANCELLED"}

        # make sure the cursor euler values are not quaternion converted floating point garbage:
        og_cursor_setting = str(context.scene.cursor.rotation_mode)
        context.scene.cursor.rotation_mode = "XYZ"
        crot = context.scene.cursor.rotation_euler
        crot.x = round(crot.x, 4)
        crot.y = round(crot.y, 4)
        crot.z = round(crot.z, 4)

        if context.object.type == 'MESH':
            if context.object.data.is_editmode:
                bpy.ops.object.mode_set(mode="OBJECT")

        if self.align == "BOTH":
            context.scene.tool_settings.use_transform_data_origin = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
                                        use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                        proportional_size=1, use_proportional_connected=False,
                                        use_proportional_projected=False)
            context.scene.tool_settings.use_transform_data_origin = False

        else:
            cursor = context.scene.cursor
            ogloc = list(cursor.location)

            if self.align == 'LOCATION':
                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.scene.tool_settings.use_transform_data_origin = False

            elif self.align == 'ROTATION':
                obj_loc = context.object.matrix_world.translation.copy()
                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
                                            use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                            proportional_size=1, use_proportional_connected=False,
                                            use_proportional_projected=False)
                cursor.location = obj_loc
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.scene.tool_settings.use_transform_data_origin = False
                cursor.location = ogloc

        bpy.ops.transform.select_orientation(orientation='LOCAL')
        context.scene.cursor.rotation_mode = og_cursor_setting

        return {'FINISHED'}


class KeAlignOriginToSelected(Operator):
    bl_idname = "view3d.align_origin_to_selected"
    bl_label = "Align Origin To Selected Elements"
    bl_description = "Edit Mode: Places origin(s) at element selection (+orientation)\n" \
                     "Object Mode (1 selected): Set Origin to geo Center\n" \
                     "Object Mode (2 selected): Set Origin to 2nd Obj Origin\n"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    invert_z : BoolProperty(default=True, name="Invert Z-Axis", description="Invert Z-Axis in Edit Mode")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        cursor = context.scene.cursor
        ogmode = str(cursor.rotation_mode)
        ogloc = cursor.location.copy()
        ogrot = cursor.rotation_quaternion.copy()

        if context.mode == "EDIT_MESH":
            cursor.rotation_mode = "QUATERNION"
            bpy.ops.view3d.cursor_fit_selected_and_orient()
            if self.invert_z:
                cursor.rotation_mode = "XYZ"
                cursor.rotation_euler.rotate_axis('Y', radians(180.0))
            bpy.ops.view3d.ke_origin_to_cursor(align="BOTH")
            bpy.ops.transform.select_orientation(orientation='LOCAL')
            context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        else:
            target_obj = None
            sel_obj = [o for o in context.selected_objects]
            if sel_obj:
                sel_obj = [o for o in sel_obj]
            if context.active_object:
                target_obj = context.active_object
            if target_obj is None and sel_obj:
                target_obj = sel_obj[-1]
            if not target_obj:
                return {'CANCELLED'}

            sel_obj = [o for o in sel_obj if o != target_obj]

            # Center to mesh if only one object selected and active
            if not sel_obj and target_obj:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            else:
                cursor.rotation_mode = "XYZ"
                cursor.location = target_obj.matrix_world.translation
                cursor.rotation_euler = target_obj.rotation_euler
                bpy.ops.object.select_all(action='DESELECT')

                for o in sel_obj:
                    o.select_set(True)
                    bpy.ops.view3d.ke_origin_to_cursor(align="BOTH")
                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)

        cursor.location = ogloc
        cursor.rotation_mode = "QUATERNION"
        cursor.rotation_quaternion = ogrot
        cursor.rotation_mode = ogmode

        return {"FINISHED"}


class KeOriginToSelected(Operator):
    bl_idname = "view3d.origin_to_selected"
    bl_label = "Origin To Selected Elements"
    bl_description = "Places origin(s) at element selection average\n" \
                     "(Location Only, Apply rotation for world rotation)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        cursor = context.scene.cursor
        rot = cursor.rotation_quaternion.copy()
        loc = cursor.location.copy()
        ogmode = str(cursor.rotation_mode)
        editmode = False if context.mode != "EDIT_MESH" else True
        print(editmode)
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                context = context.copy()
                context['area'] = area
                context['region'] = area.regions[-1]

            if not editmode:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            else:
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                cursor.location = loc
                cursor.rotation_mode = "QUATERNION"
                cursor.rotation_quaternion = rot
                cursor.rotation_mode = ogmode
                break

        return {'FINISHED'}


class KeObjectToCursor(Operator):
    bl_idname = "view3d.ke_object_to_cursor"
    bl_label = "Align Object To Cursor"
    bl_description = "Aligns selected object(s) to Cursor (Rotation & Location)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):
        cursor = context.scene.cursor
        c_loc = cursor.location
        c_rot = cursor.rotation_euler
        for obj in context.selected_objects:
            obj.location = c_loc
            og_rot_mode = str(obj.rotation_mode)
            obj.rotation_mode = "XYZ"
            obj.rotation_euler = c_rot
            obj.rotation_mode = og_rot_mode
            crot = obj.rotation_euler
            crot.x = round(crot.x, 4)
            crot.y = round(crot.y, 4)
            crot.z = round(crot.z, 4)
        return {'FINISHED'}


class KeAlignObjectToActive(Operator):
    bl_idname = "view3d.ke_align_object_to_active"
    bl_label = "Align Object(s) To Active"
    bl_description = "Align selected object(s) to the Active Objects Transforms. (You may want to apply scale)"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    align: EnumProperty(
        items=[("LOCATION", "Location", "", 1),
               ("ROTATION", "Rotation", "", 2),
               ("BOTH", "Location & Rotation", "", 3)],
        name="Align", default="BOTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "align", expand=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):
        target_obj = None
        sel_obj = [o for o in context.selected_objects]
        if context.active_object:
            target_obj = context.active_object
        if target_obj is None and sel_obj:
            target_obj = sel_obj[-1]
        if not target_obj or len(sel_obj) < 2:
            print("Insufficent selection: Need at least 2 objects.")
            return {'CANCELLED'}

        sel_obj = [o for o in sel_obj if o != target_obj]

        for o in sel_obj:

            if self.align == "LOCATION":
                o.matrix_world.translation = target_obj.matrix_world.translation
            elif self.align == "ROTATION":
                og_pos = o.matrix_world.translation.copy()
                o.matrix_world = target_obj.matrix_world
                o.matrix_world.translation = og_pos
            elif self.align == "BOTH":
                o.matrix_world = target_obj.matrix_world

        target_obj.select_set(False)
        context.view_layer.objects.active = sel_obj[0]

        return {"FINISHED"}


class KeSelectedToOrigin(Operator):
    bl_idname = "view3d.selected_to_origin"
    bl_label = "Selection to Origin"
    bl_description = "Places Selected Object Geo or Element Mode Selection at objects Origin (Location only)\n" \
                     "Object Mode function uses Set Origin - All options available in redo panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    o_type : EnumProperty(
        items=[("GEOMETRY_ORIGIN", "Geometry to Origin", "", 1),
               ("ORIGIN_GEOMETRY", "Origin to Geometry", "", 2),
               ("ORIGIN_CURSOR", "Origin to 3D Cursor", "", 3),
               ("ORIGIN_CENTER_OF_MASS", "Origin to Center of Mass (Surface)", "", 4),
               ("ORIGIN_CENTER_OF_VOLUME", "Origin to Center of Mass (Volume)", "", 5)
               ],
        name="Type",
        default="GEOMETRY_ORIGIN")

    o_center : EnumProperty(
        items=[("MEDIAN", "Median Center", "", 1),
               ("BOUNDS", "Bounds Center", "", 2)
               ],
        name="Center",
        default="MEDIAN")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            self.report({'INFO'}, "Selection Error: No object(s) selected?")
            return {"CANCELLED"}

        og_mode = str(context.mode)

        if og_mode != "OBJECT":
            if self.o_type == "GEOMETRY_ORIGIN":
                c = context.scene.cursor
                og_cursor_loc = Vector(c.location)
                og_cursor_mode = str(c.rotation_mode)
                c.rotation_mode = "XYZ"
                og_cursor_rot = Vector(c.rotation_euler)
                c.rotation_euler = 0, 0, 0

                bpy.ops.object.mode_set(mode='OBJECT')

                for o in sel_obj:
                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)
                    context.view_layer.objects.active = o
                    bpy.ops.object.mode_set(mode='EDIT')
                    if og_mode == "OBJECT":
                        bpy.ops.mesh.select_all(action="SELECT")
                    c.location = o.location
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                    o.select_set(False)
                    bpy.ops.object.mode_set(mode='OBJECT')

                c.location = og_cursor_loc
                c.rotation_euler = og_cursor_rot
                c.rotation_mode = og_cursor_mode

                for o in sel_obj:
                    o.select_set(True)

                bpy.ops.object.mode_set(mode='EDIT')
            else:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.origin_set(type=self.o_type, center=self.o_center)
        else:
            bpy.ops.object.origin_set(type=self.o_type, center=self.o_center)

        return {'FINISHED'}


class KeBBMatch(Operator):
    bl_idname = "object.ke_bbmatch"
    bl_label = "Match Active Bounding Box"
    bl_description = "Scales selected object(s) to last selected object bounding box (along axis chosen in redo)\n" \
                     "Make sure origin(s) is properly placed beforehand\nScale will be auto-applied"
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[("UNIT", "Longest Axis (Unit)", "", 1),
               ("ALL", "All Axis", "", 2),
               ("X", "X Only", "", 3),
               ("Y", "Y Only", "", 4),
               ("Z", "Z Only", "", 5),
               ],
        name="Scaling", default="UNIT",
        description="Choose which Bounding Box Axis to scale with")

    match_loc : BoolProperty(name="Location", default=False)
    match_rot : BoolProperty(name="Rotation", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "mode", expand=True)
        layout.separator(factor=0.5)
        row = layout.row()
        row.prop(self, "match_loc", toggle=True)
        row.prop(self, "match_rot", toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        if not len(sel_objects) >= 2:
            self.report({"INFO"}, "Invalid Selection (2+ required)")
            return {"CANCELLED"}

        src_obj = context.object
        src_bb = src_obj.dimensions

        if self.mode == "UNIT":
            v = sorted(src_bb)[-1]
            src_bb = [v, v, v]
        elif self.mode == "X":
            v = src_bb[0]
            src_bb = [v, 1, 1]
        elif self.mode == "Y":
            v = src_bb[1]
            src_bb = [1, v, 1]
        elif self.mode == "Z":
            v = src_bb[2]
            src_bb = [1, 1, v]

        target_objects = [o for o in sel_objects if o != src_obj]

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False, )

        for o in target_objects:

            bb = o.dimensions
            if self.mode == "UNIT":
                v = sorted(bb)[-1]
                bb = [v, v, v]
            elif self.mode == "X":
                v = bb[0]
                bb = [v, 1, 1]
            elif self.mode == "Y":
                v = bb[1]
                bb = [1, v, 1]
            elif self.mode == "Z":
                v = bb[2]
                bb = [1, 1, v]

            o.scale[0] *= (src_bb[0] / bb[0])
            o.scale[1] *= (src_bb[1] / bb[1])
            o.scale[2] *= (src_bb[2] / bb[2])

            if self.match_loc:
                o.location = src_obj.location
            if self.match_rot:
                o.rotation_euler = src_obj.rotation_euler

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

        return {"FINISHED"}


class KeStraighten(Operator):
    bl_idname = "object.ke_straighten"
    bl_label = "Straighten"
    bl_description = "Snaps selected object(s) rotation to nearest set degree"
    bl_options = {'REGISTER', 'UNDO'}

    deg: FloatProperty(description="Degree Snap", default=90, min=0, max=90)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        for o in context.selected_objects:
            r = [radians((round(degrees(i) / self.deg) * self.deg)) for i in o.rotation_euler]
            o.rotation_euler[0] = r[0]
            o.rotation_euler[1] = r[1]
            o.rotation_euler[2] = r[2]
        return {"FINISHED"}


class KeSwap(Operator):
    bl_idname = "view3d.ke_swap"
    bl_label = "Swap Places"
    bl_description = "Swap places (transforms) for two objects. loc, rot & scale. (apply scale to avoid)"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):
        # CHECK SELECTION
        sel_obj = [o for o in context.selected_objects]
        if len(sel_obj) != 2:
            print("Incorrect Selection: Select 2 objects.")
            return {'CANCELLED'}
        # SWAP
        obj1 = sel_obj[0]
        obj2 = sel_obj[1]
        obj1_swap = obj2.matrix_world.copy()
        obj2_swap = obj1.matrix_world.copy()
        obj1.matrix_world = obj1_swap
        obj2.matrix_world = obj2_swap
        return {"FINISHED"}


class KeLock(Operator):
    bl_idname = "view3d.ke_lock"
    bl_label = "Lock & Unlock"

    mode : EnumProperty(
        items=[("LOCK", "Lock", "", 1),
               ("LOCK_UNSELECTED", "Lock Unselected", "", 2),
               ("UNLOCK", "Unlock", "", 3)
               ],
        name="Lock & Unlock",
        options={'HIDDEN'},
        default="LOCK")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "LOCK":
            return "Lock: Disable Selection for selected object(s)\nSee selection status in Outliner"
        if properties.mode == "LOCK_UNSELECTED":
            return "Lock Unselected: Disable Selection for all unselected object(s)\nSee selection status in Outliner"
        else:
            return "Unlock: Enables Selection for -all- objects"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):

        if self.mode == "LOCK":
            for obj in context.selected_objects:
                obj.hide_select = True

        elif self.mode == "LOCK_UNSELECTED":
            sel = context.selected_objects[:]
            for obj in context.scene.objects:
                if obj not in sel:
                    obj.hide_select = True

        elif self.mode == "UNLOCK":
            for obj in context.scene.objects:
                obj.hide_select = False

        return {'FINISHED'}


class KeSelectBoundary(Operator):
    bl_idname = "mesh.ke_select_boundary"
    bl_label = "select boundary(+active)"
    bl_description = "Select Boundary edges & sets one edge active\n" \
                     "Run again on a selected boundary to toggle to inner region selection\n" \
                     "Nothing selected = Selects all -border- edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        og_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        if obj is None:
            obj = context.object

        bm = bmesh.from_edit_mesh(obj.data)

        sel_verts = [v for v in bm.verts if v.select]
        og_edges = [e for e in bm.edges if e.select]

        if len(sel_verts) == 0:
            bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.region_to_loop()

        sel_edges = [e for e in bm.edges if e.select]

        if sel_edges:
            sel_check = [e for e in bm.edges if e.select]
            toggle = set(og_edges) == set(sel_check)

            if toggle:
                bpy.ops.mesh.loop_to_region()

            bm.select_history.clear()
            bm.select_history.add(sel_edges[0])
        else:
            context.tool_settings.mesh_select_mode = og_mode

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


class KeSelectInvertLinked(Operator):
    bl_idname = "view3d.ke_select_invert_linked"
    bl_label = "Select Invert Linked"
    bl_description = "Inverts selection only on connected/linked mesh geo\n" \
                     "If selection is already fully linked, vanilla invert is used"
    bl_options = {'REGISTER', 'UNDO'}

    invert_type: EnumProperty(
        items=[("SAME", "Same As Selected Only", "", 1),
               ("ALL", "All types of Objects", "", 2),
               ],
        name="Type", description="Invert by Type or Invert All (- filter options below)",
        default="SAME")
    same_disp: BoolProperty(name="Same DisplayType Only", default=True,
                            description="JFYI: Lights are the same display-type as mesh ('textured') by default")
    same_coll: BoolProperty(name="Same Collection Only", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        if context.mode == "OBJECT":
            layout = self.layout
            layout.use_property_split = True
            layout.prop(self, "invert_type", expand=True)
            layout.prop(self, "same_coll")
            layout.prop(self, "same_disp")
            layout.separator()

    def execute(self, context):
        objmode = context.mode

        if context.object.type == 'MESH':
            if context.object.data.is_editmode:
                sel_mode = context.tool_settings.mesh_select_mode[:]
                me = context.object.data
                bm = bmesh.from_edit_mesh(me)
                og_sel = check_selection(bm, sel_mode)
                if og_sel:
                    bpy.ops.mesh.select_linked()
                    re_sel = check_selection(bm, sel_mode)

                    if len(re_sel) == len(og_sel):
                        bpy.ops.mesh.select_all(action='INVERT')
                    else:
                        for v in og_sel:
                            v.select = False
                bm.select_flush_mode()
                bmesh.update_edit_mesh(me)
                objmode = ""
            else:
                objmode = "OBJECT"

        if objmode == 'OBJECT':
            inv_objects = []
            # BASE LIST
            if self.invert_type == "ALL":
                inv_objects = [o for o in context.scene.objects]
            elif self.invert_type == "SAME":
                inv_objects = [o for o in context.scene.objects if o.type == context.object.type]
            # FILTERS
            if self.same_coll:
                f = flattened([c.objects for c in context.object.users_collection])
                print(f)
                inv_objects = [o for o in inv_objects if o in f]
            if self.same_disp:
                sel_type = context.object.display_type
                inv_objects = [o for o in inv_objects if o.display_type == sel_type]
            for o in inv_objects:
                o.select_set(True, view_layer=context.view_layer)
            context.object.select_set(False)
        return {'FINISHED'}


class KeShowInOutliner(Operator):
    bl_idname = "view3d.ke_show_in_outliner"
    bl_label = "Show in Outliner"
    bl_description = "[keKit] Locate the selected object(s) in the outliner (& set parent Collection as Active)\n" \
                     "(in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        override = None
        for area in context.screen.areas:
            if 'OUTLINER' in area.type:
                for region in area.regions:
                    if 'WINDOW' in region.type:
                        override = {'area': area, 'region': region}
                        break
                break

        if not sel_objects or override is None:
            self.report({"INFO"}, "Nothing selected? / Outliner not found?")
            return {"CANCELLED"}

        for obj in sel_objects:
            context.view_layer.objects.active = obj
            bpy.ops.outliner.show_active(override)
        return {"FINISHED"}


class KeSetActiveCollection(Operator):
    bl_idname = "view3d.ke_set_active_collection"
    bl_label = "Set Active Collection"
    bl_description = "[keKit] Set selected object's parent collection as Active (in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        set_active_collection(context, context.object)
        return {"FINISHED"}


class KeSelectByDisplayType(Operator):
    bl_idname = "object.ke_select_by_displaytype"
    bl_label = "Select by Display Type"
    bl_description = "Select objects in scene by viewport display type"
    bl_options = {'REGISTER', 'UNDO'}

    dt : StringProperty(name="Display Type", default="BOUNDS", options={"HIDDEN"})

    def execute(self, context):
        ac = context.preferences.addons[__package__].preferences.sel_type_coll
        ac_objects = []
        ac_check = True
        if ac:
            ac_objects = [o for o in context.view_layer.active_layer_collection.collection.objects]

        dt_is_bounds = False
        bounds = ['CAPSULE', 'CONE', 'CYLINDER', 'SPHERE', 'BOX']
        if self.dt in bounds:
            dt_is_bounds = True

        for o in context.scene.objects:
            if ac:
                ac_check = True if o in ac_objects else False
            if o.visible_get() and ac_check:
                if dt_is_bounds and o.display_type == 'BOUNDS':
                    if o.display_bounds_type == self.dt:
                        o.select_set(True)
                else:
                    if o.display_type == self.dt:
                        o.select_set(True)

        return {'FINISHED'}


class VertObjectSelect(Operator):
    bl_idname = "object.ke_select_objects_by_vertselection"
    bl_label = "Select Objects by VertSelection"
    bl_description = "In Multi-Object Edit Mode:\n" \
                     "Selects only objects that have vertices selected, and set object mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def execute(self, context):
        og_mode = str(context.mode)
        if og_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        sel = [o for o in context.selected_objects if o.type == "MESH"]
        new_sel = []
        for o in sel:
            s = [0] * len(o.data.vertices)
            o.data.vertices.foreach_get('select', s)
            if any(s):
                new_sel.append(o)

        bpy.ops.object.select_all(action="DESELECT")
        for o in new_sel:
            o.select_set(True)

        # if og_mode != "OBJECT":
        #     bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class KeStepRotate(Operator):
    bl_idname = "view3d.ke_vp_step_rotate"
    bl_label = "VP Step Rotate"
    bl_description = "Rotate object or selected elements given angle, based on viewport relative to the object.\n" \
                     "Local, Cursor & View - else Global orientation."
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    rot: bpy.props.IntProperty(min=-180, max=180, default=90)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.space_data.type == "VIEW_3D"

    def execute(self, context):
        obj = context.object
        val = self.rot
        tos = bpy.context.scene.transform_orientation_slots[0].type
        # tpp = bpy.context.scene.tool_settings.transform_pivot_point

        rm = context.space_data.region_3d.view_matrix
        ot = "GLOBAL"
        tm = Matrix().to_3x3()

        if tos == "LOCAL":
            ot = "LOCAL"
            tm = obj.matrix_world.to_3x3().normalized()
        elif tos == "VIEW":
            ot = "VIEW"
            tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()
        elif tos == "CURSOR":
            ot = "CURSOR"
            tm = context.scene.cursor.matrix.to_3x3()
        # else defaults to Global for now

        v = tm.inverted() @ Vector(rm[2]).to_3d()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
        nx, ny, nz = v[0], v[1], v[2]

        if x > y and x > z:
            axis = True, False, False
            oa = "X"
            flip = nx
        elif y > x and y > z:
            axis = False, True, False
            oa = "Y"
            flip = ny
        else:
            axis = False, False, True
            oa = "Z"
            flip = nz

        # check for axis inverse (to work with directions in pie menu (view) )
        if flip > 0:
            val *= -1

        bpy.ops.transform.rotate(value=radians(val), orient_axis=oa, orient_type=ot, orient_matrix_type=ot,
                                 constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False)

        return {"FINISHED"}


#
# Functions
#
def check_selection(bm, sel_mode):
    if sel_mode[2]:
        return [p for p in bm.faces if p.select]
    elif sel_mode[1]:
        return [e for e in bm.edges if e.select]
    else:
        return [v for v in bm.verts if v.select]


def menu_show_in_outliner(self, context):
    self.layout.operator(KeShowInOutliner.bl_idname, text=KeShowInOutliner.bl_label)


def menu_set_active_collection(self, context):
    self.layout.operator(KeSetActiveCollection.bl_idname, text=KeSetActiveCollection.bl_label)


#
# MODULE REGISTRATION
#
classes = (
    UISelectionModule,
    UISelectByDisplayType,
    KeCursorClearRot,
    KeOriginToCursor,
    KeAlignOriginToSelected,
    KeOriginToSelected,
    KeObjectToCursor,
    KeAlignObjectToActive,
    KeSelectedToOrigin,
    KeStraighten,
    KeSwap,
    KeLock,
    KeSelectBoundary,
    KeShowInOutliner,
    KeSetActiveCollection,
    KeSelectInvertLinked,
    KeSelectByDisplayType,
    KeBBMatch,
    VertObjectSelect,
    KeStepRotate,
)

modules = (
    ke_cursor_fit,
    ke_frame_view,
    ke_quick_origin_move,
    ke_mouse_side_of_active,
    ke_view_align,
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_selection:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()

        bpy.types.VIEW3D_MT_object_context_menu.append(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.append(menu_show_in_outliner)
        bpy.types.Scene.kekit_cursor_obj = bpy.props.StringProperty()


def unregister():
    if "bl_rna" in UISelectionModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()

        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_show_in_outliner)
        try:
            del bpy.types.Scene.kekit_cursor_obj
        except Exception as e:
            print('unregister fail:\n', e)
            pass


if __name__ == "__main__":
    register()
