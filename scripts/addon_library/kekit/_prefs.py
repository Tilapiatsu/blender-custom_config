import bpy
import json
import os
from bpy.types import (
    PropertyGroup,
    Operator,
    Scene,
    AddonPreferences,
    Header,
    Panel
)
from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    PointerProperty,
    FloatVectorProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import ImportHelper
from ._m_tt import KeTTHeader
from ._utils import refresh_ui

kekit_version = (0, 0, 0)  # is set from __init__
m_tooltip = "Toggles Module On/Off. Read Docs/Wiki for Module information"
path = bpy.utils.user_resource('CONFIG')
pcoll = {}
icons = ["ke_bm1.png", "ke_bm2.png", "ke_bm3.png", "ke_bm4.png", "ke_bm5.png", "ke_bm6.png",
         "ke_cursor1.png", "ke_cursor2.png", "ke_cursor3.png", "ke_cursor4.png", "ke_cursor5.png", "ke_cursor6.png",
         "ke_dot1.png", "ke_dot2.png", "ke_dot3.png", "ke_dot4.png", "ke_dot5.png", "ke_dot6.png",
         "ke_opc1.png", "ke_opc2.png", "ke_opc3.png", "ke_opc4.png", "ke_opc5.png", "ke_opc6.png",
         "ke_snap1.png", "ke_snap2.png", "ke_snap3.png", "ke_snap4.png", "ke_snap5.png", "ke_snap6.png",
         "ke_uncheck.png"]


#
# KIT FUNCTIONS
#
def load_icons():
    from bpy.utils import previews
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pr = previews.new()
    for i in icons:
        name = i[:-4]
        pr.load(name, os.path.join(icons_dir, i), 'IMAGE')
    pcoll['kekit'] = pr


def set_tt_icon_pos(self, context):
    bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
    bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)
    if bpy.context.preferences.addons[__package__].preferences.tt_icon_pos == "CENTER":
        bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
    elif bpy.context.preferences.addons[__package__].preferences.tt_icon_pos == "RIGHT":
        bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)
    elif bpy.context.preferences.addons[__package__].preferences.tt_icon_pos == "LEFT":
        bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
    # ...else REMOVE only


def draw_extras(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("outliner.show_active", icon="ZOOM_PREVIOUS", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_IN", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_OUT", text="").open = False


def save_prefs():
    ap = bpy.context.preferences.addons[__package__].preferences
    prefs = {}
    for key in ap.__annotations__.keys():
        k = getattr(ap, key)
        if str(type(k)) == "<class 'bpy_prop_array'>":
            prefs[key] = k[:]
        else:
            prefs[key] = k
    jsondata = json.dumps(prefs, indent=1, ensure_ascii=True)
    file_name = path + "/kekit_prefs" + ".json"
    with open(file_name, "w") as text_file:
        text_file.write(jsondata)
    text_file.close()


#
#  KIT OPERATORS
#
class KeSavePrefs(Operator):
    bl_idname = "kekit.prefs_export"
    bl_label = "Export keKit Settings"
    bl_description = "Export current keKit settings (to JSON-file in user config folder)"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        save_prefs()
        self.report({"INFO"}, "keKit Preferences Exported!")
        return {'FINISHED'}


class KeFileBrowser(Operator, ImportHelper):
    bl_idname = "kekit.filebrowser"
    bl_label = "Import keKit Settings"
    bl_description = "Open a filebrowser to load keKit prefs file"
    bl_options = {"INTERNAL"}

    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'})

    def execute(self, context):
        bpy.ops.kekit.prefs_import(inputpath=self.filepath)
        return {'FINISHED'}


class KeLoadPrefs(Operator):
    bl_idname = "kekit.prefs_import"
    bl_label = "Import keKit Settings"
    bl_description = "Import keKit settings (from JSON-file)"
    bl_options = {"INTERNAL"}

    inputpath : StringProperty(name="filepath", default=path + "/kekit_prefs.json", options={'HIDDEN'})

    def execute(self, context):
        ap = context.preferences.addons['kekit'].preferences
        # file_name = path + "/kekit_prefs.json"
        file_name = self.inputpath
        prefs = None
        try:
            with open(file_name, "r") as jf:
                prefs = json.load(jf)
                jf.close()
        except (OSError, IOError) as e:
            print("keKit: Prefs Load Error:", e)
            pass
        if prefs is not None and ap is not None:
            for key in prefs :
                if key in ap.__annotations__.keys():
                    v = prefs[key]
                    # Brute force assign ENUMS - won't assign with key - MEH!
                    if key == "opc1_obj_o":
                        ap.opc1_obj_o = v
                    elif key == "opc1_obj_p":
                        ap.opc1_obj_p = v
                    elif key == "opc1_edit_o":
                        ap.opc1_edit_o = v
                    elif key == "opc1_edit_p":
                        ap.opc1_edit_p = v
                    # OPC2
                    elif key == "opc2_obj_o":
                        ap.opc2_obj_o = v
                    elif key == "opc2_obj_p":
                        ap.opc2_obj_p = v
                    elif key == "opc2_edit_o":
                        ap.opc2_edit_o = v
                    elif key == "opc2_edit_p":
                        ap.opc2_edit_p = v
                    # OPC3
                    elif key == "opc3_obj_o":
                        ap.opc3_obj_o = v
                    elif key == "opc3_obj_p":
                        ap.opc3_obj_p = v
                    elif key == "opc3_edit_o":
                        ap.opc3_edit_o = v
                    elif key == "opc3_edit_p":
                        ap.opc3_edit_p = v
                    # OPC4
                    elif key == "opc4_obj_o":
                        ap.opc4_obj_o = v
                    elif key == "opc4_obj_p":
                        ap.opc4_obj_p = v
                    elif key == "opc4_edit_o":
                        ap.opc4_edit_o = v
                    elif key == "opc4_edit_p":
                        ap.opc4_edit_p = v
                    # OPC5
                    elif key == "opc5_obj_o":
                        ap.opc5_obj_o = v
                    elif key == "opc5_obj_p":
                        ap.opc5_obj_p = v
                    elif key == "opc5_edit_o":
                        ap.opc5_edit_o = v
                    elif key == "opc5_edit_p":
                        ap.opc5_edit_p = v
                    # OPC6
                    elif key == "opc6_obj_o":
                        ap.opc6_obj_o = v
                    elif key == "opc6_obj_p":
                        ap.opc6_obj_p = v
                    elif key == "opc6_edit_o":
                        ap.opc6_edit_o = v
                    elif key == "opc6_edit_p":
                        ap.opc6_edit_p = v
                    # misc
                    elif key == "tt_icon_pos":
                        ap.tt_icon_pos = v
                    elif key == "boundary_smooth":
                        ap.boundary_smooth = v
                    else:
                        try:
                            ap[key] = prefs[key]
                        except Exception as e:
                            print("keKit Prefs Import - Key not found: ", e)
            self.report({"INFO"}, "keKit Perferences Imported!")
        else:
            print("keKIT Load Settings JSON File Error")
        refresh_ui()
        return {'FINISHED'}


class KeResetPrefs(Operator):
    bl_idname = "kekit.prefs_reset"
    bl_label = "Reset keKit Settings"
    bl_description = "Reset keKit settings to default values"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = prefs.__annotations__.keys()
        for k in props:
            prefs.property_unset(k)
        refresh_ui()
        return {'FINISHED'}


class KeMouseOverInfo(Operator):
    bl_idname = "ke_mouseover.info"
    bl_label = "Info"
    bl_options = {"INTERNAL"}

    text: StringProperty(name="Info", description="Info", default='')

    @classmethod
    def description(cls, context, properties):
        return properties.text

    def execute(self, context):
        return {'INTERFACE'}


#
# (3D VIEW) UI
#
class KeIconPreload(Header):
    bl_idname = "VIEW3D_HT_KE_ICONPRELOAD"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        # Terrible OpenGL style preloading to avoid seeing (the most used) icons load
        layout = self.layout
        row = layout.row()
        row.ui_units_x = 0.01
        row.scale_y = 0.01
        row.scale_x = 0.01
        # SNAPPING
        row.label(icon_value=pcoll['kekit']['ke_snap1'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap2'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap3'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap4'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap5'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap6'].icon_id)
        # OPC
        row.label(icon_value=pcoll['kekit']['ke_opc1'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc2'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc3'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc4'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc5'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc6'].icon_id)


class UIKeKitMain(Panel):
    bl_idname = "UI_PT_kekit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_label = 'keKit'
    bl_description = 'keKit Main Panel'

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
        row = layout.row()
        row.label(text="%s" % bpy.context.preferences.addons[__package__].preferences.version)
        row.operator("wm.url_open", text="", icon="URL").url = "https://ke-code.xyz/scripts/kekit.html"
        row.separator(factor=0.5)

    def draw(self, context):
        layout = self.layout


#
# KIT PREFERENCES
#
class KeKitPropertiesTemp(PropertyGroup):
    slush: StringProperty(default="")
    view_query: StringProperty(default=" N/A ")
    toggle: BoolProperty(default=False)
    is_rendering: BoolProperty(default=False)
    cursorslot1: FloatVectorProperty(size=6)
    cursorslot2: FloatVectorProperty(size=6)
    cursorslot3: FloatVectorProperty(size=6)
    cursorslot4: FloatVectorProperty(size=6)
    cursorslot5: FloatVectorProperty(size=6)
    cursorslot6: FloatVectorProperty(size=6)
    viewslot1: FloatVectorProperty(size=9)
    viewslot2: FloatVectorProperty(size=9)
    viewslot3: FloatVectorProperty(size=9)
    viewslot4: FloatVectorProperty(size=9)
    viewslot5: FloatVectorProperty(size=9)
    viewslot6: FloatVectorProperty(size=9)
    viewtoggle: FloatVectorProperty(size=9)
    viewcycle: IntProperty(default=0, min=0, max=5)
    focus: BoolVectorProperty(size=16)
    focus_stats: BoolProperty()
    kcm_axis: EnumProperty(items=[
        ("X", "X", "", 1),
        ("Y", "Y", "", 2),
        ("Z", "Z", "", 3)],
        name="Cursor Axis", default="Y", description="Which of the cursors (local) axis to rotate around")
    kcm_rot_preset: EnumProperty(items=[
        ("5", "5\u00B0", "", 1),
        ("15", "15\u00B0", "", 2),
        ("45", "45\u00B0", "", 3),
        ("90", "90\u00B0", "", 4)],
        name="Step Presets", default="90", description="Preset rotation values for step-rotate")
    kcm_custom_rot: FloatProperty(name="Custom Step", default=0, subtype="ANGLE", unit="ROTATION", precision=3,
                                  description="Custom rotation (non zero will override preset-use) for step-rotate")


class KeKitAddonPreferences(AddonPreferences):
    bl_idname = __package__
    version: StringProperty(name="", default="")
    # KIT PREFS
    ui_scale: FloatProperty(name="Text Scale", default=1.0, min=0.1, max=10,
                            description="keKIT modal UI text scale - multiplied to Blender UI Scale")
    outliner_extras: BoolProperty(name="Outliner Buttons", default=False,
                                  description="Adds extra buttons in Outliner header for:\n'Show Active', "
                                              "'Show One Level' and 'Hide One Level'\n Use 'Reload Addons' to apply")
    experimental: BoolProperty(name="Experimental", default=False,
                               description="Toggle properties/features that work - but has some quirks\n"
                                           "See keKit Wiki for details.")
    # MODAL COLORS
    modal_color_header: FloatVectorProperty(name="Header Color", subtype='COLOR',
                                            size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_text: FloatVectorProperty(name="Text Color", subtype='COLOR',
                                          size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_subtext: FloatVectorProperty(name="Sub-Text Color", subtype='COLOR',
                                             size=4, default=[0.5, 0.5, 0.5, 1.0])
    # MODULES
    m_dupe: BoolProperty(name="1: Duplication", default=True, description=m_tooltip)
    m_main: BoolProperty(name="2: Main", default=True, description=m_tooltip)
    m_render: BoolProperty(name="3: Render", default=True, description=m_tooltip)
    m_bookmarks: BoolProperty(name="4: Bookmarks", default=True, description=m_tooltip)
    m_selection: BoolProperty(name="5: Select & Align", default=True, description=m_tooltip)
    m_modeling: BoolProperty(name="6: Modeling", default=True, description=m_tooltip)
    m_directloopcut: BoolProperty(name="6A: DirectLoopCut", default=True, description=m_tooltip)
    m_multicut: BoolProperty(name="6B: MultiCut", default=True, description=m_tooltip)
    m_subd: BoolProperty(name="6C: SubD Tools", default=True, description=m_tooltip)
    m_unrotator: BoolProperty(name="6D: Unrotator", default=True, description=m_tooltip)
    m_fitprim: BoolProperty(name="6E: FitPrim", default=True, description=m_tooltip)
    m_contexttools: BoolProperty(name="6F: Context Tools", default=True, description=m_tooltip)
    m_tt: BoolProperty(name="7: Transform Tools", default=True, description=m_tooltip)
    m_idmaterials: BoolProperty(name="8: ID Materials", default=True, description=m_tooltip)
    m_cleanup: BoolProperty(name="9: Clean-Up Tools", default=True, description=m_tooltip)
    m_piemenus: BoolProperty(name="10: Pie Menus", default=True, description=m_tooltip)
    kcm: BoolProperty(name="keKit Cursor Menu", default=True,
                      description="Show KeKit Cursor Menu icon in toolbar\nRequires keKit Select & Align Module\n"
                                  "Use 'Reload Addons' to apply")
    # OPERATOR PREFS
    # Fitprim
    fitprim_select: BoolProperty(default=False)
    fitprim_modal: BoolProperty(default=True)
    fitprim_item: BoolProperty(default=False)
    fitprim_sides: IntProperty(min=3, max=256, default=16)
    fitprim_sphere_seg: IntProperty(min=3, max=256, default=32)
    fitprim_sphere_ring: IntProperty(min=3, max=256, default=16)
    fitprim_unit: FloatProperty(min=.00001, max=256, default=0.2)
    fitprim_quadsphere_seg: IntProperty(min=1, max=128, default=8)
    # Unrotator
    unrotator_reset: BoolProperty(default=True)
    unrotator_connect: BoolProperty(description="Connect linked faces to selection (Edit Mode)", default=True)
    unrotator_nolink: BoolProperty(description="Duplicated Objects will not be data-linked", default=False)
    unrotator_nosnap: BoolProperty(description="Toggles on face surface snapping or not", default=False)
    unrotator_invert: BoolProperty(description="Invert (Z) rotation (Separate from the redo-panel)", default=False)
    unrotator_center: BoolProperty(description="Center on target face. (Tip: Shift-LMB in modal)", default=False)
    unrotator_rndz: BoolProperty(description="Randomize Z-axis rotation when duplicating", default=False)
    # Orientation & Pivot Combo 1
    opc1_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="1GLOBAL")
    opc1_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="1MEDIAN_POINT")
    opc1_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="1GLOBAL")
    opc1_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="1MEDIAN_POINT")
    # Orientation & Pivot Combo 2
    opc2_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="2LOCAL")
    opc2_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="3INDIVIDUAL_ORIGINS")
    opc2_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="3NORMAL")
    opc2_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="5ACTIVE_ELEMENT")
    # Orientation & Pivot Combo 3
    opc3_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="1GLOBAL")
    opc3_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="3INDIVIDUAL_ORIGINS")
    opc3_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="2LOCAL")
    opc3_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="3INDIVIDUAL_ORIGINS")
    # Orientation & Pivot Combo 4
    opc4_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="6CURSOR")
    opc4_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="4CURSOR")
    opc4_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="6CURSOR")
    opc4_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="4CURSOR")
    # Orientation & Pivot Combo 5
    opc5_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="1GLOBAL")
    opc5_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="4CURSOR")
    opc5_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="1GLOBAL")
    opc5_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="5ACTIVE_ELEMENT")
    # Orientation & Pivot Combo 6
    opc6_obj_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="5VIEW")
    opc6_obj_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="1MEDIAN_POINT")
    opc6_edit_o: EnumProperty(
        items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),
               ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default="5VIEW")
    opc6_edit_p: EnumProperty(
        items=[("1MEDIAN_POINT", "Median Point", ""), ("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),
               ("5ACTIVE_ELEMENT", "Active Element", "")], name="Pivot Transform", default="5ACTIVE_ELEMENT")
    # OPC naming
    opc1_name: StringProperty(description="Name OPC1", default="OPC1")
    opc2_name: StringProperty(description="Name OPC2", default="OPC2")
    opc3_name: StringProperty(description="Name OPC3", default="OPC3")
    opc4_name: StringProperty(description="Name OPC4", default="OPC4")
    opc5_name: StringProperty(description="Name OPC5", default="OPC5")
    opc6_name: StringProperty(description="Name OPC6", default="OPC6")
    # QuickMeasure
    quickmeasure: BoolProperty(default=True)
    qm_running: BoolProperty(default=False)
    # Fit2Grid
    fit2grid: FloatProperty(min=.00001, max=10000, default=0.01)
    # ViewPlane Contextual
    vptransform: BoolProperty(name="VPAutoGlobal", description="Sets Global orientation. Overrides GOT options",
                              default=False)
    loc_got: BoolProperty(name="Grab GlobalOrTool", description="VPGrab when Global, otherwise Transform (gizmo)",
                          default=True)
    rot_got: BoolProperty(name="Rotate GlobalOrTool", description="VPRotate when Global, otherwise Rotate (gizmo)",
                          default=True)
    scl_got: BoolProperty(name="Scale GlobalOrTool", description="VPResize when Global, otherwise Scale (gizmo)",
                          default=True)
    # Quick Scale
    qs_user_value: FloatProperty(
        description="Set dimension (Unit meter) or Unit fit with chosen axis. Obj & Edit mode (selection)",
        precision=3, subtype="DISTANCE", unit="LENGTH", default=1.0)
    qs_unit_size: BoolProperty(default=True)
    # Cleaning Tools
    clean_doubles: BoolProperty(name="Double Geo", default=True,
                                description="Vertices occupying the same location (within 0.0001)")
    clean_doubles_val: FloatProperty(name="Double Geo Distance", default=0.0001, precision=4)
    clean_loose: BoolProperty(name="Loose Verts/Edges", default=True,
                              description="Verts/Edges not attached to faces")
    clean_interior: BoolProperty(name="Interior Faces", default=True,
                                 description="Faces where all edges have more than 2 face users")
    clean_degenerate: BoolProperty(name="Degenerate Geo", default=True,
                                   description="Non-Manifold geo: Edges with no length & Faces with no area")
    clean_tinyedge: BoolProperty(name="Tiny Edges", default=True,
                                 description="Edges that are shorter than the Tiny-Edge Value set\n"
                                             "Selection only - will select also in Clean Mode")
    clean_tinyedge_val: FloatProperty(name="Tiny Edge Limit", default=0.002, precision=4,
                                      description="Shortest allowed Edge length for Tiny Edge Selection")
    clean_collinear: BoolProperty(name="Collinear Verts", default=True,
                                  description="Additional(Superfluous) verts in a straight line on an edge")
    # Cursor Fit OP Option
    cursorfit: BoolProperty(description="Also set Orientation & Pivot to Cursor", default=True)
    # Linear Array Global Only Option
    lineararray_go: BoolProperty(description="Applies Rotation and usese Global Orientation & Pivot during modal",
                                 default=False)
    # Material ID Colors
    idm01: FloatVectorProperty(name="IDM01", subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 0.0, 0.0, 1.0))
    idm02: FloatVectorProperty(name="IDM02", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.6, 0.0, 0.0, 1.0))
    idm03: FloatVectorProperty(name="IDM03", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.3, 0.0, 0.0, 1.0))
    idm04: FloatVectorProperty(name="IDM04", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 1.0, 0.0, 1.0))
    idm05: FloatVectorProperty(name="IDM05", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.6, 0.0, 1.0))
    idm06: FloatVectorProperty(name="IDM06", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.3, 0.0, 1.0))
    idm07: FloatVectorProperty(name="IDM07", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.0, 1.0, 1.0))
    idm08: FloatVectorProperty(name="IDM08", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.0, 0.6, 1.0))
    idm09: FloatVectorProperty(name="IDM09", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.0, 0.3, 1.0))
    idm10: FloatVectorProperty(name="IDM10", subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0))
    idm11: FloatVectorProperty(name="IDM11", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.5, 0.5, 0.5, 1.0))
    idm12: FloatVectorProperty(name="IDM12", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.0, 0.0, 1.0))
    # Material ID Names
    idm01_name: StringProperty(default="ID_RED")
    idm02_name: StringProperty(default="ID_RED_M")
    idm03_name: StringProperty(default="ID_RED_L")
    idm04_name: StringProperty(default="ID_GREEN")
    idm05_name: StringProperty(default="ID_GREEN_M")
    idm06_name: StringProperty(default="ID_GREEN_L")
    idm07_name: StringProperty(default="ID_BLUE")
    idm08_name: StringProperty(default="ID_BLUE_M")
    idm09_name: StringProperty(default="ID_BLUE_L")
    idm10_name: StringProperty(default="ID_ALPHA")
    idm11_name: StringProperty(default="ID_ALPHA_M")
    idm12_name: StringProperty(default="ID_ALPHA_L")
    # Material ID Options
    object_color: BoolProperty(description="Set ID color also to Object Viewport Display", default=False)
    matvp_color: BoolProperty(description="Set ID color also to Material Viewport Display", default=False)
    vpmuted: BoolProperty(description="Tone down ID colors slightly for Viewport Display (only)", default=False)
    # Subd Toggle
    vp_level: IntProperty(min=0, max=64, description="Viewport Levels to be used", default=2)
    render_level: IntProperty(min=0, max=64, description="Render Levels to be used", default=2)
    flat_edit: BoolProperty(description="Set Flat Shading when Subd is Level 0", default=False)
    boundary_smooth: EnumProperty(items=[("PRESERVE_CORNERS", "Preserve Corners", ""), ("ALL", "All", "")],
                                  description="Controls how open boundaries are smoothed",
                                  default="PRESERVE_CORNERS")
    limit_surface: BoolProperty(description="Use Limit Surface", default=False)
    optimal_display : BoolProperty(description="Use Optimal Display", default=True)
    on_cage: BoolProperty(description="Show On Edit Cage", default=False)
    subd_autosmooth: BoolProperty(description="ON:Autosmooth is turned off by toggle when subd is on - and vice versa\n"
                                              "OFF:Autosmooth is not changed by toggle", name="Autosmooth Toggle",
                                  default=True)
    # Snapping Combos
    snap_elements1: StringProperty(description="Snapping Element Combo 1", default="INCREMENT")
    snap_elements2: StringProperty(description="Snapping Element Combo 2", default="FACE,EDGE,EDGE_MIDPOINT,VERTEX")
    snap_elements3: StringProperty(description="Snapping Element Combo 3", default="FACE")
    snap_elements4: StringProperty(description="Snapping Element Combo 4", default="INCREMENT")
    snap_elements5: StringProperty(description="Snapping Element Combo 5", default="INCREMENT")
    snap_elements6: StringProperty(description="Snapping Element Combo 6", default="INCREMENT")
    snap_targets1: StringProperty(description="Snapping Targets Combo 1", default="ACTIVE")
    snap_targets2: StringProperty(description="Snapping Targets Combo 2", default="CLOSEST")
    snap_targets3: StringProperty(description="Snapping Targets Combo 3", default="ACTIVE")
    snap_targets4: StringProperty(description="Snapping Targets Combo 4", default="ACTIVE")
    snap_targets5: StringProperty(description="Snapping Targets Combo 5", default="ACTIVE")
    snap_targets6: StringProperty(description="Snapping Targets Combo 6", default="ACTIVE")
    snap_bools1: BoolVectorProperty(description="Snapping Bools Combo 1", size=9,
                                    default=[True, False, False, True, False, False, True, False, False])
    snap_bools2: BoolVectorProperty(description="Snapping Bools Combo 2", size=9,
                                    default=[True, False, False, True, False, False, True, False, False])
    snap_bools3: BoolVectorProperty(description="Snapping Bools Combo 3", size=9,
                                    default=[True, False, True, False, True, False, True, False, False])
    snap_bools4: BoolVectorProperty(description="Snapping Bools Combo 4", size=9,
                                    default=[True, False, False, True, False, False, True, False, False])
    snap_bools5: BoolVectorProperty(description="Snapping Bools Combo 5", size=9,
                                    default=[True, False, False, True, False, False, True, False, False])
    snap_bools6: BoolVectorProperty(description="Snapping Bools Combo 6", size=9,
                                    default=[True, False, False, True, False, False, True, False, False])
    # snap combo naming
    snap_name1: StringProperty(description="Snapping Combo 1 Name", default="Snap Combo 1")
    snap_name2: StringProperty(description="Snapping Combo 2 Name", default="Snap Combo 2")
    snap_name3: StringProperty(description="Snapping Combo 3 Name", default="Snap Combo 3")
    snap_name4: StringProperty(description="Snapping Combo 4 Name", default="Snap Combo 4")
    snap_name5: StringProperty(description="Snapping Combo 5 Name", default="Snap Combo 5")
    snap_name6: StringProperty(description="Snapping Combo 6 Name", default="Snap Combo 6")
    # Auto activation Option
    combo_autosnap: BoolProperty(name="Auto-Activate Snap",
                                 description="Auto activate snapping mode when using snap combo",
                                 default=False)
    # paste+
    plus_mpoint: BoolProperty(
        name="P",
        default=False,
        description="Paste+ Point\n"
                    "ON: Places pasted Object(s) at Mouse Point.  OFF: Original location")
    plus_merge: BoolProperty(
        name="M",
        default=False,
        description="Paste+ Merge\n"
                    "ON: Merges Pasted items with selected(Active Object) in Object Mode\n"
                    "OFF: Paste items into New Object, with or without selections in Object Mode")
    # Context Delete
    h_delete: BoolProperty(name="Hierarchy Delete", description="And the children too (in Object Mode)", default=True)
    cd_pluscut: BoolProperty(
        name="Use Cut+ Buffer",
        description="Deleted object(s) (or FACES in Edit Mode) are stored in the Cut+ buffer - can be used by Paste+",
        default=False)
    cd_smart: BoolProperty(
        name="Smart Dissolve",
        description="Dissolve Verts and Edges instead of deleting them. Faces are deleted.",
        default=False)
    # Transform Toggle
    tt_mode: BoolVectorProperty(description="Toggles between default transform tools, MouseAxis or VP", size=3,
                                default=[True, False, False])
    tt_handles: BoolProperty(description="TT Default uses the handle tools or the classic style ('Grab' etc.)",
                             default=True)
    tt_select: BoolProperty(
        description="Switches to Select Tool (Tweak) for when default handle tools are active when toggling TT",
        default=True)
    tt_extrude: BoolProperty(description="Use TT Mode for transform: Default, MouseAxis and VP, except faces",
                             default=False)
    tt_linkdupe: BoolProperty(description="Global TT Duplicate Linked Toggle (includes Mouse Axis Dupe & VP Dupe)",
                              default=False)
    # Use Render Slot Cycling
    renderslotcycle: BoolProperty(name="Render Slot Cycle",
                                  description="Enable render slot cycling (to the first empty render slot)",
                                  default=False)
    # RISC notify or wrap to 1st toggle
    renderslotfullwrap: BoolProperty(
        name="Render Slot Full-Wrap",
        description="Back to 1st slot when full and cycle step fwd, or stop and notify",
        default=False)
    # Get Set Edit Mode Element Pick
    getset_ep: BoolProperty(name="Get & Set Edit with Element Pick",
                            description="(In Edit Mode) Component Mode based on element under mouse "
                                        "(Vert, Edge or Face)", default=False)
    # Multi Cut prefs
    mc_relative: IntProperty(name="Relative Offset from endpoint. Mirrored automatically to the other end point.",
                             min=1, max=49, default=10, subtype="PERCENTAGE")
    mc_fixed: FloatProperty(name="Fixed Offset from endpoint. Mirrored automatically to the other end point.", min=0,
                            default=0, subtype="DISTANCE", unit="LENGTH")
    mc_center: IntProperty(name="Center Cut. 1 or 0 for none.", min=0, max=1, default=True)
    mc_prefs: FloatVectorProperty(size=32, precision=4,
                                  default=[0.1, 0, 0, 0, 0.1, 1, 0, 0, 0.05, 1, 0, 0, 0.05, 0, 0, 0, 0, 0, 0.05, 1, 0,
                                           1, 0.05, 1, 0, 1, 0.01, 1, 0, 0, 0.01, 1])
    mc_name0: StringProperty(description="MultiCut Preset 1", default="10-90")
    mc_name1: StringProperty(description="MultiCut Preset 2", default="10-50-90")
    mc_name2: StringProperty(description="MultiCut Preset 3", default="5-50-95")
    mc_name3: StringProperty(description="MultiCut Preset 4", default="5-95")
    mc_name4: StringProperty(description="MultiCut Preset 5", default="5 cm")
    mc_name5: StringProperty(description="MultiCut Preset 6", default="5 cm (C)")
    mc_name6: StringProperty(description="MultiCut Preset 7", default="1 cm (C)")
    mc_name7: StringProperty(description="MultiCut Preset 8", default="1 cm")
    # DLC sel only
    dlc_so: BoolProperty(name="Selection-Only Toggle",
                         description="No mouse-pick, selected element only (nearest selected edge in face limit "
                                     "selection)\nAffects all 'Direct' operators",
                         default=False)
    # Shading Toggle Tri mode
    shading_tris: BoolProperty(name="Flat Shading Triangulate",
                               description="Flat Shading Triangulate:\n"
                                           "Use Triangulate Modifier (always last) for more accurate flat shading",
                               default=False)
    # Frame All Mesh Only
    frame_mo: BoolProperty(name="Geo Only",
                           description="Ignore non-geo objects (lights, cameras etc) for Frame All (not selected)",
                           default=False)
    # Mouse Axis Move - Scale ignore
    mam_scl: BoolProperty(name="MAS",
                          description="Mouse Axis Scale - Uncheck for default (unlocked) Scale behaviour for "
                                      "TT Scale MouseAxis",
                          default=True)
    # korean toggle
    korean: BoolProperty(name="Korean/Flat Bevel Toggle",
                         description="Toggles Korean / Flat Bevel preset for Context Bevel and keKit subdtools bevels",
                         default=False)
    # select by display type active collection only toggle
    sel_type_coll: BoolProperty(name="Active Collection Only",
                                description="Select by display type in active collection only",
                                default=False)
    # Unbevel Auto-Edge Ring
    unbevel_autoring: BoolProperty(name="Unbevel Auto-EdgeRing",
                                   description="Runs Edge-Ring selection before Unbevel",
                                   default=False)
    # Context Select Object Mode Full Hierarchy
    context_select_h: BoolProperty(name="FH",
                                   description="Context Select - OBJECT MODE Full Hierarchy\n"
                                               "(not just the children, but the parents too)\n"
                                               "Note: Also applies to Extend/Subtract",
                                   default=False)
    # Context Select - Vertex Mode Behaviour
    context_select_b: BoolProperty(name="B",
                                   description="Context Select - Custom VERTEX MODE behaviour\n "
                                               "On - Selects open boundaries if any in connected geo\n"
                                               "Off - Selects connected geo",
                                   default=False)
    context_select_c: BoolProperty(name="C",
                                   description="Context Select - Select All Objects in selected object's Collection\n"
                                               "(in OBJECT MODE)",
                                   default=False)

    # TT header icons prefs
    tt_icon_pos: EnumProperty(
        name="TT Icon Placement",
        description="Viewport icons for Transform Tools (TT) module",
        items=[("LEFT", "Left", ""),
               ("CENTER", "Center", ""),
               ("RIGHT", "Right", ""),
               ("REMOVE", "Remove", "")
               ],
        update=set_tt_icon_pos,
        default="CENTER")

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        # row.operator("kekit.prefs_import", icon="IMPORT")
        row.operator("kekit.filebrowser", icon="IMPORT")

        row.operator("kekit.prefs_export", icon="EXPORT")
        row.operator("kekit.prefs_reset", icon="LOOP_BACK")

        row = layout.row()
        row.label(text="Show:")
        row.prop(self, "kcm", toggle=True)
        row.prop(self, "outliner_extras", toggle=True)
        row.prop(self, "experimental", toggle=True)

        if bpy.context.preferences.addons[__package__].preferences.m_tt:
            row = layout.row()
            row.label(text="Viewport TT Icons:")
            row.prop(self, "tt_icon_pos", expand=True)

        box = layout.box()
        row = box.row()
        row.label(text="keKit Main Panel Modules:")
        row.operator("script.reload", text="Reload Add-ons", icon="FILE_REFRESH")
        row = box.row()
        row.prop(self, "m_dupe", toggle=True)
        row.prop(self, "m_main", toggle=True)
        row.prop(self, "m_render", toggle=True)

        row = box.row()
        row.label(text="keKit Modules:")
        gf = box.grid_flow(row_major=True, columns=4)
        gf.prop(self, "m_bookmarks", toggle=True)
        gf.prop(self, "m_selection", toggle=True)
        gf.prop(self, "m_modeling", toggle=True)
        gf.prop(self, "m_directloopcut", toggle=True)
        gf.prop(self, "m_multicut", toggle=True)
        gf.prop(self, "m_subd", toggle=True)
        gf.prop(self, "m_unrotator", toggle=True)
        gf.prop(self, "m_fitprim", toggle=True)
        gf.prop(self, "m_contexttools", toggle=True)
        gf.prop(self, "m_tt", toggle=True)
        gf.prop(self, "m_idmaterials", toggle=True)
        gf.prop(self, "m_cleanup", toggle=True)
        gf.prop(self, "m_piemenus", toggle=True)

        layout.label(text="Modal Text:")
        gf = layout.grid_flow(row_major=True, columns=2)
        gf.use_property_split = True
        gf.prop(self, "ui_scale")
        gf.prop(self, 'modal_color_header')
        gf.prop(self, 'modal_color_text')
        gf.prop(self, 'modal_color_subtext')


classes = (
    KeKitAddonPreferences,
    UIKeKitMain,
    KeKitPropertiesTemp,
    KeSavePrefs,
    KeLoadPrefs,
    KeFileBrowser,
    KeResetPrefs,
    KeMouseOverInfo,
    KeIconPreload
)

modules = ()


def register():
    load_icons()

    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.kekit_temp = PointerProperty(type=KeKitPropertiesTemp)

    bpy.types.VIEW3D_HT_header.append(KeIconPreload.draw)

    if bpy.context.preferences.addons[__package__].preferences.outliner_extras:
        bpy.types.OUTLINER_HT_header.append(draw_extras)

    v = "v" + str(kekit_version[0]) + "." + str(kekit_version[1]) + str(kekit_version[2])
    bpy.context.preferences.addons[__package__].preferences.version = v


def unregister():
    save_prefs()

    try:
        bpy.types.OUTLINER_HT_header.remove(draw_extras)
    except Exception as e:
        print('keKit Draw Extras Header Unregister Fail: ', e)
        pass

    bpy.types.VIEW3D_HT_header.remove(KeIconPreload.draw)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    try:
        del Scene.kekit_temp
    except Exception as e:
        print('keKit Temp-Props Unregister Exception: ', e)
        pass

    for pr in pcoll.values():
        bpy.utils.previews.remove(pr)
    pcoll.clear()


if __name__ == "__main__":
    register()
