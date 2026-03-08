"""
NetScan - Main Entry Point
WiFi Scanner CLI Tool with Custom Terminal GUI
"""

import sys
import os
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME
from scanner import WiFiScanner
from display import (
    get_welcome,
    get_help,
    get_scan_table,
    get_network_detail,
    get_qr_display,
    get_error,
    get_warning,
    get_info,
    get_success,
)
from qrcode_gen import generate_qr_code, generate_qr_image
from terminal_gui import create_terminal_gui
from qr_window import show_qr_window


class NetScanApp:
    """Main application class"""

    def __init__(self):
        self.scanner = WiFiScanner()
        self.networks = []
        self.last_command = ""
        self.gui = None  # Store reference to GUI for QR window
    
    def handle_command(self, command: str) -> str:
        """
        Handle user command and return response string.
        """
        command = command.strip().lower()
        self.last_command = command
        
        # Parse command and arguments
        parts = command.split()
        cmd = parts[0] if parts else ""
        arg = parts[1] if len(parts) > 1 else None
        
        # Command handlers
        if cmd == "exit" or cmd == "quit":
            return self._cmd_exit()
        elif cmd == "help":
            return self._cmd_help()
        elif cmd == "clear" or cmd == "cls":
            return self._cmd_clear()
        elif cmd == "scan":
            return self._cmd_scan()
        elif cmd == "refresh":
            return self._cmd_refresh()
        elif cmd == "info" and arg:
            return self._cmd_info(arg)
        elif cmd == "qr" and arg:
            return self._cmd_qr(arg)
        elif cmd == "back":
            return self._cmd_back()
        elif cmd == "":
            return ""
        else:
            return get_error(f"Perintah tidak dikenali: '{cmd}'. Ketik 'help' untuk daftar perintah.")
    
    def _cmd_exit(self) -> str:
        """Handle exit command — tutup QR window (jika ada) lalu tutup main window"""
        if self.gui:
            self.gui.after(100, self.gui.close_all)
        return get_info("Menutup aplikasi...")
    
    def _cmd_help(self) -> str:
        """Handle help command"""
        return get_help()
    
    def _cmd_clear(self) -> str:
        """Handle clear command"""
        # Return special marker for clear
        return "\x0c"  # Form feed character as clear signal
    
    def _cmd_scan(self) -> str:
        """Handle scan command"""
        output = ""
        output += get_info("🔍 Memindai jaringan WiFi...")
        
        self.networks = self.scanner.scan()
        
        if self.scanner.has_error():
            error = self.scanner.get_last_error()
            output += get_error(error)
            output += get_warning("Pastikan WiFi adapter aktif dan aplikasi dijalankan sebagai Administrator.")
        else:
            output += get_scan_table(self.networks)
        
        return output
    
    def _cmd_refresh(self) -> str:
        """Handle refresh command"""
        return self._cmd_scan()
    
    def _cmd_info(self, arg: str) -> str:
        """Handle info command with network index"""
        if not self.networks:
            return get_warning("Belum ada hasil scan. Ketik 'scan' terlebih dahulu.")
        
        try:
            index = int(arg)
            network = self.scanner.get_network_by_index(index)
            
            if network:
                # Try to get password for this network
                ssid = network.get("ssid", "")
                password = self._get_wifi_password(ssid)
                return get_network_detail(network, index, password=password)
            else:
                return get_error(f"Jaringan nomor {index} tidak ditemukan. Gunakan nomor 1-{len(self.networks)}.")
        except ValueError:
            return get_error(f"Nomor tidak valid: '{arg}'. Gunakan angka (contoh: info 1)")
    
    def _get_wifi_password(self, ssid: str) -> str:
        """
        Get saved WiFi password from Windows profile.
        Returns password string or empty string if not found.
        """
        try:
            cmd = ["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            if result.returncode != 0:
                return ""

            # Parse the output for Key Content (English and Indonesian)
            for line in result.stdout.split('\n'):
                line = line.strip()
                # Check for various possible key names
                if any(x in line for x in ["Key Content", "Konten Kunci", "Isi Kunci"]):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        password = parts[1].strip()
                        # Only return if password is not empty
                        if password:
                            return password

            return ""
        except Exception:
            return ""
    
    def _cmd_qr(self, arg: str) -> str:
        """Handle qr command with network index"""
        if not self.networks:
            return get_warning("Belum ada hasil scan. Ketik 'scan' terlebih dahulu.")

        try:
            index = int(arg)
            network = self.scanner.get_network_by_index(index)

            if network:
                ssid = network.get("ssid", "Unknown")
                encryption = network.get("encryption", "Unknown")
                
                # Get password for this network
                password = self._get_wifi_password(ssid)
                
                # Debug: print password status
                print(f"[DEBUG] SSID: {ssid}, Password: {'[FOUND]' if password else '[NOT FOUND]'}")

                # Show QR code in popup window
                show_qr_window(self.gui, ssid, encryption, password)
                
                return get_info(f"QR Code untuk '{ssid}' ditampilkan di window baru.")
            else:
                return get_error(f"Jaringan nomor {index} tidak ditemukan. Gunakan nomor 1-{len(self.networks)}.")
        except ValueError:
            return get_error(f"Nomor tidak valid: '{arg}'. Gunakan angka (contoh: qr 1)")
    
    def _cmd_back(self) -> str:
        """Handle back command"""
        if self.networks:
            return get_scan_table(self.networks)
        else:
            return get_warning("Belum ada hasil scan. Ketik 'scan' terlebih dahulu.")
    
    def run(self):
        """Run the application"""
        # Create GUI
        self.gui = create_terminal_gui(self.handle_command)

        # Show welcome message and store banner for clear command
        welcome = get_welcome()
        self.gui.banner_text = welcome  # Store for clear to re-display
        self.gui.append_colored_text(welcome)

        # Show initial command prompt
        self.gui.show_command_prompt()

        # Start GUI main loop
        self.gui.run()


def main():
    """Main entry point"""
    app = NetScanApp()
    app.run()


if __name__ == "__main__":
    main()