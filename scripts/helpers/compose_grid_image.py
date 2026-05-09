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


# =====================================================
# USER SETTINGS
# =====================================================

INPUT_FOLDER = r"/path/to/images"
NAME_FILTER = "contains"

MAX_PER_ROW = 4
GAP = 20

NORMALIZE_MODE = "width"  # None / "height" / "width"

BACKGROUND = (0, 0, 0, 1)

MAX_OUTPUT_WIDTH = 6000
MAX_OUTPUT_HEIGHT = 6000

JPG_QUALITY = 95

# =====================================================
# HELPERS
# =====================================================


def find_images(folder, name_filter):
    exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

    files = []
    for f in os.listdir(folder):
        if f.lower().endswith(exts) and name_filter.lower() in f.lower():
            files.append(os.path.join(folder, f))

    return sorted(files)


def crop_alpha(img):
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()

    if bbox:
        return img.crop(bbox)
    return img


def normalize_images(images, mode):
    """
    Scale UP smaller images only.
    Use largest width or height as target.
    Never scale down.
    """

    if mode == "height":
        target = max(img.height for img in images)

        out = []
        for img in images:
            if img.height < target:
                scale = target / img.height
                new_w = int(img.width * scale)
                img = img.resize((new_w, target), Image.LANCZOS)
            out.append(img)

        return out

    elif mode == "width":
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


def build_rows(images, max_per_row):
    rows = []
    for i in range(0, len(images), max_per_row):
        rows.append(images[i : i + max_per_row])
    return rows


def compute_canvas_size(rows, gap):
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


def compose(rows, gap, bg):
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


def fit_max_size(img, max_w, max_h):
    w, h = img.size

    scale = min(max_w / w, max_h / h, 1.0)

    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    return img


# =====================================================
# MAIN
# =====================================================


def main():

    files = find_images(INPUT_FOLDER, NAME_FILTER)

    if not files:
        print("No matching images found.")
        return

    images = []

    for f in files:
        img = Image.open(f).convert("RGBA")
        img = crop_alpha(img)
        images.append(img)

    # Normalize only if requested
    if NORMALIZE_MODE in ("height", "width"):
        images = normalize_images(images, NORMALIZE_MODE)

    rows = build_rows(images, MAX_PER_ROW)

    final_img = compose(rows, GAP, BACKGROUND)

    final_img = fit_max_size(final_img, MAX_OUTPUT_WIDTH, MAX_OUTPUT_HEIGHT)

    output_base = os.path.join(INPUT_FOLDER, NAME_FILTER + "_composite")

    png_path = output_base + ".png"
    jpg_path = output_base + ".jpg"

    final_img.save(png_path)

    rgb = Image.new("RGB", final_img.size, BACKGROUND[:3])
    rgb.paste(final_img, mask=final_img.getchannel("A"))
    rgb.save(jpg_path, quality=JPG_QUALITY)

    print("Saved:")
    print(png_path)
    print(jpg_path)


if __name__ == "__main__":
    main()
