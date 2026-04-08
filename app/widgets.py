"""
Reusable styled widgets — Meta Reality Labs Neo-Dark Theme v3
LCD Demura Simulator

Visual design:
  • Cards: warm elevated surface (#1A1A1F) with visible border (#2C2C34)
  • Buttons: 36px, 8px radius, accent glow border on primary
  • Inputs: 34px, recessed (#141418), focus-blue border
  • Typography: 15px bold section titles, 13px body, 11px hints
  • Header: 64px with generous inner spacing + accent underline
"""

import customtkinter as ctk
from PIL import Image
from app.theme import Colors, Fonts, Spacing, Heights
from app.config import LOGO_PNG


# ═══════════════════════════════════════════════════════════════════
#  SECTION CARD
# ═══════════════════════════════════════════════════════════════════
class SectionCard(ctk.CTkFrame):
    """Card with elevated surface, visible border, and accent-striped header."""

    def __init__(self, parent, title: str = "", icon: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_ELEVATED,
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=Spacing.BORDER_WIDTH,
            border_color=Colors.BORDER_CARD,
            **kwargs,
        )

        if title:
            header = ctk.CTkFrame(self, fg_color="transparent", height=36)
            header.pack(
                fill="x",
                padx=Spacing.CARD_PAD,
                pady=(Spacing.CARD_PAD, Spacing.CARD_PAD_HEADER),
            )
            header.pack_propagate(False)

            ctk.CTkFrame(
                header, width=4, height=20,
                fg_color=Colors.ACCENT_BLUE,
                corner_radius=2,
            ).pack(side="left", padx=(0, Spacing.PAD_SM + 2), pady=7)

            label_text = f"{icon}  {title}" if icon else title
            ctk.CTkLabel(
                header, text=label_text,
                font=ctk.CTkFont(
                    family=Fonts.FAMILY,
                    size=Fonts.SECTION_SIZE,
                    weight="bold",
                ),
                text_color=Colors.TEXT_PRIMARY,
            ).pack(side="left")

    def get_content_frame(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(
            fill="both", expand=True,
            padx=Spacing.CARD_PAD,
            pady=(0, Spacing.CARD_PAD),
        )
        return content


# ═══════════════════════════════════════════════════════════════════
#  ACCENT BUTTON
# ═══════════════════════════════════════════════════════════════════
class AccentButton(ctk.CTkButton):
    """Styled button with accent glow border on primary variant."""

    STYLES = {
        "primary": (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER),
        "secondary": (Colors.BTN_SECONDARY, Colors.BTN_SECONDARY_HOVER),
        "success": (Colors.BTN_SUCCESS, Colors.BTN_SUCCESS_HOVER),
        "danger": (Colors.BTN_DANGER, Colors.BTN_DANGER_HOVER),
    }

    _TEXT_COLORS = {
        "secondary": Colors.TEXT_SECONDARY,
    }

    _BORDER_COLORS = {
        "primary": Colors.ACCENT_BLUE_DIM,
        "secondary": Colors.BORDER,
        "success": Colors.SUCCESS_DIM,
        "danger": Colors.ERROR_DIM,
    }

    def __init__(self, parent, text: str, style: str = "primary", icon: str = "", **kwargs):
        fg, hover = self.STYLES.get(style, self.STYLES["primary"])
        text_color = self._TEXT_COLORS.get(style, Colors.TEXT_ON_ACCENT)
        border_color = self._BORDER_COLORS.get(style, Colors.BORDER)
        display_text = f"{icon}  {text}" if icon else text

        super().__init__(
            parent,
            text=display_text,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            border_color=border_color,
            border_width=1,
            font=ctk.CTkFont(
                family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold",
            ),
            corner_radius=Spacing.CORNER_RADIUS_SM,
            height=Heights.BUTTON,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════
#  STATUS BAR
# ═══════════════════════════════════════════════════════════════════
class StatusBar(ctk.CTkFrame):
    """Bottom status bar with color-coded status dot and divider."""

    _COLOR_MAP = {
        "ready": Colors.SUCCESS,
        "running": Colors.ACCENT_BLUE,
        "warning": Colors.WARNING,
        "error": Colors.ERROR,
    }

    def __init__(self, parent, version: str = ""):
        super().__init__(
            parent, fg_color=Colors.BG_DEEPEST,
            height=Heights.STATUS_BAR, corner_radius=0,
        )
        self.pack_propagate(False)

        ctk.CTkFrame(
            self, height=1, fg_color=Colors.BORDER_CARD, corner_radius=0,
        ).pack(fill="x", side="top")

        self._dot = ctk.CTkLabel(
            self, text="●", font=ctk.CTkFont(size=10),
            text_color=Colors.SUCCESS, width=18,
        )
        self._dot.pack(side="left", padx=(Spacing.PAD_MD, 0))

        self._status_label = ctk.CTkLabel(
            self, text="Ready",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
            text_color=Colors.TEXT_MUTED,
        )
        self._status_label.pack(side="left", padx=Spacing.PAD_XS)

        if version:
            ctk.CTkLabel(
                self, text=version,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
                text_color=Colors.TEXT_FAINT,
            ).pack(side="right", padx=Spacing.PAD_MD)

            ctk.CTkLabel(
                self, text="·",
                font=ctk.CTkFont(size=Fonts.SMALL_SIZE),
                text_color=Colors.TEXT_FAINT,
            ).pack(side="right")

            ctk.CTkLabel(
                self, text="Meta Reality Labs",
                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
                text_color=Colors.TEXT_FAINT,
            ).pack(side="right", padx=Spacing.PAD_MD)

    def set_status(self, text: str, status: str = "ready"):
        self._status_label.configure(text=text)
        self._dot.configure(
            text_color=self._COLOR_MAP.get(status, Colors.TEXT_MUTED),
        )


# ═══════════════════════════════════════════════════════════════════
#  HEADER BANNER
# ═══════════════════════════════════════════════════════════════════
class HeaderBanner(ctk.CTkFrame):
    """Branded header with Meta logo, title, subtitle, and accent underline."""

    def __init__(self, parent, title: str, subtitle: str):
        super().__init__(
            parent, fg_color=Colors.BG_DEEPEST,
            height=Heights.HEADER_BANNER, corner_radius=0,
        )
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.PAD_XL)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y", pady=Spacing.PAD_SM)

        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(LOGO_PNG),
                dark_image=Image.open(LOGO_PNG),
                size=(130, 44),
            )
            ctk.CTkLabel(
                left, image=logo_image, text="",
            ).pack(side="left", padx=(0, Spacing.PAD_LG))
            self._logo_image = logo_image
        except Exception:
            logo_frame = ctk.CTkFrame(
                left, width=40, height=40,
                fg_color=Colors.ACCENT_BLUE,
                corner_radius=Spacing.CORNER_RADIUS,
            )
            logo_frame.pack(side="left", padx=(0, Spacing.PAD_LG))
            logo_frame.pack_propagate(False)
            ctk.CTkLabel(
                logo_frame, text="◈",
                font=ctk.CTkFont(size=22),
                text_color=Colors.TEXT_ON_ACCENT,
            ).place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(left, fg_color="transparent")
        text_frame.pack(side="left", fill="y", anchor="center")

        ctk.CTkLabel(
            text_frame, text=title,
            font=ctk.CTkFont(
                family=Fonts.FAMILY,
                size=Fonts.SUBHEADER_SIZE,
                weight="bold",
            ),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame, text=subtitle,
            font=ctk.CTkFont(
                family=Fonts.FAMILY, size=Fonts.SMALL_SIZE,
            ),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(
            self, height=2, fg_color=Colors.ACCENT_BLUE, corner_radius=0,
        ).pack(side="bottom", fill="x")


# ═══════════════════════════════════════════════════════════════════
#  STYLED ENTRY
# ═══════════════════════════════════════════════════════════════════
class StyledEntry(ctk.CTkEntry):
    """Recessed input field with consistent styling."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_FAINT,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
            corner_radius=Spacing.CORNER_RADIUS_SM,
            border_width=Spacing.BORDER_WIDTH,
            height=Heights.INPUT,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════
#  STYLED LABEL
# ═══════════════════════════════════════════════════════════════════
class StyledLabel(ctk.CTkLabel):
    """Label with 4 visual hierarchy tiers."""

    _STYLES = {
        "body": (Fonts.BODY_SIZE, "normal", Colors.TEXT_SECONDARY),
        "title": (Fonts.SECTION_SIZE, "bold", Colors.TEXT_PRIMARY),
        "small": (Fonts.SMALL_SIZE, "normal", Colors.TEXT_MUTED),
        "accent": (Fonts.BODY_SIZE, "bold", Colors.TEXT_ACCENT),
    }

    def __init__(self, parent, text: str, style: str = "body", **kwargs):
        size, weight, color = self._STYLES.get(style, self._STYLES["body"])
        super().__init__(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=size, weight=weight),
            text_color=color,
            **kwargs,
        )
