bl_info = {
    "name": "kekit_prefs",
    "author": "Kjell Emanuelsson",
    "category": "preferences",
    "version": (2, 0, 2),
    "blender": (2, 80, 0),
}
import bpy
import rna_keymap_ui
from bpy import utils
import json
from bpy.types import (
        PropertyGroup,
        Operator,
        Scene,
        AddonPreferences,
        Menu
        )
from bpy.props import (
        BoolProperty,
        PointerProperty,
        FloatVectorProperty,
        IntProperty,
        FloatProperty,
        EnumProperty,
        StringProperty,
        BoolVectorProperty
        )

# -------------------------------------------------------------------------------------------------
# EXTERNAL FILE PREFS
# -------------------------------------------------------------------------------------------------
# IO

def write_prefs(data):
    jsondata = json.dumps(data, indent=1, ensure_ascii=True)
    wpath = utils.script_path_user()
    file_name = wpath + "/ke_prefs" + ".json"
    with open(file_name, "w") as text_file:
        text_file.write(jsondata)
    text_file.close()


def read_prefs():
    wpath = utils.script_path_user()
    file_name = wpath + "/ke_prefs.json"
    try:
        with open(file_name, "r") as jf:
            prefs = json.load(jf)
            jf.close()
    except (OSError,IOError):
        prefs = None
    return prefs


def get_scene_prefs(context):
    pd = {}
    for key in context.scene.kekit.__annotations__.keys():
        k = getattr(context.scene.kekit, key)
        if str(type(k)) == "<class 'bpy_prop_array'>":
            pd[key] = k[:]
        else:
            pd[key] = k
    return  pd


# DEFAULTS

default_values = {
    'fitprim_select'		: False,
    'fitprim_modal'			: True,
    'fitprim_item'			: False,
    'fitprim_sides'			: 16,
    'fitprim_sphere_seg'	: 32,
    'fitprim_sphere_ring'	: 16,
    'fitprim_unit'			: 0.2,
    'fitprim_quadsphere_seg': 8,
    'unrotator_reset'		: True,
    'unrotator_connect'		: True,
    'unrotator_nolink'		: False,
    'unrotator_nosnap'		: False,
    'unrotator_invert'		: False,
    'unrotator_center'		: False,
    'opc1_obj_o'			: "1GLOBAL",
    'opc1_obj_p'			: "1MEDIAN_POINT",
    'opc1_edit_o'			: "1GLOBAL",
    'opc1_edit_p'			: "1MEDIAN_POINT",
    'opc2_obj_o'			: "2LOCAL",
    'opc2_obj_p'			: "3INDIVIDUAL_ORIGINS",
    'opc2_edit_o'			: "3NORMAL",
    'opc2_edit_p'			: "5ACTIVE_ELEMENT",
    'opc3_obj_o'			: "1GLOBAL",
    'opc3_obj_p'			: "3INDIVIDUAL_ORIGINS",
    'opc3_edit_o'			: "2LOCAL",
    'opc3_edit_p'			: "3INDIVIDUAL_ORIGINS",
    'opc4_obj_o'			: "6CURSOR",
    'opc4_obj_p'			: "4CURSOR",
    'opc4_edit_o'			: "6CURSOR",
    'opc4_edit_p'			: "4CURSOR",
    'selmode_mouse'			: False,
    'quickmeasure'			: True,
    'fit2grid'				: 0.01,
    'vptransform'			: False,
    'loc_got'				: True,
    'rot_got'				: True,
    'scl_got'				: True,
    'qs_user_value'			: 1.0,
    'qs_unit_size'			: True,
    'clean_doubles'			: True,
    'clean_doubles_val'		: 0.0001,
    'clean_loose'			: True,
    'clean_interior'		: True,
    'clean_degenerate'		: True,
    'clean_degenerate_val'	: 0.0001,
    'clean_collinear'		: True,
    'cursorfit'				: True,
    'lineararray_go'		: False,
    'idm01'					: (1.0, 0.0, 0.0, 1.0),
    'idm02'					: (0.6, 0.0, 0.0, 1.0),
    'idm03'					: (0.3, 0.0, 0.0, 1.0),
    'idm04'					: (0.0, 1.0, 0.0, 1.0),
    'idm05'					: (0.0, 0.6, 0.0, 1.0),
    'idm06'					: (0.0, 0.3, 0.0, 1.0),
    'idm07'					: (0.0, 0.0, 1.0, 1.0),
    'idm08'					: (0.0, 0.0, 0.6, 1.0),
    'idm09'					: (0.0, 0.0, 0.3, 1.0),
    'idm10'					: (1.0, 1.0, 1.0, 1.0),
    'idm11'					: (0.5, 0.5, 0.5, 1.0),
    'idm12'					: (0.0, 0.0, 0.0, 1.0),
    'idm01_name'			: "ID_RED",
    'idm02_name'			: "ID_RED_M",
    'idm03_name'			: "ID_RED_L",
    'idm04_name'			: "ID_GREEN",
    'idm05_name'			: "ID_GREEN_M",
    'idm06_name'			: "ID_GREEN_L",
    'idm07_name'			: "ID_BLUE",
    'idm08_name'			: "ID_BLUE_M",
    'idm09_name'			: "ID_BLUE_L",
    'idm10_name'			: "ID_ALPHA",
    'idm11_name'			: "ID_ALPHA_M",
    'idm12_name'			: "ID_ALPHA_L",
    'object_color' 			: False,
    'matvp_color' 			: False,
    'vpmuted' 				: False,
    'vp_level' 				: 2,
    'render_level' 			: 2,
    'flat_edit' 			: False,
    'boundary_smooth'		: "PRESERVE_CORNERS",
    'limit_surface'			: False,
    'optimal_display'		: True,
    'on_cage'				: False,
    'snap_elements1'        : "INCREMENT",
    'snap_elements2'        : "INCREMENT",
    'snap_elements3'        : "INCREMENT",
    'snap_elements4'        : "INCREMENT",
    'snap_targets1'         : "ACTIVE",
    'snap_targets2'         : "ACTIVE",
    'snap_targets3'         : "ACTIVE",
    'snap_targets4'         : "ACTIVE",
    'snap_bools1'           : [True, False, False, True, False, False, True, False, False],
    'snap_bools2'           : [True, False, False, True, False, False, True, False, False],
    'snap_bools3'           : [True, False, False, True, False, False, True, False, False],
    'snap_bools4'           : [True, False, False, True, False, False, True, False, False],
    'paste_merge'           : True,
    'opc1_name'             : "OPC1",
    'opc2_name'             : "OPC2",
    'opc3_name'             : "OPC3",
    'opc4_name'             : "OPC4",
    'h_delete'              : False,
    'tt_hide'               : False,
    'tt_mode'               : [True, False, False],
    'tt_handles'            : True,
    'tt_select'             : True,
    'tt_extrude'            : False,
    'renderslotcycle'       : False,
    'ra_autoarrange'        : True,
    'renderslotfullwrap'    : False,
    'getset_ep'             : False,
    'mc_relative'           : 10,
    'mc_fixed'              : 0,
    'mc_center'             : True,
    'mc_prefs'              : [0.1, 0, 0, 0,
                               0.1, 1, 0, 0,
                               0.05, 1, 0, 0,
                               0.05, 0, 0, 0,
                               0, 0, 0.05, 1,
                               0, 1, 0.05, 1,
                               0, 1, 0.01, 1,
                               0, 0, 0.01, 1],
    'mc_name0'		        : "10-90",
    'mc_name1'			    : "10-50-90",
    'mc_name2'			    : "5-50-95",
    'mc_name3'			    : "5-95",
    'mc_name4'			    : "5 cm",
    'mc_name5'			    : "5 cm (C)",
    'mc_name6'			    : "1 cm (C)",
    'mc_name7'			    : "1 cm",
    'snap_name1'            : "Snap Combo 1",
    'snap_name2'            : "Snap Combo 2",
    'snap_name3'            : "Snap Combo 3",
    'snap_name4'            : "Snap Combo 4",
    'tt_linkdupe'           : False

}

# PROCESS

path = utils.script_path_user()
v = read_prefs()

# Default values if no prefs-file
if not v:
    v = default_values
    write_prefs(v)
    print("keKit Prefs file not found - Default settings applied")

# Update prefs if new prop is added
elif len(default_values) > len(v):
    for p in default_values:
        if p not in v:
            v[p] = default_values.get(p)
    write_prefs(v)
    print("keKit Prefs is old/missing items - Prefs updated")

else:
    # print("keKit Prefs location:", path)
    print("keKit Prefs found - File Settings Applied :", path)


# PROPERTIES

class kekit_properties(PropertyGroup):
    # Fitprim
    fitprim_select : BoolProperty(default=v["fitprim_select"])
    fitprim_modal : BoolProperty(default=v["fitprim_modal"])
    fitprim_item : BoolProperty(default=v["fitprim_item"])
    fitprim_sides : IntProperty(min=3, max=256, default=v["fitprim_sides"])
    fitprim_sphere_seg : IntProperty(min=3, max=256, default=v["fitprim_sphere_seg"])
    fitprim_sphere_ring : IntProperty(min=3, max=256, default=v["fitprim_sphere_ring"])
    fitprim_unit : FloatProperty(min=.00001, max=256, default=v["fitprim_unit"])
    fitprim_quadsphere_seg : IntProperty(min=1, max=128, default=v["fitprim_quadsphere_seg"])
    # Unrotator
    unrotator_reset : BoolProperty(default=v["unrotator_reset"])
    unrotator_connect : BoolProperty(description="Connect linked faces from selection", default=v["unrotator_connect"])
    unrotator_nolink : BoolProperty(description="Duplicated Objects will not be data-linked", default=v["unrotator_nolink"])
    unrotator_nosnap : BoolProperty(description="Toggles on face surface snapping or not",default=v["unrotator_nosnap"])
    unrotator_invert : BoolProperty(description="Invert (Z) rotation", default=v["unrotator_invert"])
    unrotator_center: BoolProperty(description="Place geo on the target face center",default=v["unrotator_center"])
    # Orientation & Pivot Combo 1
    opc1_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc1_obj_o"])
    opc1_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc1_obj_p"])
    opc1_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")], name="Orientation", default=v["opc1_edit_o"])
    opc1_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc1_edit_p"])
    # Orientation & Pivot Combo 2
    opc2_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""), ("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc2_obj_o"])
    opc2_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc2_obj_p"])
    opc2_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")], name="Orientation", default=v["opc2_edit_o"])
    opc2_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc2_edit_p"])
    # Orientation & Pivot Combo 3
    opc3_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc3_obj_o"])
    opc3_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc3_obj_p"])
    opc3_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""), ("2LOCAL", "Local", ""), ("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""), ("5VIEW", "View", ""), ("6CURSOR", "Cursor", "")],name="Orientation", default=v["opc3_edit_o"])
    opc3_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform", default=v["opc3_edit_p"])
    # Orientation & Pivot Combo 4
    opc4_obj_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=v["opc4_obj_o"])
    opc4_obj_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=v["opc4_obj_p"])
    opc4_edit_o: EnumProperty(items=[("1GLOBAL", "Global", ""),("2LOCAL", "Local", ""),("3NORMAL", "Normal", ""),("4GIMBAL", "Gimbal", ""),("5VIEW", "View", ""),("6CURSOR", "Cursor", "")],name="Orientation",default=v["opc4_edit_o"])
    opc4_edit_p: EnumProperty(items=[("1MEDIAN_POINT", "Median Point", ""),("2BOUNDING_BOX_CENTER", "Bounding Box Center", ""),("3INDIVIDUAL_ORIGINS", "Individual Origins", ""),("4CURSOR", "Cursor", ""),("5ACTIVE_ELEMENT", "Active Element", "")],name="Pivot Transform",default=v["opc4_edit_p"])
    # Mouse Over Mode Toggle
    selmode_mouse : BoolProperty(description="Mouse-Over Mode Toggle", default=v["selmode_mouse"])
    # QuickMeasure  - default: 1
    quickmeasure : BoolProperty(default=v["quickmeasure"])
    # Fit2Grid - default : 0.01
    fit2grid : FloatProperty(min=.00001, max=10000, default=v["fit2grid"])
    # ViewPlane Contextual - default : 1
    vptransform : BoolProperty(description="VPAutoGlobal - Sets Global orientation. Overrides GOT options",default=v["vptransform"])
    loc_got : BoolProperty(description="Grab GlobalOrTool - VPGrab when Global, otherwise Transform (gizmo)",default=v["loc_got"])
    rot_got : BoolProperty(description="Rotate GlobalOrTool - VPRotate when Global, otherwise Rotate (gizmo)",default=v["rot_got"])
    scl_got : BoolProperty(description="Scale GlobalOrTool - VPResize when Global, otherwise Scale (gizmo)",default=v["scl_got"])
    # Quick Scale
    qs_user_value : FloatProperty(default=v["qs_user_value"], description="Set dimension (Unit meter) or Unit sized to fit value with chosen axis. Obj & Edit mode (selection)", precision=3, subtype="DISTANCE", unit="LENGTH")
    qs_unit_size : BoolProperty(default=v["qs_unit_size"])
    # Cleaning Tools
    clean_doubles : BoolProperty(default=v["clean_doubles"])
    clean_doubles_val : FloatProperty(default=v["clean_doubles_val"], precision=4)
    clean_loose : BoolProperty(default=v["clean_loose"])
    clean_interior : BoolProperty(default=v["clean_interior"])
    clean_degenerate : BoolProperty(default=v["clean_degenerate"])
    clean_degenerate_val : FloatProperty(default=v["clean_degenerate_val"], precision=4)
    clean_collinear : BoolProperty(default=v["clean_collinear"])
    # Cursor Fit OP Option
    cursorfit : BoolProperty(description="Also set Orientation & Pivot to Cursor", default=v["cursorfit"])
    # Linear Array Global Only Option
    lineararray_go : BoolProperty(description="Applies Rotation and usese Global Orientation & Pivot during modal", default=v["lineararray_go"])
    # Material ID Colors
    idm01 : FloatVectorProperty(name="IDM01", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm01"])
    idm02 : FloatVectorProperty(name="IDM02", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm02"])
    idm03 : FloatVectorProperty(name="IDM03", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm03"])
    idm04 : FloatVectorProperty(name="IDM04", subtype='COLOR', size=4, min=0.0, max=1.0, default=v["idm04"])
    idm05 : FloatVectorProperty(name="IDM05", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm05'])
    idm06 : FloatVectorProperty(name="IDM06", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm06'])
    idm07 : FloatVectorProperty(name="IDM07", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm07'])
    idm08 : FloatVectorProperty(name="IDM08", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm08'])
    idm09 : FloatVectorProperty(name="IDM09", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm09'])
    idm10 : FloatVectorProperty(name="IDM10", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm10'])
    idm11 : FloatVectorProperty(name="IDM11", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm11'])
    idm12 : FloatVectorProperty(name="IDM12", subtype='COLOR', size=4, min=0.0, max=1.0, default=v['idm12'])
    # Material ID Names
    idm01_name : StringProperty(default=v["idm01_name"])
    idm02_name : StringProperty(default=v["idm02_name"])
    idm03_name : StringProperty(default=v["idm03_name"])
    idm04_name : StringProperty(default=v["idm04_name"])
    idm05_name : StringProperty(default=v["idm05_name"])
    idm06_name : StringProperty(default=v["idm06_name"])
    idm07_name : StringProperty(default=v["idm07_name"])
    idm08_name : StringProperty(default=v["idm08_name"])
    idm09_name : StringProperty(default=v["idm09_name"])
    idm10_name : StringProperty(default=v["idm10_name"])
    idm11_name : StringProperty(default=v["idm11_name"])
    idm12_name : StringProperty(default=v["idm12_name"])
    # Material ID Options
    object_color : BoolProperty(description="Set ID color also to Object Viewport Display",default=v["object_color"])
    matvp_color : BoolProperty(description="Set ID color also to Material Viewport Display", default=v["matvp_color"])
    vpmuted : BoolProperty(description="Tone down ID colors slightly for Viewport Display (only)", default=v["vpmuted"])
    # Subd Toggle
    vp_level : IntProperty(min=0, max=64,description="Viewport Levels to be used", default=v["vp_level"]) # 2
    render_level : IntProperty(min=0, max=64, description="Render Levels to be used", default=v["render_level"]) # 2
    flat_edit : BoolProperty(description="Set Flat Shading when Subd is Level 0", default=v["flat_edit"]) # False
    boundary_smooth : EnumProperty(items=[("PRESERVE_CORNERS", "Preserve Corners", ""),("ALL", "All", "")],description="Controls how open boundaries are smoothed",default=v["boundary_smooth"])
    limit_surface : BoolProperty(description="Use Limit Surface", default=v["limit_surface"]) # False
    optimal_display : BoolProperty(description="Use Optimal Display", default=v["optimal_display"]) # True
    on_cage : BoolProperty(description="Show On Edit Cage", default=v["on_cage"]) # False
    # Snapping Combos
    snap_elements1 : StringProperty(description="Snapping Element Combo 1", default=v["snap_elements1"])
    snap_elements2 : StringProperty(description="Snapping Element Combo 2", default=v["snap_elements2"])
    snap_elements3 : StringProperty(description="Snapping Element Combo 3", default=v["snap_elements3"])
    snap_elements4 : StringProperty(description="Snapping Element Combo 4", default=v["snap_elements4"])
    snap_targets1 : StringProperty(description="Snapping Targets Combo 1", default=v["snap_targets1"])
    snap_targets2 : StringProperty(description="Snapping Targets Combo 2", default=v["snap_targets2"])
    snap_targets3 : StringProperty(description="Snapping Targets Combo 3", default=v["snap_targets3"])
    snap_targets4 : StringProperty(description="Snapping Targets Combo 4", default=v["snap_targets4"])
    snap_bools1 : BoolVectorProperty(description="Snapping Bools Combo 1", size=9, default=v["snap_bools1"])
    snap_bools2 : BoolVectorProperty(description="Snapping Bools Combo 2", size=9, default=v["snap_bools2"])
    snap_bools3 : BoolVectorProperty(description="Snapping Bools Combo 3", size=9, default=v["snap_bools3"])
    snap_bools4 : BoolVectorProperty(description="Snapping Bools Combo 4", size=9, default=v["snap_bools4"])
    # paste+ merge option
    paste_merge : BoolProperty(description="(Paste+ Object Mode) ON:Merge (edit mode) cache to selected object. OFF:Make new object", default=v["paste_merge"])
    # OPC naming
    opc1_name : StringProperty(description="Name OPC1", default=v["opc1_name"])
    opc2_name : StringProperty(description="Name OPC2", default=v["opc2_name"])
    opc3_name : StringProperty(description="Name OPC3", default=v["opc3_name"])
    opc4_name : StringProperty(description="Name OPC4", default=v["opc4_name"])
    # Context Delete Hierarchy
    h_delete : BoolProperty(description="And the children too (in Object Mode)", default=v["h_delete"])
    # Transform Toggle
    tt_hide : BoolProperty(description="Hide the viewport TT Toggle header icons", default=v["tt_hide"])
    tt_mode : BoolVectorProperty(description="Toggles between default transform tools, MouseAxis or VP", size=3, default=v["tt_mode"])
    tt_handles : BoolProperty(description="TT Default uses the handle tools or the classic style ('Grab' etc.)", default=v["tt_handles"])
    tt_select : BoolProperty(description="Switches to Select Tool if default handle tools are active when toggling TT", default=v["tt_select"])
    tt_extrude : BoolProperty(description="Use TT Mode for transform: Default, MouseAxis and VP, except faces", default=v["tt_extrude"])
    tt_linkdupe : BoolProperty(description="Global TT Duplicate Linked Toggle (includes Mouse Axis Dupe & VP Dupe)", default=v["tt_linkdupe"])
    # Use Render Slot Cycling
    renderslotcycle : BoolProperty(description="Enable render slot cycling (to the first empty render slot)", default=v["renderslotcycle"])
    # radial array autoarrange
    ra_autoarrange : BoolProperty(description="Auto-arrange object to Radial Array or use current placement", default=v["ra_autoarrange"])
    # RISC notify or wrap to 1st toggle
    renderslotfullwrap : BoolProperty(description="Full-Wrap: Back to 1st slot when full and cycle step fwd, or stop and notify", default=v["renderslotfullwrap"])
    # Get Set Edit Mode Element Pick
    getset_ep : BoolProperty(name="Get & Set Edit with Element Pick", description="(In Edit Mode) Component Mode based on element under mouse (Vert, Edge or Face)", default=v["getset_ep"])
    # Multi Cut prefs
    mc_relative : IntProperty(name="Relative Offset from endpoint. Mirrored automatically to the other end point.", min=1, max=49, default=v["mc_relative"], subtype="PERCENTAGE")
    mc_fixed : FloatProperty(name="Fixed Offset from endpoint. Mirrored automatically to the other end point.", min=0, default=v["mc_fixed"], subtype="DISTANCE", unit="LENGTH")
    mc_center : IntProperty(name="Center Cut. 1 or 0 for none.", min=0, max=1, default=v["mc_center"])
    mc_prefs : FloatVectorProperty(size=32, default=v["mc_prefs"])
    mc_name0 : StringProperty(description="MultiCut Preset 1", default=v["mc_name0"])
    mc_name1 : StringProperty(description="MultiCut Preset 2", default=v["mc_name1"])
    mc_name2 : StringProperty(description="MultiCut Preset 3", default=v["mc_name2"])
    mc_name3 : StringProperty(description="MultiCut Preset 4", default=v["mc_name3"])
    mc_name4 : StringProperty(description="MultiCut Preset 5", default=v["mc_name4"])
    mc_name5 : StringProperty(description="MultiCut Preset 6", default=v["mc_name5"])
    mc_name6 : StringProperty(description="MultiCut Preset 7", default=v["mc_name6"])
    mc_name7 : StringProperty(description="MultiCut Preset 8", default=v["mc_name7"])
    # snap combo naming
    snap_name1 : StringProperty(description="Snapping Combo 1 Name", default=v["snap_name1"])
    snap_name2 : StringProperty(description="Snapping Combo 2 Name", default=v["snap_name2"])
    snap_name3 : StringProperty(description="Snapping Combo 3 Name", default=v["snap_name3"])
    snap_name4 : StringProperty(description="Snapping Combo 4 Name", default=v["snap_name4"])



# MENU OP FOR PREFS SAVING

class VIEW3D_OT_ke_prefs_save(Operator):
    bl_idname = "view3d.ke_prefs_save"
    bl_label = "Save Settings"
    bl_description = "Saves current kit settings (prefs-file, global & persistent)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    def execute(self, context):
        prefs = get_scene_prefs(context)
        write_prefs(prefs)
        self.report({"INFO"}, "keKit Settings Saved!")
        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Add-On Preferences
# -------------------------------------------------------------------------------------------------

def get_hotkey_entry_item(km, kmi_name, kmi_value):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if km.keymap_items[i].properties.name == kmi_value:
                return km_item
    return None


class kekit_addon_preferences(AddonPreferences):
    bl_idname = __package__

    modal_color_header  : FloatVectorProperty(name="Modal Header Text Color", subtype='COLOR',
                                              size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_text    : FloatVectorProperty(name="Modal Text Color", subtype='COLOR',
                                              size=4, default=[0.8, 0.8, 0.8, 1.0])
    modal_color_subtext : FloatVectorProperty(name="Modal Sub-Text Color", subtype='COLOR',
                                              size=4, default=[0.5, 0.5, 0.5, 1.0])

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop(self, 'modal_color_header')
        row = box.row()
        row.prop(self, 'modal_color_text')
        row = box.row()
        row.prop(self, 'modal_color_subtext')

        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(text='Custom Operator Hotkeys')
        col.separator()

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View Generic']
        kmi = get_hotkey_entry_item(km, 'ke.call_pie', "KE_MT_shading_pie")
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="keShading Pie - No hotkey entry found - Restore 'Global View 3d Generic'")
            # col.operator(Template_Add_Hotkey.bl_idname, text="Add hotkey entry)", icon='ZOOM_IN') # not working.skip.


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    kekit_properties,
    VIEW3D_OT_ke_prefs_save,
    kekit_addon_preferences
    )

def register():

    for cls in classes:
        utils.register_class(cls)

    Scene.kekit = PointerProperty(type=kekit_properties)

    prefs = read_prefs()
    if not prefs:
        print("keKit Prefs file not found - Default settings applied")
        write_prefs(default_values)

def unregister():

    for cls in reversed(classes):
        utils.unregister_class(cls)
    try:
        del Scene.kekit
    except Exception as e:
        print('unregister fail:\n', e)
        pass

if __name__ == "__main__":
    register()
