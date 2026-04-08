"""
GUI tab for n x k image downsampling.
Lets the user pick a folder, set n and k, and run the resize.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.theme import Colors, Fonts, Spacing
from app.config import BASE_DIR
from app.widgets import SectionCard, AccentButton, StyledEntry, StyledLabel
from app.resize_nxk import resize_folder


class ResizeTab:
    def __init__(
        self,
        parent: ctk.CTkFrame,
        root: ctk.CTk,
        status_bar=None,
    ):
        self._root = root
        self._status_bar = status_bar

        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # ── Settings card ──
        card = SectionCard(parent, title="n x k Downsampling", icon="🔎")
        card.grid(
            row=0, column=0, sticky="ew",
            padx=Spacing.PAD_LG, pady=(Spacing.PAD_MD, Spacing.PAD_SM),
        )
        content = card.get_content_frame()
        content.grid_columnconfigure(1, weight=1)

        # -- Folder path --
        StyledLabel(content, text="Image Folder:", style="body").grid(
            row=0, column=0, sticky="w",
            padx=(0, Spacing.PAD_MD), pady=(Spacing.PAD_SM, 0),
        )
        StyledLabel(
            content,
            text="All images in this folder (recursive) will be downsampled",
            style="small",
        ).grid(row=0, column=1, sticky="e", pady=(Spacing.PAD_SM, 0))

        folder_row = ctk.CTkFrame(content, fg_color="transparent")
        folder_row.grid(
            row=1, column=0, columnspan=2, sticky="ew",
            pady=(2, Spacing.PAD_SM),
        )
        folder_row.grid_columnconfigure(0, weight=1)

        default_camera_dir = os.path.join(BASE_DIR, "_in", "camera_image")
        self._folder_var = ctk.StringVar(value=default_camera_dir)
        self._folder_entry = StyledEntry(folder_row, textvariable=self._folder_var)
        self._folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.PAD_SM))

        AccentButton(
            folder_row, text="Browse", style="secondary", icon="📁", width=110,
            command=self._browse_folder,
        ).grid(row=0, column=1)

        # -- n and k inputs --
        nk_frame = ctk.CTkFrame(
            content, fg_color=Colors.BG_SURFACE,
            corner_radius=Spacing.CORNER_RADIUS_SM,
            border_width=Spacing.BORDER_WIDTH, border_color=Colors.BORDER,
        )
        nk_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew",
            pady=(0, Spacing.PAD_SM),
        )
        nk_frame.grid_columnconfigure(1, weight=1)
        nk_frame.grid_columnconfigure(3, weight=1)

        StyledLabel(nk_frame, text="n (rows):", style="body").grid(
            row=0, column=0, sticky="w",
            padx=Spacing.PAD_MD, pady=Spacing.PAD_SM,
        )
        self._n_var = ctk.StringVar(value="2")
        StyledEntry(nk_frame, textvariable=self._n_var, width=80).grid(
            row=0, column=1, sticky="w",
            padx=(0, Spacing.PAD_LG), pady=Spacing.PAD_SM,
        )

        StyledLabel(nk_frame, text="k (cols):", style="body").grid(
            row=0, column=2, sticky="w",
            padx=(Spacing.PAD_MD, Spacing.PAD_SM), pady=Spacing.PAD_SM,
        )
        self._k_var = ctk.StringVar(value="2")
        StyledEntry(nk_frame, textvariable=self._k_var, width=80).grid(
            row=0, column=3, sticky="w",
            padx=(0, Spacing.PAD_MD), pady=Spacing.PAD_SM,
        )

        StyledLabel(
            content,
            text="n x k box averaging (each block averaged into one pixel). "
                 "Output saved to <folder>/<n>x<k>_resized/",
            style="small",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, Spacing.PAD_SM))

        # -- Run button --
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, Spacing.PAD_SM))

        AccentButton(
            btn_frame, text="Run Resize", style="success", icon="▶",
            width=180, command=self._run_resize,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_frame, text="Open Output Folder", style="secondary", icon="📂",
            width=190, command=self._open_output,
        ).pack(side="left")

        # ── Console log ──
        console_header = ctk.CTkFrame(parent, fg_color="transparent")
        console_header.grid(
            row=1, column=0, sticky="new",
            padx=Spacing.PAD_LG, pady=(Spacing.PAD_SM, 0),
        )

        left = ctk.CTkFrame(console_header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(
            left, text="●", font=ctk.CTkFont(size=8),
            text_color=Colors.ACCENT_CYAN, width=14,
        ).pack(side="left", padx=(0, Spacing.PAD_XS))
        StyledLabel(left, text="Resize Log", style="title").pack(side="left")

        AccentButton(
            console_header, text="Clear", style="secondary", icon="🗑",
            width=90, command=self._clear_log,
        ).pack(side="right")

        self._log_widget = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.MONO_SIZE),
            fg_color=Colors.CONSOLE_BG,
            text_color=Colors.TEXT_SECONDARY,
            border_color=Colors.CONSOLE_BORDER,
            border_width=Spacing.BORDER_WIDTH,
            corner_radius=Spacing.CORNER_RADIUS_SM,
            state="disabled",
        )
        self._log_widget.grid(
            row=2, column=0, sticky="nsew",
            padx=Spacing.PAD_LG, pady=(Spacing.PAD_SM, Spacing.PAD_LG),
        )
        parent.grid_rowconfigure(2, weight=1)

        self._last_output_dir = ""

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _browse_folder(self):
        init_dir = self._folder_var.get() or BASE_DIR
        folder = filedialog.askdirectory(
            title="Select Image Folder",
            initialdir=init_dir if os.path.isdir(init_dir) else BASE_DIR,
        )
        if folder:
            self._folder_var.set(folder)

    def _append_log(self, text: str):
        def _update():
            self._log_widget.configure(state="normal")
            self._log_widget.insert("end", text)
            self._log_widget.see("end")
            self._log_widget.configure(state="disabled")
        self._root.after(0, _update)

    def _clear_log(self):
        self._log_widget.configure(state="normal")
        self._log_widget.delete("1.0", "end")
        self._log_widget.configure(state="disabled")

    def _set_status(self, text: str, status: str = "ready"):
        if self._status_bar:
            self._root.after(0, lambda: self._status_bar.set_status(text, status))

    def _open_output(self):
        if self._last_output_dir and os.path.isdir(self._last_output_dir):
            os.startfile(self._last_output_dir)
        else:
            messagebox.showinfo(
                "No Output Yet",
                "Run resize first, or the output folder does not exist.",
            )

    # ------------------------------------------------------------------ #
    #  Run
    # ------------------------------------------------------------------ #
    def _run_resize(self):
        folder = self._folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Invalid Folder", f"Folder not found:\n{folder}")
            return

        try:
            n = int(self._n_var.get().strip())
            k = int(self._k_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "n and k must be integers.")
            return

        if n < 1 or k < 1:
            messagebox.showerror("Invalid Input", "n and k must be >= 1.")
            return

        def _task():
            self._set_status(f"Resizing {n}x{k} ...", "running")
            out = resize_folder(folder, n, k, log_callback=self._append_log)
            self._last_output_dir = out
            self._set_status("Resize complete", "ready")

        threading.Thread(target=_task, daemon=True).start()
