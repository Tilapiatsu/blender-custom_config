import os
import gc
import bpy

from math import ceil
from array import array
from typing import List, NamedTuple, Union
from ..pidgeon_tool_bag.PTB_Functions import render_image
from bpy.types import (
    Camera,
    Context,
    Object,
    RenderSettings,
    Scene
)

class SavedRenderSettings(NamedTuple):
    old_file_path: str
    old_file_format: str
    old_resolution_percentage: int
    old_res_x: int
    old_res_y: int
    old_camera_name: str
    old_shift_x: float
    old_shift_y: float
    old_aperture_fstop: float
    old_focal_length: float
    old_focal_unit: str
    old_use_border: bool
    old_use_crop_to_border: bool
    old_border_min_x: float
    old_border_min_y: float
    old_border_max_x: float
    old_border_max_y: float


def save_render_settings(context: Context, camera_object: Object) -> SavedRenderSettings:
    scene: Scene = context.scene
    render: RenderSettings = scene.render
    camera_data: Camera = camera_object.data

    return SavedRenderSettings(
        old_file_path = render.filepath,
        old_file_format = render.image_settings.file_format,
        old_resolution_percentage = render.resolution_percentage,
        old_res_x = render.resolution_x,
        old_res_y = render.resolution_y,
        old_camera_name = camera_object.name,
        old_shift_x = camera_data.shift_x,
        old_shift_y = camera_data.shift_y,
        old_aperture_fstop = camera_data.dof.aperture_fstop,
        old_focal_length = camera_data.lens,
        old_focal_unit = camera_data.lens_unit,
        old_use_border = render.use_border,
        old_use_crop_to_border = render.use_crop_to_border,
        old_border_min_x = render.border_min_x,
        old_border_min_y = render.border_min_y,
        old_border_max_x = render.border_max_x,
        old_border_max_y = render.border_max_y,
    )


def restore_render_settings(context: Context, settings: SavedRenderSettings, camera_object: Object):
    scene: Scene = context.scene
    render: RenderSettings = scene.render
    camera_data: Camera = camera_object.data

    render.filepath = settings.old_file_path
    render.image_settings.file_format = settings.old_file_format
    render.resolution_percentage = settings.old_resolution_percentage 
    render.resolution_x = settings.old_res_x
    render.resolution_y = settings.old_res_y
    render.use_border = settings.old_use_border
    render.use_crop_to_border = settings.old_use_crop_to_border
    render.border_min_x = settings.old_border_min_x
    render.border_min_y = settings.old_border_min_y
    render.border_max_x = settings.old_border_max_x
    render.border_max_y = settings.old_border_max_y
    camera_object.name = settings.old_camera_name
    camera_data.shift_x = settings.old_shift_x
    camera_data.shift_y = settings.old_shift_y
    camera_data.dof.aperture_fstop = settings.old_aperture_fstop
    camera_data.lens_unit = settings.old_focal_unit
    camera_data.lens = settings.old_focal_length

class RenderTileCameraShiftSettings(NamedTuple):
    tile_x: int
    tile_y: int
    f_len: float
    fstop: float
    shift_x: float
    shift_y: float

class TileCameraSplitSettings(NamedTuple):
    camera_name: str
    f_len: float
    fstop: float
    shift_x: float
    shift_y: float

class RenderTileRenderBorderSettings(NamedTuple):
    border_min_x: float
    border_min_y: float
    border_max_x: float
    border_max_y: float

TileSettings = Union[
    RenderTileCameraShiftSettings,
    RenderTileRenderBorderSettings,
    TileCameraSplitSettings,
]

class RenderTile(NamedTuple):
    render_method: str # Python 3.8+: Literal['camshift', 'border', 'camsplit']
    tile_settings: TileSettings
    filepath: str
    file_format: str


def do_render_tile(context: Context, render_tile: RenderTile, camera_object: Object):
    scene = context.scene
    render = scene.render

    # Prepare render settings
    render.filepath = render_tile.filepath
    render.image_settings.file_format = render_tile.file_format

    if render_tile.render_method == 'camshift':
        camera_data: Camera = camera_object.data
        settings: RenderTileCameraShiftSettings = render_tile.tile_settings

        render.resolution_percentage = 100
        render.resolution_x = settings.tile_x
        render.resolution_y = settings.tile_y
        camera_data.lens_unit = 'MILLIMETERS'
        camera_data.lens = settings.f_len
        camera_data.dof.aperture_fstop = settings.fstop
        camera_data.shift_x = settings.shift_x
        camera_data.shift_y = settings.shift_y

    elif render_tile.render_method == 'border':
        settings: RenderTileRenderBorderSettings = render_tile.tile_settings

        render.use_border = True
        render.use_crop_to_border = True
        render.border_min_x = settings.border_min_x
        render.border_min_y = settings.border_min_y
        render.border_max_x = settings.border_max_x
        render.border_max_y = settings.border_max_y

    # Render tile
    render_image(render_tile.filepath, mode='INVOKE_DEFAULT')


def generate_tiles(context: Context, saved_settings: SavedRenderSettings) -> List[RenderTile]:
    scene = context.scene

    render = scene.render
    settings = scene.srr_settings

    # Get image dimensions
    res_x = render.resolution_x
    res_y = render.resolution_y
    focal_length = saved_settings.old_focal_length
    aperture_fstop = saved_settings.old_aperture_fstop
    existing_shift_x = saved_settings.old_shift_x
    existing_shift_y = saved_settings.old_shift_y
    aspect = res_x if res_x >= res_y else res_y
    shift_offset_x = existing_shift_x * aspect
    shift_offset_y = existing_shift_y * -aspect

    # Calculate things
    # Divisions | Tiling | Tile Count
    #     1     |   2x2  |      4
    #     2     |   4x4  |     16
    #     3     |   8x8  |     64
    #     4     |  16x16 |    256
    number_divisions = int(settings.subdivisions)

    tiles_per_side = 2 ** number_divisions
    ideal_tile_x = res_x / tiles_per_side
    ideal_tile_y = res_y / tiles_per_side
    max_tile_x = ceil(ideal_tile_x)
    max_tile_y = ceil(ideal_tile_y)
    last_tile_x = res_x - (max_tile_x * (tiles_per_side - 1))
    last_tile_y = res_y - (max_tile_y * (tiles_per_side - 1))

    def get_offset(col, row, tile_x, tile_y, is_last_col, is_last_row):
        offset_x = res_x - (tile_x / 2) if is_last_col else (col + 0.5) * tile_x
        offset_y = res_y - (tile_y / 2) if is_last_row else (row + 0.5) * tile_y
        return (offset_x, offset_y)

    def get_shift(x, y, tile_x, tile_y):
        widest_aspect = tile_x if tile_x >= tile_y else tile_y
        shift_x = ((-res_x / 2) + x) / widest_aspect
        shift_y = ((res_y / 2) - y) / widest_aspect
        return (shift_x, shift_y)

    def get_border(col, row, tile_x, tile_y, is_last_col, is_last_row):
        min_x = res_x - tile_x if is_last_col else col * tile_x
        max_x = res_x if is_last_col else (col + 1) * tile_x
        min_y = 0 if is_last_row else res_y - ((row + 1) * tile_y)
        max_y = tile_y if is_last_row else res_y - (row * tile_y)
        border_min_x = min_x / res_x
        border_max_x = max_x / res_x
        border_min_y = min_y / res_y
        border_max_y = max_y / res_y
        return (border_min_x, border_min_y, border_max_x, border_max_y)

    # Create tiles
    tiles: List[RenderTile] = []
    for current_row in range(tiles_per_side):
        # Start a new row
        is_last_row = current_row == (tiles_per_side - 1)

        for current_col in range(tiles_per_side):
            # Start a new column
            is_last_col = current_col == (tiles_per_side - 1)
            tile_settings: TileSettings = None
            tile_suffix = get_tile_suffix(current_col, current_row)

            # Set Resolution (and aspect ratio)
            tile_x = ideal_tile_x if settings.render_method == 'camsplit' else \
                last_tile_x if is_last_col else max_tile_x
            tile_y = ideal_tile_y if settings.render_method == 'camsplit' else \
                last_tile_y if is_last_row else max_tile_y

            if settings.render_method in ['camshift', 'camsplit']:
                # Set CameraZoom
                f_len = focal_length * ((res_x / tile_x) if tile_x >= tile_y else (res_y / tile_y))
                fstop = aperture_fstop * (f_len / focal_length)

                # Set Camera Shift
                (x, y) = get_offset(current_col, current_row, tile_x, tile_y, is_last_col, is_last_row)
                x += shift_offset_x
                y += shift_offset_y
                (shift_x, shift_y) = get_shift(x, y, tile_x, tile_y)

                if settings.render_method == 'camshift':
                    tile_settings = RenderTileCameraShiftSettings(
                        tile_x = tile_x,
                        tile_y = tile_y,
                        f_len = f_len,
                        fstop = fstop,
                        shift_x = shift_x,
                        shift_y = shift_y,
                    )
                elif settings.render_method == 'camsplit':
                    camera_name = f"{saved_settings.old_camera_name}{tile_suffix}"
                    tile_settings = TileCameraSplitSettings(
                        camera_name = camera_name,
                        f_len = f_len,
                        fstop = fstop,
                        shift_x = shift_x,
                        shift_y = shift_y,
                    )

            elif settings.render_method == 'border':
                (border_min_x, border_min_y, border_max_x, border_max_y) = get_border(
                    current_col, current_row, tile_x, tile_y, is_last_col, is_last_row)

                tile_settings = RenderTileRenderBorderSettings(
                    border_min_x = border_min_x,
                    border_min_y = border_min_y,
                    border_max_x = border_max_x,
                    border_max_y = border_max_y,
                )

            else:
                raise f"Unhandled render method {settings.render_method}"

            # Render
            filepath = get_tile_filepath(tile_suffix)
            tile = RenderTile(
                render_method = settings.render_method,
                tile_settings = tile_settings,
                filepath = filepath,
                file_format = 'OPEN_EXR',
            )

            tiles.append(tile)

    return tiles

def get_tile_suffix(col: int, row: int) -> str:
    return f"_R{(row + 1):02}_C{(col + 1):02}"

def get_tile_filepath(tile_suffix: str) -> str:
    file_extension = get_file_ext('OPEN_EXR')
    filepath = os.path.join(bpy.context.scene.srr_settings.render_path, "PartTiles", f"Part{tile_suffix}{file_extension}")
    return filepath


def get_file_ext(file_format: str) -> str:
    """
    `file_format` can be one of the following values:
    - `BMP` BMP, Output image in bitmap format.
    - `IRIS` Iris, Output image in (old!) SGI IRIS format.
    - `PNG` PNG, Output image in PNG format.
    - `JPEG` JPEG, Output image in JPEG format.
    - `JPEG2000` JPEG 2000, Output image in JPEG 2000 format.
    - `TARGA` Targa, Output image in Targa format.
    - `TARGA_RAW` Targa Raw, Output image in uncompressed Targa format.
    - `CINEON` Cineon, Output image in Cineon format.
    - `DPX` DPX, Output image in DPX format.
    - `OPEN_EXR_MULTILAYER` OpenEXR MultiLayer, Output image in multilayer OpenEXR format.
    - `OPEN_EXR` OpenEXR, Output image in OpenEXR format.
    - `HDR` Radiance HDR, Output image in Radiance HDR format.
    - `TIFF` TIFF, Output image in TIFF format.
    """
    if file_format == 'BMP':
        return ".bmp"
    elif file_format == 'IRIS':
        return ".iris"
    elif file_format == 'PNG':
        return ".png"
    elif file_format == 'JPEG':
        return ".jpg"
    elif file_format == 'JPEG2000':
        return ".jp2"
    elif file_format in {'TARGA', 'TARGA_RAW'}:
        return ".tga"
    elif file_format == 'CINEON':
        return ".cin"
    elif file_format == 'DPX':
        return ".dpx"
    elif file_format in {'OPEN_EXR', 'OPEN_EXR_MULTILAYER'}:
        return ".exr"
    elif file_format == 'HDR':
        return ".hdr"
    elif file_format == 'TIFF':
        return ".tif"

    return "." + file_format.lower()

class MergeTile(NamedTuple):
    dimensions: tuple
    offset: tuple
    filepath: str

def generate_tiles_for_merge(context: Context) -> List[MergeTile]:
    scene = context.scene

    render = scene.render
    settings = scene.srr_settings

    res_x = render.resolution_x
    res_y = render.resolution_y

    # Calculate things
    # Divisions | Tiling | Tile Count
    #     1     |   2x2  |      4
    #     2     |   4x4  |     16
    #     3     |   8x8  |     64
    #     4     |  16x16 |    256
    number_divisions = int(settings.subdivisions)

    tiles_per_side = 2 ** number_divisions
    max_tile_x = ceil(res_x / tiles_per_side)
    max_tile_y = ceil(res_y / tiles_per_side)
    last_tile_x = res_x - (max_tile_x * (tiles_per_side - 1))
    last_tile_y = res_y - (max_tile_y * (tiles_per_side - 1))

    # Create tiles
    tiles: List[MergeTile] = []
    offset_y = res_y
    for current_row in range(tiles_per_side):
        # Start a new row
        is_last_row = current_row == (tiles_per_side - 1)

        # Set vertical resolution
        tile_y = last_tile_y if is_last_row else max_tile_y
        # Set vertical offset (image data runs bottom-to-top)
        offset_y -= tile_y

        offset_x = 0

        for current_col in range(tiles_per_side):
            # Start a new column
            is_last_col = current_col == (tiles_per_side - 1)

            # Set horizontal resolution
            tile_x = last_tile_x if is_last_col else max_tile_x

            tile_suffix = get_tile_suffix(current_col, current_row)
            filepath = get_tile_filepath(tile_suffix)
            tile = MergeTile(
                dimensions = (tile_x, tile_y),
                offset = (offset_x, offset_y),
                filepath = filepath,
            )

            tiles.append(tile)

            offset_x += max_tile_x

    return tiles


def do_merge_tiles(context: Context, tiles: List[MergeTile]) -> None:
    scene = context.scene
    settings = scene.srr_settings
    render = scene.render

    res_x = render.resolution_x
    res_y = render.resolution_y

    # Potentially free up memory from a previous merge
    final_image_name = "super_res_render_output"
    if final_image_name in bpy.data.images.keys():
        print("Removing previous merge image from Blender's memory...")
        try:
            final_image = bpy.data.images[final_image_name]
            final_image.buffers_free()
        except Exception as e:
            print("Error freeing previous merge image:", e)
        finally:
            bpy.data.images.remove(final_image)
            final_image = None
            gc.collect()

    try:
        print(f"Allocating storage for {res_x * res_y * 4} floats ({res_x * res_y} output pixels)...")
        final_image_pixels = array('f', [0.0, 0.0, 0.0, 0.0] * res_x * res_y)
        bytes_allocated = final_image_pixels.buffer_info()[1] * final_image_pixels.itemsize
        print(f"Allocated {bytes_allocated / 1024 / 1024:,.2f} MBytes of memory.\n")

        for (dimensions, offset, filepath) in tiles:
            tile_x, tile_y = dimensions
            offset_x, offset_y = offset

            print(f"Loading tile: {filepath}")

            try:
                tile_image = bpy.data.images.load(filepath, check_existing=False)
                image_x, image_y = tile_image.size

                if not (image_x == tile_x and image_y == tile_y):
                    raise RuntimeError(f"Image tile {filepath} has incorrect dimensions {image_x}x{image_y}! Expected {tile_x}x{tile_y}.")

                if not tile_image.channels == 4:
                    raise RuntimeError(f"Image tile {filepath} has {tile_image.channels} channels! Expected 4.")

                # Copy the pixels
                tile_pixels = list(tile_image.pixels)

                for y in range(tile_y):
                    # Copy a row
                    source_pixel_start = y * tile_x * 4
                    source_pixel_end = source_pixel_start + (tile_x * 4)

                    target_y = offset_y + y
                    target_pixel_start = (target_y * res_x + offset_x) * 4
                    target_pixel_end = target_pixel_start + (tile_x * 4)

                    final_image_pixels[target_pixel_start:target_pixel_end] = array('f', tile_pixels[source_pixel_start:source_pixel_end])

                del tile_pixels
                print(f"Copied {tile_x * tile_y} pixels OK.")

            finally:
                tile_image.buffers_free()
                bpy.data.images.remove(tile_image)
                del tile_image

    except Exception as e:
        print("Error compositing image tiles:", e)
        raise

    # Free up any memory still held by loaded images
    print("\nFreeing image memory...")
    gc.collect()

    if not len(final_image_pixels) == res_x * res_y * 4:
        raise RuntimeError(f"Got {len(final_image_pixels)} pixels; expected {res_x * res_y * 4}.")

    final_image_ext = get_file_ext(render.image_settings.file_format)
    final_image_filepath = f"{settings.render_path}/Merged"
    final_image_filepath = bpy.path.ensure_ext(final_image_filepath, final_image_ext)
    final_image_filepath = os.path.realpath(bpy.path.abspath(final_image_filepath))

    print(f'Composited output OK. Saving to "{final_image_filepath}" ...')

    final_image = bpy.data.images.new(final_image_name, alpha=True, float_buffer=True, width=res_x, height=res_y)
    final_image.alpha_mode = 'STRAIGHT'
    final_image.colorspace_settings.name = "sRGB"
    final_image.generated_type = 'BLANK'
    final_image.filepath_raw = final_image_filepath
    final_image.file_format = render.image_settings.file_format

    final_image.pixels.foreach_set(final_image_pixels)

    final_image.save_render(final_image_filepath)

    del final_image_pixels
    final_image.buffers_free()
    bpy.data.images.remove(final_image)
    final_image = None
    gc.collect()
