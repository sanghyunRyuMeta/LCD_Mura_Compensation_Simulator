"""
Meta Reality Labs — Neo-Dark Theme v3
LCD Demura Simulator

Color philosophy — warm dark tones with clear layering:
  ┌──────────────────────────────────────────────────────────┐
  │  BG_DEEPEST   #0C0C0E  ← Chrome, status bar             │
  │  BG_PRIMARY   #121215  ← Main canvas                     │
  │  BG_ELEVATED  #1A1A1F  ← Cards (clearly lifted)          │
  │  BG_INPUT     #141418  ← Input recessed into card        │
  │  BG_HOVER     #222228  ← Hover / interactive             │
  │  BORDER       #27272A  ← Standard borders                │
  │  BORDER_CARD  #2C2C34  ← Card edges — visible!           │
  └──────────────────────────────────────────────────────────┘

Typography scale (1.25 ratio):
  26 → 18 → 15 → 13 → 11
"""


class Colors:
    # ── Layered backgrounds (warm dark) ──
    BG_DEEPEST = "#0C0C0E"
    BG_PRIMARY = "#121215"
    BG_ELEVATED = "#1A1A1F"
    BG_INPUT = "#141418"
    BG_HOVER = "#222228"
    BG_ACTIVE = "#2A2A32"

    # Backward-compat aliases
    BG_DARKEST = BG_DEEPEST
    BG_DARK = BG_DEEPEST
    BG_SURFACE = BG_ELEVATED
    BG_CARD = BG_ELEVATED
    BG_CARD_HOVER = BG_HOVER

    # ── Accent — vivid blue with glow variants ──
    ACCENT_BLUE = "#3B82F6"
    ACCENT_BLUE_HOVER = "#60A5FA"
    ACCENT_BLUE_DIM = "#2563EB"
    ACCENT_BLUE_MUTED = "#3B82F618"
    ACCENT_BLUE_GLOW = "#3B82F630"

    ACCENT_CYAN = "#2DD4BF"
    ACCENT_TEAL = "#2DD4BF"
    ACCENT_PURPLE = "#A78BFA"
    ACCENT_PURPLE_HOVER = "#C4B5FD"
    ACCENT_GRADIENT_START = "#3B82F6"
    ACCENT_GRADIENT_END = "#A78BFA"

    # ── Semantic colors (vivid, modern) ──
    SUCCESS = "#34D399"
    SUCCESS_DIM = "#059669"
    WARNING = "#FBBF24"
    WARNING_DIM = "#D97706"
    ERROR = "#F87171"
    ERROR_DIM = "#DC2626"

    # ── Text hierarchy (high contrast) ──
    TEXT_PRIMARY = "#F4F4F5"
    TEXT_SECONDARY = "#A1A1AA"
    TEXT_MUTED = "#71717A"
    TEXT_FAINT = "#52525B"
    TEXT_ACCENT = "#60A5FA"
    TEXT_ON_ACCENT = "#FFFFFF"

    # ── Borders ──
    BORDER = "#27272A"
    BORDER_CARD = "#2C2C34"
    BORDER_SUBTLE = "#1E1E22"
    BORDER_ACCENT = "#3B82F640"
    BORDER_INPUT_FOCUS = "#60A5FA"

    # ── Buttons ──
    BTN_PRIMARY = "#3B82F6"
    BTN_PRIMARY_HOVER = "#60A5FA"
    BTN_SECONDARY = "#27272A"
    BTN_SECONDARY_HOVER = "#3F3F46"
    BTN_DANGER = "#DC2626"
    BTN_DANGER_HOVER = "#EF4444"
    BTN_SUCCESS = "#059669"
    BTN_SUCCESS_HOVER = "#34D399"

    # ── Tabs ──
    TAB_BG = "#121215"
    TAB_SELECTED = "#3B82F6"
    TAB_HOVER = "#27272A"

    # ── Console ──
    CONSOLE_BG = "#0A0A0C"
    CONSOLE_BORDER = "#27272A"
    CONSOLE_TEXT = "#86EFAC"


class Fonts:
    FAMILY = "Segoe UI"
    MONO = "Cascadia Code"
    MONO_FALLBACK = "Consolas"

    HEADER_SIZE = 26
    SUBHEADER_SIZE = 18
    SECTION_SIZE = 15
    TITLE_SIZE = 15
    BODY_SIZE = 13
    SMALL_SIZE = 11
    MONO_SIZE = 12


class Spacing:
    """8px grid — balanced for 1920×1080 @ 100-125% DPI."""
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 14
    PAD_LG = 22
    PAD_XL = 28
    PAD_XXL = 32

    CARD_PAD = 18
    CARD_PAD_HEADER = 12
    SECTION_GAP = 14
    WIDGET_GAP = 6
    FORM_LABEL_GAP = 8

    CORNER_RADIUS = 12
    CORNER_RADIUS_SM = 8
    CORNER_RADIUS_LG = 16

    BORDER_WIDTH = 1
    BORDER_WIDTH_ACCENT = 2


class Heights:
    """Fixed-height elements — balanced for 1080p."""
    HEADER_BANNER = 64
    STATUS_BAR = 30
    BUTTON = 36
    INPUT = 34
    EDITOR_TOOLBAR = 42


APP_TITLE = "LCD Demura Simulator"
APP_VERSION = "v2.0"
APP_SUBTITLE = "Meta Reality Labs  ·  LCD Demura Simulator"
