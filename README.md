# LCD Mura Compensation Simulator

**LCD Mura Compensation Simulator v2.1**

A desktop GUI application for LCD mura compensation simulation. It provides an end-to-end workflow for encoding and decoding mura compensation data, **direct DLL-based demura processing**, editing register/config files, and batch-resizing camera images — interface built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

---

## Screenshots

### LCD Mura Compensation Simulator Tab
Configure panel parameters, register settings, simulator options, and decoder mode. Run the encoder, decoder, or both sequentially with real-time console output.

![LCD Mura Compensation Simulator](docs/images/Mura_Compensation_Simulator.png)

### DLL Mode Tab
Run the LX89507 Demura DLL directly without the simulator. Supports all three demura modes with automatic configuration file management.

### Resizing Function Tab
Batch downsample images using n×k box averaging. All images in a folder are recursively processed and saved to a dedicated output directory.

![Resizing Function](docs/images/resizing.png)

### Register Setting Tab
View and edit the hardware register configuration file (`reg.txt`) directly within the application. Supports save and reload operations.

![Register Setting](docs/images/RegistorSetting.png)

### SW Config Setting Tab
View and edit the simulator software configuration file (`lxs_para_sim.txt`) for parameters like block size, target radius, output format, and FBIT mode.

![SW Config Setting](docs/images/SW_Config_Setting.png)

---

## Features

- **Encoder / Decoder Simulation** — Run the LX89507 mura compensation encoder and decoder executables with configurable parameters (panel, register, gray levels, decoder mode)
- **DLL Mode** — Direct DLL-based demura processing without simulator overhead, outputting binary LUT and Total CRC files
- **Register & Config Editing** — Built-in text editors for `reg.txt` and `lxs_para_sim.txt` with save/reload functionality
- **Image Resizing** — n×k box-averaging downsampler for batch processing camera images (supports PNG, BMP, TIFF, JPEG)
- **Input Validation** — Automatic camera image naming validation, resolution checks against `H_RES`/`V_RES` in register file, and auto-rename proposals for misnamed files
- **Config Sync** — GUI parameters (DMR_MODE, PLANE values, OUTPUT_TXT, FBIT_AUTO) are automatically synced to config files before each run

---

## Demura Modes

| Mode | Description | Planes | Input Images | Output Size |
|------|-------------|--------|--------------|-------------|
| **Mode 0** | RGB Mode with compression | 2 | RED/GRN/BLU 32, 64 | ~73,300 bytes |
| **Mode 1** | RGB Mode with compression | 3 | RED/GRN/BLU 32, 64, 128 | ~77,056 bytes |
| **Mode 2** | White Mode (POR) | 3 | W32, W64, W128 | ~73,744 bytes |

---

## Project Structure

```
LCD_Mura_Compensation_Simulator/
├── main.py                  # Application entry point
├── app/
│   ├── __init__.py           # Package exports
│   ├── gui.py                # Main window (MuraCompGUI) — tab layout, header, status bar
│   ├── config.py             # Path constants and default parameter values
│   ├── simulator.py          # Simulator class — runs encoder/decoder executables
│   ├── dll_runner.py         # DLL runner class — direct DLL demura processing
│   ├── file_utils.py         # Read/write tab-separated config files (reg.txt, lxs_para_sim)
│   ├── resize_nxk.py         # n×k box-averaging image downsampler
│   ├── theme.py              # Color palette, fonts, spacing (Clay Light Mode Theme)
│   ├── widgets.py            # Reusable styled widgets (SectionCard, AccentButton, StatusBar, etc.)
│   ├── assets/               # Logo and icon files
│   └── tabs/
│       ├── run_tab.py        # LCD Mura Compensation Simulator tab — parameters, config, decoder mode, run actions
│       ├── dll_tab.py        # DLL Mode tab — direct DLL demura processing
│       ├── editor_tab.py     # Register / SW Config editor tab — load, edit, save config files
│       └── resize_tab.py     # Resizing Function tab — folder selection, n×k inputs, batch resize
├── DLL/                      # DLL files and configuration
│   ├── LX89507_Demura.dll    # Demura DLL library
│   ├── lxs_para.ini          # DLL parameter configuration
│   └── lxs_reg.ini           # DLL register configuration
├── Simulator/                # Encoder/decoder executables and parameter files
│   ├── LX89507_Demura_MDC_enc.exe
│   ├── LX89507_Demura_MDC_dec.exe
│   └── lxs_para_sim.txt
├── _in/                      # Input files
│   ├── camera_image/         # Camera-captured images organized by panel (J1, J2, etc.)
│   ├── display_image/        # Display test images (BMP)
│   └── register/             # Register configuration files (reg.txt)
├── _out/                     # Output directory for simulation results
└── docs/
    └── images/               # GUI screenshots for documentation
```

---

## Requirements

- **Python** 3.10+
- **Dependencies:**
  - [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — Modern GUI framework
  - [Pillow](https://python-pillow.org/) — Image loading and processing
  - [NumPy](https://numpy.org/) — Array operations for image downsampling

Install dependencies:

```bash
pip install customtkinter pillow numpy
```

---

## Usage

### Run the Application

```bash
python main.py
```

### Workflow (Simulator Mode)

1. **Set Parameters** — In the *LCD Mura Compensation Simulator* tab, configure panel name, register file, and gray levels
2. **Configure Register** — Adjust DMR_MODE and PLANE values, or edit `reg.txt` directly in the *Register Setting* tab
3. **Configure Simulator** — Set output format and FBIT mode, or edit `lxs_para_sim.txt` in the *SW Config Setting* tab
4. **Place Camera Images** — Put camera-captured images in `_in/camera_image/<panel>/` following the naming convention:
   - White mode: `<panel>_W<level>_DISP_RAW.png`
   - RGB mode: `<panel>_<color><level>_DISP_RAW.png` (color = RED, GRN, BLU)
5. **Run Simulation** — Click *Run Encoder*, *Run Decoder*, or *Run Both* to execute the compensation pipeline
6. **Check Results** — Output files are saved to the `_out/` directory

### Workflow (DLL Mode)

1. **Select Input Folder** — In the *DLL Mode* tab, browse to the folder containing camera images
2. **Select Demura Mode** — Choose Mode 0 (RGB 2-plane), Mode 1 (RGB 3-plane), or Mode 2 (White 3-plane)
3. **Select Output Folder** — Choose the destination for output files
4. **Run DLL Demura** — Click *Run DLL Demura* to process images and generate LUT binary files
5. **Output Files** — `<output>.bin` (LUT data) and `<output>_Total_crc.bin` (CRC checksum)

### Image Resizing

Use the *Resizing Function* tab to batch-downsample images:

1. Select the image folder
2. Set n (rows) and k (cols) downsample factors
3. Click *Run Resize* — results are saved to `<folder>/<n>x<k>_resized/`

---

## License

Internal use only.
