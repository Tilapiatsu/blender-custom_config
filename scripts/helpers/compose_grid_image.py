try:
    from PIL import Image

except ModuleNotFoundError as e:
    print(e)
    import subprocess
    import sys

    print(subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"]))
    from PIL import Image

import os
import math
from pathlib import Path
from enum import Enum

# =====================================================
# USER SETTINGS
# =====================================================


class NormalizeMode(Enum):
    NONE = 0
    WIDTH = 1
    HEIGHT = 2


class Settings:
    def __init__(
        self,
        input_folder: Path,
        name_filter: str,
        max_per_row: int,
        gap: int,
        normalize_mode: NormalizeMode,
        background_color: tuple,
        max_output_size: tuple,
        export_png: bool = True,
        export_jpg: bool = True,
        jpg_quality: int = 95,
    ):

        self.input_folder = input_folder
        self.name_filter = name_filter
        self.max_per_row = max_per_row
        self.gap = gap
        self.normalize_mode = normalize_mode
        self.background_color = background_color
        self.max_output_size = max_output_size
        self.export_png = export_png
        self.export_jpg = export_jpg
        self.jpg_quality = jpg_quality


INPUT_FOLDER = Path(r"/path/to/images/")
BACKGROUND = (0, 0, 0, 1)
MAX_OUTPUT_SIZE = (6000, 6000)
JPG_QUALITY = 95

compose_settings = []

# turn_settings
compose_settings.append(
    Settings(
        INPUT_FOLDER,
        "contains_name_greyscale",
        3,
        40,
        NormalizeMode.NONE,
        BACKGROUND,
        MAX_OUTPUT_SIZE,
    )
)


#  match_settings
compose_settings.append(
    Settings(
        INPUT_FOLDER,
        "contains_name_beauty",
        2,
        40,
        NormalizeMode.WIDTH,
        BACKGROUND,
        MAX_OUTPUT_SIZE,
    )
)


# =====================================================
# HELPERS
# =====================================================


def find_images(folder: Path, name_filter: str):
    exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

    files = []
    for f in os.listdir(folder):
        if (
            f.lower().endswith(exts)
            and name_filter.lower() in f.lower()
            and os.path.splitext(f.lower())[0] != (name_filter + "_composite").lower()
        ):
            files.append(os.path.join(folder, f))

    return sorted(files)


def crop_alpha(img):
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()

    if bbox:
        return img.crop(bbox)
    return img


def normalize_images(images: list, mode: NormalizeMode):
    """
    Scale UP smaller images only.
    Use largest width or height as target.
    Never scale down.
    """

    if mode == NormalizeMode.HEIGHT:
        target = max(img.height for img in images)

        out = []
        for img in images:
            if img.height < target:
                scale = target / img.height
                new_w = int(img.width * scale)
                img = img.resize((new_w, target), Image.LANCZOS)
            out.append(img)

        return out

    elif mode == NormalizeMode.WIDTH:
        target = max(img.width for img in images)

        out = []
        for img in images:
            if img.width < target:
                scale = target / img.width
                new_h = int(img.height * scale)
                img = img.resize((target, new_h), Image.LANCZOS)
            out.append(img)

        return out

    return images


def build_rows(images: list, max_per_row: int):
    rows = []
    for i in range(0, len(images), max_per_row):
        rows.append(images[i : i + max_per_row])
    return rows


def compute_canvas_size(rows: list, gap: int):
    total_w = 0
    total_h = 0
    row_sizes = []

    for row in rows:
        row_w = sum(img.width for img in row) + gap * (len(row) - 1)
        row_h = max(img.height for img in row)

        row_sizes.append((row_w, row_h))

        total_w = max(total_w, row_w)
        total_h += row_h

    total_h += gap * (len(rows) - 1)

    return total_w, total_h, row_sizes


def compose(rows: list, gap: int, bg: tuple):
    canvas_w, canvas_h, row_sizes = compute_canvas_size(rows, gap)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)

    y = 0

    for row_index, row in enumerate(rows):
        row_w, row_h = row_sizes[row_index]

        x = 0
        for img in row:
            offset_y = y + (row_h - img.height) // 2
            canvas.paste(img, (x, offset_y), img)
            x += img.width + gap

        y += row_h + gap

    return canvas


def fit_max_size(img, max_w: int, max_h: int):
    w, h = img.size

    scale = min(max_w / w, max_h / h, 1.0)

    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    return img


def compose_all_images(settings: Settings):
    files = find_images(settings.input_folder, settings.name_filter)

    if not files:
        print("No matching images found.")
        return

    images = []

    for f in files:
        img = Image.open(f).convert("RGBA")
        img = crop_alpha(img)
        images.append(img)

    # Normalize only if requested
    if settings.normalize_mode in (NormalizeMode.WIDTH, NormalizeMode.HEIGHT):
        images = normalize_images(images, settings.normalize_mode)

    rows = build_rows(images, settings.max_per_row)

    final_img = compose(rows, settings.gap, settings.background_color)

    final_img = fit_max_size(final_img, settings.max_output_size[0], settings.max_output_size[1])

    output_base = os.path.join(settings.input_folder, settings.name_filter + "_composite")

    if settings.export_jpg or settings.export_png:
        print("Saved:")

    if settings.export_png:
        png_path = output_base + ".png"
        final_img.save(png_path)
        print(png_path)

    if settings.export_jpg:
        jpg_path = output_base + ".jpg"
        rgb = Image.new("RGB", final_img.size, settings.background_color[:3])
        rgb.paste(final_img, mask=final_img.getchannel("A"))
        rgb.save(jpg_path, quality=settings.jpg_quality)
        print(jpg_path)


# =====================================================
# MAIN
# =====================================================


def main():
    for s in compose_settings:
        compose_all_images(s)


if __name__ == "__main__":
    main()
