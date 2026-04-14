"""
DLL Tab - Direct DLL usage for demura processing without the Simulator.
Outputs total_crc.bin and LUT.bin files.
"""

import os
import tkinter as tk
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.theme import Colors, Fonts, Spacing
from app.config import BASE_DIR, OUT_DIR, DLL_DIR, DLL_REG_FILE, DLL_PARA_FILE
from app.widgets import SectionCard, AccentButton, StyledEntry, StyledLabel
from app.dll_runner import DLLRunner
from app.file_utils import read_config, write_config_values


DMR_MODE_INFO = {
    "0": ("RGB Mode, 2 Planes (32, 64)", 2),
    "1": ("RGB Mode, 3 Planes (32, 64, 128)", 3),
    "2": ("White Mode, 3 Planes (32, 64, 128) - POR", 3),
}


class DLLTab:
    """Tab for direct DLL usage."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        root: ctk.CTk,
        status_bar=None,
    ):
        self._root = root
        self._status_bar = status_bar
        self._dll_runner = DLLRunner(log_callback=self._append_log)

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
        self._build_input_section(scroll, row); row += 1
        self._build_dmr_mode_section(scroll, row); row += 1
        self._build_output_section(scroll, row); row += 1
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

        # Fix sash position
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

        def _retry_sash():
            if not self._sash_fixed:
                _fix_sash()
                parent.after(500, _retry_sash)
        parent.after(500, _retry_sash)

        # Load initial config
        self._load_config_from_files()

    # ------------------------------------------------------------------ #
    #  Input Section
    # ------------------------------------------------------------------ #
    def _build_input_section(self, parent, row):
        card = SectionCard(parent, title="Input Images", icon="📁")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=(Spacing.PAD_MD, Spacing.PAD_SM))
        content = card.get_content_frame()
        content.grid_columnconfigure(0, weight=1)

        # Panel folder path
        StyledLabel(content, text="Camera Image Folder:", style="body").pack(anchor="w", pady=(0, Spacing.PAD_XS))
        StyledLabel(content, text="Folder containing camera images (e.g., J1_W32_DISP_RAW.png)", style="small").pack(anchor="w")

        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=(Spacing.PAD_XS, Spacing.PAD_SM))
        path_frame.grid_columnconfigure(0, weight=1)

        self.input_path_var = ctk.StringVar(value=os.path.join(BASE_DIR, "_in", "camera_image", "J1"))
        self._input_path_entry = StyledEntry(path_frame, textvariable=self.input_path_var)
        self._input_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.PAD_SM))

        AccentButton(
            path_frame, text="Browse", style="secondary", icon="📂", width=110,
            command=self._browse_input_folder,
        ).grid(row=0, column=1)

    def _browse_input_folder(self):
        camera_dir = os.path.join(BASE_DIR, "_in", "camera_image")
        folder = filedialog.askdirectory(
            title="Select Camera Image Folder",
            initialdir=camera_dir if os.path.isdir(camera_dir) else BASE_DIR,
        )
        if folder:
            self.input_path_var.set(folder)

    # ------------------------------------------------------------------ #
    #  DMR_MODE Section
    # ------------------------------------------------------------------ #
    def _build_dmr_mode_section(self, parent, row):
        card = SectionCard(parent, title="Demura Mode (DMR_MODE)", icon="⚙")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)
        content = card.get_content_frame()
        content.grid_columnconfigure(1, weight=1)

        # Radio buttons for DMR_MODE
        self.dmr_mode_var = ctk.StringVar(value="2")

        for mode_val, (desc, planes) in DMR_MODE_INFO.items():
            mode_frame = ctk.CTkFrame(content, fg_color=Colors.BG_SURFACE, corner_radius=Spacing.CORNER_RADIUS_SM,
                                       border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER)
            mode_frame.pack(fill="x", pady=(0, Spacing.PAD_SM))

            ctk.CTkRadioButton(
                mode_frame, text=f"Mode {mode_val}  —  {desc}",
                variable=self.dmr_mode_var, value=mode_val,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                text_color=Colors.TEXT_PRIMARY, fg_color="#000000",
                hover_color="#333333", border_color=Colors.BORDER,
            ).pack(anchor="w", padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)

            # Image requirements hint
            if mode_val == "0":
                hint = "Requires: {Panel}_RED32, RED64, GRN32, GRN64, BLU32, BLU64 images"
            elif mode_val == "1":
                hint = "Requires: {Panel}_RED32, RED64, RED128, GRN32, GRN64, GRN128, BLU32, BLU64, BLU128 images"
            else:
                hint = "Requires: {Panel}_W32, W64, W128 images (Recommended for production)"

            StyledLabel(mode_frame, text=hint, style="small").pack(anchor="w", padx=(40, Spacing.PAD_MD), pady=(0, Spacing.PAD_SM))

    # ------------------------------------------------------------------ #
    #  Output Section
    # ------------------------------------------------------------------ #
    def _build_output_section(self, parent, row):
        card = SectionCard(parent, title="Output", icon="💾")
        card.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)
        content = card.get_content_frame()
        content.grid_columnconfigure(0, weight=1)

        StyledLabel(content, text="Output Bin File Name:", style="body").pack(anchor="w", pady=(0, Spacing.PAD_XS))
        StyledLabel(content, text="Name for output files (creates {name}.bin and {name}_Total_crc.bin in _out folder)", style="small").pack(anchor="w")

        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=(Spacing.PAD_XS, Spacing.PAD_SM))
        path_frame.grid_columnconfigure(0, weight=1)

        self.output_name_var = ctk.StringVar(value="DLL_output")
        self._output_name_entry = StyledEntry(path_frame, textvariable=self.output_name_var)
        self._output_name_entry.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.PAD_SM))

        # Auto-generate name from input folder
        AccentButton(
            path_frame, text="Auto Name", style="secondary", icon="✨", width=110,
            command=self._auto_generate_name,
        ).grid(row=0, column=1)

    def _auto_generate_name(self):
        """Auto-generate output name from input folder name and mode."""
        input_path = self.input_path_var.get().strip()
        if input_path and os.path.isdir(input_path):
            panel_name = os.path.basename(input_path)
            mode = self.dmr_mode_var.get()
            mode_suffix = {
                "0": "_RGB2P",
                "1": "_RGB3P",
                "2": "_W3P"
            }.get(mode, "")
            self.output_name_var.set(f"{panel_name}{mode_suffix}")

    # ------------------------------------------------------------------ #
    #  Action Buttons
    # ------------------------------------------------------------------ #
    def _build_action_buttons(self, parent, row):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=Spacing.PAD_SM)

        AccentButton(
            btn_frame, text="Run DLL Demura", style="success", icon="▶",
            width=200, command=self._run_dll,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_frame, text="Open DLL Folder", style="secondary", icon="📂",
            width=160, command=self._open_dll_folder,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

    def _open_dll_folder(self):
        if os.path.isdir(DLL_DIR):
            os.startfile(DLL_DIR)
        else:
            messagebox.showwarning("Folder Not Found", f"DLL folder does not exist:\n{DLL_DIR}")

    # ------------------------------------------------------------------ #
    #  Console Toolbar
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
                     ).pack(side="right")

    def _open_out_folder(self):
        if os.path.isdir(OUT_DIR):
            os.startfile(OUT_DIR)
        else:
            messagebox.showwarning("Folder Not Found", f"Output folder does not exist:\n{OUT_DIR}")

    # ------------------------------------------------------------------ #
    #  Config Loading
    # ------------------------------------------------------------------ #
    def _load_config_from_files(self):
        """Load initial DMR_MODE from lxs_reg.ini"""
        reg = read_config(DLL_REG_FILE)
        if "DMR_MODE" in reg:
            self.dmr_mode_var.set(reg["DMR_MODE"])

    # ------------------------------------------------------------------ #
    #  Run DLL
    # ------------------------------------------------------------------ #
    def _validate_inputs(self) -> bool:
        """Validate inputs before running."""
        input_path = self.input_path_var.get().strip()
        output_name = self.output_name_var.get().strip()

        if not input_path:
            messagebox.showerror("Missing Input", "Please specify the camera image folder.")
            return False

        if not os.path.isdir(input_path):
            messagebox.showerror("Invalid Input", f"Camera image folder not found:\n{input_path}")
            return False

        if not output_name:
            messagebox.showerror("Missing Output", "Please specify the output bin file name.")
            return False

        return True

    def _run_dll(self):
        """Run the DLL demura process."""
        if not self._validate_inputs():
            return

        input_path = self.input_path_var.get().strip()
        output_name = self.output_name_var.get().strip()
        output_path = os.path.join(OUT_DIR, output_name)
        dmr_mode = int(self.dmr_mode_var.get())

        def _task():
            self._set_status("Running DLL Demura...", "running")
            try:
                total_crc = self._dll_runner.run_demura(input_path, output_path, dmr_mode)
                self._set_status(f"DLL finished - CRC: {total_crc}", "ready")
                self._root.after(0, lambda: messagebox.showinfo(
                    "DLL Complete",
                    f"Demura processing complete!\n\nTotal CRC: {total_crc}\nOutput: {output_path}.bin"
                ))
            except Exception as e:
                self._set_status("DLL error", "error")
                self._append_log(f"[ERROR] {e}\n")
                self._root.after(0, lambda: messagebox.showerror("DLL Error", str(e)))

        threading.Thread(target=_task, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  Status & Log Helpers
    # ------------------------------------------------------------------ #
    def _set_status(self, text: str, status: str = "ready"):
        if self._status_bar:
            self._root.after(0, lambda: self._status_bar.set_status(text, status))

    def _append_log(self, text: str):
        def _update():
            self._log_widget.configure(state="normal")
            self._log_widget.insert("end", text)
            self._log_widget.see("end")
            self._log_widget.configure(state="disabled")

        self._root.after(0, _update)

    def append_log(self, text: str):
        """Public method for external callers."""
        self._append_log(text)

    def _clear_log(self):
        self._log_widget.configure(state="normal")
        self._log_widget.delete("1.0", "end")
        self._log_widget.configure(state="disabled")
