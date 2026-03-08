@echo off
echo ============================================
echo   NetScan - Setup Virtual Environment
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak terinstall!
    echo Download dan install Python dari: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python terdeteksi...
python --version
echo.

REM Check if venv already exists
if exist "venv\" (
    echo [WARNING] Virtual environment sudah ada!
    set /p overwrite="Apakah ingin membuat ulang? (y/n): "
    if /i "%overwrite%"=="y" (
        echo [INFO] Menghapus venv lama...
        rmdir /s /q venv
    ) else (
        echo [INFO] Menggunakan venv yang ada.
        echo.
        echo Untuk aktivasi, jalankan:
        echo   venv\Scripts\activate
        pause
        exit /b 0
    )
)

echo [INFO] Membuat virtual environment...
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Gagal membuat virtual environment!
    pause
    exit /b 1
)

echo [INFO] Virtual environment berhasil dibuat.
echo.
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate

echo [INFO] Menginstall dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Gagal install dependencies!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup Selesai!
echo ============================================
echo.
echo Untuk menjalankan aplikasi:
echo   1. Aktifkan venv: venv\Scripts\activate
echo   2. Jalankan: python main.py
echo.
echo Untuk build ke EXE:
echo   build.bat
echo.
pause
