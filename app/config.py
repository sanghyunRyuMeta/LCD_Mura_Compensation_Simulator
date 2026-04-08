import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMULATOR_DIR = os.path.join(BASE_DIR, "Simulator")
REG_FILE = os.path.join(BASE_DIR, "_in", "register", "reg.txt")
PARA_FILE = os.path.join(SIMULATOR_DIR, "lxs_para_sim.txt")
OUT_DIR = os.path.join(BASE_DIR, "_out")
IN_DIR = os.path.join(BASE_DIR, "_in")

ENC_EXE = os.path.join(SIMULATOR_DIR, "LX89507_Demura_MDC_enc.exe")
DEC_EXE = os.path.join(SIMULATOR_DIR, "LX89507_Demura_MDC_dec.exe")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
ICON_ICO = os.path.join(ASSETS_DIR, "meta_icon.ico")
ICON_PNG = os.path.join(ASSETS_DIR, "meta_icon.png")
LOGO_PNG = os.path.join(ASSETS_DIR, "meta_logo.png")

DEFAULT_PANEL = "J1"
DEFAULT_REG = "reg"
DEFAULT_GRAYLEVELS = "32,64,128"
DEFAULT_IMAGE = "checkerboard_2328x2488_size100.bmp"
