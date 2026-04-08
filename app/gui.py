"""
Main GUI window for the LCD Mura Compensation Simulator.
Clay Light Mode Theme.
Auto-sizes to fit 1920×1080 at any DPI scaling.
"""

import os

import customtkinter as ctk

from app.theme import Colors, APP_TITLE, APP_VERSION, APP_SUBTITLE
from app.config import REG_FILE, PARA_FILE, ICON_ICO
from app.widgets import HeaderBanner, StatusBar
from app.tabs.run_tab import RunTab
from app.tabs.editor_tab import EditorTab
from app.tabs.resize_tab import ResizeTab


class MuraCompGUI(ctk.CTk):
    """Main application window — DPI-aware sizing."""

    SCREEN_RATIO_W = 0.58
    SCREEN_RATIO_H = 0.88
    MIN_W, MIN_H = 850, 600
    MAX_W, MAX_H = 1400, 960

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.configure(fg_color=Colors.BG_PRIMARY)

        if os.path.exists(ICON_ICO):
            self.iconbitmap(ICON_ICO)

        self._apply_dynamic_geometry()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header banner ──
        header = HeaderBanner(self, title=APP_TITLE, subtitle=APP_SUBTITLE)
        header.grid(row=0, column=0, sticky="ew")

        # ── Main content area ──
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        tabview = ctk.CTkTabview(
            main_frame,
            fg_color=Colors.BG_PRIMARY,
            segmented_button_fg_color=Colors.TAB_BG,
            segmented_button_selected_color=Colors.TAB_SELECTED,
            segmented_button_selected_hover_color="#E8A930",
            segmented_button_unselected_color=Colors.TAB_BG,
            segmented_button_unselected_hover_color=Colors.TAB_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=0,
        )
        tabview.grid(row=0, column=0, sticky="nsew")

        tabview.add("🔎  Resizing Function")
        tabview.add("🔬  LCD Mura Compensation Simulator")
        tabview.add("📋  Register Setting")
        tabview.add("⚙  SW Config Setting")

        for tab_name in [
            "🔎  Resizing Function",
            "🔬  LCD Mura Compensation Simulator",
            "📋  Register Setting",
            "⚙  SW Config Setting",
        ]:
            tabview.tab(tab_name).configure(fg_color=Colors.BG_PRIMARY)

        # ── Status bar ──
        self.status_bar = StatusBar(self, version=APP_VERSION)
        self.status_bar.grid(row=2, column=0, sticky="ew")

        # ── Build tabs ──
        self.run_tab = RunTab(
            tabview.tab("🔬  LCD Mura Compensation Simulator"), self, self.status_bar,
        )
        self.resize_tab = ResizeTab(
            tabview.tab("🔎  Resizing Function"), self, self.status_bar,
        )

        log_callback = self.run_tab.append_log
        self.reg_editor = EditorTab(
            tabview.tab("📋  Register Setting"), REG_FILE, log_callback,
        )
        self.para_editor = EditorTab(
            tabview.tab("⚙  SW Config Setting"), PARA_FILE, log_callback,
        )

    def _apply_dynamic_geometry(self):
        """Size window relative to screen, center it."""
        self.update_idletasks()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        win_w = int(screen_w * self.SCREEN_RATIO_W)
        win_h = int(screen_h * self.SCREEN_RATIO_H)

        win_w = max(self.MIN_W, min(win_w, self.MAX_W))
        win_h = max(self.MIN_H, min(win_h, self.MAX_H))

        x = (screen_w - win_w) // 2
        y = max(0, (screen_h - win_h) // 2 - 20)

        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.minsize(self.MIN_W, self.MIN_H)
