"""
NetScan - QR Code Window Module
Display QR code in a small popup window with white background
"""

import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional
import qrcode
import os
import sys
from utils import generate_wifi_qr_string, sanitize_ssid


def get_icon_path():
    """Get the correct icon path for both frozen and development mode"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        icon_path = os.path.join(os.path.dirname(sys.executable), "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(sys.executable), "assets", "icon.ico")
    else:
        # Running in development
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
    
    return icon_path if os.path.exists(icon_path) else None


class QRWindow(tk.Toplevel):
    """Small popup window to display QR code with white background"""

    def __init__(self, parent, ssid: str, encryption: str, password: str = ""):
        super().__init__(parent)

        self.ssid = ssid
        self.encryption = encryption
        self.password = password

        # Configure window
        self.title(f"QR Code - {ssid[:30]}")
        self.configure(bg="white")
        self.resizable(True, True)

        # Set window icon
        icon_path = get_icon_path()
        if icon_path:
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Set window size (fixed, but resizable)
        window_size = 350
        self.geometry(f"{window_size}x{window_size}")

        # Center window on parent
        if parent:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            x = parent_x + (parent_width - window_size) // 2
            y = parent_y + (parent_height - window_size) // 2
            self.geometry(f"+{x}+{y}")

        # Daftarkan ke parent agar bisa ditutup oleh close_all()
        if parent and hasattr(parent, 'qr_windows'):
            parent.qr_windows.append(self)
            self.protocol("WM_DELETE_WINDOW", lambda: self._on_close(parent))
        else:
            self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Build UI
        self._build_ui()

        # Generate and display QR code
        self._generate_qr_code()

    def _build_ui(self):
        """Build the window UI"""
        # Main frame with white background
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title label
        self.title_label = tk.Label(
            self.main_frame,
            text=f"WiFi: {self.ssid[:25]}",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="black"
        )
        self.title_label.pack(pady=(0, 10))

        # QR code label
        self.qr_label = tk.Label(self.main_frame, bg="white")
        self.qr_label.pack(pady=10)

        # Instructions label
        self.instructions_label = tk.Label(
            self.main_frame,
            text="Scan dengan kamera HP untuk connect",
            font=("Arial", 9),
            bg="white",
            fg="#666666"
        )
        self.instructions_label.pack(pady=(10, 0))

        # Close button
        self.close_button = tk.Button(
            self.main_frame,
            text="Tutup",
            command=self.destroy,
            font=("Arial", 10),
            bg="#0078D4",
            fg="white",
            activebackground="#005A9E",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        self.close_button.pack(pady=15)

    def _generate_qr_code(self):
        """Generate and display the QR code image"""
        try:
            # Sanitize SSID
            ssid = sanitize_ssid(self.ssid)

            # Generate WiFi QR string
            qr_string = generate_wifi_qr_string(ssid, self.encryption, self.password)

            # Create QR code with good quality for scanning
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_string)
            qr.make(fit=True)

            # Create image with white background
            img = qr.make_image(fill_color="black", back_color="white")

            # Resize for better display
            img_size = 250
            img = img.resize((img_size, img_size), Image.Resampling.LANCZOS)

            # Convert to PhotoImage for tkinter
            self.photo = ImageTk.PhotoImage(img)

            # Display in label
            self.qr_label.config(image=self.photo)

        except Exception as e:
            self.qr_label.config(text=f"Error: {str(e)}", fg="red")

    def _on_close(self, parent):
        """Handle window close and remove from parent's list"""
        if hasattr(parent, 'qr_windows') and self in parent.qr_windows:
            parent.qr_windows.remove(self)
        self.destroy()


def show_qr_window(parent, ssid: str, encryption: str, password: str = ""):
    """
    Convenience function to show QR code window.

    Args:
        parent: Parent window (can be None)
        ssid: WiFi network name
        encryption: Encryption type (WPA2, WEP, etc.)
        password: WiFi password (optional)
    """
    window = QRWindow(parent, ssid, encryption, password)
    if parent:
        window.transient(parent)  # Make window modal to parent
    window.focus_set()
    return window
