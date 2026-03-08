"""
NetScan - WiFi Scanner Module
Scan WiFi networks using Windows netsh command
"""

import subprocess
from typing import List, Dict, Optional
from utils import parse_netsh_output


class WiFiScanner:
    """WiFi Scanner using Windows netsh command"""
    
    def __init__(self):
        self.networks: List[Dict] = []
        self.last_error: Optional[str] = None
    
    def scan(self) -> List[Dict]:
        """
        Scan for WiFi networks using netsh command.
        Returns list of network dictionaries.
        """
        try:
            # Run netsh command to scan networks
            cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0:
                self.last_error = f"Scan failed: {result.stderr}"
                return []
            
            # Parse the output
            self.networks = parse_netsh_output(result.stdout)
            self.last_error = None
            
            return self.networks
            
        except subprocess.TimeoutExpired:
            self.last_error = "Scan timeout - please try again"
            return []
        except FileNotFoundError:
            self.last_error = "netsh command not found - Windows only"
            return []
        except Exception as e:
            self.last_error = f"Scan error: {str(e)}"
            return []
    
    def get_networks(self) -> List[Dict]:
        """Get the last scanned networks"""
        return self.networks
    
    def get_network_by_index(self, index: int) -> Optional[Dict]:
        """Get a specific network by index (1-based)"""
        if 1 <= index <= len(self.networks):
            return self.networks[index - 1]
        return None
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error
    
    def has_error(self) -> bool:
        """Check if there was an error in the last scan"""
        return self.last_error is not None


def scan_wifi() -> tuple:
    """
    Convenience function to scan WiFi networks.
    Returns (networks_list, error_message)
    """
    scanner = WiFiScanner()
    networks = scanner.scan()
    error = scanner.get_last_error()
    return networks, error
