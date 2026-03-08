"""
NetScan - Utility Functions
Helper functions for signal conversion, parsing, and formatting
"""


def dbm_to_percent(dbm: int) -> int:
    """
    Convert dBm signal strength to percentage.
    dBm range: typically -100 (weak) to -30 (strong)
    """
    if dbm >= -30:
        return 100
    elif dbm <= -100:
        return 0
    else:
        # Linear interpolation between -100 and -30
        return int(((dbm + 100) / 70) * 100)


def render_signal_bar(percent: int, length: int = 5) -> str:
    """
    Render a visual signal bar using block characters.
    Example: ████▓ for 80%
    """
    filled = int((percent / 100) * length)
    if filled >= length:
        return "█" * length
    elif filled == 0:
        return "░" * length
    else:
        # Partial block for the last character
        partial_chars = ["░", "▒", "▓", "█"]
        partial_idx = int((percent % 20) / 5)
        return "█" * (filled - 1) + partial_chars[min(partial_idx, 3)] + "░" * (length - filled)


def get_signal_quality(percent: int) -> str:
    """
    Get signal quality description based on percentage.
    """
    if percent >= 80:
        return "Excellent"
    elif percent >= 60:
        return "Good"
    elif percent >= 40:
        return "Fair"
    elif percent >= 20:
        return "Weak"
    else:
        return "Very Weak"


def parse_netsh_output(output: str) -> list:
    """
    Parse the output of 'netsh wlan show networks mode=bssid' command.
    Returns a list of dictionaries with network information.
    """
    networks = []
    current_network = None
    current_bss = None
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Detect new network (SSID)
        # netsh output format: "SSID 1 : NetworkName"
        if line.startswith("SSID ") and " : " in line:
            if current_network and current_bss:
                networks.append(current_bss.copy())
            
            # Split on " : " and take everything after it as the SSID
            ssid = line.split(" : ", 1)[1].strip().strip('"').strip("'")
            current_network = {
                "ssid": ssid if ssid else "<Hidden Network>",
                "bssid": "",
                "signal": 0,
                "encryption": "Unknown",
                "frequency": "Unknown",
                "channel": 0,
            }
            current_bss = current_network.copy()
        
        # Detect BSSID
        elif line.startswith("BSSID"):
            if current_network:
                bssid = line.split(":", 1)[1].strip() if ":" in line else ""
                current_bss["bssid"] = bssid
        
        # Detect Signal strength
        elif line.startswith("Signal"):
            if current_network:
                try:
                    signal_str = line.split(":", 1)[1].strip().replace("%", "")
                    signal = int(signal_str)
                    current_bss["signal"] = signal
                except (ValueError, IndexError):
                    current_bss["signal"] = 0
        
        # Detect Encryption/Auth
        elif "Authentication" in line:
            if current_network:
                auth = line.split(":", 1)[1].strip() if ":" in line else "Unknown"
                current_bss["encryption"] = auth
        
        # Detect Frequency
        elif line.startswith("Band"):
            if current_network:
                band = line.split(":", 1)[1].strip() if ":" in line else "Unknown"
                current_bss["frequency"] = band
        
        # Detect Channel
        elif line.startswith("Channel"):
            if current_network:
                try:
                    channel_str = line.split(":", 1)[1].strip()
                    channel = int(channel_str.split()[0])
                    current_bss["channel"] = channel
                except (ValueError, IndexError):
                    current_bss["channel"] = 0
        
        # End of BSSID entry - save and reset
        elif line.startswith("Network type"):
            if current_network and current_bss:
                networks.append(current_bss.copy())
                current_bss = current_network.copy()
    
    # Don't forget the last network
    if current_network and current_bss:
        networks.append(current_bss.copy())
    
    # Filter out networks without BSSID
    networks = [n for n in networks if n.get("bssid", "")]
    
    return networks


def generate_wifi_qr_string(ssid: str, encryption: str, password: str = "") -> str:
    """
    Generate WiFi QR Code string in standard format.
    Format: WIFI:S:<SSID>;T:<WPA/WEP/nopass>;P:<password>;;
    """
    # Determine encryption type
    if encryption.lower() in ["open", "none", "unknown"]:
        auth_type = "nopass"
        password = ""
    elif "WPA3" in encryption:
        auth_type = "WPA3"
    elif "WPA2" in encryption:
        auth_type = "WPA2"
    elif "WPA" in encryption:
        auth_type = "WPA"
    elif "WEP" in encryption:
        auth_type = "WEP"
    else:
        auth_type = "WPA2"  # Default
    
    # Build QR string
    qr_string = f"WIFI:S:{ssid};T:{auth_type};"
    if password:
        qr_string += f"P:{password};"
    qr_string += "H:false;;"
    
    return qr_string


def sanitize_ssid(ssid: str) -> str:
    """
    Sanitize SSID for display and QR code generation.
    """
    # Remove or replace special characters that might cause issues
    return ssid.replace("\n", "").replace("\r", "").strip()