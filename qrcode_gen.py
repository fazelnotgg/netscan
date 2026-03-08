"""
NetScan - QR Code Generator Module
Generate QR codes for WiFi networks
"""

from typing import Optional, Tuple
from io import BytesIO
import qrcode
from PIL import Image
from utils import generate_wifi_qr_string, sanitize_ssid


class QRCodeGenerator:
    """Generate QR codes for WiFi networks"""
    
    def __init__(self):
        self.last_qr_image: Optional[Image.Image] = None
        self.last_error: Optional[str] = None
    
    def generate(self, ssid: str, encryption: str, password: str = "") -> Tuple[Optional[str], Optional[str]]:
        """
        Generate QR code for WiFi network.
        Returns (qr_ascii_string, error_message)
        """
        try:
            # Sanitize SSID
            ssid = sanitize_ssid(ssid)
            
            # Generate WiFi QR string
            qr_string = generate_wifi_qr_string(ssid, encryption, password)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_string)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            self.last_qr_image = img
            
            # Convert to ASCII art
            ascii_art = self._image_to_ascii(img)
            
            return ascii_art, None
            
        except Exception as e:
            self.last_error = str(e)
            return None, f"Failed to generate QR code: {str(e)}"
    
    def _image_to_ascii(self, img: Image.Image, width: int = 40) -> str:
        """
        Convert QR code image to block art with 1:1 aspect ratio.
        Uses Unicode half-block characters to pair two pixel rows into one
        terminal row, compensating for the ~2:1 height:width ratio of
        monospaced font characters.
        
        Half-block mapping (top_pixel, bottom_pixel):
          (black, black) -> █  (full block)
          (black, white) -> ▀  (upper half block)
          (white, black) -> ▄  (lower half block)
          (white, white) -> ' ' (space)
        """
        # Make height even so we can pair rows cleanly
        height = width if width % 2 == 0 else width + 1
        
        img_resized = img.resize((width, height), Image.Resampling.NEAREST)
        img_bw = img_resized.convert('1')  # Convert to pure black & white
        
        pixels = list(img_bw.getdata())
        
        ascii_art = ""
        # Process two rows at a time
        for row in range(0, height, 2):
            line = ""
            for col in range(width):
                top_idx = row * width + col
                bot_idx = (row + 1) * width + col
                
                # 0 = black, 255 = white  in mode '1'
                top_black = top_idx < len(pixels) and pixels[top_idx] == 0
                bot_black = bot_idx < len(pixels) and pixels[bot_idx] == 0
                
                if top_black and bot_black:
                    line += "█"
                elif top_black and not bot_black:
                    line += "▀"
                elif not top_black and bot_black:
                    line += "▄"
                else:
                    line += " "
            ascii_art += line + "\n"
        
        return ascii_art
    
    def save_image(self, filename: str, ssid: str, size: int = 300) -> bool:
        """
        Save QR code as PNG image file.
        Returns True if successful, False otherwise.
        """
        try:
            if self.last_qr_image is None:
                return False
            
            # Create a larger image with better quality
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=15,
                border=4,
            )
            qr_string = generate_wifi_qr_string(sanitize_ssid(ssid), "WPA2")
            qr.add_data(qr_string)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            img.save(filename, "PNG")
            
            return True
            
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error


def generate_qr_code(ssid: str, encryption: str, password: str = "") -> Tuple[Optional[str], Optional[str]]:
    """
    Convenience function to generate QR code.
    Returns (qr_ascii_string, error_message)
    """
    generator = QRCodeGenerator()
    return generator.generate(ssid, encryption, password)


def generate_qr_image(ssid: str, encryption: str, password: str = "") -> Tuple[Optional[Image.Image], Optional[str]]:
    """
    Convenience function to generate QR code as PIL Image.
    Returns (qr_image, error_message)
    """
    try:
        # Sanitize SSID
        ssid = sanitize_ssid(ssid)

        # Generate WiFi QR string
        qr_string = generate_wifi_qr_string(ssid, encryption, password)

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

        return img, None

    except Exception as e:
        return None, str(e)
