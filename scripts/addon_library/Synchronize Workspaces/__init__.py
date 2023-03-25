import copy
import bpy
from bpy.app.handlers import persistent

from . import tools

bl_info = {
    "name": "Synchronize Workspaces",
    "author": "Michael Soluyanov (multlabs.com)",
    "version": (1, 11),
    "blender": (3, 0, 0),
    "location": "View3D -> Top Bar",
    "description": "Synchronize 3D views between workspaces",
    "warning": "",
    "doc_url": "https://blenderartists.org/t/synchronize-workspaces-blender-add-on/1356695",
    "category": "Interface",
}


class sinchmanager_class:
    last_area = ""
    last_workspace = ""


def check_screen(sc):
    for window in bpy.context.window_manager.windows:
        if window.screen == sc:
            return True
    return False


def get_biggest_area(workspace, type, checkscreen=False):
    max_size = 0
    nextArea = None
    for screen in workspace.screens:
        if(checkscreen):
            if not check_screen(screen):
                continue
        for area in screen.areas:
            if area.type == type:
                size = area.width * area.height
                if size > max_size:
                    nextArea = area
                    max_size = size
    return nextArea


def update_workspace(args):
    """Main component that performs the sync
    args - dummy value from subscribe_rna"""
    if not bpy.context.scene.synch_settings.active:
        return
    if not bpy.context.workspace.synch_active:
        return

    if sinchmanager.last_workspace == bpy.context.workspace.name:
        return
    if sinchmanager.last_workspace not in bpy.data.workspaces:
        sinchmanager.last_workspace = bpy.context.workspace.name
        return
    prev = bpy.data.workspaces[sinchmanager.last_workspace]
    next1 = bpy.context.workspace

    nextArea = get_biggest_area(next1, "VIEW_3D", True)
    prevArea = sinchmanager.last_area
    if prevArea is None:
        prevArea = get_biggest_area(prev, "VIEW_3D", False)

    sinchmanager.last_area = nextArea

    if nextArea is None:
        return

    sinchmanager.last_workspace = bpy.context.workspace.name
    sinchmanager.last_area = nextArea

    if prevArea is None:
        return

    for ns3d in nextArea.spaces:
        if ns3d.type == "VIEW_3D":
            break
    for ps3d in prevArea.spaces:
        if ps3d.type == "VIEW_3D":
            break

    nr3d = ns3d.region_3d
    pr3d = ps3d.region_3d

    if (ps3d.local_view is not None):
        objects = [ob for ob in bpy.context.view_layer.objects
                   if ob.visible_get(viewport=ps3d)]

        selected = bpy.context.selected_objects[:]
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.update()
        if (ns3d.local_view is None):

            override = {'area': nextArea}
            bpy.ops.view3d.localview(override, frame_selected=False)
        else:
            objectsn = [ob for ob in bpy.context.view_layer.objects
                        if ob.visible_get(viewport=ns3d)]
            for obj in objects:
                if obj not in objectsn:
                    obj.local_view_set(ns3d, True)
                obj.select_set(obj in selected)
            for obj in objectsn:
                if obj not in objects:
                    obj.local_view_set(ns3d, False)
            bpy.context.view_layer.update()

    elif (ns3d.local_view is not None) and (ps3d.local_view is None):
        override = {'area': nextArea}
        bpy.ops.view3d.localview(override, frame_selected=False)

    # region 3d settings:
    nr3d.view_distance = pr3d.view_distance
    nr3d.view_matrix = copy.copy(pr3d.view_matrix)

    nr3d.is_orthographic_side_view = pr3d.is_orthographic_side_view
    nr3d.is_perspective = pr3d.is_perspective
    nr3d.view_perspective = pr3d.view_perspective
    nr3d.view_rotation = pr3d.view_rotation
    nr3d.is_orthographic_side_view = pr3d.is_orthographic_side_view

    nr3d.view_camera_offset = pr3d.view_camera_offset
    nr3d.view_camera_zoom = pr3d.view_camera_zoom

    # TODO is there a better way? 90deg, 180 deg is culling here
    nr3d.view_matrix = copy.copy(pr3d.view_matrix)
    if nr3d.is_orthographic_side_view:
        tools.setView(nextArea, pr3d.view_rotation)
        nr3d.view_rotation = pr3d.view_rotation

    nr3d.view_location = pr3d.view_location

    # space 3d settings:
    tools.copy_settings(ps3d, ns3d)

    if bpy.context.scene.synch_settings.shading_type:
        ns3d.shading.type = ps3d.shading.type

    if bpy.context.scene.synch_settings.shading_settings:
        tools.copy_settings(ps3d.shading, ns3d.shading)

    if bpy.context.scene.synch_settings.overlays:
        tools.copy_settings(ps3d.overlay, ns3d.overlay)

    nr3d.update()
    nextArea.tag_redraw()


# Triggers when window's workspace is changed
subscribe_to = bpy.types.Window, "workspace"
sinchmanager = sinchmanager_class()


@persistent
def load_handler(context, a):
    sinchmanager.last_workspace = bpy.context.workspace.name
    register_rna_sub()


def register_rna_sub():
    bpy.msgbus.clear_by_owner(sinchmanager)
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=sinchmanager,
        args=(bpy.context,),
        notify=update_workspace,
        options={"PERSISTENT"}
    )


class SYNCW_PT_link1(bpy.types.Panel):
    """You can toggle synchronization on specific workspaces"""
    bl_label = "Synchronize settings"
    bl_idname = "VIEW3D_SYNCW_PT_link1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_context = "layout"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Synchronize 3D Views:")
        for w in bpy.data.workspaces:
            layout.prop(w, 'synch_active', text=w.name)

        row = self.layout.row(align=True)
        row.prop(context.scene.synch_settings, "shading_type", text="",
                 toggle=True, icon='SHADING_TEXTURE')
        row.prop(context.scene.synch_settings, "shading_settings", text="",
                 toggle=True, icon='PREFERENCES')
        row.prop(context.scene.synch_settings, "overlays", text="",
                 toggle=True, icon='OVERLAY')


def setCurrent(self, context):
    if bpy.context.scene.synch_settings.active:
        bigestarea = get_biggest_area(context.workspace, "VIEW_3D", True)
        if bigestarea:
            sinchmanager.last_workspace = bpy.context.workspace.name
    return None


def drawheader(self, context):
    bigestarea = get_biggest_area(context.workspace, "VIEW_3D", True)
    if bigestarea != context.area:
        return

    # this is a derty hack if subscribe_rna will not work
    if sinchmanager.last_workspace != bpy.context.workspace.name:
        update_workspace(context)

    sinchmanager.last_area = context.area

    # toggle & popover.
    row = self.layout.row(align=True)
    if context.scene.synch_settings.active:
        icon = 'LOCKVIEW_ON'
    else:
        icon = 'LOCKVIEW_OFF'
    row.prop(context.scene.synch_settings, "active", text="",
             toggle=True, icon=icon)
    sub = row.row(align=True)
    sub.active = context.scene.synch_settings.active
    sub.popover(
        SYNCW_PT_link1.bl_idname,
        text='',
        text_ctxt='',
        icon='NONE',
        icon_value=0
    )


class SyncSettings(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="Toggle synchronization",
        default=True,
        update=setCurrent)
    shading_type: bpy.props.BoolProperty(
        name="Synchronize also shading type",
        default=False)
    shading_settings: bpy.props.BoolProperty(
        name="Synchronize also shading settings",
        default=False)
    overlays: bpy.props.BoolProperty(
        name="Synchronize also overlays",
        default=False)


classes = (SYNCW_PT_link1, SyncSettings)


def register():
    bpy.types.WorkSpace.synch_active = bpy.props.BoolProperty(
        name="Toggle synchronization for the workspace",
        default=True,
        update=setCurrent
    )
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.synch_settings = bpy.props.PointerProperty(
        type=SyncSettings
    )
    bpy.app.handlers.load_post.append(load_handler)
    register_rna_sub()
    if hasattr(bpy.types, 'VIEW3D_HT_header'):
        bpy.types.VIEW3D_HT_header.append(drawheader)
    else:
        for pt in bpy.types.Header.__subclasses__():
            if pt.__name__ == "VIEW3D_HT_header":
                break
        pt.append(drawheader)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.msgbus.clear_by_owner(sinchmanager)
    if hasattr(bpy.types, 'VIEW3D_HT_header'):
        bpy.types.VIEW3D_HT_header.remove(drawheader)
    else:
        for pt in bpy.types.Header.__subclasses__():
            if pt.__name__ == "VIEW3D_HT_header":
                break
        pt.remove(drawheader)
    bpy.types.Scene.synch_settings = None
    bpy.types.WorkSpace.synch_active = None
    for cls in classes:
        bpy.utils.unregister_class(cls)
