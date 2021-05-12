import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .node_tree import BakeWrangler_Tree_Socket, BakeWrangler_Tree_Node

#icons = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_RIGHT', 'DISCLOSURE_TRI_DOWN', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'DUPLICATE', 'TRASH', 'COLLECTION_NEW', 'NODE', 'NODE_SEL', 'WINDOW', 'WORKSPACE', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ADD', 'REMOVE', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'CHECKMARK', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'FCURVE_SNAPSHOT', 'OBJECT_HIDDEN', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'UNLINKED', 'LINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'DRIVER_DISTANCE', 'DRIVER_ROTATIONAL_DIFFERENCE', 'DRIVER_TRANSFORM', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'FILE_NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'THREE_DOTS', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'LIGHT', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'OUTPUT', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TOOL_SETTINGS', 'SHADERFX', 'MODIFIER', 'BLANK1', 'FAKE_USER_OFF', 'FAKE_USER_ON', 'VIEW3D', 'GRAPH', 'OUTLINER', 'PROPERTIES', 'FILEBROWSER', 'IMAGE', 'INFO', 'SEQUENCE', 'TEXT', 'SOUND', 'ACTION', 'NLA', 'PREFERENCES', 'TIME', 'NODETREE', 'CONSOLE', 'TRACKER', 'ASSET_MANAGER', 'NODE_COMPOSITING', 'NODE_TEXTURE', 'NODE_MATERIAL', 'UV', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'UV_DATA', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'TRACKING', 'TRACKING_BACKWARDS', 'TRACKING_FORWARDS', 'TRACKING_BACKWARDS_SINGLE', 'TRACKING_FORWARDS_SINGLE', 'TRACKING_CLEAR_BACKWARDS', 'TRACKING_CLEAR_FORWARDS', 'TRACKING_REFINE_BACKWARDS', 'TRACKING_REFINE_FORWARDS', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LIGHT_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'COMMUNITY', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'CAMERA_STEREO', 'PACKAGE', 'UGLYPACKAGE', 'EXPERIMENTAL', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'PRESET', 'RENDER_ANIMATION', 'RENDER_STILL', 'LIBRARY_DATA_BROKEN', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'LINE_DATA', 'LIBRARY_DATA_OVERRIDE', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'FACE_MAPS', 'RNA', 'RNA_ADD', 'MOUSE_LMB', 'MOUSE_MMB', 'MOUSE_RMB', 'MOUSE_MOVE', 'MOUSE_LMB_DRAG', 'MOUSE_MMB_DRAG', 'MOUSE_RMB_DRAG', 'PRESET_NEW', 'DECORATE', 'DECORATE_KEYFRAME', 'DECORATE_ANIMATE', 'DECORATE_DRIVER', 'DECORATE_LINKED', 'DECORATE_LIBRARY_OVERRIDE', 'DECORATE_UNLOCKED', 'DECORATE_LOCKED', 'DECORATE_OVERRIDE', 'FUND', 'TRACKER_DATA', 'HEART', 'ORPHAN_DATA', 'USER', 'SYSTEM', 'SETTINGS', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LIGHT', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'OUTLINER_OB_FORCE_FIELD', 'OUTLINER_OB_GROUP_INSTANCE', 'OUTLINER_OB_GREASEPENCIL', 'OUTLINER_OB_LIGHTPROBE', 'OUTLINER_OB_IMAGE', 'RESTRICT_COLOR_OFF', 'RESTRICT_COLOR_ON', 'HIDE_ON', 'HIDE_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_RENDER_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_INSTANCED_OFF', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LIGHT', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_LIGHTPROBE', 'OUTLINER_DATA_GP_LAYER', 'OUTLINER_DATA_GREASEPENCIL', 'GP_SELECT_POINTS', 'GP_SELECT_STROKES', 'GP_MULTIFRAME_EDITING', 'GP_ONLY_SELECTED', 'GP_SELECT_BETWEEN_STROKES', 'MODIFIER_OFF', 'MODIFIER_ON', 'ONIONSKIN_OFF', 'ONIONSKIN_ON', 'RESTRICT_VIEW_ON', 'RESTRICT_VIEW_OFF', 'RESTRICT_INSTANCED_ON', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'MESH_CAPSULE', 'EMPTY_SINGLE_ARROW', 'LIGHT_POINT', 'LIGHT_SUN', 'LIGHT_SPOT', 'LIGHT_HEMI', 'LIGHT_AREA', 'CUBE', 'SPHERE', 'CONE', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'EMPTY_AXIS', 'STROKE', 'EMPTY_ARROWS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'LIGHTPROBE_CUBEMAP', 'LIGHTPROBE_PLANAR', 'LIGHTPROBE_GRID', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_BLUE', 'TRIA_RIGHT_BAR', 'TRIA_DOWN_BAR', 'TRIA_LEFT_BAR', 'TRIA_UP_BAR', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'FORCE_SMOKEFLOW', 'RIGID_BODY', 'RIGID_BODY_CONSTRAINT', 'IMAGE_PLANE', 'IMAGE_BACKGROUND', 'IMAGE_REFERENCE', 'NODE_INSERT_ON', 'NODE_INSERT_OFF', 'NODE_TOP', 'NODE_SIDE', 'NODE_CORNER', 'SELECT_SET', 'SELECT_EXTEND', 'SELECT_SUBTRACT', 'SELECT_INTERSECT', 'SELECT_DIFFERENCE', 'ALIGN_LEFT', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_JUSTIFY', 'ALIGN_FLUSH', 'ALIGN_TOP', 'ALIGN_MIDDLE', 'ALIGN_BOTTOM', 'BOLD', 'ITALIC', 'UNDERLINE', 'SMALL_CAPS', 'CON_ACTION', 'HOLDOUT_OFF', 'HOLDOUT_ON', 'INDIRECT_ONLY_OFF', 'INDIRECT_ONLY_ON', 'CON_CAMERASOLVER', 'CON_FOLLOWTRACK', 'CON_OBJECTSOLVER', 'CON_LOCLIKE', 'CON_ROTLIKE', 'CON_SIZELIKE', 'CON_TRANSLIKE', 'CON_DISTLIMIT', 'CON_LOCLIMIT', 'CON_ROTLIMIT', 'CON_SIZELIMIT', 'CON_SAMEVOL', 'CON_TRANSFORM', 'CON_TRANSFORM_CACHE', 'CON_CLAMPTO', 'CON_KINEMATIC', 'CON_LOCKTRACK', 'CON_SPLINEIK', 'CON_STRETCHTO', 'CON_TRACKTO', 'CON_ARMATURE', 'CON_CHILDOF', 'CON_FLOOR', 'CON_FOLLOWPATH', 'CON_PIVOT', 'CON_SHRINKWRAP', 'MODIFIER_DATA', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'MOD_TINT', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_SMOKE', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'MOD_OCEAN', 'MOD_WARP', 'MOD_SKIN', 'MOD_TRIANGULATE', 'MOD_WIREFRAME', 'MOD_DATA_TRANSFER', 'MOD_NORMALEDIT', 'MOD_PARTICLE_INSTANCE', 'MOD_HUE_SATURATION', 'MOD_NOISE', 'MOD_OFFSET', 'MOD_SIMPLIFY', 'MOD_THICKNESS', 'MOD_INSTANCE', 'MOD_TIME', 'MOD_OPACITY', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_SOUND', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'ACTION_TWEAK', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'KEYFRAME_HLT', 'KEYFRAME', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'NLA_PUSHDOWN', 'IPO_CONSTANT', 'IPO_LINEAR', 'IPO_BEZIER', 'IPO_SINE', 'IPO_QUAD', 'IPO_CUBIC', 'IPO_QUART', 'IPO_QUINT', 'IPO_EXPO', 'IPO_CIRC', 'IPO_BOUNCE', 'IPO_ELASTIC', 'IPO_BACK', 'IPO_EASE_IN', 'IPO_EASE_OUT', 'IPO_EASE_IN_OUT', 'NORMALIZE_FCURVES', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'CURSOR', 'PIVOT_BOUNDBOX', 'PIVOT_CURSOR', 'PIVOT_INDIVIDUAL', 'PIVOT_MEDIAN', 'PIVOT_ACTIVE', 'CENTER_ONLY', 'ROOTCURVE', 'SMOOTHCURVE', 'SPHERECURVE', 'INVERSESQUARECURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PROP_PROJECTED', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'SNAP_FACE_CENTER', 'SNAP_PERPENDICULAR', 'SNAP_MIDPOINT', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_GRID', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'SNAP_INCREMENT', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'OBJECT_ORIGIN', 'ORIENTATION_GLOBAL', 'ORIENTATION_GIMBAL', 'ORIENTATION_LOCAL', 'ORIENTATION_NORMAL', 'ORIENTATION_VIEW', 'COPYDOWN', 'PASTEDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'VIS_SEL_11', 'VIS_SEL_10', 'VIS_SEL_01', 'VIS_SEL_00', 'AUTOMERGE_OFF', 'AUTOMERGE_ON', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'TRANSFORM_ORIGINS', 'GIZMO', 'ORIENTATION_CURSOR', 'NORMALS_VERTEX', 'NORMALS_FACE', 'NORMALS_VERTEX_FACE', 'SHADING_BBOX', 'SHADING_WIRE', 'SHADING_SOLID', 'SHADING_RENDERED', 'SHADING_TEXTURE', 'OVERLAY', 'XRAY', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'NDOF_DOM', 'NDOF_TURN', 'NDOF_FLY', 'NDOF_TRANS', 'LAYER_USED', 'LAYER_ACTIVE', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'SHORTDISPLAY', 'LONGDISPLAY', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'FILE_TEXT', 'SORT_DESC', 'SORT_ASC', 'LINK_BLEND', 'APPEND_BLEND', 'IMPORT', 'EXPORT', 'LOOP_BACK', 'LOOP_FORWARDS', 'BACK', 'FORWARD', 'FILE_ARCHIVE', 'FILE_CACHE', 'FILE_VOLUME', 'FILE_3D', 'FILE_HIDDEN', 'FILE_BACKUP', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'MATSHADERBALL', 'MATCLOTH', 'MATFLUID', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'DESKTOP', 'EXTERNAL_DRIVE', 'NETWORK_DRIVE', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'SEQ_STRIP_META', 'SEQ_STRIP_DUPLICATE', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'VIEW_PERSPECTIVE', 'VIEW_ORTHO', 'VIEW_CAMERA', 'VIEW_PAN', 'VIEW_ZOOM', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLAY_STRIPS', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_MASK', 'BRUSH_MIX', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_TEXDRAW', 'BRUSH_TEXFILL', 'BRUSH_TEXMASK', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'GPBRUSH_SMOOTH', 'GPBRUSH_THICKNESS', 'GPBRUSH_STRENGTH', 'GPBRUSH_GRAB', 'GPBRUSH_PUSH', 'GPBRUSH_TWIST', 'GPBRUSH_PINCH', 'GPBRUSH_RANDOMIZE', 'GPBRUSH_CLONE', 'GPBRUSH_WEIGHT', 'GPBRUSH_PENCIL', 'GPBRUSH_PEN', 'GPBRUSH_INK', 'GPBRUSH_INKNOISE', 'GPBRUSH_BLOCK', 'GPBRUSH_MARKER', 'GPBRUSH_FILL', 'GPBRUSH_AIRBRUSH', 'GPBRUSH_CHISEL', 'GPBRUSH_ERASE_SOFT', 'GPBRUSH_ERASE_HARD', 'GPBRUSH_ERASE_STROKE', 'SMALL_TRI_RIGHT_VEC', 'KEYTYPE_KEYFRAME_VEC', 'KEYTYPE_BREAKDOWN_VEC', 'KEYTYPE_EXTREME_VEC', 'KEYTYPE_JITTER_VEC', 'KEYTYPE_MOVING_HOLD_VEC', 'HANDLETYPE_FREE_VEC', 'HANDLETYPE_ALIGNED_VEC', 'HANDLETYPE_VECTOR_VEC', 'HANDLETYPE_AUTO_VEC', 'HANDLETYPE_AUTO_CLAMP_VEC', 'COLORSET_01_VEC', 'COLORSET_02_VEC', 'COLORSET_03_VEC', 'COLORSET_04_VEC', 'COLORSET_05_VEC', 'COLORSET_06_VEC', 'COLORSET_07_VEC', 'COLORSET_08_VEC', 'COLORSET_09_VEC', 'COLORSET_10_VEC', 'COLORSET_11_VEC', 'COLORSET_12_VEC', 'COLORSET_13_VEC', 'COLORSET_14_VEC', 'COLORSET_15_VEC', 'COLORSET_16_VEC', 'COLORSET_17_VEC', 'COLORSET_18_VEC', 'COLORSET_19_VEC', 'COLORSET_20_VEC', 'EVENT_A', 'EVENT_B', 'EVENT_C', 'EVENT_D', 'EVENT_E', 'EVENT_F', 'EVENT_G', 'EVENT_H', 'EVENT_I', 'EVENT_J', 'EVENT_K', 'EVENT_L', 'EVENT_M', 'EVENT_N', 'EVENT_O', 'EVENT_P', 'EVENT_Q', 'EVENT_R', 'EVENT_S', 'EVENT_T', 'EVENT_U', 'EVENT_V', 'EVENT_W', 'EVENT_X', 'EVENT_Y', 'EVENT_Z', 'EVENT_SHIFT', 'EVENT_CTRL', 'EVENT_ALT', 'EVENT_OS', 'EVENT_F1', 'EVENT_F2', 'EVENT_F3', 'EVENT_F4', 'EVENT_F5', 'EVENT_F6', 'EVENT_F7', 'EVENT_F8', 'EVENT_F9', 'EVENT_F10', 'EVENT_F11', 'EVENT_F12', 'EVENT_ESC', 'EVENT_TAB', 'EVENT_PAGEUP', 'EVENT_PAGEDOWN', 'EVENT_RETURN', 'EVENT_SPACEKEY']

#
# Bake Wrangler nodes system
#

BW_TREE_VERSION = 1

# Socket for sharing high poly mesh, or really any mesh data that should be in the bake but isn't the target
class BakeWrangler_Socket_HighPolyMesh(NodeSocket, BakeWrangler_Tree_Socket):
    '''Socket for connecting a high poly mesh node'''
    bl_label = 'Bake From'
    
    # Called to filter objects listed in the value search field. Only objects of type 'MESH' are shown.
    def value_prop_filter(self, object):
        if self.collection:
            return len(object.all_objects)
        else:
            return object.type in ['MESH', 'CURVE']
    
    # Called when the value property changes.
    def value_prop_update(self, context):
        if self.node and self.node.bl_idname == 'BakeWrangler_Input_HighPolyMesh':
            self.node.update_inputs()
    
    # Called when the collection property changes
    def collection_prop_update(self, context):
        if self.collection == False and self.value:
            self.value = None
        
    value: bpy.props.PointerProperty(name="Bake From Object(s)", description="Geometry to be part of selection when doing a 'selected to active' type bake", type=bpy.types.ID, poll=value_prop_filter, update=value_prop_update)
    collection: bpy.props.BoolProperty(name="Collection", description="When enabled whole collections will be selected instead of individual objects", update=collection_prop_update, default=False)
    recursive: bpy.props.BoolProperty(name="Recursive Selection", description="When enabled all collections within the selected collection will be used", default=False)
    
    def draw(self, context, layout, node, text):
        if node.bl_idname == 'BakeWrangler_Input_Mesh' and node.multi_res:
            layout.label(text=text + " [ignored]")
        elif not self.is_output and not self.is_linked and node.bl_idname != 'BakeWrangler_Input_Mesh':
            row = layout.row()
            if self.collection:
                if self.value:
                    row.prop_search(self, "value", context.scene.collection, "children", text="", icon='GROUP')
                else:
                    row.prop(self, "collection", icon='GROUP', text="")
                    row.prop_search(self, "value", context.scene.collection, "children", text="", icon='NONE')
                row.prop(self, "recursive", icon='OUTLINER', text="")
            else:
                ico = 'NONE'
                if self.value:
                    obj = bpy.types.Object(self.value)
                    if  obj.type == 'MESH':
                        ico = 'MESH_DATA'
                    elif obj.type == 'CURVE':
                        ico = 'CURVE_DATA'
                else:
                    row.prop(self, "collection", icon='GROUP', text="")
                row.prop_search(self, "value", context.scene, "objects", text="", icon=ico)
        else:
            layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))

    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (0.0, 0.2, 1.0, 1.0))

            
# Input node that takes any number of objects that should be selected during a bake
class BakeWrangler_Input_HighPolyMesh(Node, BakeWrangler_Tree_Node):
    '''High poly mesh data node'''
    bl_label = 'Bake From'
    
    # Makes sure there is always one empty input socket at the bottom by adding and removing sockets
    def update_inputs(self):
        BakeWrangler_Tree_Node.update_inputs(self, 'BakeWrangler_Socket_HighPolyMesh', "Bake From")
    
    # Returns a list of all chosen mesh objects. May recurse through multiple connected nodes.
    def get_objects(self):
        objects = []
        for input in self.inputs:
            if not input.is_linked:
                if input.value:
                    if input.collection:
                        col_objects = []
                        if input.recursive:
                            col_objects = input.value.all_objects
                        else:
                            col_objects = input.value.objects
                        visible_objects = [ob for ob in col_objects if ob.type in ['MESH', 'CURVE']]
                        for ob in visible_objects:
                            objects.append(ob)
                    else:
                        objects.append(input.value)
            else:
                linked_objects = []
                if input.links[0].is_valid and input.valid:
                    linked_objects = input.links[0].from_node.get_objects()
                if len(linked_objects):
                    objects.extend(linked_objects)
        return objects
    
    def init(self, context):
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_HighPolyMesh', "Bake From")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_HighPolyMesh', "Bake From")
  
    def draw_buttons(self, context, layout):
        layout.label(text="Objects:")

        
# Input node that takes a single target mesh and its bake settings. High poly mesh nodes can be added as input.
class BakeWrangler_Input_Mesh(Node, BakeWrangler_Tree_Node):
    '''Mesh data and settings node'''
    bl_label = 'Mesh'
    bl_width_default = 146
    
    # Returns the most identifing string for the node
    def get_name(self):
        name = BakeWrangler_Tree_Node.get_name(self)
        if self.mesh_object:
            name += " (%s)" % (self.mesh_object.name)
        return name
        
    def update_inputs(self):
        pass
    
    # Check node settings are valid to bake. Returns true/false, plus error message.
    def validate(self, check_materials=False):
        valid = [True]
        # Is a mesh selected?
        if not self.mesh_object:
            valid[0] = False
            valid.append(_print("No valid mesh object selected", node=self, ret=True))
        # Check for multires modifier if multires is enabled
        if self.multi_res and self.mesh_object:
            has_multi_mod = False
            if len(self.mesh_object.modifiers):
                for mod in self.mesh_object.modifiers:
                    if mod.type == 'MULTIRES' and mod.total_levels > 0:
                        has_multi_mod = True
                        break
            if not has_multi_mod:
                valid[0] = False
                valid.append(_print("Multires enabled but no multires data on selected mesh object", node=self, ret=True))
        # Check cage if enabled
        if self.cage:
            if not self.cage_obj:
                valid[0] = False
                valid.append(_print("Cage enabled but no cage object selected", node=self, ret=True))
            if self.mesh_object and self.cage_obj and len(self.mesh_object.data.polygons) != len(self.cage_obj.data.polygons):
                    valid[0] = False
                    valid.append(_print("Cage object face count does not match mesh object", node=self, ret=True))
            if self.mesh_object and len(self.get_objects()) < 2:
                valid[0] = False
                valid.append(_print("Cage enabled but no high poly objects selected", node=self, ret=True))
        # Check valid UV Map
        if self.mesh_object and len(self.mesh_object.data.uv_layers) < 1:
            valid[0] = False
            valid.append(_print("Mesh object has no UV map(s)", node=self, ret=True))
        if self.mesh_object and len(self.mesh_object.data.uv_layers) > 1 and self.uv_map and self.uv_map not in self.mesh_object.data.uv_layers:
            valid[0] = False
            valid.append(_print("Selected UV map not present on object (it could have been deleted or renamed)", node=self, ret=True))
        # Validated?
        if not valid[0]:
            return valid
        
        # Valid, should materials also be checked?
        if check_materials:
            # Some bake types need to modify the materials, check if this can be done. A failure wont invalidate
            # but warnings will be issued about the materails that fail.
            mats = []
            others = self.get_objects()
            if self.multi_res or len(others) < 2:
                # Just check self materials
                if len(self.mesh_object.data.materials):
                    for mat in self.mesh_object.data.materials:
                        if mats.count(mat) == 0:
                            mats.append(mat)
            else:
                # Just check not self materials
                others.pop(0)
                for obj in others:
                    if len(obj.data.materials):
                        for mat in obj.data.materials:
                            if mats.count(mat) == 0:
                                mats.append(mat)
            
            # Go through the list of materials and see if they will pass the prep phase
            for mat in mats:
                nodes = mat.node_tree.nodes
                node_outputs = []
                passed = False
                
                # Not a node based material or not enough nodes to be valid
                if not nodes or len(nodes) < 2:
                    valid.append(_print("'%s' not node based or too few nodes" % (mat.name), node=self, ret=True))
                    continue
                
                # Collect all outputs
                for node in nodes:
                    if node.type == 'OUTPUT_MATERIAL':
                        if node.target == 'CYCLES' or node.target == 'ALL':
                            node_outputs.append(node)
                            
                # Try to find at least one usable node pair from the outputs
                for node in node_outputs:
                    passed = material_recursor(node)
                    if passed:
                        break
                
                # Didn't find any usable node pairs
                if not passed:
                    valid.append(_print("'%s' Output doesn't appear to be a valid combination of Principled and Mix shaders. Baked values will not be correct for this material." % (mat.name), node=self, ret=True))
                     
        return valid
    
    # Returns a list of all chosen mesh objects. The bake target will be at index 0, extra objects indicate
    # a 'selected to active' type bake should be performed. May recurse through multiple prior nodes. If no
    # mesh_object is set an empty list will be returned instead. Only unique objects will be returned.
    def get_objects(self):
        objects = []
        if self.mesh_object:
            objects.append(self.mesh_object)
            if not self.inputs[0].is_linked:
                if self.inputs[0].value and objects.count(self.inputs[0].value) == 0:
                    objects.append(self.inputs[0].value)
            else:
                linked_objects = []
                if self.inputs[0].links[0].is_valid and self.inputs[0].valid:
                    linked_objects = self.inputs[0].links[0].from_node.get_objects()
                if len(linked_objects):
                    for obj in linked_objects:
                        if objects.count(obj) == 0:
                            objects.append(obj)
        return objects
    
    # Filter for prop_search field used to select mesh_object
    def mesh_object_filter(self, object):
        return object.type == 'MESH'
    
    multi_res_passes = (
        ('NORMALS', "Normals", "Bake normals"),
        ('DISPLACEMENT', "Displacment", "Bake displacement"),
    )
    
    mesh_object: bpy.props.PointerProperty(name="Bake Target", description="Mesh that will be the active object during the bake", type=bpy.types.Object, poll=mesh_object_filter)
    ray_dist: bpy.props.FloatProperty(name="Ray Distance", description="Distance to use for inward ray cast when using a selected to active bake", default=0.01, step=1, min=0.0, unit='LENGTH')
    margin: bpy.props.IntProperty(name="Margin", description="Extends the baked result as a post process filter", default=0, min=0, subtype='PIXEL')
    mask_margin: bpy.props.IntProperty(name="Mask Margin", description="Adds extra padding to the mask bake. Use if edge details are being cut off", default=0, min=0, subtype='PIXEL')
    multi_res: bpy.props.BoolProperty(name="Multires", description="Bake directly from multires object. This will disable or ignore the other bake settings.\nOnly Normals and Displacment can be baked")
    multi_res_pass: bpy.props.EnumProperty(name="Pass", description="Choose shading information to bake into the image.\nMultires pass will override any connected bake pass", items=multi_res_passes, default='NORMALS')
    cage: bpy.props.BoolProperty(name="Cage", description="Cast rays to active object from a cage. The cage must have the same number of faces")
    cage_obj: bpy.props.PointerProperty(name="Cage Object", description="Object to use as a cage instead of calculating the cage from the active object", type=bpy.types.Object, poll=mesh_object_filter)
    uv_map: bpy.props.StringProperty(name="UV Map", description="Pick map to bake if object has multiple layers. Leave blank to use active layer")
    
    def init(self, context):
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_HighPolyMesh', "Bake From")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_Mesh', "Mesh")

    def draw_buttons(self, context, layout):
        layout.label(text="Mesh Object:")
        layout.prop_search(self, "mesh_object", context.scene, "objects", text="")
        layout.prop(self, "margin", text="Margin")
        layout.prop(self, "mask_margin", text="Padding")
        if self.mesh_object and len(self.mesh_object.data.uv_layers) > 1:
            split = layout.split(factor=0.21)
            split.label(text="UV:")
            split.prop_search(self, "uv_map", self.mesh_object.data, "uv_layers", text="")
        layout.prop(self, "multi_res", text="From Multires")
        if not self.multi_res:
            if not self.cage:
                layout.prop(self, "cage", text="Cage")
            else:
                layout.prop(self, "cage", text="Cage:")
                layout.prop_search(self, "cage_obj", context.scene, "objects", text="")
            layout.label(text="Bake From:")
            layout.prop(self, "ray_dist", text="Ray Dist")
        else:
            layout.prop(self, "multi_res_pass")

# All bakery classes that need to be registered
classes = (
    BakeWrangler_Socket_HighPolyMesh,
    BakeWrangler_Input_HighPolyMesh,
    BakeWrangler_Input_Mesh,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()