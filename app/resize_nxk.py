"""
n x k image downsampling utility.
Box averaging: each n×k block of pixels is averaged into one output pixel.
"""

import os
import glob
import numpy as np
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".bmp", ".tif", ".tiff", ".jpg", ".jpeg"}


def downsample_image(img_array: np.ndarray, n: int, k: int) -> np.ndarray:
    """
    Downsample by n×k box averaging.

    Divides the image into non-overlapping n×k blocks and computes the
    mean of each block.  Pixels that don't fit into a complete block at
    the bottom / right edges are cropped.
    """
    if img_array.ndim == 2:
        h, w = img_array.shape
        h_crop = (h // n) * n
        w_crop = (w // k) * k
        cropped = img_array[:h_crop, :w_crop].astype(np.float64)
        reshaped = cropped.reshape(h_crop // n, n, w_crop // k, k)
        return reshaped.mean(axis=(1, 3)).astype(img_array.dtype)
    else:
        h, w, c = img_array.shape
        h_crop = (h // n) * n
        w_crop = (w // k) * k
        cropped = img_array[:h_crop, :w_crop, :].astype(np.float64)
        reshaped = cropped.reshape(h_crop // n, n, w_crop // k, k, c)
        return reshaped.mean(axis=(1, 3)).astype(img_array.dtype)


def resize_folder(
    folder_path: str,
    n: int,
    k: int,
    log_callback=None,
) -> str:
    """
    Recursively find images in *folder_path* and downsample each by n x k.
    Resized images are saved under ``<folder_path>/<n>x<k>_resized/``.

    Parameters
    ----------
    folder_path : str
        Root folder containing images.
    n, k : int
        Row / column downsample factors (>= 1).
    log_callback : callable, optional
        ``log_callback(text)`` is called for each progress message.

    Returns
    -------
    str
        Path to the output folder.
    """
    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        _log(f"[ERROR] Folder not found: {folder_path}\n")
        return ""

    out_root = os.path.join(folder_path, f"{n}x{k}_resized")
    os.makedirs(out_root, exist_ok=True)

    image_files = []
    for ext in SUPPORTED_EXTENSIONS:
        image_files.extend(
            glob.glob(os.path.join(folder_path, "**", f"*{ext}"), recursive=True)
        )
        image_files.extend(
            glob.glob(os.path.join(folder_path, "**", f"*{ext.upper()}"), recursive=True)
        )

    image_files = sorted(
        set(f for f in image_files if f"{n}x{k}_resized" not in f)
    )

    if not image_files:
        _log(f"[WARNING] No image files found in: {folder_path}\n")
        return out_root

    _log(f"Found {len(image_files)} image(s) in '{folder_path}'\n")
    _log(f"Downsample factor: {n} x {k}  (row x col)\n")
    _log(f"Output folder: {out_root}\n")
    _log("-" * 60 + "\n")

    for img_path in image_files:
        rel_path = os.path.relpath(img_path, folder_path)
        out_path = os.path.join(out_root, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        try:
            img = Image.open(img_path)
            img_array = np.array(img)
            original_shape = img_array.shape

            resized_array = downsample_image(img_array, n, k)
            resized_img = Image.fromarray(resized_array)
            resized_img.save(out_path)

            new_shape = resized_array.shape
            _log(f"  [OK] {rel_path}: {original_shape} -> {new_shape}\n")
        except Exception as e:
            _log(f"  [FAIL] {rel_path}: {e}\n")

    _log("-" * 60 + "\n")
    _log("Done.\n")
    return out_root
