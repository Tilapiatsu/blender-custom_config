bl_info = {
    "name": "Tilapiatsu Hotkeys",
    "description": "Hotkeys",
    "author": "Tilapiatsu",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Hotkeys"
    }

import bpy
import os

def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: Keymap '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def kmi_km_replace(kmi, km, *kwargs):
    try:
        setattr(kmi, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def kmi_get_kmi(km, tool_name):
    try:
        km_idname = [k.idname for k in km]
        if tool_name in km_idname:
            for k in km:
                if k.idname == tool_name:
                    pass

    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def tila_keymaps():
# Define global variables
    print("Setting Tilapiatsu's keymaps")
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    k_viewfit = 'MIDDLEMOUSE'
    k_manip = 'LEFTMOUSE'
    k_cursor = 'MIDDLEMOUSE'
    k_nav = 'MIDDLEMOUSE'
    k_menu = 'SPACE'
    k_select = 'LEFTMOUSE'
    k_lasso =  'RIGHTMOUSE'
    k_context =  'RIGHTMOUSE'
    k_more = 'UP_ARROW'
    k_less = 'UP_ARROW'
    k_linked = 'W'

# Functions
    def global_keys():
        kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
        kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
        kmi = km.keymap_items.new('screen.animation_play', k_menu, 'PRESS', shift=True)
        kmi = km.keymap_items.new("popup.hp_properties", 'V',"PRESS", ctrl=True, shift=True)

    def navigation_keys(kmis=None, pan=None, orbit=None, dolly=None):
        if orbit:
            kmi = km.keymap_items.new(orbit, k_manip, "PRESS", alt=True)
        if pan:
            kmi = km.keymap_items.new(pan, k_manip, "PRESS", alt=True, shift=True)
        if dolly:
            kmi = km.keymap_items.new(dolly, k_manip, "PRESS", alt=True, ctrl=True)

    def selection_keys( kmis=None,
                        select_tool=None, 
                        lasso_tool=None,
                        shortestpath_tool=None,  
                        loop_tool=None, ring_tool=None,  
                        more_tool=None, less_tool=None, 
                        linked_tool=None):

        if kmis:
            km_idname = [k.idname for k in kmis]

    # Select / Deselect / Add
        if select_tool:
            if select_tool in km_idname:
                for k in kmis:
                    if k.idname == select_tool:
                        pass


            kmi = km.keymap_items.new(select_tool, k_select, 'CLICK')
            kmi = km.keymap_items.new(select_tool, k_select, 'CLICK', shift=True)
            kmi_props_setattr(kmi.properties, 'extend', True)
            kmi = km.keymap_items.new(select_tool, k_select, 'CLICK', ctrl=True)
            kmi_props_setattr(kmi.properties, 'deselect', True)
    
    # Lasso Select / Deselect / Add
        if lasso_tool:
            kmi = km.keymap_items.new(select_tool, k_lasso, 'PRESS')
            kmi_props_setattr(kmi.properties, 'mode', 'SET')
            kmi = km.keymap_items.new(select_tool, k_lasso, 'PRESS', shift=True)
            kmi_props_setattr(kmi.properties, 'mode', 'ADD')
            kmi = km.keymap_items.new(select_tool, k_lasso, 'PRESS', ctrl=True)
            kmi_props_setattr(kmi.properties, 'mode', 'SUB')

    #  shortest Path Select / Deselect / Add
        if shortestpath_tool:
            kmi = km.keymap_items.new(shortestpath_tool, k_lasso, 'CLICK')

    # Loop Select / Deselect / Add
        if loop_tool:
            kmi = km.keymap_items.new(loop_tool, k_select, 'DOUBLE_CLICK')
            kmi = km.keymap_items.new(loop_tool, k_select, 'DOUBLE_CLICK', shift=True)
            kmi_props_setattr(kmi.properties, 'extend', True)
            kmi_props_setattr(kmi.properties, 'ring', False)
            kmi = km.keymap_items.new(loop_tool, k_select, 'DOUBLE_CLICK', ctrl=True)
            kmi_props_setattr(kmi.properties, 'extend', False)
            kmi_props_setattr(kmi.properties, 'deselect', True)

    # Ring Select / Deselect / Add
        if ring_tool:
            kmi = km.keymap_items.new(ring_tool, k_cursor, 'CLICK', ctrl=True)
            kmi_props_setattr(kmi.properties, 'ring', True)
            kmi_props_setattr(kmi.properties, 'deselect', True)
            kmi_props_setattr(kmi.properties, 'extend', False)
            kmi_props_setattr(kmi.properties, 'toggle', False)
            kmi = km.keymap_items.new(ring_tool, k_cursor, 'CLICK', ctrl=True, shift=True)
            kmi_props_setattr(kmi.properties, 'ring', True)
            kmi_props_setattr(kmi.properties, 'deselect', False)
            kmi_props_setattr(kmi.properties, 'extend', True)
            kmi_props_setattr(kmi.properties, 'toggle', False)
            kmi = km.keymap_items.new(ring_tool, k_cursor, 'DOUBLE_CLICK', ctrl=True)
            kmi_props_setattr(kmi.properties, 'ring', True)
            kmi_props_setattr(kmi.properties, 'deselect', True)
            kmi_props_setattr(kmi.properties, 'extend', False)
            kmi_props_setattr(kmi.properties, 'toggle', False)

    # Select More / Less
        if more_tool:
            kmi = km.keymap_items.new(more_tool, k_more, 'PRESS')

        if less_tool:
            kmi = km.keymap_items.new(less_tool, k_more, 'PRESS')

    # Linked
        if linked_tool:
            kmi = km.keymap_items.new(linked_tool, k_linked, 'PRESS')

    def selection_tool():
        kmi = km.keymap_items.new('wm.tool_set_by_name', k_menu, "PRESS")
        kmi_props_setattr(kmi.properties, 'name', 'Select')

# Window
    km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True)
    kmi = km.keymap_items.new("wm.revert_without_prompt","N","PRESS", shift=True)
    kmi = km.keymap_items.new('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)     

# 3D View
    # Replace Existing
    view3d = kc.keymaps['3D View'].keymap_items
    km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
    global_keys()
    navigation_keys(kmis=view3d,
                    pan='view3d.move',
                    orbit='view3d.rotate',
                    dolly='view3d.dolly')

    selection_keys( kmis=view3d,
                    select_tool='view3d.select', 
                    lasso_tool='view3d.select_lasso')


# View2D
    km = kc.keymaps.new('View2D', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    navigation_keys(kmis=view3d, pan='view2d.pan', orbit=None, dolly='view2d.zoom')
    
# View2D buttons List
    km = kc.keymaps.new('View2D Buttons List', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    navigation_keys(kmis=view3d, pan='view2d.pan', orbit=None, dolly='view2d.zoom')

# Image
    km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
    global_keys()
    navigation_keys(kmis=view3d, pan='image.view_pan', orbit=None, dolly='image.view_zoom')

# UV Editor
    km = kc.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()

# Mesh
    km = kc.keymaps.new(name='Mesh')
    global_keys()
    selection_tool()
    selection_keys(shortestpath_tool='mesh.shortest_path_pick',
                   loop_tool='mesh.loop_select',
                   ring_tool='mesh.loop_select',
                   more_tool='mesh.select_more',
                   less_tool='mesh.select_less',
                   linked_tool='mesh.select_linked_pick' )

# Object Mode
    km = kc.keymaps.new(name='Object Mode')
    global_keys()
    selection_tool()

# Curve
    km = kc.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    selection_tool()
    kmi = km.keymap_items.new('curve.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi = km.keymap_items.new('curve.select_linked_pick', k_select, 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.shortest_path_pick', k_select, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

# Outliner
    km = kc.keymaps.new('Outliner', space_type='OUTLINER', region_type='WINDOW', modal=False)
    global_keys()

# Dopesheet editor
    km = kc.keymaps.new('Dopesheet Editor', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
    global_keys()

# Grease Pencil
    km = kc.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()

# Graph Editor
    km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
    global_keys()

# Animation
    km = kc.keymaps.new('Animation', space_type='EMPTY', region_type='WINDOW', modal=False)

    

def hp_keymaps():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    k_viewfit = 'MIDDLEMOUSE'
    k_manip = 'LEFTMOUSE'
    k_cursor = 'RIGHTMOUSE'
    k_nav = 'MIDDLEMOUSE'
    k_menu = 'SPACE'
    k_select = 'LEFTMOUSE'
    k_lasso =  'RIGHTMOUSE'

    def global_keys():
        kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
        kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
        kmi = km.keymap_items.new('screen.animation_play', 'PERIOD', 'PRESS')
        kmi = km.keymap_items.new("popup.hp_properties", 'V',"PRESS", ctrl=True, shift=True)
    # kmi = km.keymap_items.new('gpencil.blank_frame_add', 'B', 'PRESS', key_modifier='FOUR')
# "ACCENT_GRAVE"
#Window
    km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('object.hide_viewport', 'H', 'PRESS')
    kmi = km.keymap_items.new('wm.save_homefile', 'U', 'PRESS', ctrl=True)     
    kmi = km.keymap_items.new('transform.translate', 'SPACE', 'PRESS')

    kmi = km.keymap_items.new('view3d.smart_delete', 'X', 'PRESS')
    kmi = km.keymap_items.new('mesh.dissolve_mode', 'X', 'PRESS',ctrl=True)
#kmi = km.keymap_items.new('transform.resize', 'SPACE', 'PRESS', alt=True)
    kmi = km.keymap_items.new('transform.rotate', 'C', 'PRESS')
    kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
    kmi = km.keymap_items.new("wm.revert_without_prompt","N","PRESS", alt=True)
    kmi = km.keymap_items.new("screen.redo_last","D","PRESS")
    kmi = km.keymap_items.new('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)     

    kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True).properties.name="pie.save"
    kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True, shift=True).properties.name="pie.importexport"
    kmi = km.keymap_items.new('script.reload', 'U', 'PRESS', shift=True)
    kmi = km.keymap_items.new("screen.repeat_last","THREE","PRESS", ctrl=True, shift=True)
    kmi = km.keymap_items.new("ed.undo","TWO","PRESS", ctrl=True, shift=True)
    kmi = km.keymap_items.new('popup.hp_materials', 'V', 'PRESS', shift=True)   
    kmi = km.keymap_items.new('screen.frame_jump', 'PERIOD', 'PRESS', shift=True)
# Map Image
    km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('image.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi_props_setattr(kmi.properties, 'fit_view', True)
    kmi = km.keymap_items.new('image.view_pan', k_nav, 'PRESS', shift=True)
    kmi = km.keymap_items.new('image.view_zoom', k_nav, 'PRESS', ctrl=True)

# Map Node Editor
    km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('node.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('node.select_box', 'EVT_TWEAK_L', 'ANY')
    kmi_props_setattr(kmi.properties, 'extend', True)
    kmi_props_setattr(kmi.properties, 'tweak', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map View2D
    km = kc.keymaps.new('View2D', space_type='EMPTY', region_type='WINDOW', modal=False)
# Map Animation
    km = kc.keymaps.new('Animation', space_type='EMPTY', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('anim.change_frame', k_select, 'PRESS')

    

# Map Graph Editor
    km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('graph.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('graph.cursor_set', k_cursor, 'PRESS')
    # kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
    # kmi_props_setattr(kmi.properties, 'extend', True)
    # kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
    # kmi_props_setattr(kmi.properties, 'deselect', True)
    kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', ctrl=True, shift=True)
    kmi_props_setattr(kmi.properties, 'deselect', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY')
    kmi_props_setattr(kmi.properties, 'extend', False)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', shift=True)
    kmi_props_setattr(kmi.properties, 'extend', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map UV Editor
    km = kc.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True, alt=True).properties.name="pie.rotate90"
    kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
    kmi_props_setattr(kmi.properties, 'extend', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
    kmi_props_setattr(kmi.properties, 'deselect', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
    kmi_props_setattr(kmi.properties, 'extend', True)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY')
    kmi_props_setattr(kmi.properties, 'extend', False)
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map Mask Editing
#    km = kc.keymaps.new('Mask Editing', space_type='EMPTY', region_type='WINDOW', modal=False)
#3D View
    km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('mesh.hp_extrude', 'SPACE', 'PRESS', shift=True)
    kmi = km.keymap_items.new('view3d.render_border', 'B', 'PRESS',shift=True, ctrl=True)
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
#    kmi = km.keymap_items.new('view3d.select_lasso', 'EVT_TWEAK_L', 'ANY', alt=True)
    kmi = km.keymap_items.new('view3d.view_selected', k_nav, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('view3d.move', k_nav, 'PRESS', shift=True)
    kmi = km.keymap_items.new('view3d.zoom', k_nav, 'PRESS', ctrl=True)
    kmi = km.keymap_items.new('view3d.rotate', k_nav, 'PRESS')
    kmi = km.keymap_items.new('view3d.manipulator', k_manip, 'PRESS')
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True).properties.name="pie.select"
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu, 'PRESS',ctrl=True, alt=True).properties.name="pie.rotate90"
    kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'PRESS').properties.name="pie.view"
    kmi = km.keymap_items.new('wm.call_menu_pie', k_menu,'PRESS',ctrl=True, shift=True).properties.name="pie.pivots"
    kmi = km.keymap_items.new("wm.call_menu_pie","Z","PRESS").properties.name="pie.shading"
    kmi = km.keymap_items.new("wm.call_menu_pie","D","PRESS",ctrl=True, shift=True).properties.name="pie.specials"
    kmi = km.keymap_items.new("wm.call_menu_pie","ONE","PRESS").properties.name="pie.modifiers"
    kmi = km.keymap_items.new("wm.call_menu_pie","X","PRESS",shift=True).properties.name="pie.symmetry"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'B', 'PRESS',ctrl=True).properties.name="pie.hp_boolean"
    kmi = km.keymap_items.new("screen.repeat_last","Z","PRESS",ctrl=True, alt=True)
    kmi = km.keymap_items.new("screen.repeat_last","WHEELINMOUSE","PRESS",ctrl=True, shift=True, alt=True)
    kmi = km.keymap_items.new("ed.undo","WHEELOUTMOUSE","PRESS",ctrl=True, shift=True, alt=True)
    kmi = km.keymap_items.new("view3d.screencast_keys","U","PRESS",alt=True)
    kmi = km.keymap_items.new("paint.sample_color","V","PRESS",ctrl=True, shift=True)
    kmi = km.keymap_items.new('view3d.select_lasso', k_select, 'CLICK_DRAG', shift=True, ctrl=True)
    kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', ctrl=True).properties.mode='SUB'
    kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', shift=True).properties.mode='ADD'
    kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG').properties.mode='SET'
    kmi = km.keymap_items.new("wm.search_menu","FIVE","PRESS")
    kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
    kmi = km.keymap_items.new("view3d.smart_snap_cursor","RIGHTMOUSE","PRESS",ctrl=True)
    kmi = km.keymap_items.new("view3d.smart_snap_origin","RIGHTMOUSE","PRESS",ctrl=True, shift=True)
#Mesh
    km = kc.keymaps.new(name='Mesh')
    global_keys()
    #kmi = km.keymap_items.new('view3d.extrude_normal', 'EVT_TWEAK_L', 'ANY', shift=True)
    kmi = km.keymap_items.new("mesh.dupli_extrude_cursor", 'E', 'PRESS')
    kmi = km.keymap_items.new("transform.edge_bevelweight", 'E', 'PRESS', ctrl=True, shift=True)
    #kmi = km.keymap_items.new("mesh.primitive_cube_add_gizmo", 'EVT_TWEAK_L', 'ANY', alt=True)
    kmi = km.keymap_items.new('view3d.select_through_border', k_select, 'CLICK_DRAG')
    kmi = km.keymap_items.new('view3d.select_through_border_add', k_select, 'CLICK_DRAG', shift=True)
    kmi = km.keymap_items.new('view3d.select_through_border_sub', k_select, 'CLICK_DRAG', ctrl=True)
    kmi = km.keymap_items.new("wm.call_menu_pie","A","PRESS", shift=True).properties.name="pie.add"
    kmi = km.keymap_items.new("wm.call_menu","W","PRESS").properties.name="VIEW3D_MT_edit_mesh_specials"
    kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
    kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
#    kmi = km.keymap_items.new('mesh.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
    kmi = km.keymap_items.new('mesh.shortest_path_pick', 'LEFTMOUSE', 'CLICK',ctrl=True, shift=True).properties.use_fill=True
    kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK')
    kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
    kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
    kmi = km.keymap_items.new('mesh.select_more', 'WHEELINMOUSE', 'PRESS',ctrl=True, shift=True)    
    kmi = km.keymap_items.new('mesh.select_less', 'WHEELOUTMOUSE', 'PRESS',ctrl=True, shift=True)
    kmi = km.keymap_items.new('mesh.select_more', 'Z', 'PRESS',alt=True)    
    kmi = km.keymap_items.new('mesh.select_next_item', 'WHEELINMOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.select_next_item', 'Z', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.select_prev_item', 'WHEELOUTMOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.edgering_select', k_select, 'DOUBLE_CLICK', alt=True).properties.extend = False
    kmi = km.keymap_items.new('mesh.loop_multi_select', k_select, 'DOUBLE_CLICK', alt=True, shift=True)
    kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True, shift=True).properties.extend = True
    kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True).properties.extend = False
    kmi = km.keymap_items.new('mesh.normals_make_consistent', 'N', 'PRESS', ctrl=True).properties.inside = False
    kmi = km.keymap_items.new("wm.call_menu_pie","FOUR","PRESS").properties.name="GPENCIL_PIE_tool_palette"
    kmi = km.keymap_items.new("mesh.select_prev_item","TWO","PRESS")
    kmi = km.keymap_items.new("mesh.select_next_item","THREE","PRESS")
    kmi = km.keymap_items.new("mesh.select_less","TWO","PRESS", ctrl=True)
    kmi = km.keymap_items.new("mesh.select_more","THREE","PRESS", ctrl=True)
    kmi = km.keymap_items.new("mesh.inset", "SPACE", "PRESS", alt=True)
    kmi = km.keymap_items.new("mesh.push_and_slide","G","PRESS", shift=True)
#    kmi_props_setattr(kmi.properties, 'use_even_offset', True)
    kmi = km.keymap_items.new('mesh.separate_and_select', 'P', 'PRESS')
#    kmi = km.keymap_items.new('view3d.extrude_normal', 'B', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', ctrl=True, shift=True).properties.number_cuts = 12
    kmi = km.keymap_items.new('transform.edge_bevelweight','B', 'PRESS', alt=True).properties.value = 1
    kmi = km.keymap_items.new('mesh.smart_bevel','B', 'PRESS')
    kmi = km.keymap_items.new('mesh.merge', 'J', 'PRESS', ctrl=True)
    kmi_props_setattr(kmi.properties, 'type', 'LAST')
    kmi = km.keymap_items.new('mesh.reveal', 'H', 'PRESS', ctrl=True, shift=True)
#Grease Pencil
    km = kc.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG')
    kmi_props_setattr(kmi.properties, 'mode', 'SET')
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG', ctrl=True)
    kmi_props_setattr(kmi.properties, 'mode', 'SUB')
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    kmi = km.keymap_items.new('gpencil.select_box', k_select, 'CLICK_DRAG', shift=True)
    kmi_props_setattr(kmi.properties, 'mode', 'ADD')
    kmi_props_setattr(kmi.properties, 'wait_for_input',False)

#Object Mode
    km = kc.keymaps.new(name='Object Mode')
    global_keys()    
    kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK_DRAG')
    kmi_props_setattr(kmi.properties, 'action', 'DESELECT')
#    kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
    kmi = km.keymap_items.new('object.hide_view_clear', 'H', 'PRESS', ctrl=True, shift=True)

# Map Curve
    km = kc.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('curve.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi = km.keymap_items.new('curve.select_linked_pick', k_select, 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.shortest_path_pick', k_select, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

# Outliner
    km = kc.keymaps.new('Outliner', space_type='OUTLINER', region_type='WINDOW', modal=False)
    global_keys()

#    kmi = km.keymap_items.new('outliner.collection_drop', k_select, 'CLICK_DRAG',shift=True)
#    kmi = km.keymap_items.new('outliner.select_box', 'EVT_TWEAK_L', 'ANY')
    kmi = km.keymap_items.new('outliner.show_active', k_nav, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('wm.delete_without_prompt', 'X', 'PRESS')
# Map DOPESHEET_EDITOR
    km = kc.keymaps.new('Dopesheet Editor', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
    global_keys()
    kmi = km.keymap_items.new('time.start_frame_set', 'S', 'PRESS')
    kmi = km.keymap_items.new('time.end_frame_set', 'E', 'PRESS')
    kmi = km.keymap_items.new('time.view_all', 'HOME', 'PRESS')
    kmi = km.keymap_items.new('time.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('time.view_all', 'NDOF_BUTTON_FIT', 'PRESS')
    kmi = km.keymap_items.new('time.view_frame', 'NUMPAD_0', 'PRESS')



def register():
    tila_keymaps()

def unregister():
    tila_keymaps()

if __name__ == "__main__":
    register()
