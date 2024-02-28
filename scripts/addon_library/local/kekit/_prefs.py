import json
import bpy
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
from bpy.types import (
    PropertyGroup,
    Operator,
    Scene,
    AddonPreferences,
)
from bpy_extras.io_utils import ImportHelper
from ._utils import refresh_ui, get_prefs
from ._ui import UIKeKitMain, prefs_ui
from .m_tt import set_tt_icon_pos

kekit_version = (0, 0, 0)  # is set from __init__
m_tooltip = "Toggles Module On/Off. Read Docs/Wiki for Module information"
path = bpy.utils.user_resource('CONFIG')


# Updating kekit tab location will require "Reload Add-ons": TBD: run op here?
# (avoiding managing importing all the module & submodule panels manually & future panels added)
def update_panel(self, context):
    k = get_prefs()
    error_message = "keKit : panel update failed"
    try:
        if "bl_rna" in UIKeKitMain.__dict__:
            bpy.utils.unregister_class(UIKeKitMain)

        UIKeKitMain.bl_category = k.category
        bpy.utils.register_class(UIKeKitMain)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, error_message, e))
        pass


def save_prefs():
    ap = get_prefs()
    prefs = {}
    for key in ap.__annotations__.keys():
        k = getattr(ap, key)
        if str(type(k)) == "<class 'bpy_prop_array'>":
            prefs[key] = k[:]
        else:
            prefs[key] = k
    jsondata = json.dumps(prefs, indent=1, ensure_ascii=True)
    file_name = path + "/kekit_prefs.json"
    with open(file_name, "w") as text_file:
        text_file.write(jsondata)
    text_file.close()


class KeSavePrefs(Operator):
    bl_idname = "kekit.prefs_export"
    bl_label = "Export keKit Settings"
    bl_description = "Export current keKit settings (to JSON-file in user config folder)\n" \
                     "Note: keKit automatically exports when closing Blender"
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

    inputpath: StringProperty(name="filepath", default=path + "/kekit_prefs.json", options={'HIDDEN'})

    def execute(self, context):
        ap = get_prefs()
        prefs = None
        # Loading prefs file
        try:
            with open(self.inputpath, "r") as jf:
                prefs = json.load(jf)
                jf.close()
        except (OSError, IOError) as e:
            print("keKit: Prefs Load Error:", e)
            pass
        # Assigning properties prefs file -> add-on prefs
        if prefs is not None and ap is not None:
            for key in prefs:
                if key in ap.__annotations__.keys():
                    v = prefs[key]
                    try:
                        setattr(ap, key, v)
                    except Exception as e:
                        print("keKit Prefs Import - Key not found: ", e)
            self.report({"INFO"}, "keKit Perferences Imported!")
        else:
            print("keKIT Load Settings: Path/JSON File Error")
        refresh_ui()
        return {'FINISHED'}


class KeResetPrefs(Operator):
    bl_idname = "kekit.prefs_reset"
    bl_label = "Reset keKit Settings"
    bl_description = "Reset keKit settings to default values"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        prefs = get_prefs()
        props = prefs.__annotations__.keys()
        for k in props:
            prefs.property_unset(k)
        refresh_ui()
        return {'FINISHED'}


class KePropToggle(Operator):
    bl_idname = "ke.prop_toggle"
    bl_label = "keKit Property Toggle"
    bl_description = "Toggle keKit Properties - Boolean On/Off props only\n" \
                     "Set as shortcut - Assign prop name to shortcut prop field"
    bl_options = {"INTERNAL"}

    prop: bpy.props.StringProperty()

    def execute(self, context):
        k = get_prefs()
        k[self.prop] = not k[self.prop]
        refresh_ui()
        return {"FINISHED"}


# TBD:
# class KeKitTempSession(PropertyGroup):
#     # Session (WM) Stored "temp"
#     int = IntProperty()


class KeKitPropertiesTemp(PropertyGroup):
    # Scene Stored "temp"
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
    material_extras: BoolProperty(name="Material Buttons", default=False,
                                  description="Adds extra buttons in Material Properties Surface for:\n"
                                              "'Sync Viewport Display'. Use 'Reload Addons' to apply")
    experimental: BoolProperty(name="Experimental", default=False,
                               description="Toggle properties/features that work - but has some quirks\n"
                                           "See keKit Wiki for details.")
    # MODAL COLORS
    modal_color_header: FloatVectorProperty(name="Header Color", subtype='COLOR',
                                            size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_text: FloatVectorProperty(name="Text Color", subtype='COLOR',
                                          size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_subtext: FloatVectorProperty(name="SubText Color", subtype='COLOR',
                                             size=4, default=[0.5, 0.5, 0.5, 1.0])
    # MODULES
    m_geo: BoolProperty(name="1: Geometry", default=True, description=m_tooltip)
    m_render: BoolProperty(name="2: Render & Shade", default=True, description=m_tooltip)
    m_bookmarks: BoolProperty(name="3: Bookmarks", default=True, description=m_tooltip)
    m_selection: BoolProperty(name="4: Select & Align", default=True, description=m_tooltip)
    m_modeling: BoolProperty(name="5: Modeling", default=True, description=m_tooltip)
    m_modifiers: BoolProperty(name="6: Modifiers", default=True, description=m_tooltip)
    m_contexttools: BoolProperty(name="7: Context Tools", default=True, description=m_tooltip)
    m_tt: BoolProperty(name="8: Transform Tools", default=True, description=m_tooltip)
    m_cleanup: BoolProperty(name="9: Clean-Up Tools", default=True, description=m_tooltip)
    m_piemenus: BoolProperty(name="10: Pie Menus", default=True, description=m_tooltip)
    # SPECIAL MODULE
    kcm: BoolProperty(name="Cursor Menu", default=True,
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
    fitprim_quadsphere_seg: IntProperty(min=0, max=128, default=8)
    fitprim_shading: EnumProperty(
        items=[("FLAT", "Flat", ""), ("SMOOTH", "Smooth", ""), ("AUTO", "AutoSmooth", "")],
        name="FitPrim Default Shading", default="AUTO")
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
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="GLOBAL")
    opc1_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="MEDIAN_POINT")
    opc1_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="GLOBAL")
    opc1_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="MEDIAN_POINT")
    # Orientation & Pivot Combo 2
    opc2_obj_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="LOCAL")
    opc2_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="INDIVIDUAL_ORIGINS")
    opc2_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="NORMAL")
    opc2_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="ACTIVE_ELEMENT")
    # Orientation & Pivot Combo 3
    opc3_obj_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="GLOBAL")
    opc3_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="INDIVIDUAL_ORIGINS")
    opc3_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="LOCAL")
    opc3_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="INDIVIDUAL_ORIGINS")
    # Orientation & Pivot Combo 4
    opc4_obj_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="CURSOR")
    opc4_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="CURSOR")
    opc4_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="CURSOR")
    opc4_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="CURSOR")
    # Orientation & Pivot Combo 5
    opc5_obj_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="GLOBAL")
    opc5_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="CURSOR")
    opc5_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="GLOBAL")
    opc5_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="ACTIVE_ELEMENT")
    # Orientation & Pivot Combo 6
    opc6_obj_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="VIEW")
    opc6_obj_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="MEDIAN_POINT")
    opc6_edit_o: EnumProperty(
        items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""),
               ("VIEW", "View", ""), ("CURSOR", "Cursor", ""), ("PARENT", "Parent", "")],
        name="Orientation", default="VIEW")
    opc6_edit_p: EnumProperty(
        items=[("MEDIAN_POINT", "Median Point", ""), ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
               ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("CURSOR", "Cursor", ""),
               ("ACTIVE_ELEMENT", "Active Element", "")],
        name="Pivot", default="ACTIVE_ELEMENT")
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
    clean_collinear_val: IntProperty(name="Collinear Tolerance", min=0, max=100, default=0, subtype="PERCENTAGE",
                                     description="Increase to catch larger angle differences\n"
                                                 "Note: There is a very small tolerance even at 0")
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
    limit_surface: BoolProperty(name="Use Limit Surface", description="Use Limit Surface", default=False)
    optimal_display: BoolProperty(name="Use Optimal Display", description="Use Optimal Display", default=True)
    em_vis: BoolProperty(name="Edit-Mode Visibility", description="Edit-Mode Visibility", default=True)
    on_cage: BoolProperty(name="On Cage", description="Show On Edit Cage", default=False)
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
    snap_elements_ind1: StringProperty(description="Snapping Element Combo 1", default="FACE_PROJECT")
    snap_elements_ind2: StringProperty(description="Snapping Element Combo 2", default="FACE_PROJECT")
    snap_elements_ind3: StringProperty(description="Snapping Element Combo 3", default="FACE_PROJECT,FACE_NEAREST")
    snap_elements_ind4: StringProperty(description="Snapping Element Combo 4", default="FACE_PROJECT")
    snap_elements_ind5: StringProperty(description="Snapping Element Combo 5", default="FACE_PROJECT")
    snap_elements_ind6: StringProperty(description="Snapping Element Combo 6", default="FACE_PROJECT")
    snap_targets1: StringProperty(description="Snapping Targets Combo 1", default="ACTIVE")
    snap_targets2: StringProperty(description="Snapping Targets Combo 2", default="CLOSEST")
    snap_targets3: StringProperty(description="Snapping Targets Combo 3", default="ACTIVE")
    snap_targets4: StringProperty(description="Snapping Targets Combo 4", default="ACTIVE")
    snap_targets5: StringProperty(description="Snapping Targets Combo 5", default="ACTIVE")
    snap_targets6: StringProperty(description="Snapping Targets Combo 6", default="ACTIVE")
    snap_bools1: BoolVectorProperty(
        description="Snapping Bools Combo 1", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    snap_bools2: BoolVectorProperty(
        description="Snapping Bools Combo 2", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    snap_bools3: BoolVectorProperty(
        description="Snapping Bools Combo 3", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    snap_bools4: BoolVectorProperty(
        description="Snapping Bools Combo 4", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    snap_bools5: BoolVectorProperty(
        description="Snapping Bools Combo 5", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    snap_bools6: BoolVectorProperty(
        description="Snapping Bools Combo 6", size=11,
        default=[True, False, False, False, False, False, False, False, False, False, False])
    # snap combo naming
    snap_name1: StringProperty(description="Snapping Combo 1 Name", default="Snap Combo 1")
    snap_name2: StringProperty(description="Snapping Combo 2 Name", default="Snap Combo 2")
    snap_name3: StringProperty(description="Snapping Combo 3 Name", default="Snap Combo 3")
    snap_name4: StringProperty(description="Snapping Combo 4 Name", default="Snap Combo 4")
    snap_name5: StringProperty(description="Snapping Combo 5 Name", default="Snap Combo 5")
    snap_name6: StringProperty(description="Snapping Combo 6 Name", default="Snap Combo 6")
    # Auto activation Option
    combo_autosnap: BoolProperty(name="Auto-Activate Snap", default=False,
                                 description="Auto activate snapping mode when using snap combo")
    # paste+
    plus_mpoint: BoolProperty(name="P", default=False,
                              description="Paste+ at Mouse Point\n"
                                          "ON: Places pasted Object(s) at Mouse Point.  OFF: Original location")
    plus_merge: BoolProperty(name="M", default=False,
                             description="Paste+ Object Mode Merge\n"
                                         "ON: Merges Pasted items with selected(Active Object) (in Object Mode)\n"
                                         "OFF: Always Paste items into New Object (in Object Mode)")
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
    # Direct Loop Cut -  sel only
    dlc_so: BoolProperty(name="Selection Only", default=False,
                         description="ON: Pre-selected element only (& nearest selected edge in face selection)\n"
                                     "OFF: Picks Edge by Mouse position (Fallback to pre-selected, if in space)\n"
                                     "Note: Affects all 'Direct' operators")
    # Shading Toggle Tri mode
    shading_tris: BoolProperty(name="Flat Shading Triangulate", default=False,
                               description="Flat Shading Triangulate:\n"
                                           "Use Triangulate Modifier (always last) for more accurate flat shading")
    # Frame All Mesh Only
    frame_mo: BoolProperty(name="Geo Only", default=False,
                           description="Ignore non-geo objects (lights, cameras etc) for Frame All (not selected)")
    # Mouse Axis Move - Scale ignore
    mam_scl: BoolProperty(name="MAS",
                          description="Mouse Axis Scale - Uncheck for default (unlocked) Scale behaviour for "
                                      "TT Scale MouseAxis", default=True)
    # korean toggle
    korean: BoolProperty(
        name="Flat Profile Bevels", default=False,
        description="Toggles flat profile (aka 'Korean/Solid/Square bevels') bevel preset (2-seg, 1-profile)\n"
                    "for Context Bevel and keKit SubD pie menu bevels")
    # select by display type active collection only toggle
    sel_type_coll: BoolProperty(name="Active Collection Only",
                                description="Select by display type in active collection only",
                                default=False)
    # Unbevel Auto-Edge Ring
    unbevel_autoring: BoolProperty(name="Unbevel Auto-EdgeRing", default=False,
                                   description="Runs Edge-Ring selection before Unbevel")
    # Context Select Object Mode Full Hierarchy
    context_select_h: BoolProperty(name="Full Hierarchy Select", default=False,
                                   description="Context Select - OBJECT MODE Full Hierarchy\n"
                                               "(not just the children, but the parents too)\n"
                                               "Note: Also applies to Extend/Subtract")
    # Context Select - Vertex Mode Behaviour
    context_select_b: BoolProperty(name="Vertex Mode Behaviour", default=False,
                                   description="On - Selects open boundaries, if any, in connected geo\n"
                                               "Off - Selects connected geo")
    context_select_c: BoolProperty(name="Collection Select", default=False,
                                   description="Context Select - Select All Objects in selected object's Collection\n"
                                               "(in OBJECT MODE)")
    # Auto-Apply Scale
    apply_scale: BoolProperty(name="Auto-Apply Scale", description="Apply Scale before operation", default=True)
    # Mouse Axis Scale Mode
    mam_scale_mode: BoolProperty(name="Scale Constrain", default=False,
                                 description="When mouse is over selected object(s) use non-constrained scale.\n"
                                             "Else, use axis constrain relative to mouse (default mouse axis move)")
    # Show / Hide SubMenus
    show_modules: BoolProperty(name="keKit Modules", default=False)
    show_ui: BoolProperty(name="keKit UI Settings", default=False)
    show_shortcuts: BoolProperty(name="Show Assigned keKit Shortcuts", default=False)
    show_conflicts: BoolProperty(name="Show Possible Shortcut Conflicts", default=False)
    # Toggle Weights
    toggle_same: BoolProperty(default=True, name="Toggle All Same",
                              description="Set all weights to the same (most common) value AFTER toggling\n"
                                          "(All will be 1 if already mostly 1 and vice versa, else inverted)")
    toggle_add: BoolProperty(default=True, name="Toggle & Add Modifier",
                             description="Adds a Bevel (Weights) or SubD Toggle (Crease) mod if not already present")
    # Mouse Merge
    merge2mouse_ec: BoolProperty(default=True, name="Edge Mode Behaviour",
                                 description="In Edge-Mode: ON: Edge Row-Collapse, OFF: Vert Merge (all the same)")
    # Unwrap Macro
    uv_obj_seam: BoolProperty(default=True, name="Object Mode Auto-Seam",
                              description="In Object Mode, always ON\n"
                                          "In Edit Mode, always OFF")
    # UI options
    color_icons: BoolProperty(default=True, name="Color Icons",
                              description="Use custom color icons for various modules -or- just numbers (if disabled)")
    ext_tools: BoolProperty(default=False, name="Extend Tool Settings",
                            description="Extend Tool Settings menu with additional buttons\n"
                                        "Also displays buttons (but disabled) in Object Mode (to show state)")
    ext_factor: FloatProperty(default=1.0, name="Separator factor", min=0, max=999,
                          description="UI-separator value the Extend Tool Settings menu is offset (from the right)")

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

    category: StringProperty(
        name="Tab Category",
        description="Choose a name (category) for tab placement",
        default="kekit",
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout
        prefs_ui(self, layout)


classes = (
    KeKitAddonPreferences,
    KeKitPropertiesTemp,
    KeSavePrefs,
    KeLoadPrefs,
    KeFileBrowser,
    KeResetPrefs,
    KePropToggle,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.kekit_temp = PointerProperty(type=KeKitPropertiesTemp)
    # bpy.types.WindowManager.kekit_session = PointerProperty(type=KeKitTempSession)

    v = "v" + str(kekit_version[0]) + "." + str(kekit_version[1]) + str(kekit_version[2])
    bpy.context.preferences.addons[__package__].preferences.version = v


def unregister():
    save_prefs()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    try:
        del Scene.kekit_temp
    except Exception as e:
        print('keKit Temp-Props Unregister Exception: ', e)
        pass
