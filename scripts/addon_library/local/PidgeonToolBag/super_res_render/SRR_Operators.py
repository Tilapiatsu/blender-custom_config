import bpy
from bpy.types import (
    Context,
    Operator,
    Object,
    Collection,
    Timer
)

from .SRR_Functions import *
from ..pidgeon_tool_bag.PTB_Functions import deselect_all, bcolors

class SRR_OT_SplitCamera(Operator):
    bl_idname = "superresrender.splitcam"
    bl_label = "Split Active Camera"
    bl_description = "Subdivides the active Camera"

    tiles: List[RenderTile] = None
    saved_settings: SavedRenderSettings = None

    def execute(self, context: Context):
        active_object: Object = bpy.context.active_object
        if not active_object or active_object.type != 'CAMERA':
            return {'CANCELLED'}

        self.saved_settings = save_render_settings(context, camera_object=active_object)

        self.tiles = generate_tiles(context, self.saved_settings)
        if not self.tiles:
            return {'CANCELLED'}

        # create an Empty to parent all the new cameras onto
        parent_empty = self.make_empty(context, camera_object=active_object)

        # split cameras
        new_cameras: List[Object] = []
        for tile in self.tiles:
            new_camera = self.split_camera(context, camera_object=active_object, tile=tile)
            new_cameras.append(new_camera)

        # parent the cameras onto the Empty
        deselect_all(self, context)
        for camera in new_cameras:
            camera.select_set(True)
        parent_empty.select_set(True)
        context.view_layer.objects.active = parent_empty
        bpy.ops.object.parent_set(type='OBJECT')

        return {'FINISHED'}

    def split_camera(self, context: Context, camera_object: Object, tile: RenderTile) -> Object:
        tile_settings: TileCameraSplitSettings = tile.tile_settings

        deselect_all(self, context)

        # select original camera
        camera_object.select_set(True)
        context.view_layer.objects.active = camera_object

        # duplicate camera
        bpy.ops.object.duplicate()

        # apply settings to new camera
        new_camera: Object = context.view_layer.objects.active
        new_camera.name = tile_settings.camera_name

        divider = 1 / (2 ** int(context.scene.srr_settings.subdivisions))
        new_camera.scale = (divider,divider,divider)

        camera_data: Camera = new_camera.data
        camera_data.lens_unit = 'MILLIMETERS'
        camera_data.lens = tile_settings.f_len
        camera_data.dof.aperture_fstop = tile_settings.fstop
        camera_data.shift_x = tile_settings.shift_x
        camera_data.shift_y = tile_settings.shift_y

        return new_camera

    def make_empty(self, context: Context, camera_object: Object) -> Object:
        # put the empty in the same location as the original camera
        camera_location = camera_object.location
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=camera_location, scale=(1, 1, 1))
        empty: Object = context.view_layer.objects.active
        empty.name = f"{self.saved_settings.old_camera_name}_Split"

        # link the Empty to all the same collections as the parent camera
        for collection in camera_object.users_collection:
            collection: Collection
            try:
                collection.objects.link(empty)
            except RuntimeError:
                # the object might already be in this collection
                pass

        # add the Empty to the same parent as the original camera, if it has one
        if camera_object.parent:
            parent_object = camera_object.parent

            deselect_all(self, context)

            empty.select_set(True)
            parent_object.select_set(True)
            context.view_layer.objects.active = parent_object
            bpy.ops.object.parent_set(type='OBJECT')

        return empty
    

class SRR_OT_StartRender(Operator):
    bl_idname = "superresrender.startrender"
    bl_label = "Start Render"
    bl_description = "Subdivides your Image"

    _timer: Timer = None
    stop: bool = False
    rendering: bool = False
    tiles: List[RenderTile] = None
    saved_settings: SavedRenderSettings = None

    # Render callbacks
    def render_pre(self, scene: Scene, dummy):
        self.rendering = True

    def render_post(self, scene: Scene, dummy):
        settings = scene.srr_settings
        status = settings.status

        # We're done with this tile.
        self.tiles.pop(0)
        status.tiles_done += 1

        # Move on to the next
        self.rendering = False

    def render_cancel(self, scene: Scene, dummy):
        self.stop = True


    def execute(self, context: Context):
        scene = context.scene
        settings = scene.srr_settings
        status = settings.status

        # Reset state
        self.stop = False
        self.rendering = False

        # Save settings
        self.saved_settings = save_render_settings(context, scene.camera)

        # Prepare tiles
        self.tiles = generate_tiles(context, self.saved_settings)
        if settings.start_tile > 1:
            self.tiles = self.tiles[settings.start_tile - 1:]
        if not self.tiles:
            return {'CANCELLED'}

        status.tiles_total = len(self.tiles)
        status.tiles_done = 0
        status.is_rendering = True
        status.should_stop = False

        # Setup callbacks
        bpy.app.handlers.render_pre.append(self.render_pre)
        bpy.app.handlers.render_post.append(self.render_post)
        bpy.app.handlers.render_cancel.append(self.render_cancel)

        # Setup timer and modal
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
        

    def modal(self, context: Context, event):
        scene = context.scene
        settings = scene.srr_settings
        status = settings.status

        if event.type == 'ESC':
            self.stop = True

        if event.type == 'TIMER':
            was_cancelled = self.stop or status.should_stop

            if was_cancelled or not self.tiles:
                
                # Remove callbacks & clean up
                bpy.app.handlers.render_pre.remove(self.render_pre)
                bpy.app.handlers.render_post.remove(self.render_post)
                bpy.app.handlers.render_cancel.remove(self.render_cancel)
                context.window_manager.event_timer_remove(self._timer)

                status.should_stop = False
                status.is_rendering = False

                restore_render_settings(context, self.saved_settings, scene.camera)

                if was_cancelled:
                    self.report({'WARNING'}, "Rendering aborted")
                    return {'CANCELLED'}

                self.report({'INFO'}, "Rendering done")

                return {'FINISHED'}

            elif self.rendering is False:
                tile = self.tiles[0]

                do_render_tile(context, tile, scene.camera)

        return {'PASS_THROUGH'}

class SRR_OT_StopRender(Operator):
    bl_idname = "superresrender.stoprender"
    bl_label = "Stop Render"

    def execute(self, context: Context):
        settings = context.scene.srr_settings
        status = settings.status

        status.should_stop = True

        return {'FINISHED'}
    
class SRR_OT_OpenFolderRendered(Operator):
    bl_idname = "superresrender.openfolder"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Rendered Images"

    def execute(self, context: Context):
        settings = bpy.context.scene.srr_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.render_path))):
            self.report({'ERROR'}, "Folder does not exist, please render first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.render_path)))
        return {'FINISHED'}

class SRR_OT_Merge(Operator):
    bl_idname = "superresrender.merge"
    bl_label = "Merge Frames"
    bl_description = "Merge Frames into one Image"

    @classmethod
    def poll(cls, context: Context):
        scene = context.scene
        settings = scene.srr_settings
        status = settings.status

        return not status.is_rendering

    def execute(self, context: Context):
        self.report({'INFO'}, "Merging tiles...")

        tiles = generate_tiles_for_merge(context)

        do_merge_tiles(context, tiles)

        self.report({'INFO'}, "Merge tiles done!")

        return {'FINISHED'}
    
classes = (
    SRR_OT_SplitCamera,
    SRR_OT_StartRender,
    SRR_OT_StopRender,
    SRR_OT_OpenFolderRendered,
    SRR_OT_Merge,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")
