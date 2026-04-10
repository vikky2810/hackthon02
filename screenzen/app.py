"""
ScreenZen — Main Application Window.
Assembles all widgets and backend services into the desktop GUI.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Optional

from screenzen.database import DatabaseManager
from screenzen.ocr_engine import OCREngine
from screenzen.search_engine import SearchEngine
from screenzen.image_manager import ImageManager
from screenzen.widgets.sidebar import Sidebar
from screenzen.widgets.search_bar import SearchBar
from screenzen.widgets.gallery import Gallery
from screenzen.widgets.drop_zone import DropZone
from screenzen.widgets.confirm_dialog import ConfirmationDialog
from screenzen.background_monitor import ScreenshotWatcher


class ScreenZenApp(ctk.CTk):
    """Main ScreenZen application window."""

    APP_TITLE = "ScreenZen — Screenshot Super-Organizer"
    DEFAULT_WIDTH = 1300
    DEFAULT_HEIGHT = 800

    def __init__(self):
        super().__init__()

        # ── Window setup ──
        self.title(self.APP_TITLE)
        self.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}")
        self.minsize(1200, 600)

        # Dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#181825")

        # ── Icon ──
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"[ScreenZen] Could not set icon: {e}")

        # ── Backend services ──
        self.db = DatabaseManager()
        self.ocr = OCREngine()
        self.search = SearchEngine(self.db)
        self.img_mgr = ImageManager()

        # Threading protection
        self._sidebar_lock = threading.Lock()

        # ── Build UI ──
        self._build_layout()
        self._refresh_ui()

        # Show OCR status in sidebar
        self.sidebar.set_ocr_status(self.ocr.get_status())

        # ── Background Watcher ──
        self.watcher = ScreenshotWatcher(self._on_screenshot_detected)
        self.watcher.start()

        # Handle window close (minimize to tray instead)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ────────────────────────────────────────────
    #  Layout
    # ────────────────────────────────────────────

    def _build_layout(self):
        """Construct the main window layout."""

        # ── Sidebar (left) ──
        self.sidebar = Sidebar(
            self,
            on_tag_click=self._filter_by_tag,
            on_date_click=self._filter_by_date,
            on_show_all=self._show_all,
        )
        self.sidebar.pack(side="left", fill="y")

        # ── Main content area (right) ──
        self.content = ctk.CTkFrame(self, fg_color="#181825", corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        # ── Top bar: search + action buttons ──
        top_bar = ctk.CTkFrame(self.content, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(12, 4))

        self.search_bar = SearchBar(top_bar, on_search=self._on_search)
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Action buttons
        btn_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame.pack(side="right")

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="＋  Add Screenshots",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#a6e3a1",
            hover_color="#94e2d5",
            text_color="#1e1e2e",
            corner_radius=10,
            height=38,
            width=160,
            command=self._browse_files,
        )
        self.add_btn.pack(side="left", padx=4)

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️  Delete",
            font=ctk.CTkFont(size=13),
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="#1e1e2e",
            corner_radius=10,
            height=38,
            width=100,
            command=self._delete_selected,
        )
        self.delete_btn.pack(side="left", padx=4)

        self.export_btn = ctk.CTkButton(
            btn_frame,
            text="📦  Export",
            font=ctk.CTkFont(size=13),
            fg_color="#89b4fa",
            hover_color="#74c7ec",
            text_color="#1e1e2e",
            corner_radius=10,
            height=38,
            width=100,
            command=self._export_selected,
        )
        self.export_btn.pack(side="left", padx=4)

        # ── Drop zone ──
        self.drop_zone = DropZone(self.content, on_click=self._browse_files)
        self.drop_zone.pack(fill="x", padx=16, pady=8)

        # ── Gallery ──
        self.gallery = Gallery(
            self.content,
            on_card_click=self._on_card_click,
            on_selection_change=self._on_selection_change,
        )
        self.gallery.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # ── Status bar ──
        self.status_bar = ctk.CTkLabel(
            self.content,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#6c7086",
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=20, pady=(0, 8))

    # ────────────────────────────────────────────
    #  Refresh / Data Loading
    # ────────────────────────────────────────────

    def _refresh_ui(self):
        """Reload all data and update every widget."""
        screenshots = self.db.get_all_screenshots()
        self.gallery.display_screenshots(screenshots)

        if not self._sidebar_lock.acquire(blocking=False):
            return # Skip if already updating

        try:
            # Sidebar data
            stats = self.db.get_stats()
            self.sidebar.update_stats(stats)
            self.sidebar.update_tags(self.search.get_tag_cloud())
            self.sidebar.update_dates(self.search.get_available_dates())
        except Exception as e:
            print(f"[ScreenZen] App refresh error: {e}")
        finally:
            self._sidebar_lock.release()

        self._set_status(f"{stats['total_screenshots']} screenshot(s) loaded")

    # ────────────────────────────────────────────
    #  File Import
    # ────────────────────────────────────────────

    def _browse_files(self):
        """Open a file dialog to select images."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif"),
            ("All files", "*.*"),
        ]
        paths = filedialog.askopenfilenames(
            title="Select screenshots to import",
            filetypes=filetypes,
        )
        if paths:
            self._import_files(list(paths))

    def _import_files(self, file_paths: List[str]):
        """Import a list of image files (runs OCR in background)."""
        self.drop_zone.set_processing(f"Importing {len(file_paths)} file(s)...")
        self.add_btn.configure(state="disabled")
        self._set_status("Importing...")

        def _worker():
            imported = 0
            for path in file_paths:
                try:
                    result = self.img_mgr.import_image(path)
                    if result is None:
                        continue

                    # Add to database
                    row_id = self.db.add_screenshot(
                        filename=result["filename"],
                        original_path=path,
                        stored_path=result["stored_path"],
                        thumbnail_path=result["thumbnail_path"],
                        file_size=result["file_size"],
                        width=result["width"],
                        height=result["height"],
                    )

                    # Run OCR
                    ocr_text = self.ocr.extract_text(result["stored_path"])
                    tags = OCREngine.extract_tags(ocr_text)
                    self.db.update_ocr_result(row_id, ocr_text, tags)

                    imported += 1
                except Exception as e:
                    print(f"[ScreenZen] Import error for {path}: {e}")

            # Update UI on main thread
            self.after(0, lambda: self._on_import_complete(imported, len(file_paths)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_import_complete(self, imported: int, total: int):
        """Called on the main thread after import finishes."""
        self.drop_zone.set_ready()
        self.add_btn.configure(state="normal")
        self._set_status(f"Imported {imported}/{total} file(s)")
        self._refresh_ui()

    # ────────────────────────────────────────────
    #  Search / Filter
    # ────────────────────────────────────────────

    def _on_search(self, query: str):
        """Handle search input."""
        if query:
            results = self.search.search(query)
            self.gallery.display_screenshots(results)
            self.search_bar.set_result_count(len(results), query)
            self._set_status(f"Search: {len(results)} result(s) for \"{query}\"")
        else:
            self._show_all()

    def _filter_by_tag(self, tag: str):
        """Show screenshots matching a tag."""
        results = self.search.filter_by_tag(tag)
        self.gallery.display_screenshots(results)
        self.search_bar.set_result_count(len(results), f"tag:{tag}")
        self._set_status(f"Tag filter: #{tag} — {len(results)} result(s)")

    def _filter_by_date(self, date_str: str):
        """Show screenshots from a specific date."""
        results = self.search.filter_by_date(date_str)
        self.gallery.display_screenshots(results)
        self.search_bar.set_result_count(len(results), f"date:{date_str}")
        self._set_status(f"Date filter: {date_str} — {len(results)} result(s)")

    def _show_all(self):
        """Reset filters and show all screenshots."""
        self.search_bar.clear_search()
        self._refresh_ui()

    # ────────────────────────────────────────────
    #  Card Actions
    # ────────────────────────────────────────────

    def _on_card_click(self, screenshot_data: dict):
        """Handle click on a gallery card — show a detail preview."""
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(screenshot_data.get("filename", "Preview"))
        detail_win.geometry("700x500")
        detail_win.configure(fg_color="#1e1e2e")
        detail_win.transient(self)
        detail_win.grab_set()

        # Preview image
        from PIL import Image, ImageTk
        preview_img = self.img_mgr.get_preview_image(screenshot_data.get("stored_path", ""))
        if preview_img:
            photo = ImageTk.PhotoImage(preview_img)
            img_label = ctk.CTkLabel(detail_win, image=photo, text="")
            img_label.image = photo  # prevent GC
            img_label.pack(padx=16, pady=(16, 8))

        # Info
        info_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        info_frame.pack(fill="x", padx=16)

        ctk.CTkLabel(
            info_frame,
            text=screenshot_data.get("filename", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cdd6f4",
        ).pack(anchor="w")

        tags = screenshot_data.get("tags_list", [])
        if tags:
            ctk.CTkLabel(
                info_frame,
                text=" ".join(f"#{t}" for t in tags),
                font=ctk.CTkFont(size=12),
                text_color="#89b4fa",
            ).pack(anchor="w", pady=(4, 0))

        ocr_text = screenshot_data.get("ocr_text", "")
        if ocr_text and not ocr_text.startswith("[OCR"):
            ocr_box = ctk.CTkTextbox(
                detail_win,
                font=ctk.CTkFont(size=12),
                fg_color="#11111b",
                height=120,
                corner_radius=8,
            )
            ocr_box.insert("1.0", ocr_text)
            ocr_box.configure(state="disabled")
            ocr_box.pack(fill="x", padx=16, pady=(8, 16))

    def _on_selection_change(self, selected_ids):
        """Update status when selection changes."""
        count = len(selected_ids)
        if count:
            self._set_status(f"{count} screenshot(s) selected")
        else:
            total = self.db.get_stats()["total_screenshots"]
            self._set_status(f"{total} screenshot(s) loaded")

    # ────────────────────────────────────────────
    #  Delete / Export
    # ────────────────────────────────────────────

    def _delete_selected(self):
        """Delete all selected screenshots."""
        ids = self.gallery.selected_ids
        if not ids:
            messagebox.showinfo("Delete", "No screenshots selected.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {len(ids)} screenshot(s)? This cannot be undone.",
        )
        if not confirm:
            return

        for sid in list(ids):
            record = self.db.delete_screenshot(sid)
            if record:
                self.img_mgr.delete_image_files(
                    record.get("stored_path", ""),
                    record.get("thumbnail_path", ""),
                )

        self._refresh_ui()
        self._set_status(f"Deleted {len(ids)} screenshot(s)")

    def _export_selected(self):
        """Export selected screenshots as a ZIP."""
        ids = self.gallery.selected_ids
        if not ids:
            messagebox.showinfo("Export", "No screenshots selected.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Export as ZIP",
            defaultextension=".zip",
            filetypes=[("ZIP archive", "*.zip")],
            initialfile="screenzen_export.zip",
        )
        if not output_path:
            return

        screenshots = [self.db.get_screenshot(sid) for sid in ids if self.db.get_screenshot(sid)]
        try:
            self.img_mgr.export_zip(screenshots, output_path)
            self._set_status(f"Exported {len(screenshots)} screenshot(s) to {os.path.basename(output_path)}")
            messagebox.showinfo("Export", f"Exported {len(screenshots)} file(s) successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ────────────────────────────────────────────
    #  Helpers
    # ────────────────────────────────────────────

    def _set_status(self, text: str):
        """Update the status bar text."""
        self.status_bar.configure(text=text)

    # ────────────────────────────────────────────
    #  Background / Watcher Logic
    # ────────────────────────────────────────────

    def _on_screenshot_detected(self, file_path: str):
        """Callback from watcher thread when a new screenshot is found."""
        print(f"[ScreenZen] === New Screenshot Event ===: {file_path}")
        # Run OCR in background thread, then show dialog
        threading.Thread(target=self._process_detected_screenshot, args=(file_path,), daemon=True).start()

    def _process_detected_screenshot(self, file_path: str):
        """Process detected file: Run OCR and then trigger confirmation UI."""
        print(f"[ScreenZen] Starting OCR processing for: {file_path}")
        try:
            # Short sleep to ensure system has finished writing the file
            import time
            time.sleep(1.0)

            if not os.path.exists(file_path):
                print(f"[ScreenZen] ERROR: File disappeared before processing: {file_path}")
                return

            ocr_text = self.ocr.extract_text(file_path)
            print(f"[ScreenZen] OCR Extraction complete ({len(ocr_text)} chars)")
            tags = OCREngine.extract_tags(ocr_text)
            print(f"[ScreenZen] Generated tags: {tags}")

            # Show dialog on main thread
            print(f"[ScreenZen] Scheduling dialog popup on main thread...")
            self.after(0, lambda: self._show_confirmation(file_path, ocr_text, tags))
        except Exception as e:
            print(f"[ScreenZen] ERROR in _process_detected_screenshot: {e}")

    def _show_confirmation(self, file_path: str, ocr_text: str, tags: List[str]):
        """Show the confirmation popup."""
        print(f"[ScreenZen] Showing popup for: {file_path}")
        # Make sure main window is ready
        self.deiconify()
        self.lift()
        
        try:
            def on_confirm(new_name: str, target_folder: str):
                print(f"[ScreenZen] User confirmed save: {new_name} to {target_folder}")
                self._import_detected_file(file_path, new_name, target_folder, ocr_text, tags)

            def on_cancel():
                print(f"[ScreenZen] User discarded detection.")
                self._set_status("Detection discarded.")
                # Optionally delete the temp screenshot? 
                # Let's keep it in Pictures/Screenshots for now.

            diag = ConfirmationDialog(self, file_path, ocr_text, tags, on_confirm, on_cancel)
            diag.focus_force()
            print(f"[ScreenZen] Dialog initialized: {diag}")
        except Exception as e:
            print(f"[ScreenZen] ERROR showing ConfirmationDialog: {e}")

    def _import_detected_file(self, source_path: str, new_name: str, target_folder: str, ocr_text: str, tags: List[str]):
        """Import the detected file after user confirmation."""
        import shutil
        self._set_status(f"Moving to {target_folder}...")

        def _worker():
            try:
                # 1. Ensure target folder exists
                os.makedirs(target_folder, exist_ok=True)

                # 2. Prepare final name
                ext = os.path.splitext(source_path)[1]
                if not new_name.lower().endswith(ext.lower()):
                    filename = new_name + ext
                else:
                    filename = new_name
                
                target_path = os.path.join(target_folder, filename)

                # 3. Handle name collisions
                counter = 1
                while os.path.exists(target_path):
                    name_part, ext_part = os.path.splitext(filename)
                    target_path = os.path.join(target_folder, f"{name_part}_{counter}{ext_part}")
                    counter += 1

                # 4. Move the file from Screenshots to the new location
                print(f"[ScreenZen] Moving {source_path} -> {target_path}")
                shutil.move(source_path, target_path)

                # 5. Let the ImageManager "import" it from its new location (for thumbnails)
                result = self.img_mgr.import_image(target_path)
                
                if result:
                    # 6. Save to Database
                    row_id = self.db.add_screenshot(
                        filename=os.path.basename(target_path),
                        original_path=target_path,
                        stored_path=result["stored_path"], # internal copy
                        thumbnail_path=result["thumbnail_path"],
                        file_size=result["file_size"],
                        width=result["width"],
                        height=result["height"],
                    )
                    self.db.update_ocr_result(row_id, ocr_text, tags)

                    print(f"[ScreenZen] Successfully saved to DB: {row_id}")
                    self.after(0, self._refresh_ui)
                    self.after(0, lambda: self._set_status(f"✅ Organized: {os.path.basename(target_path)}"))
                else:
                    print(f"[ScreenZen] ERROR: ImageManager failed to generate thumbnail for {target_path}")

            except Exception as e:
                print(f"[ScreenZen] Background import error: {e}")
                self.after(0, lambda: messagebox.showerror("Save Error", str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_close(self):
        """Handle window close event."""
        res = messagebox.askyesno("Exit ScreenZen?",
                                  "Do you want to exit ScreenZen completely?\n\n"
                                  "Click 'No' to keep it running in the background.")
        if res is True:  # Yes: Exit
            if hasattr(self, 'watcher'):
                self.watcher.stop()
            self.destroy()
        else:  # No: Minimize to tray (actually just withdraw for now)
            self.withdraw()
            print("[ScreenZen] Running in background. Capture a screenshot to see the popup.")
