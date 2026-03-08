"""
NetScan - Display Module
Semua box dan tabel menggunakan rich.Table / rich.Panel
agar otomatis responsif berdasarkan panjang konten.
"""

from typing import List, Dict
from io import StringIO
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box as rich_box
from utils import render_signal_bar, get_signal_quality
from config import APP_NAME, APP_VERSION, APP_SUBTITLE

# Lebar konsol default untuk render (cukup lebar, tidak akan dipotong)
_CONSOLE_WIDTH = 120


def _console() -> tuple:
    """Buat Console yang menulis ke StringIO, return (console, buf)."""
    buf = StringIO()
    c = Console(file=buf, highlight=False, markup=True, width=_CONSOLE_WIDTH)
    return c, buf


# ─────────────────────────────────────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────────────────────────────────────

def get_welcome() -> str:
    ascii_art = r"""
 ███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
 ██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║
 ██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║
 ██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║
 ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
"""
    c, buf = _console()

    # Tabel 1 kolom untuk subtitle + versi
    t = Table(
        box=rich_box.ROUNDED,
        border_style="bright_blue",
        show_header=False,
        padding=(0, 2),
    )
    t.add_column(justify="center")
    t.add_row(f"[bold cyan]📡  WiFi Scanner Tool  —  {APP_SUBTITLE}[/bold cyan]")
    t.add_row(f"[dim]v{APP_VERSION}[/dim]")
    c.print(t)

    instructions = (
        " Ketik  [bold green]scan[/bold green]    untuk memindai WiFi di sekitar\n"
        " Ketik  [bold green]help[/bold green]    untuk melihat semua perintah\n"
        " Ketik  [bold green]exit[/bold green]    untuk keluar\n"
    )
    c.print(instructions)
    return ascii_art + buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  Help
# ─────────────────────────────────────────────────────────────────────────────

def get_help() -> str:
    commands = [
        ("scan",        "Pindai semua WiFi di sekitar"),
        ("info [no]",   "Tampilkan detail WiFi  (contoh: info 2)"),
        ("qr [no]",     "Tampilkan QR Code WiFi (contoh: qr 2)"),
        ("refresh",     "Scan ulang jaringan"),
        ("clear",       "Bersihkan layar terminal"),
        ("help",        "Tampilkan daftar perintah ini"),
        ("exit",        "Keluar dari aplikasi"),
    ]

    c, buf = _console()
    t = Table(
        title="[bold cyan]📖 Daftar Perintah NetScan[/bold cyan]",
        box=rich_box.ROUNDED,
        border_style="cyan",
        show_header=False,
        padding=(0, 2),
    )
    t.add_column("Perintah",   style="bold green", no_wrap=True)
    t.add_column("Deskripsi",  style="white")
    for cmd, desc in commands:
        t.add_row(cmd, desc)
    c.print(t)
    return "\n" + buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  Scan table
# ─────────────────────────────────────────────────────────────────────────────

def get_scan_table(networks: List[Dict]) -> str:
    if not networks:
        return "\n[yellow]⚠️  Tidak ada jaringan WiFi terdeteksi[/yellow]\n\n"

    c, buf = _console()
    t = Table(
        title="[bold]🔍 Jaringan WiFi Terdeteksi[/bold]",
        box=rich_box.ROUNDED,
        border_style="blue",
        header_style="bold cyan",
    )
    t.add_column("No",        style="dim",     no_wrap=True)
    t.add_column("SSID",      style="green",   no_wrap=True)
    t.add_column("Sinyal",    style="yellow",  no_wrap=True)
    t.add_column("Enkripsi",  style="magenta", no_wrap=True)
    t.add_column("Frekuensi", style="cyan",    no_wrap=True)
    t.add_column("Channel",   style="white",   no_wrap=True)

    for i, net in enumerate(networks, 1):
        ssid       = net.get("ssid", "Unknown")
        signal_pct = net.get("signal", 0)
        signal_bar = render_signal_bar(signal_pct)
        encryption = net.get("encryption", "Unknown")
        frequency  = net.get("frequency", "Unknown")
        channel    = str(net.get("channel", 0))
        t.add_row(f"[{i}]", ssid, f"{signal_bar} {signal_pct}%",
                  encryption, frequency, channel)

    c.print(t)
    c.print(f"\n[green]Total ditemukan: {len(networks)} jaringan[/green]")
    c.print("[dim]Ketik nomor WiFi untuk melihat detail (contoh: 'info 1')[/dim]\n")
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  Network detail
# ─────────────────────────────────────────────────────────────────────────────

def get_network_detail(network: Dict, index: int, password: str = "") -> str:
    ssid          = network.get("ssid", "Unknown")
    bssid         = network.get("bssid", "Unknown")
    signal_pct    = network.get("signal", 0)
    signal_dbm    = int((signal_pct / 100) * -70) - 30
    signal_bar    = render_signal_bar(signal_pct)
    encryption    = network.get("encryption", "Unknown")
    frequency     = network.get("frequency", "Unknown")
    channel       = str(network.get("channel", 0))
    quality       = get_signal_quality(signal_pct)
    password_disp = password if password else "[dim](tidak tersedia)[/dim]"

    fields = [
        ("SSID",      ssid),
        ("BSSID",     bssid),
        ("Sinyal",    f"{signal_dbm} dBm  {signal_bar} ({signal_pct}%)"),
        ("Enkripsi",  encryption),
        ("Frekuensi", frequency),
        ("Channel",   channel),
        ("Kualitas",  quality),
        ("Password",  password_disp),
        ("Status",    "[green]Tersedia[/green]"),
    ]

    c, buf = _console()
    t = Table(
        title="[bold]📶 Detail Jaringan WiFi[/bold]",
        box=rich_box.ROUNDED,
        border_style="blue",
        show_header=False,
        padding=(0, 2),
    )
    t.add_column("Label", style="bold cyan",  no_wrap=True)
    t.add_column("Value", style="white")
    for lbl, val in fields:
        t.add_row(lbl, val)
    c.print(t)
    c.print(f"\n[dim]🔗 Ketik 'qr {index}' untuk menampilkan QR Code koneksi[/dim]\n")
    return "\n" + buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  QR display (text fallback)
# ─────────────────────────────────────────────────────────────────────────────

def get_qr_display(ssid: str, qr_ascii: str) -> str:
    c, buf = _console()
    c.print(Panel(
        qr_ascii,
        title=f"[bold]QR Code — {ssid}[/bold]",
        border_style="green",
        padding=(1, 2),
    ))
    c.print("[cyan]📱 Scan QR Code ini dengan kamera HP untuk auto-connect![/cyan]")
    c.print("[dim]⚠️  Android 10+ / iOS 11+  •  Ketik 'back' untuk kembali[/dim]\n")
    return "\n" + buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  Status messages
# ─────────────────────────────────────────────────────────────────────────────

def _msg(markup: str) -> str:
    c, buf = _console()
    c.print(markup)
    return buf.getvalue()

def get_error(message: str)   -> str: return _msg(f"\n[red]❌ Error: {message}[/red]\n")
def get_warning(message: str) -> str: return _msg(f"\n[yellow]⚠️  {message}[/yellow]\n")
def get_info(message: str)    -> str: return _msg(f"\n[cyan]ℹ️  {message}[/cyan]\n")
def get_success(message: str) -> str: return _msg(f"\n[green]✅ {message}[/green]\n")


# ─────────────────────────────────────────────────────────────────────────────
#  Legacy class shim (agar main.py tidak perlu diubah)
# ─────────────────────────────────────────────────────────────────────────────

class DisplayFormatter:
    def get_welcome(self)                                    -> str: return get_welcome()
    def get_help(self)                                       -> str: return get_help()
    def get_scan_table(self, networks)                       -> str: return get_scan_table(networks)
    def get_network_detail(self, net, idx, password="")      -> str: return get_network_detail(net, idx, password)
    def get_qr_display(self, ssid, qr_ascii)                 -> str: return get_qr_display(ssid, qr_ascii)
    def get_error(self, msg)                                 -> str: return get_error(msg)
    def get_warning(self, msg)                               -> str: return get_warning(msg)
    def get_info(self, msg)                                  -> str: return get_info(msg)
    def get_success(self, msg)                               -> str: return get_success(msg)
    def get_banner(self)                                     -> str: return get_welcome()