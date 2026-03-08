"""
NetScan - Terminal GUI Module
Custom terminal window using customtkinter with inline command input and blinking cursor
"""

import os
import customtkinter as ctk
from tkinter import font as tkfont
from typing import Callable, Optional
from config import (
    TERMINAL_BG_COLOR,
    TERMINAL_FG_COLOR,
    TERMINAL_INPUT_BG_COLOR,
    TERMINAL_ACCENT_COLOR,
    TERMINAL_ERROR_COLOR,
    TERMINAL_WARNING_COLOR,
    TERMINAL_INFO_COLOR,
    TERMINAL_FONT_FAMILY,
    TERMINAL_FONT_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    APP_NAME,
    ICON_PATH,
)


class TerminalGUI(ctk.CTk):
    """Custom terminal window GUI using customtkinter with inline input"""
    
    def __init__(self, command_handler: Callable[[str], str]):
        super().__init__()
        
        self.command_handler = command_handler
        self.current_networks = []
        self.input_buffer = ""
        self.cursor_visible = True
        self.cursor_after_id = None
        self.banner_text = ""  # Store banner text for clear command
        self.command_history: list = []   # Riwayat perintah yang sudah dijalankan
        self.history_index: int = -1      # Posisi navigasi history (-1 = input baru)
        self.current_input_backup = ""    # Backup input saat navigasi history
        self.qr_windows: list = []        # Referensi semua QR window yang terbuka
        
        # Configure window
        self.title(f"📡 {APP_NAME} — WiFi Scanner Tool")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=TERMINAL_BG_COLOR)

        # Set window icon - handle both frozen and development mode
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            icon_path = os.path.join(os.path.dirname(sys.executable), ICON_PATH)
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(sys.executable), "icon.ico")
        else:
            # Running in development
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ICON_PATH)
        
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        
        # Set up fonts
        self.terminal_font = ctk.CTkFont(
            family=TERMINAL_FONT_FAMILY,
            size=TERMINAL_FONT_SIZE,
        )
        
        # Build UI
        self._build_ui()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Build the user interface"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create output text area (scrollable)
        self.output_frame = ctk.CTkFrame(self, fg_color=TERMINAL_BG_COLOR)
        self.output_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            font=self.terminal_font,
            text_color=TERMINAL_FG_COLOR,
            fg_color=TERMINAL_BG_COLOR,
            border_color=TERMINAL_INPUT_BG_COLOR,
            border_width=1,
            wrap="char",
            activate_scrollbars=True,
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure text tags
        self._configure_text_tags()
        
        # Track input positions
        self.command_start_index = "1.0"
        self.input_start_index = "1.0"
        
        self.is_input_active = False
        
        # Bind keyboard events directly to the window and textbox
        self.bind("<Key>", self._on_key_press)
        self.output_text._textbox.bind("<Key>", self._on_key_press)
        
        # Allow mouse selection in textbox but keep keyboard focus on window
        self.output_text._textbox.bind("<ButtonRelease-1>", self._on_text_click)
        
        # Allow text selection via mouse drag (don't block mouse events)
        # Only block keyboard input that isn't copy (Ctrl+C)
        self.output_text._textbox.bind("<KeyPress>", self._on_textbox_key)
    
    def _configure_text_tags(self):
        """Configure text tags for colored output"""
        text_widget = self.output_text._textbox
        text_widget.tag_configure("normal", foreground=TERMINAL_FG_COLOR)
        text_widget.tag_configure("success", foreground=TERMINAL_ACCENT_COLOR)
        text_widget.tag_configure("error", foreground=TERMINAL_ERROR_COLOR)
        text_widget.tag_configure("warning", foreground=TERMINAL_WARNING_COLOR)
        text_widget.tag_configure("info", foreground=TERMINAL_INFO_COLOR)
        text_widget.tag_configure("dim", foreground="#888888")
        text_widget.tag_configure("prompt", foreground=TERMINAL_ACCENT_COLOR)
        text_widget.tag_configure("input", foreground=TERMINAL_FG_COLOR)
        text_widget.tag_configure("cursor", foreground=TERMINAL_FG_COLOR)
    
    def _on_text_click(self, event):
        """Handle click/release on text area - keep focus on main window"""
        # Check if there's a selection - if so, don't steal focus
        text_widget = self.output_text._textbox
        try:
            text_widget.get("sel.first", "sel.last")
            # There's a selection, don't interfere
            return
        except Exception:
            pass
        self.focus_force()
        self.is_input_active = True
        self._start_cursor_blink()
    
    def _on_textbox_key(self, event):
        """Handle key press in textbox - allow Ctrl+C for copy, block everything else"""
        # Allow Ctrl+C for copying selected text
        if event.state & 0x4 and event.keysym.lower() == "c":
            return  # Allow default copy behavior
        return "break"
    
    def _focus_input(self):
        """Focus the main window for keyboard input"""
        self.focus_force()
        self.is_input_active = True
        self._start_cursor_blink()
    
    def _start_cursor_blink(self):
        """Start cursor blinking"""
        self._stop_cursor_blink()
        self.cursor_visible = True
        self._update_cursor()
        self._cursor_blink()
    
    def _stop_cursor_blink(self):
        """Stop cursor blinking"""
        if self.cursor_after_id:
            self.after_cancel(self.cursor_after_id)
            self.cursor_after_id = None
    
    def _cursor_blink(self):
        """Toggle cursor visibility"""
        self.cursor_visible = not self.cursor_visible
        self._update_cursor()
        self.cursor_after_id = self.after(500, self._cursor_blink)
    
    def _update_cursor(self):
        """Update cursor display at the correct position"""
        text_widget = self.output_text._textbox
        
        # Remove any existing cursor marker first
        self._remove_cursor()
        
        if self.cursor_visible and self.is_input_active:
            # Insert cursor block character at end, tagged with "cursor"
            text_widget.configure(state="normal")
            text_widget.insert("end", "█", "cursor")
    
    def _remove_cursor(self):
        """Remove cursor from display using the 'cursor' tag"""
        text_widget = self.output_text._textbox
        try:
            text_widget.configure(state="normal")
            # Find all ranges tagged with "cursor" and delete them
            while True:
                cursor_range = text_widget.tag_ranges("cursor")
                if not cursor_range:
                    break
                # Delete the first tagged range (start, end)
                text_widget.delete(cursor_range[0], cursor_range[1])
        except Exception:
            pass
    
    def _insert_text(self, text: str, tag: str = "normal"):
        """Safely insert text into the text widget"""
        text_widget = self.output_text._textbox
        text_widget.configure(state="normal")
        text_widget.insert("end", text, tag)
    
    def append_output(self, text: str, tag: str = "normal"):
        """Append text to output area with specified color tag"""
        self._remove_cursor()
        self._insert_text(text, tag)
        text_widget = self.output_text._textbox
        text_widget.see("end")
        if self.is_input_active:
            self._update_cursor()
    
    def append_colored_text(self, text: str):
        """
        Append text with embedded ANSI-like color codes.
        """
        self._remove_cursor()
        text_widget = self.output_text._textbox
        text_widget.configure(state="normal")
        
        current_text = ""
        current_tag = "normal"
        i = 0
        
        while i < len(text):
            if text[i:i+1] == '[':
                end_bracket = text.find(']', i+1)
                if end_bracket != -1:
                    if current_text:
                        text_widget.insert("end", current_text, current_tag)
                        current_text = ""
                    
                    tag_name = text[i+1:end_bracket]
                    
                    if tag_name == '/':
                        current_tag = "normal"
                    elif tag_name in ['green', 'success']:
                        current_tag = "success"
                    elif tag_name in ['red', 'error']:
                        current_tag = "error"
                    elif tag_name in ['yellow', 'warning']:
                        current_tag = "warning"
                    elif tag_name in ['cyan', 'info']:
                        current_tag = "info"
                    elif tag_name == 'dim':
                        current_tag = "dim"
                    elif tag_name == 'bold':
                        pass
                    else:
                        current_text = text[i:end_bracket+1]
                    
                    i = end_bracket + 1
                    continue
            
            current_text += text[i]
            i += 1
        
        if current_text:
            text_widget.insert("end", current_text, current_tag)
        
        text_widget.see("end")
        if self.is_input_active:
            self._update_cursor()
    
    def show_command_prompt(self):
        """Show command prompt for new input"""
        self._remove_cursor()
        text_widget = self.output_text._textbox
        text_widget.configure(state="normal")
        text_widget.insert("end", f"\ncommand: ", "prompt")
        self.command_start_index = text_widget.index("end-1c")
        self.input_start_index = self.command_start_index
        self.input_buffer = ""
        text_widget.see("end")
        self._update_cursor()
        self._focus_input()
    
    def get_current_command(self) -> str:
        """Get the current command from input buffer"""
        return self.input_buffer.strip()
    
    def _on_key_press(self, event):
        """Handle key press for input"""
        if not self.is_input_active:
            return "break"
        
        text_widget = self.output_text._textbox
        
        # Handle Enter
        if event.keysym == "Return":
            self._process_command()
            return "break"
        
        # Handle Backspace
        if event.keysym == "BackSpace":
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                self._remove_cursor()
                text_widget.configure(state="normal")
                text_widget.delete("end-2c", "end-1c")
                self._update_cursor()
            return "break"
        
        # Up arrow — navigasi ke perintah sebelumnya
        if event.keysym == "Up":
            if self.command_history:
                if self.history_index == -1:
                    # Simpan input yang sedang diketik sebelum navigasi
                    self.current_input_backup = self.input_buffer
                    self.history_index = len(self.command_history) - 1
                elif self.history_index > 0:
                    self.history_index -= 1
                self._replace_input(self.command_history[self.history_index])
            return "break"

        # Down arrow — navigasi ke perintah berikutnya
        if event.keysym == "Down":
            if self.history_index != -1:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self._replace_input(self.command_history[self.history_index])
                else:
                    # Kembali ke input yang sedang diketik sebelum navigasi
                    self.history_index = -1
                    self._replace_input(self.current_input_backup)
            return "break"

        # Left/Right dan key lain yang tidak dipakai
        if event.keysym in ["Left", "Right", "Home", "End", "Delete", "Escape", "Tab"]:
            return "break"
        
        # Handle Ctrl+C - copy selected text
        if event.state & 0x4 and event.keysym.lower() == "c":
            text_widget = self.output_text._textbox
            try:
                selected = text_widget.get("sel.first", "sel.last")
                if selected:
                    self.clipboard_clear()
                    self.clipboard_append(selected)
            except Exception:
                pass
            return "break"
        
        # Handle Ctrl+V (paste)
        if event.state & 0x4 and event.keysym == "v":
            try:
                clipboard = self.clipboard_get()
                if clipboard:
                    # Clean clipboard - only allow printable chars, no newlines
                    clipboard = clipboard.replace("\n", "").replace("\r", "")
                    self.input_buffer += clipboard
                    self._remove_cursor()
                    self._insert_text(clipboard, "input")
                    self._update_cursor()
            except Exception:
                pass
            return "break"
        
        # Handle Ctrl+A
        if event.state & 0x4 and event.keysym == "a":
            return "break"
        
        # Ignore modifier keys and function keys
        if event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R",
                            "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock",
                            "F1", "F2", "F3", "F4", "F5", "F6",
                            "F7", "F8", "F9", "F10", "F11", "F12",
                            "Win_L", "Win_R", "Menu"]:
            return "break"
        
        # Handle normal character input
        if event.char and len(event.char) == 1 and ord(event.char) >= 32:
            self.input_buffer += event.char
            self._remove_cursor()
            self._insert_text(event.char, "input")
            self._update_cursor()
            text_widget.see("end")
            return "break"
        
        return "break"
    
    def _process_command(self):
        """Process the current command"""
        command = self.get_current_command()
        # Simpan ke history jika tidak kosong dan berbeda dari entry terakhir
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
        self.history_index = -1  # Reset posisi history setelah enter
        self.current_input_backup = ""
        
        self._remove_cursor()
        text_widget = self.output_text._textbox
        text_widget.configure(state="normal")
        text_widget.insert("end", "\n")
        
        try:
            response = self.command_handler(command)
            
            if response == "\x0c":
                # Clear all content but keep the banner
                text_widget.delete("1.0", "end")
                if self.banner_text:
                    self.append_colored_text(self.banner_text)
                self.show_command_prompt()
                return
            
            if response:
                self.append_colored_text(response)
        except Exception as e:
            self.append_output(f"\nError: {str(e)}\n", "error")
        
        self.show_command_prompt()
    
    def _replace_input(self, new_text: str):
        """Ganti teks input buffer saat ini dengan new_text (untuk navigasi history)"""
        text_widget = self.output_text._textbox
        self._remove_cursor()
        text_widget.configure(state="normal")
        # Hapus semua karakter input yang ada (sejak input_start_index)
        try:
            text_widget.delete(self.input_start_index, "end")
        except Exception:
            pass
        self.input_buffer = new_text
        if new_text:
            text_widget.insert("end", new_text, "input")
        self._update_cursor()
        text_widget.see("end")

    def close_all(self):
        """Tutup semua QR window yang terbuka, lalu tutup main window"""
        # Tutup semua QR window
        for win in list(self.qr_windows):
            try:
                win.destroy()
            except Exception:
                pass
        self.qr_windows.clear()
        self._on_close()

    def clear_output(self):
        """Clear the output area"""
        self.output_text.delete("1.0", "end")
    
    def set_networks(self, networks: list):
        """Store current networks list"""
        self.current_networks = networks
    
    def get_networks(self) -> list:
        """Get current networks list"""
        return self.current_networks
    
    def _on_close(self):
        """Handle window close"""
        self._stop_cursor_blink()
        self.quit()
        self.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.after(100, self._focus_input)
        self.mainloop()


def create_terminal_gui(command_handler: Callable[[str], str]) -> TerminalGUI:
    """Create and return a TerminalGUI instance."""
    return TerminalGUI(command_handler)