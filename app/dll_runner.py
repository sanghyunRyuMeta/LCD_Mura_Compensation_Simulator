"""
DLL runner module for direct DLL usage without the Simulator.
Provides functions to call the LX89507_Demura.dll directly.
"""

import os
import ctypes
import numpy as np
from PIL import Image
import time

from app.config import BASE_DIR, DLL_DIR, DLL_PATH, DLL_REG_FILE, DLL_PARA_FILE


def numpy_to_ctypes_4d(array):
    """Convert a 4D numpy array to ctypes pointer structure."""
    depth1, depth2, height, width = array.shape
    array_ctype = (ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_double))) * depth1)()
    for i in range(depth1):
        array_ctype[i] = (ctypes.POINTER(ctypes.POINTER(ctypes.c_double)) * depth2)()
        for j in range(depth2):
            array_ctype[i][j] = (ctypes.POINTER(ctypes.c_double) * height)()
            for k in range(height):
                array_ctype[i][j][k] = (array[i][j][k].ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    return array_ctype


def ctypes_to_numpy_4d(array_ctype, depth1, depth2, height, width):
    """Convert ctypes pointer structure back to numpy array."""
    numpy_array = np.zeros((depth1, depth2, height, width), dtype=np.float64)
    for i in range(depth1):
        for j in range(depth2):
            for k in range(height):
                for l in range(width):
                    numpy_array[i, j, k, l] = array_ctype[i][j][k][l]
    return numpy_array


def load_16bit_image(image_path):
    """Load a 16-bit PNG image and return as numpy array."""
    with Image.open(image_path) as img:
        return np.array(img, dtype=np.float64)


def save_16bit_image(image_data, output_filename):
    """Save numpy array as 16-bit PNG image."""
    image_data = image_data.astype(np.uint16)
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    image_pil = Image.fromarray(image_data, mode='I;16')
    image_pil.save(output_filename)


def read_camera_images(panel_path: str, demura_mode: int, log_callback=None):
    """
    Read camera images based on DEMURA_MODE.

    DEMURA_MODE = 0: RGB32, RGB64 (2 planes)
    DEMURA_MODE = 1: RGB32, RGB64, RGB128 (3 planes)
    DEMURA_MODE = 2: W32, W64, W128 (3 planes, White mode - only color channel 0)

    Returns: 4D numpy array [plane][color][height][width]
             Format per DLL: double **** [plane][color][x][y]
    """
    def _log(msg):
        if log_callback:
            log_callback(msg)

    # Get panel name from path
    panel_name = os.path.basename(panel_path)

    # Determine image dimensions from first available image
    height, width = None, None

    test_files = [
        f"{panel_name}_W32_DISP_RAW.png",
        f"{panel_name}_RED32_DISP_RAW.png",
    ]
    for test_file in test_files:
        filepath = os.path.join(panel_path, test_file)
        if os.path.exists(filepath):
            with Image.open(filepath) as img:
                width, height = img.size
            break

    if height is None or width is None:
        raise FileNotFoundError(f"No valid camera images found in {panel_path}")

    _log(f"[DLL] Image dimensions: {width}x{height}\n")

    # Create 4D array: [3 planes][3 colors][height][width]
    img_array = np.zeros((3, 3, height, width), dtype=np.float64)

    if demura_mode == 0:
        # RGB mode, 2 planes: 32, 64
        levels = [(0, 32), (1, 64)]
        for plane_idx, level in levels:
            for color_idx, color in enumerate(['RED', 'GRN', 'BLU']):
                filename = f"{panel_name}_{color}{level}_DISP_RAW.png"
                filepath = os.path.join(panel_path, filename)
                if os.path.exists(filepath):
                    img_data = load_16bit_image(filepath)
                    img_array[plane_idx, color_idx, :, :] = img_data
                    _log(f"[DLL] Loaded: {filename} -> plane[{plane_idx}][color{color_idx}]\n")
                else:
                    _log(f"[DLL] Warning: Missing {filename}\n")

    elif demura_mode == 1:
        # RGB mode, 3 planes: 32, 64, 128
        levels = [(0, 32), (1, 64), (2, 128)]
        for plane_idx, level in levels:
            for color_idx, color in enumerate(['RED', 'GRN', 'BLU']):
                filename = f"{panel_name}_{color}{level}_DISP_RAW.png"
                filepath = os.path.join(panel_path, filename)
                if os.path.exists(filepath):
                    img_data = load_16bit_image(filepath)
                    img_array[plane_idx, color_idx, :, :] = img_data
                    _log(f"[DLL] Loaded: {filename} -> plane[{plane_idx}][color{color_idx}]\n")
                else:
                    _log(f"[DLL] Warning: Missing {filename}\n")

    else:  # demura_mode == 2
        # White mode, 3 planes: W32, W64, W128
        # ONLY fills color channel 0 (per vendor code)
        levels = [(0, 32), (1, 64), (2, 128)]
        for plane_idx, level in levels:
            filename = f"{panel_name}_W{level}_DISP_RAW.png"
            filepath = os.path.join(panel_path, filename)
            if os.path.exists(filepath):
                img_data = load_16bit_image(filepath)
                img_array[plane_idx, 0, :, :] = img_data
                _log(f"[DLL] Loaded: {filename} -> plane[{plane_idx}][color0]\n")
            else:
                _log(f"[DLL] Warning: Missing {filename}\n")

    return img_array


class DLLRunner:
    """Class to manage DLL operations for demura processing."""

    def __init__(self, log_callback=None):
        self._log_callback = log_callback
        self._dll = None

    def _log(self, msg: str):
        if self._log_callback:
            self._log_callback(msg)

    def _load_dll(self):
        """Load the DLL if not already loaded."""
        if self._dll is None:
            if not os.path.exists(DLL_PATH):
                raise FileNotFoundError(f"DLL not found: {DLL_PATH}")
            self._dll = ctypes.CDLL(DLL_PATH)
            self._log(f"[DLL] Loaded: {DLL_PATH}\n")
        return self._dll

    def update_reg_file(self, updates: dict):
        """Update lxs_reg.ini with new values."""
        if not os.path.exists(DLL_REG_FILE):
            self._log(f"[DLL] Warning: {DLL_REG_FILE} not found\n")
            return

        lines = []
        with open(DLL_REG_FILE, 'r') as f:
            lines = f.readlines()

        updated_keys = set()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if '=' in stripped:
                key = stripped.split('=')[0].strip()
                if key in updates:
                    lines[i] = f"{key} = {updates[key]}\n"
                    updated_keys.add(key)

        with open(DLL_REG_FILE, 'w') as f:
            f.writelines(lines)

        if updated_keys:
            self._log(f"[DLL] Updated lxs_reg.ini: {', '.join(f'{k}={updates[k]}' for k in updated_keys)}\n")

    def update_para_file(self, updates: dict):
        """Update lxs_para.ini with new values."""
        if not os.path.exists(DLL_PARA_FILE):
            self._log(f"[DLL] Warning: {DLL_PARA_FILE} not found\n")
            return

        lines = []
        with open(DLL_PARA_FILE, 'r') as f:
            lines = f.readlines()

        updated_keys = set()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if '=' in stripped:
                key = stripped.split('=')[0].strip()
                if key in updates:
                    lines[i] = f"{key} = {updates[key]}\n"
                    updated_keys.add(key)

        with open(DLL_PARA_FILE, 'w') as f:
            f.writelines(lines)

        if updated_keys:
            self._log(f"[DLL] Updated lxs_para.ini: {', '.join(f'{k}={updates[k]}' for k in updated_keys)}\n")

    def run_demura(self, panel_path: str, output_path: str, demura_mode: int = 2):
        """
        Run the demura DLL with camera images.

        Args:
            panel_path: Path to folder containing camera images
            output_path: Path for output files (total_crc.bin, LUT.bin)
            demura_mode: 0=RGB 2planes, 1=RGB 3planes, 2=White 3planes (default)

        Returns:
            total_crc value from DLL
        """
        self._log("\n" + "="*60 + "\n")
        self._log("[DLL] Meta DEMURA Start...\n")
        self._log("="*60 + "\n\n")

        total_start_time = time.time()

        # Update DMR_MODE in reg file
        self.update_reg_file({"DMR_MODE": str(demura_mode)})

        # Read camera images
        self._log("[DLL] Loading camera images...\n")
        start_time = time.time()
        try:
            img = read_camera_images(panel_path, demura_mode, self._log_callback)
        except Exception as e:
            self._log(f"[DLL] ERROR loading images: {e}\n")
            raise

        elapsed = time.time() - start_time
        self._log(f"[DLL] Images loaded in {elapsed:.4f}s\n\n")

        # Convert to ctypes
        self._log("[DLL] Converting to ctypes...\n")
        start_time = time.time()
        img_ctypes = numpy_to_ctypes_4d(img)
        elapsed = time.time() - start_time
        self._log(f"[DLL] Conversion done in {elapsed:.4f}s\n\n")

        # Load and run DLL
        self._log("[DLL] Running LX89507_Demura DLL...\n")
        start_time = time.time()

        # Save current directory and change to DLL directory
        # (DLL looks for ini files in current working directory)
        original_cwd = os.getcwd()

        try:
            os.chdir(DLL_DIR)
            self._log(f"[DLL] Changed to DLL directory: {DLL_DIR}\n")

            dll = self._load_dll()
            demura_func = dll.LX89507_Demura_main
            demura_func.argtypes = [
                ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_double)))),
                ctypes.c_wchar_p
            ]
            demura_func.restype = ctypes.c_char_p

            # Ensure output directory exists
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # Run DLL
            total_crc = demura_func(img_ctypes, output_path)

            elapsed = time.time() - start_time
            self._log(f"[DLL] DLL execution done in {elapsed:.4f}s\n\n")

            # Clean up temporary files in DLL directory
            for temp_file in ['out_Register.txt', 'out_LUT.txt', 'mem_output.txt', 'lxs_log.txt']:
                temp_path = os.path.join(DLL_DIR, temp_file)
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

            total_elapsed = time.time() - total_start_time

            self._log("="*60 + "\n")
            self._log(f"[DLL] Total CRC: {total_crc}\n")
            self._log(f"[DLL] Total Runtime: {total_elapsed:.4f}s\n")
            self._log(f"[DLL] Output saved to: {output_path}\n")
            self._log("="*60 + "\n")
            self._log("[DLL] Meta DEMURA Finish\n\n")

            return total_crc

        except Exception as e:
            self._log(f"[DLL] ERROR: {e}\n")
            raise
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
