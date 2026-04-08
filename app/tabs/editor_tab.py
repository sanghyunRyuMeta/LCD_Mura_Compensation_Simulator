import customtkinter as ctk
from tkinter import messagebox

from app.theme import Colors, Fonts, Spacing
from app.widgets import SectionCard, AccentButton, StyledLabel


class EditorTab:
    def __init__(self, parent: ctk.CTkFrame, filepath: str, log_callback):
        self._filepath = filepath
        self._log = log_callback

        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # ── Toolbar ──
        toolbar = ctk.CTkFrame(
            parent,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CORNER_RADIUS_SM,
            border_width=Spacing.BORDER_WIDTH,
            border_color=Colors.BORDER,
            height=48,
        )
        toolbar.grid(row=0, column=0, sticky="ew", padx=Spacing.PAD_LG, pady=(Spacing.PAD_MD, Spacing.PAD_SM))
        toolbar.pack_propagate(False)

        # File icon + path
        path_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        path_frame.pack(side="left", fill="y", padx=Spacing.PAD_MD)

        ctk.CTkLabel(
            path_frame,
            text="📄",
            font=ctk.CTkFont(size=16),
            width=24,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        StyledLabel(path_frame, text="File:", style="small").pack(side="left")

        ctk.CTkLabel(
            path_frame,
            text=f"  {filepath}",
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.SMALL_SIZE),
            text_color=Colors.TEXT_ACCENT,
        ).pack(side="left")

        # Buttons
        AccentButton(
            toolbar, text="Save", style="primary", icon="💾", width=100,
            command=self._save,
        ).pack(side="right", padx=(Spacing.PAD_SM, Spacing.PAD_MD), pady=Spacing.PAD_SM)

        AccentButton(
            toolbar, text="Reload", style="secondary", icon="↻", width=100,
            command=self._load,
        ).pack(side="right", pady=Spacing.PAD_SM)

        # ── Editor ──
        editor_frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.CONSOLE_BG,
            corner_radius=Spacing.CORNER_RADIUS_SM,
            border_width=Spacing.BORDER_WIDTH,
            border_color=Colors.CONSOLE_BORDER,
        )
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=Spacing.PAD_LG, pady=(0, Spacing.PAD_LG))
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        self._editor = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.MONO_SIZE),
            fg_color=Colors.CONSOLE_BG,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=0,
            wrap="none",
            border_width=0,
        )
        self._editor.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self._load()

    def _load(self):
        try:
            with open(self._filepath, "r") as f:
                content = f.read()
            self._editor.configure(state="normal")
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", content)
            self._log(f"[INFO] Loaded {self._filepath}\n")
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"Cannot find:\n{self._filepath}")

    def _save(self):
        content = self._editor.get("1.0", "end")
        try:
            with open(self._filepath, "w") as f:
                f.write(content)
            self._log(f"[INFO] Saved {self._filepath}\n")
            messagebox.showinfo("Saved", f"File saved successfully:\n{self._filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
