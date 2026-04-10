"""
Image Card Widget for ScreenZen.
Displays a single screenshot thumbnail with metadata.
"""

import os
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Callable, Optional, Dict


class ImageCard(ctk.CTkFrame):
    """
    A card widget displaying a screenshot thumbnail with filename,
    OCR status indicator, and selection checkbox.
    """

    CARD_SIZE = 140
    THUMB_SIZE = 110

    def __init__(self, parent, screenshot_data: Dict,
                 on_click: Callable[[Dict], None] = None,
                 on_select: Callable[[int, bool], None] = None,
                 **kwargs):
        super().__init__(
            parent,
            fg_color="#1e1e2e",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
            height=self.CARD_SIZE + 50,
            **kwargs
        )

        self.screenshot_data = screenshot_data
        self.on_click = on_click
        self.on_select = on_select
        self.is_selected = False
        self._photo_image = None  # Keep reference to prevent GC

        self.pack_propagate(False)

        # Selection checkbox
        self.select_var = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.select_var,
            width=24,
            height=24,
            corner_radius=6,
            fg_color="#89b4fa",
            hover_color="#74c7ec",
            border_color="#585b70",
            command=self._on_select_toggle,
        )
        self.checkbox.place(x=8, y=8)

        # Thumbnail image
        self.image_frame = ctk.CTkFrame(
            self,
            fg_color="#11111b",
            corner_radius=8,
            width=self.THUMB_SIZE,
            height=self.THUMB_SIZE - 20,
        )
        self.image_frame.pack(padx=12, pady=(36, 4))
        self.image_frame.pack_propagate(False)

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="📷",
            font=ctk.CTkFont(size=32),
        )
        self.image_label.pack(expand=True, fill="both")

        # Load thumbnail
        self._load_thumbnail()

        # Filename label
        filename = screenshot_data.get("filename", "Unknown")
        display_name = filename[:22] + "..." if len(filename) > 25 else filename

        self.name_label = ctk.CTkLabel(
            self,
            text=display_name,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#cdd6f4",
            anchor="w",
        )
        self.name_label.pack(padx=12, pady=(2, 2), anchor="w")

        # Tags preview
        tags = screenshot_data.get("tags_list", [])[:3]
        if tags:
            tag_text = " ".join(f"#{t}" for t in tags)
            if len(tag_text) > 28:
                tag_text = tag_text[:28] + "..."

            self.tags_label = ctk.CTkLabel(
                self,
                text=tag_text,
                font=ctk.CTkFont(size=10),
                text_color="#89b4fa",
                anchor="w",
            )
            self.tags_label.pack(padx=12, pady=(0, 6), anchor="w")

        # Bind click events
        for widget in [self, self.image_frame, self.image_label, self.name_label]:
            widget.bind("<Button-1>", self._on_card_click)

        # Hover effects
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)

    def _load_thumbnail(self):
        """Load and display the thumbnail image."""
        thumb_path = self.screenshot_data.get("thumbnail_path", "")

        if thumb_path and os.path.isfile(thumb_path):
            try:
                img = Image.open(thumb_path)
                img.thumbnail((self.THUMB_SIZE - 20, self.THUMB_SIZE - 40), Image.LANCZOS)
                self._photo_image = ImageTk.PhotoImage(img)
                self.image_label.configure(image=self._photo_image, text="")
            except Exception:
                pass  # Keep default emoji icon

    def _on_card_click(self, event=None):
        """Handle card click."""
        if self.on_click:
            self.on_click(self.screenshot_data)

    def _on_select_toggle(self):
        """Handle selection checkbox toggle."""
        self.is_selected = self.select_var.get()
        if self.on_select:
            self.on_select(self.screenshot_data.get("id"), self.is_selected)

        # Visual feedback
        border_color = "#89b4fa" if self.is_selected else "#313244"
        self.configure(border_color=border_color)

    def _on_hover_enter(self, event=None):
        """Hover enter effect."""
        if not self.is_selected:
            self.configure(border_color="#45475a")

    def _on_hover_leave(self, event=None):
        """Hover leave effect."""
        if not self.is_selected:
            self.configure(border_color="#313244")

    def set_selected(self, selected: bool):
        """Programmatically set selection state."""
        self.select_var.set(selected)
        self.is_selected = selected
        border_color = "#89b4fa" if selected else "#313244"
        self.configure(border_color=border_color)
