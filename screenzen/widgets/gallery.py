"""
Gallery Widget for ScreenZen.
Displays screenshot cards in a responsive grid layout.
"""

import customtkinter as ctk
from typing import Callable, Dict, List, Optional, Set
from screenzen.widgets.image_card import ImageCard


class Gallery(ctk.CTkScrollableFrame):
    """
    Scrollable gallery grid displaying screenshot cards.
    Supports selection, click-to-preview, and dynamic layout.
    """

    def __init__(self, parent,
                 on_card_click: Callable[[Dict], None] = None,
                 on_selection_change: Callable[[Set[int]], None] = None,
                 **kwargs):
        super().__init__(
            parent,
            fg_color="#181825",
            corner_radius=0,
            **kwargs
        )

        self.on_card_click = on_card_click
        self.on_selection_change = on_selection_change
        self.cards: List[ImageCard] = []
        self.selected_ids: Set[int] = set()
        self._current_screenshots: List[Dict] = []

        # Empty state label
        self.empty_label = ctk.CTkLabel(
            self,
            text="📂  No screenshots yet\n\nClick 'Add Screenshots' to get started",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#585b70",
        )

        # Bind resize for responsive layout
        self.bind("<Configure>", self._on_resize)
        self._last_width = 0

    def display_screenshots(self, screenshots: List[Dict]):
        """Display a list of screenshots in the gallery grid."""
        self._current_screenshots = screenshots

        # Clear existing cards
        self._clear_cards()

        if not screenshots:
            self.empty_label.pack(expand=True, pady=100)
            return

        self.empty_label.pack_forget()

        # Create grid frame
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Force exactly 6 columns and make them fill the full width
        cols = 6
        for i in range(cols):
            self.grid_frame.columnconfigure(i, weight=1)

        # Create cards in grid
        for idx, ss in enumerate(screenshots):
            row = idx // cols
            col = idx % cols

            card = ImageCard(
                self.grid_frame,
                screenshot_data=ss,
                on_click=self.on_card_click,
                on_select=self._on_card_select,
            )
            # Use sticky="nsew" to fill the column width
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self.cards.append(card)

    def _clear_cards(self):
        """Remove all cards from the gallery."""
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        self.selected_ids.clear()

        # Remove grid frame if it exists
        for widget in self.winfo_children():
            if widget != self.empty_label:
                widget.destroy()

    def _on_card_select(self, screenshot_id: int, is_selected: bool):
        """Handle card selection change."""
        if is_selected:
            self.selected_ids.add(screenshot_id)
        else:
            self.selected_ids.discard(screenshot_id)

        if self.on_selection_change:
            self.on_selection_change(self.selected_ids)

    def _on_resize(self, event):
        """Re-layout cards when gallery is resized."""
        new_width = event.width
        if abs(new_width - self._last_width) > 50 and self._current_screenshots:
            self._last_width = new_width
            # Debounce relayout
            if hasattr(self, "_relayout_id"):
                self.after_cancel(self._relayout_id)
            self._relayout_id = self.after(200, lambda: self.display_screenshots(self._current_screenshots))

    def select_all(self):
        """Select all cards."""
        for card in self.cards:
            card.set_selected(True)
            ss_id = card.screenshot_data.get("id")
            if ss_id:
                self.selected_ids.add(ss_id)

        if self.on_selection_change:
            self.on_selection_change(self.selected_ids)

    def deselect_all(self):
        """Deselect all cards."""
        for card in self.cards:
            card.set_selected(False)
        self.selected_ids.clear()

        if self.on_selection_change:
            self.on_selection_change(self.selected_ids)

    def get_selected_count(self) -> int:
        """Get number of selected cards."""
        return len(self.selected_ids)
