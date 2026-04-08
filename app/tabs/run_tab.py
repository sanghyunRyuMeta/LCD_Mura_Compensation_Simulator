import os
import tkinter as tk
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from app.theme import Colors, Fonts, Spacing
from app.config import (
    BASE_DIR,
    IN_DIR,
    OUT_DIR,
    REG_FILE,
    PARA_FILE,
    DEFAULT_PANEL,
    DEFAULT_REG,
    DEFAULT_GRAYLEVELS,
    DEFAULT_IMAGE,
)
from app.widgets import SectionCard, AccentButton, StyledEntry, StyledLabel
from app.simulator import Simulator
from app.file_utils import read_config, write_config_values


DMR_MODE_INFO = {
    "0": ("RGB Mode, 2 Planes, Compression", 2),
    "1": ("RGB Mode, 3 Planes, Compression", 3),
    "2": ("White Mode, 3 Planes, No Compression", 3),
}


class RunTab:
    def __init__(
        self,
        parent: ctk.CTkFrame,
        root: ctk.CTk,
        status_bar=None,
    ):
        self._root = root
        self._status_bar = status_bar
        self._simulator = Simulator(log_callback=self._append_log)

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # ── PanedWindow for draggable split between settings and console ──
        paned = tk.PanedWindow(
            parent,
            orient=tk.VERTICAL,
            sashwidth=6,
            sashrelief=tk.FLAT,
            bg="#FBBD41",
            opaqueresize=True,
        )
        paned.grid(row=0, column=0, sticky="nsew")

        # ── Top pane: scrollable settings ──
        top_frame = ctk.CTkFrame(paned, fg_color=Colors.BG_PRIMARY, corner_radius=0)

        scroll = ctk.CTkScrollableFrame(
            top_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_CARD,
            scrollbar_button_hover_color=Colors.BG_CARD_HOVER,
        )
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)

        row = 0
        self._build_parameters(scroll, row); row += 1
        self._build_register_config(scroll, row); row += 1
        self._build_simulator_config(scroll, row); row += 1
        self._build_decoder_mode(scroll, row); row += 1
        self._build_action_buttons(scroll, row); row += 1

        paned.add(top_frame, stretch="always")

        # ── Bottom pane: console toolbar + log ──
        bottom_frame = ctk.CTkFrame(paned, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        bottom_frame.grid_rowconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        self._build_console_toolbar(bottom_frame, grid_row=0)

        self._log_widget = ctk.CTkTextbox(
            bottom_frame,
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.MONO_SIZE),
            fg_color=Colors.CONSOLE_BG,
            text_color=Colors.CONSOLE_TEXT,
            border_color=Colors.CONSOLE_BORDER,
            border_width=Spacing.BORDER_WIDTH,
            corner_radius=Spacing.CORNER_RADIUS_SM,
            state="disabled",
        )
        self._log_widget.grid(
            row=1, column=0, sticky="nsew",
            padx=Spacing.PAD_LG, pady=(Spacing.PAD_SM, Spacing.PAD_LG),
        )

        paned.add(bottom_frame, minsize=200, stretch="always")

        # Fix the sash position when this tab becomes visible.
        # When another tab is the default, paned has 0 height at init time,
        # so we defer until the widget is actually mapped/visible.
        self._paned = paned
        self._sash_fixed = False

        def _fix_sash(event=None):
            if self._sash_fixed:
                return
            try:
                h = paned.winfo_height()
                if h > 50:
                    paned.sash_place(0, 0, max(h - 250, 200))
                    self._sash_fixed = True
            except Exception:
                pass

        paned.bind("<Map>", _fix_sash)
        paned.bind("<Configure>", _fix_sash)
        # Fallback: retry periodically until fixed
        def _retry_sash():
            if not self._sash_fixed:
                _fix_sash()
                parent.after(500, _retry_sash)
        parent.after(500, _retry_sash)

        # Load initial values from files
        self._load_config_from_files()

    # ------------------------------------------------------------------ #
    #  Parameters
    # ------------------------------------------------------------------ #
    def _build_parameters(self, parent, row):
        card = SectionCard(parent, title="Parameters", icon="⚙")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=(Spacing.PAD_MD, Spacing.PAD_SM))
        content = card.get_content_frame()
        content.grid_columnconfigure(1, weight=1)

        labels = ["Panel", "Register", "Gray Levels"]
        defaults = [DEFAULT_PANEL, DEFAULT_REG, DEFAULT_GRAYLEVELS]
        hints = ["Panel identifier (e.g., J1, J2)", "Register file name (without .txt)", "Comma-separated gray levels"]
        self.param_vars = {}

        for i, (label, default, hint) in enumerate(zip(labels, defaults, hints)):
            StyledLabel(content, text=f"{label}:", style="body").grid(
                row=i * 2, column=0, sticky="w", padx=(0, Spacing.PAD_MD), pady=(Spacing.PAD_SM, 0)
            )
            StyledLabel(content, text=hint, style="small").grid(
                row=i * 2, column=1, sticky="e", pady=(Spacing.PAD_SM, 0)
            )
            var = ctk.StringVar(value=default)
            entry = StyledEntry(content, textvariable=var)
            entry.grid(row=i * 2 + 1, column=0, columnspan=2, sticky="ew", pady=(2, Spacing.PAD_XS))
            self.param_vars[label] = var

    # ------------------------------------------------------------------ #
    #  Register config (DMR_MODE, PLANE values)
    # ------------------------------------------------------------------ #
    def _build_register_config(self, parent, row):
        card = SectionCard(parent, title="Register Config  (reg.txt)", icon="📋")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)
        content = card.get_content_frame()
        content.grid_columnconfigure(1, weight=1)

        # -- DMR_MODE --
        dmr_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                  border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
        dmr_frame.pack(fill="x", pady=(0, Spacing.PAD_SM))
        dmr_frame.grid_columnconfigure(1, weight=1)

        StyledLabel(dmr_frame, text="DMR_MODE:", style="body").grid(
            row=0, column=0, sticky="w", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM
        )

        self.dmr_mode_var = ctk.StringVar(value="2")
        self._dmr_menu = ctk.CTkOptionMenu(
            dmr_frame,
            variable=self.dmr_mode_var,
            values=["0", "1", "2"],
            command=self._on_dmr_mode_change,
            width=80,
            fg_color=Colors.BG_INPUT,
            button_color="#55534E",
            button_hover_color="#9F9B93",
            dropdown_fg_color=Colors.BG_ELEVATED,
            dropdown_hover_color=Colors.BG_HOVER,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
        )
        self._dmr_menu.grid(row=0, column=1, sticky="w", padx=Spacing.PAD_SM, pady=Spacing.PAD_SM)

        self._dmr_desc_label = StyledLabel(dmr_frame, text="", style="small")
        self._dmr_desc_label.grid(row=0, column=2, sticky="e", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)

        # -- PLANE values --
        plane_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                    border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
        plane_frame.pack(fill="x")
        plane_frame.grid_columnconfigure(1, weight=1)
        plane_frame.grid_columnconfigure(3, weight=1)
        plane_frame.grid_columnconfigure(5, weight=1)

        self.plane_vars = {}
        for i, plane in enumerate(["PLANE00", "PLANE01", "PLANE02"]):
            StyledLabel(plane_frame, text=f"{plane}:", style="body").grid(
                row=0, column=i * 2, sticky="w", padx=(Spacing.PAD_MD if i == 0 else Spacing.PAD_SM, 4), pady=Spacing.PAD_SM
            )
            var = ctk.StringVar(value="0")
            entry = StyledEntry(plane_frame, textvariable=var, width=80)
            entry.grid(row=0, column=i * 2 + 1, sticky="ew", padx=(0, Spacing.PAD_SM), pady=Spacing.PAD_SM)
            self.plane_vars[plane] = var

        StyledLabel(
            content,
            text="PLANE values correspond to input gray levels. DMR_MODE determines how many planes are active.",
            style="small",
        ).pack(anchor="w", pady=(Spacing.PAD_XS, 0))

    def _on_dmr_mode_change(self, value):
        desc, _ = DMR_MODE_INFO.get(value, ("Unknown", 0))
        self._dmr_desc_label.configure(text=desc)

    # ------------------------------------------------------------------ #
    #  Simulator config (OUTPUT_TXT, FBIT_AUTO)
    # ------------------------------------------------------------------ #
    def _build_simulator_config(self, parent, row):
        card = SectionCard(parent, title="Simulator Config  (lxs_para_sim)", icon="🔬")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)
        content = card.get_content_frame()

        options_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                      border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
        options_frame.pack(fill="x")
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)

        # -- OUTPUT_TXT --
        StyledLabel(options_frame, text="Output Format:", style="body").grid(
            row=0, column=0, sticky="w", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM
        )
        self.output_format_var = ctk.StringVar(value="TXT (.txt)")
        self._output_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.output_format_var,
            values=["TXT (.txt)", "Binary (.bin)"],
            width=140,
            fg_color=Colors.BG_INPUT,
            button_color="#55534E",
            button_hover_color="#9F9B93",
            dropdown_fg_color=Colors.BG_ELEVATED,
            dropdown_hover_color=Colors.BG_HOVER,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
        )
        self._output_menu.grid(row=0, column=1, sticky="w", padx=Spacing.PAD_SM, pady=Spacing.PAD_SM)

        # -- FBIT_AUTO --
        StyledLabel(options_frame, text="FBIT Mode:", style="body").grid(
            row=0, column=2, sticky="w", padx=(Spacing.PAD_LG, Spacing.PAD_SM), pady=Spacing.PAD_SM
        )
        self.fbit_auto_var = ctk.StringVar(value="Auto")
        self._fbit_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.fbit_auto_var,
            values=["Auto", "Manual"],
            width=110,
            fg_color=Colors.BG_INPUT,
            button_color="#55534E",
            button_hover_color="#9F9B93",
            dropdown_fg_color=Colors.BG_ELEVATED,
            dropdown_hover_color=Colors.BG_HOVER,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
        )
        self._fbit_menu.grid(row=0, column=3, sticky="w", padx=Spacing.PAD_SM, pady=Spacing.PAD_SM)

        StyledLabel(
            content,
            text="Output Format: TXT saves LUT & registers as .txt files; Binary saves as .bin  │  "
                 "FBIT: Auto lets encoder set fraction bits; Manual uses values from reg.txt",
            style="small",
        ).pack(anchor="w", pady=(Spacing.PAD_XS, 0))

    # ------------------------------------------------------------------ #
    #  Load initial values from files
    # ------------------------------------------------------------------ #
    def _load_config_from_files(self):
        # Read reg.txt
        reg_name = self.param_vars["Register"].get().strip()
        reg_path = os.path.join(BASE_DIR, "_in", "register", f"{reg_name}.txt")
        reg = read_config(reg_path)

        if "DMR_MODE" in reg:
            self.dmr_mode_var.set(reg["DMR_MODE"])
            self._on_dmr_mode_change(reg["DMR_MODE"])
        for plane in ["PLANE00", "PLANE01", "PLANE02"]:
            if plane in reg:
                self.plane_vars[plane].set(reg[plane])

        # Read lxs_para_sim
        para = read_config(PARA_FILE)
        if "OUTPUT_TXT" in para:
            self.output_format_var.set("TXT (.txt)" if para["OUTPUT_TXT"] == "1" else "Binary (.bin)")
        if "FBIT_AUTO" in para:
            self.fbit_auto_var.set("Auto" if para["FBIT_AUTO"] == "1" else "Manual")

    # ------------------------------------------------------------------ #
    #  Sync config to files before run
    # ------------------------------------------------------------------ #
    def _sync_config_to_files(self):
        reg_name = self.param_vars["Register"].get().strip()
        reg_path = os.path.join(BASE_DIR, "_in", "register", f"{reg_name}.txt")

        # Update reg.txt: DMR_MODE + PLANE values
        reg_updates = {
            "DMR_MODE": self.dmr_mode_var.get(),
            "PLANE00": self.plane_vars["PLANE00"].get().strip(),
            "PLANE01": self.plane_vars["PLANE01"].get().strip(),
            "PLANE02": self.plane_vars["PLANE02"].get().strip(),
        }
        updated = write_config_values(reg_path, reg_updates)
        if updated:
            self._append_log(f"[SYNC] Updated reg.txt: {', '.join(f'{k}={reg_updates[k]}' for k in updated)}\n")

        # Update lxs_para_sim: OUTPUT_TXT + FBIT_AUTO
        output_val = "1" if self.output_format_var.get() == "TXT (.txt)" else "0"
        fbit_val = "1" if self.fbit_auto_var.get() == "Auto" else "0"
        para_updates = {"OUTPUT_TXT": output_val, "FBIT_AUTO": fbit_val}
        updated = write_config_values(PARA_FILE, para_updates)
        if updated:
            self._append_log(f"[SYNC] Updated lxs_para_sim: {', '.join(f'{k}={para_updates[k]}' for k in updated)}\n")

    # ------------------------------------------------------------------ #
    #  Decoder mode
    # ------------------------------------------------------------------ #
    def _build_decoder_mode(self, parent, row):
        card = SectionCard(parent, title="Decoder Mode", icon="🔧")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)
        content = card.get_content_frame()
        content.grid_columnconfigure(1, weight=1)

        self.dec_mode = ctk.StringVar(value="0")

        mode0_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                    border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
        mode0_frame.pack(fill="x", pady=(0, Spacing.PAD_SM))

        ctk.CTkRadioButton(
            mode0_frame, text="Mode 0  —  Grayscale Image",
            variable=self.dec_mode, value="0", command=self._on_dec_mode_change,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
            text_color=Colors.TEXT_PRIMARY, fg_color="#000000",
            hover_color="#333333", border_color=Colors.BORDER,
        ).pack(anchor="w", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)

        StyledLabel(mode0_frame, text="Uses Gray Levels parameter for grayscale compensation images", style="small",
                    ).pack(anchor="w", padx=(40, Spacing.PAD_MD), pady=(0, Spacing.PAD_SM))

        mode1_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                    border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
        mode1_frame.pack(fill="x")

        ctk.CTkRadioButton(
            mode1_frame, text="Mode 1  —  Custom Image",
            variable=self.dec_mode, value="1", command=self._on_dec_mode_change,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
            text_color=Colors.TEXT_PRIMARY, fg_color="#000000",
            hover_color="#333333", border_color=Colors.BORDER,
        ).pack(anchor="w", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)

        img_row = ctk.CTkFrame(mode1_frame, fg_color="transparent")
        img_row.pack(fill="x", padx=(40, Spacing.PAD_MD), pady=(0, Spacing.PAD_SM))
        img_row.grid_columnconfigure(0, weight=1)

        self.custom_image_var = ctk.StringVar(value=DEFAULT_IMAGE)
        self._custom_image_entry = StyledEntry(img_row, textvariable=self.custom_image_var)
        self._custom_image_entry.configure(state="disabled")
        self._custom_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.PAD_SM))

        self._browse_btn = AccentButton(
            img_row, text="Browse", style="secondary", icon="📁", width=110,
            command=self._browse_custom_image,
        )
        self._browse_btn.configure(state="disabled")
        self._browse_btn.grid(row=0, column=1)

    def _on_dec_mode_change(self):
        if self.dec_mode.get() == "1":
            self._custom_image_entry.configure(state="normal")
            self._browse_btn.configure(state="normal")
        else:
            self._custom_image_entry.configure(state="disabled")
            self._browse_btn.configure(state="disabled")

    def _browse_custom_image(self):
        display_dir = os.path.join(BASE_DIR, "_in", "display_image")
        filepath = filedialog.askopenfilename(
            title="Select Custom Image",
            initialdir=display_dir if os.path.isdir(display_dir) else BASE_DIR,
            filetypes=[("Image files", "*.bmp *.png *.jpg *.jpeg *.tif *.tiff"), ("All files", "*.*")],
        )
        if filepath:
            self.custom_image_var.set(os.path.basename(filepath))

    # ------------------------------------------------------------------ #
    #  Action buttons
    # ------------------------------------------------------------------ #
    def _build_action_buttons(self, parent, row):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)

        AccentButton(
            btn_frame, text="Run Encoder", style="primary", icon="▶",
            width=170, command=self._run_encoder,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_frame, text="Run Decoder", style="primary", icon="▶",
            width=170, command=self._run_decoder,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_frame, text="Run Both (Enc → Dec)", style="success", icon="▶▶",
            width=220, command=self._run_both,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

    # ------------------------------------------------------------------ #
    #  Console toolbar (placed in parent, outside scrollable frame)
    # ------------------------------------------------------------------ #
    def _build_console_toolbar(self, parent, grid_row):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=grid_row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=(Spacing.PAD_MD, 0))

        left = ctk.CTkFrame(toolbar, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left, text="●", font=ctk.CTkFont(size=8), text_color=Colors.SUCCESS, width=14,
        ).pack(side="left", padx=(0, Spacing.PAD_XS))

        StyledLabel(left, text="Console Output", style="title").pack(side="left")

        right = ctk.CTkFrame(toolbar, fg_color="transparent")
        right.pack(side="right")

        AccentButton(right, text="Clear", style="secondary", icon="🗑", width=90, command=self._clear_log,
                     ).pack(side="right", padx=(Spacing.PAD_SM, 0))
        AccentButton(right, text="OutputFolder", style="secondary", icon="📂", width=145, command=self._open_out_folder,
                     ).pack(side="right", padx=(Spacing.PAD_SM, 0))
        AccentButton(right, text="InputFolder", style="secondary", icon="📂", width=140, command=self._open_in_folder,
                     ).pack(side="right")

    @staticmethod
    def _open_in_folder():
        if os.path.isdir(IN_DIR):
            os.startfile(IN_DIR)
        else:
            messagebox.showwarning("Folder Not Found", f"_in folder does not exist:\n{IN_DIR}")

    @staticmethod
    def _open_out_folder():
        if os.path.isdir(OUT_DIR):
            os.startfile(OUT_DIR)
        else:
            messagebox.showwarning("Folder Not Found", f"_out folder does not exist:\n{OUT_DIR}")

    # ------------------------------------------------------------------ #
    #  Image name validation
    # ------------------------------------------------------------------ #
    def _extract_level(self, filename: str, levels: list[str]) -> str | None:
        name = os.path.splitext(filename)[0]
        for level in levels:
            if f"W{level}" in name or f"w{level}" in name:
                return level
            if name == level:
                return level
        return None

    def _validate_camera_images(self) -> bool:
        panel = self.param_vars["Panel"].get().strip()
        graylevels = self.param_vars["Gray Levels"].get().strip()
        levels = [g.strip() for g in graylevels.split(",") if g.strip()]
        mode = self.dec_mode.get()
        is_rgb = mode in ("0", "1")

        camera_dir = os.path.join(BASE_DIR, "_in", "camera_image", panel)

        if is_rgb:
            return self._validate_camera_images_rgb(panel, levels, camera_dir)
        return self._validate_camera_images_white(panel, levels, camera_dir)

    def _validate_camera_images_rgb(self, panel: str, levels: list[str], camera_dir: str) -> bool:
        if not os.path.isdir(camera_dir):
            messagebox.showerror("Missing Folder", f"Camera image folder not found:\n{camera_dir}")
            return False

        colors = ["RED", "GRN", "BLU"]
        existing_files = [
            f for f in os.listdir(camera_dir)
            if f.lower() != "thumbs.db" and os.path.isfile(os.path.join(camera_dir, f))
        ]

        missing = []
        for color in colors:
            for level in levels:
                expected = f"{panel}_{color}{level}_DISP_RAW.png"
                if expected not in existing_files:
                    missing.append(expected)

        if missing:
            msg = (
                "Expected but MISSING RGB images:\n  • "
                + "\n  • ".join(missing)
                + "\n\nDo you want to continue anyway?"
            )
            return messagebox.askyesno("Missing RGB Images", msg)

        return True

    def _validate_camera_images_white(self, panel: str, levels: list[str], camera_dir: str) -> bool:
        if not os.path.isdir(camera_dir):
            messagebox.showerror("Missing Folder", f"Camera image folder not found:\n{camera_dir}")
            return False

        existing_files = [
            f for f in os.listdir(camera_dir)
            if f.lower() != "thumbs.db" and os.path.isfile(os.path.join(camera_dir, f))
        ]

        rgb_pattern = {f"{panel}_{c}{l}_DISP_RAW.png" for c in ["RED", "GRN", "BLU"] for l in levels}

        correct = set()
        bad_names = []
        rename_map = {}

        for fname in existing_files:
            if fname in rgb_pattern:
                continue
            is_correct = False
            for level in levels:
                if fname == f"{panel}_W{level}_DISP_RAW.png":
                    correct.add(level)
                    is_correct = True
                    break
            if not is_correct:
                bad_names.append(fname)

        missing_levels = [l for l in levels if l not in correct]

        for fname in bad_names:
            level = self._extract_level(fname, missing_levels)
            if level:
                expected = f"{panel}_W{level}_DISP_RAW.png"
                rename_map[fname] = expected
                missing_levels.remove(level)

        unresolved_bad = [f for f in bad_names if f not in rename_map]

        if rename_map:
            lines = [f"  {old}  →  {new}" for old, new in rename_map.items()]
            msg = (
                f"The following files in '{panel}/' don't match the expected naming "
                f"convention ({panel}_W{{level}}_DISP_RAW.png).\n\n"
                "Proposed renames:\n" + "\n".join(lines)
            )
            if missing_levels:
                msg += "\n\nStill missing (no matching file found):\n  • " + "\n  • ".join(
                    f"{panel}_W{l}_DISP_RAW.png" for l in missing_levels
                )
            if unresolved_bad:
                msg += "\n\nUnrecognized files (will be ignored):\n  • " + "\n  • ".join(unresolved_bad)
            msg += "\n\nRename and continue?"

            if not messagebox.askyesno("Rename Camera Images?", msg):
                return False

            for old_name, new_name in rename_map.items():
                old_path = os.path.join(camera_dir, old_name)
                new_path = os.path.join(camera_dir, new_name)
                try:
                    os.rename(old_path, new_path)
                    self._append_log(f"[RENAME] {old_name} → {new_name}\n")
                except Exception as e:
                    messagebox.showerror("Rename Error", f"Failed to rename {old_name}:\n{e}")
                    return False

            if missing_levels:
                msg = "Some images are still missing after rename:\n  • " + "\n  • ".join(
                    f"{panel}_W{l}_DISP_RAW.png" for l in missing_levels
                )
                msg += "\n\nContinue anyway?"
                return messagebox.askyesno("Missing Images", msg)
            return True

        if missing_levels or unresolved_bad:
            msg_parts = []
            if missing_levels:
                msg_parts.append(
                    "Expected but MISSING:\n  • "
                    + "\n  • ".join(f"{panel}_W{l}_DISP_RAW.png" for l in missing_levels)
                )
            if unresolved_bad:
                msg_parts.append(
                    f"Unexpected file names (should be {panel}_W{{level}}_DISP_RAW.png):\n  • "
                    + "\n  • ".join(unresolved_bad)
                )
            msg = "\n\n".join(msg_parts)
            msg += "\n\nDo you want to continue anyway?"
            return messagebox.askyesno("Camera Image Naming Issue", msg)

        return True

    # ------------------------------------------------------------------ #
    #  Image resolution validation
    # ------------------------------------------------------------------ #
    def _read_reg_resolution(self) -> tuple[int, int] | None:
        reg_name = self.param_vars["Register"].get().strip()
        reg_path = os.path.join(BASE_DIR, "_in", "register", f"{reg_name}.txt")
        h_res = None
        v_res = None
        try:
            with open(reg_path, "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        if parts[0] == "H_RES":
                            h_res = int(parts[1])
                        elif parts[0] == "V_RES":
                            v_res = int(parts[1])
            if h_res is not None and v_res is not None:
                return (h_res, v_res)
        except Exception:
            pass
        return None

    def _validate_image_resolution(self) -> bool:
        resolution = self._read_reg_resolution()
        if resolution is None:
            messagebox.showwarning(
                "Resolution Check Skipped",
                "Could not read H_RES / V_RES from reg.txt.\nSkipping resolution validation.",
            )
            return True

        expected_w, expected_h = resolution
        panel = self.param_vars["Panel"].get().strip()
        graylevels = self.param_vars["Gray Levels"].get().strip()
        levels = [g.strip() for g in graylevels.split(",") if g.strip()]
        camera_dir = os.path.join(BASE_DIR, "_in", "camera_image", panel)
        mode = self.dec_mode.get()
        is_rgb = mode in ("0", "1")

        mismatches = []
        if is_rgb:
            for color in ["RED", "GRN", "BLU"]:
                for level in levels:
                    fname = f"{panel}_{color}{level}_DISP_RAW.png"
                    fpath = os.path.join(camera_dir, fname)
                    if not os.path.isfile(fpath):
                        continue
                    try:
                        with Image.open(fpath) as img:
                            img_w, img_h = img.size
                        if img_w != expected_w or img_h != expected_h:
                            mismatches.append(
                                f"  {fname}:  {img_w}×{img_h}  (expected {expected_w}×{expected_h})"
                            )
                    except Exception as e:
                        mismatches.append(f"  {fname}:  could not read — {e}")
        else:
            for level in levels:
                fname = f"{panel}_W{level}_DISP_RAW.png"
                fpath = os.path.join(camera_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                try:
                    with Image.open(fpath) as img:
                        img_w, img_h = img.size
                    if img_w != expected_w or img_h != expected_h:
                        mismatches.append(
                            f"  {fname}:  {img_w}×{img_h}  (expected {expected_w}×{expected_h})"
                        )
                except Exception as e:
                    mismatches.append(f"  {fname}:  could not read — {e}")

        if mismatches:
            msg = (
                f"Image resolution does not match reg.txt "
                f"(H_RES={expected_w}, V_RES={expected_h}):\n\n"
                + "\n".join(mismatches)
                + "\n\nPlease fix the images or update H_RES / V_RES in reg.txt."
            )
            messagebox.showerror("Resolution Mismatch", msg)
            return False

        return True

    # ------------------------------------------------------------------ #
    #  Run helpers
    # ------------------------------------------------------------------ #
    def _get_params(self):
        mode = self.dec_mode.get()
        last_arg = self.param_vars["Gray Levels"].get().strip() if mode == "0" else self.custom_image_var.get().strip()
        return {
            "panel": self.param_vars["Panel"].get().strip(),
            "reg": self.param_vars["Register"].get().strip(),
            "mode": mode,
            "last_arg": last_arg,
        }

    def _set_status(self, text: str, status: str = "ready"):
        if self._status_bar:
            self._root.after(0, lambda: self._status_bar.set_status(text, status))

    def _pre_run_checks(self) -> bool:
        if not self._validate_camera_images():
            return False
        if not self._validate_image_resolution():
            return False
        self._sync_config_to_files()
        return True

    def _run_encoder(self):
        if not self._pre_run_checks():
            return
        p = self._get_params()

        def _task():
            self._set_status("Running encoder...", "running")
            self._simulator.run_encoder(p["panel"], p["reg"])
            self._set_status("Encoder finished", "ready")

        threading.Thread(target=_task, daemon=True).start()

    def _run_decoder(self):
        if not self._pre_run_checks():
            return
        p = self._get_params()

        def _task():
            self._set_status("Running decoder...", "running")
            self._simulator.run_decoder(p["panel"], p["reg"], p["mode"], p["last_arg"])
            self._set_status("Decoder finished", "ready")

        threading.Thread(target=_task, daemon=True).start()

    def _run_both(self):
        if not self._pre_run_checks():
            return
        p = self._get_params()

        def _task():
            self._set_status("Running encoder...", "running")
            self._simulator.run_encoder(p["panel"], p["reg"])
            self._set_status("Running decoder...", "running")
            self._simulator.run_decoder(p["panel"], p["reg"], p["mode"], p["last_arg"])
            self._set_status("Pipeline finished", "ready")

        threading.Thread(target=_task, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  Log helpers
    # ------------------------------------------------------------------ #
    def _append_log(self, text: str):
        def _update():
            self._log_widget.configure(state="normal")
            self._log_widget.insert("end", text)
            self._log_widget.see("end")
            self._log_widget.configure(state="disabled")

        self._root.after(0, _update)

    def append_log(self, text: str):
        """Public method for external callers (e.g., EditorTab)."""
        self._append_log(text)

    def _clear_log(self):
        self._log_widget.configure(state="normal")
        self._log_widget.delete("1.0", "end")
        self._log_widget.configure(state="disabled")
