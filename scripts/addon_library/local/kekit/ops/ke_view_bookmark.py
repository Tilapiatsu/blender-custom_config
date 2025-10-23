import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator, Panel
from mathutils import Vector, Quaternion

from .._ui import pcoll


class UIViewBookmarksModule(Panel):
    bl_idname = "UI_PT_M_view_bookmarks"
    bl_label = "View Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_BOOKMARKS"
    bl_options = {'DEFAULT_CLOSED'}

    info_view = "Save & Load Viewport Camera transform (loc, rot & persp/ortho status)"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_view

    def draw(self, context):
        layout = self.layout
        kt = context.scene.kekit_temp

        slots = [i for i in kt.keys() if i[:2] == "vb"]
        slot_items = []
        for i in slots:
            nr, nm = i[2:].split("\x1f")
            slot_items.append((nr, nm))
        slot_items.sort(key=lambda x: int(x[0]))

        col = layout.column(align=False)

        if slot_items:
            for i, (idx, name) in enumerate(slot_items, 1):
                row = col.row(align=True)
                ico_idx = str(i)[-1]
                ico = pcoll['kekit']['ke_bm' + ico_idx].icon_id
                pid = "vb" + str(idx) + "\x1f" + name

                loader = row.operator('view3d.ke_view_bookmark', text=name, icon_value=ico)
                loader.op = "LOAD"
                loader.preset_id = pid

                saving = row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT")
                saving.op = "SAVE"
                saving.preset_id = pid
                row.separator()

                removing = row.operator('view3d.ke_view_bookmark', text="", icon="X")
                removing.op = "DELETE"
                removing.preset_id = pid

        row = col.row(align=True)
        row.prop(kt, "view_name")
        new = row.operator('view3d.ke_view_bookmark', text="", icon="ADD")
        new.op = "SAVE"
        new.preset_id = ""

        col.separator(factor=1.25)

        row = col.row()
        row.enabled = True if slot_items else False
        row.operator('view3d.ke_view_bookmark', text="Cycle View Bookmarks", icon="LOOP_FORWARDS").op = "CYCLE"
        col.separator(factor=0.25)

        sub = col.row(align=True)
        sub.alignment = "CENTER"
        sub.operator('view3d.ke_viewpos', text="Get").mode = "GET"
        sub.prop(kt, "view_query", text="")
        sub.operator('view3d.ke_viewpos', text="Set").mode = "SET"


def assign_slot_nr(slot_items):
    # Check for missing or return +1
    numbers = [int(i[0]) for i in slot_items]
    numbers.sort()
    for i in range(numbers[0], numbers[-1] + 1):
        if i not in numbers:
            return str(i)
    return str(numbers[-1] + 1)


class KeViewBookmark(Operator):
    bl_idname = "view3d.ke_view_bookmark"
    bl_label = "View Bookmarks"
    bl_description = "Save & Load Viewport Camera transform (loc, rot & persp/ortho status)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    op: EnumProperty(items=[
        ("SAVE", "", ""), ("LOAD", "", ""), ("DELETE", "", ""), ("CYCLE", "", ""), ("EXPORT", "", ""),
        ("IMPORT", "", ""), ("CLEAR", "", ""), ("RENAME", "", ""), ("TOGGLE_RENAME", "", "")],
        default="LOAD", options={"HIDDEN"})
    preset_id : StringProperty(name="Preset", default="", options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        return properties.op

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        rv3d = context.space_data.region_3d
        kt = context.scene.kekit_temp

        # check existing
        slots = [i for i in kt.keys() if i[:2] == "vb"]
        slot_items = []
        for i in slots:
            nr, nm = i[2:].split("\x1f")
            slot_items.append((nr, nm))
        slot_items.sort(key=lambda x: int(x[0]))

        if self.op == "CYCLE":
            current = str(kt.viewcycle)
            next_idx = ""
            next_name = ""

            slot_items.append((slot_items[0]))  # cycles back to 1
            found = False
            # taking (possibly) missing nr/slots into account:
            for nr, nm in slot_items:
                if found:
                    next_idx = nr
                    next_name = nm
                    break
                if nr == current:
                    found = True

            if next_idx and next_name:
                self.preset_id = "vb" + next_idx + "\x1f" + next_name
                kt.viewcycle = int(next_idx)
                self.op = "LOAD"
                # bpy.ops.view3d.ke_view_bookmark(op="LOAD", preset_id=preset_id)

        if self.op == "SAVE":
            autonr = False
            if not self.preset_id:
                # New, Auto-name & Construct preset id
                new_name = kt.view_name
                if not new_name:
                    new_name = "ViewPos"
                    autonr = True
                preset_nr, preset_name = "0", new_name
            else:
                # De-Construct preset_id
                preset_nr, preset_name = self.preset_id.split("\x1f")
                preset_nr = [i for i in preset_nr if i.isdigit()]
                preset_nr = ''.join(preset_nr)

            # NEW
            if preset_nr == "0" and not slots:
                preset_nr = str(1)
            # ADDING
            elif preset_nr == "0" and slots:
                preset_nr = assign_slot_nr(slot_items)

            # (or, OVERWRITING)
            if autonr:
                preset_name += preset_nr
            self.preset_id = "vb" + preset_nr + "\x1f" + preset_name

            # Apply (to both adding new & overwriting old presets)
            kt[self.preset_id] = [0.0] * 9
            slot = kt[self.preset_id]

            slot[0] = int(rv3d.is_perspective)
            slot[1] = rv3d.view_distance
            slot[2], slot[3], slot[4] = [i for i in rv3d.view_location]
            slot[5], slot[6], slot[7], slot[8] = [i for i in rv3d.view_rotation]

            print(f"View Pos saved: {preset_name}, idx:{preset_nr} ")

        elif self.op == "DELETE":
            try:
                del kt[self.preset_id]
            except KeyError:
                pass

        elif self.op == "LOAD":
            # LOAD
            slot = kt.get(self.preset_id, None)
            if slot is None:
                print("View Bookmark: Bookmark not found - Op Cancelled")
                return {"CANCELLED"}

            if not rv3d.is_perspective and bool(slot[0]):
                bpy.ops.view3d.view_persportho()
            rv3d.view_distance = slot[1]
            rv3d.view_location = Vector(slot[2:5])
            rv3d.view_rotation = Quaternion(slot[5:9])
            # A little on-screen validation!
            self.report({"INFO"}, self.preset_id.split("\x1f")[1])

        elif self.op == "TOGGLE_RENAME":
            kt.nr_toggle = int(self.preset_id)
            # kt.view_name = ""  # nah, might be a 'happy accident' - for re-using naming?

        elif self.op == "RENAME":
            new_name = kt.view_name
            if new_name:
                slot = kt.get(self.preset_id, None)
                if slot is not None:
                    try:
                        preset_nr, preset_name = self.preset_id.split("\x1f")
                        preset_nr = [i for i in preset_nr if i.isdigit()]
                        preset_nr = ''.join(preset_nr)
                        new_preset_id = "vb" + preset_nr + "\x1f" + new_name
                        kt[new_preset_id] = slot
                        del kt[self.preset_id]
                    except Exception as e:
                        print("Renaming failed:", e)
                        pass

            kt.nr_toggle = 0
        else:
            print("View Bookmark: Bookmark not found - Op Cancelled")

        return {"FINISHED"}


class KeViewBookmarkCycle(Operator):
    bl_idname = "view3d.ke_view_bookmark_cycle"
    bl_label = "Cycle View Bookmarks"
    bl_description = "Cycle stored Viewport Bookmarks"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        kt = context.scene.kekit_temp
        # check existing
        slots = [i for i in kt.keys() if i[:2] == "vb"]
        slot_items = []
        for i in slots:
            nr, nm = i[2:].split("\x1f")
            slot_items.append((nr, nm))
        slot_items.sort(key=lambda x: int(x[0]))

        current = str(kt.viewcycle)
        next_idx = ""
        next_name = ""

        # taking (possibly) missing nr/slots into account:
        if slot_items:
            if current not in [i[0] for i in slot_items]:
                current = slot_items[0]

        slot_items.append((slot_items[0]))  # cycles back to 1
        found = False
        for nr, nm in slot_items:
            if found:
                next_idx = nr
                next_name = nm
                break
            if nr == current:
                found = True

        if next_idx and next_name:
            preset_id = "vb" + next_idx + "\x1f" + next_name
            kt.viewcycle = int(next_idx)
            bpy.ops.view3d.ke_view_bookmark(op="LOAD", preset_id=preset_id)
        else:
            print("Failed View Cycle: Could not find slot/index?")

        return {"FINISHED"}


class KeViewPos(Operator):
    bl_idname = "view3d.ke_viewpos"
    bl_label = "Get & Set Viewpos"
    bl_description = "Get & Set Viewpos"
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[("GET", "Get Viewpos", "", "GET", 1),
               ("SET", "Set Viewpos", "", "SET", 2),
               ],
        name="Viewpos", options={"HIDDEN"},
        default="SET")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "GET":
            return "Get Viewport transform"
        else:
            return "Set Viewport transform"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        rv3d = context.space_data.region_3d

        if self.mode == "GET":
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            v = str(v)
            context.scene.kekit_temp.view_query = v

        else:
            try:
                q = str(context.scene.kekit_temp.view_query)[1:-1]
                qs = q.split(",")
                v = [float(i) for i in qs]
            except Exception as e:
                print("\n", e, "\n Incorrect values. Aborting.")
                return {'CANCELLED'}

            if len(v) == 9:
                if not rv3d.is_perspective and bool(v[0]):
                    bpy.ops.view3d.view_persportho()
                rv3d.view_distance = v[1]
                rv3d.view_location = Vector(v[2:5])
                rv3d.view_rotation = Quaternion(v[5:9])

        return {'FINISHED'}
