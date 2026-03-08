# 📡 NetScan — WiFi Scanner Tool

> ⚠️ **DISCLAIMER EDUKASI**  
> Tool ini dibuat **HANYA UNTUK TUJUAN EDUKASI DAN PEMBELAJARAN** di bidang networking.  
> Bukan untuk kegiatan hacking, pembobolan, atau penyalahgunaan jaringan orang lain tanpa izin.  
> Gunakan secara bertanggung jawab dan sesuai hukum yang berlaku.

Tool berbasis CLI untuk memindai WiFi di sekitar, menampilkan informasi teknis jaringan, dan menghasilkan QR Code untuk koneksi cepat via smartphone.

**Platform:** Windows (output `.exe`)  
**Bahasa:** Python 3.x

---

## ⚖️ Penafian Hukum & Etika

### ✅ Penggunaan yang Diizinkan
- Pembelajaran jaringan komputer dan protokol WiFi
- Memindai jaringan WiFi **milik sendiri** atau **dengan izin pemilik**
- Edukasi keamanan jaringan di lingkungan sekolah/kampus
- Eksperimen dan penelitian di lab jaringan

### ❌ Penggunaan yang Dilarang
- Membobol WiFi orang lain tanpa izin
- Mencuri akses internet ilegal
- Kegiatan hacking yang melanggar hukum
- Memata-matai jaringan pihak lain
- Aktivitas kriminal lainnya

> 📌 **Catatan:** Tool ini hanya membaca informasi jaringan WiFi yang broadcast secara publik (SSID, BSSID, signal strength). Tool ini **TIDAK** melakukan:
> - Brute force password
> - Exploit keamanan WiFi
> - Man-in-the-middle attacks
> - Packet sniffing atau intercept

---

## 🚀 Quick Start

### 1. Setup Virtual Environment

Jalankan script setup otomatis:

```bash
setup_venv.bat
```

Atau manual:

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan venv (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
python main.py
```

### 3. Build ke EXE (Opsional)

```bash
build.bat
```

File `.exe` akan ada di folder `dist/NetScan.exe`

---

## 📖 Perintah

| Perintah | Deskripsi |
|----------|-----------|
| `scan` | Pindai semua WiFi di sekitar |
| `info <no>` | Tampilkan detail WiFi (contoh: `info 1`) |
| `qr <no>` | Tampilkan QR Code WiFi (contoh: `qr 1`) |
| `refresh` | Scan ulang jaringan |
| `clear` | Bersihkan layar terminal |
| `help` | Tampilkan daftar perintah |
| `exit` | Keluar dari aplikasi |

---

## 📁 Struktur Proyek

```
netscan/
├── main.py              # Entry point utama
├── terminal_gui.py      # GUI terminal custom (customtkinter)
├── scanner.py           # Logika scan WiFi (netsh)
├── display.py           # Format output (rich)
├── qrcode_gen.py        # Generate QR Code
├── utils.py             # Helper functions
├── config.py            # Konfigurasi aplikasi
├── requirements.txt     # Dependencies
├── setup_venv.bat       # Script setup venv
├── build.bat            # Script build EXE
├── netscan.spec         # PyInstaller config
├── create_icon.py       # Script buat icon
└── assets/
    ├── icon.ico         # Icon aplikasi (opsional)
```

---

## 🛠️ Dependencies

- `customtkinter` — GUI framework modern
- `rich` — Format output teks (tabel, warna, panel)
- `qrcode[pil]` — Generate QR Code
- `Pillow` — Image processing
- `pyinstaller` — Build ke EXE

---

## ⚙️ Cara Kerja

### Scan WiFi
Aplikasi menggunakan perintah Windows `netsh wlan show networks mode=bssid` untuk memindai jaringan WiFi di sekitar. Output diparse menjadi data terstruktur (SSID, BSSID, sinyal, enkripsi, frekuensi, channel).

### QR Code
QR Code dihasilkan menggunakan format standar WiFi:
```
WIFI:S:<SSID>;T:<WPA/WPA2/WPA3/nopass>;P:<password>;;
```

Scan QR Code dengan kamera HP (Android 10+ / iOS 11+) untuk auto-connect.

### Custom Terminal GUI
GUI dibangun dengan `customtkinter` untuk tampilan seperti terminal profesional:
- Background gelap
- Font monospace (Consolas)
- Output berwarna (hijau=sukses, merah=error, kuning=warning, biru=info)
- Input bar di bawah dengan prompt

---

## ⚠️ Catatan Penting

1. **Permission Administrator**: Scan WiFi di Windows memerlukan run as Administrator untuk hasil optimal.

2. **WiFi Adapter**: Pastikan WiFi adapter aktif dan driver terinstall.

3. **Kompatibilitas**: Tool ini **hanya membaca** jaringan WiFi — tidak bisa hack atau bypass password.

4. **QR Code & Password**: 
   - WiFi open (tanpa password): QR langsung bisa digunakan
   - WiFi dengan password: QR berisi info SSID, password tidak disertakan (standar keamanan)

---

## 📸 Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│  📡 NetScan — WiFi Scanner Tool                       _ □ ✕ │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ╔═══════════════════════════════════════════════════════╗  │
│  ║      📡  N E T S C A N  —  WiFi Scanner Tool         ║  │
│  ║           Tool Edukasi Networking                     ║  │
│  ╚═══════════════════════════════════════════════════════╝  │
│                                                             │
│  NetScan> scan                                              │
│                                                             │
│  🔍 Memindai jaringan WiFi...                               │
│                                                             │
│  No   SSID                  Sinyal      Enkripsi    Channel │
│  ────────────────────────────────────────────────────────── │
│  [1]  HomeNet               ████▓ 87%   WPA2        36      │
│  [2]  OfficeWifi            ███░░ 65%   WPA3        6       │
│                                                             │
│  NetScan> _                                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  > [ input perintah di sini... ]           [  Kirim  ]      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### "netsh command not found"
- Pastikan menggunakan Windows
- Jalankan sebagai Administrator

### "Tidak ada WiFi terdeteksi"
- Pastikan WiFi adapter aktif
- Check driver WiFi terinstall
- Jalankan sebagai Administrator

### Build EXE gagal
- Pastikan venv aktif: `venv\Scripts\activate`
- Install ulang dependencies: `pip install -r requirements.txt`
- Check PyInstaller: `pip install --upgrade pyinstaller`

---

## 📄 License

Dibuat untuk keperluan edukasi dan pembelajaran networking.

Tool ini bersifat **edukatif** — hanya membaca informasi jaringan WiFi yang broadcast secara publik, tidak memodifikasi atau membobol keamanan jaringan.

### 🎓 Tujuan Edukasi
Tool ini dibuat untuk:
- Pembelajaran jaringan komputer
- Memahami protokol WiFi dan 802.11
- Eksperimen dengan QR Code untuk koneksi otomatis
- Demonstrasi tools network administration

### ⚠️ Tanggung Jawab Pengguna
Pengguna bertanggung jawab penuh atas penggunaan tool ini. Developer tidak bertanggung jawab atas penyalahgunaan tool untuk kegiatan ilegal.

---

## 👨‍💻 Developer

Dibuat dengan ❤️ untuk Teknologi Jaringan
