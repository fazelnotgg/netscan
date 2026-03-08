@echo off
echo [NetScan] Memulai proses build...
call venv\Scripts\activate

REM Build using spec file for proper icon embedding
echo [NetScan] Building with spec file...
pyinstaller --clean netscan.spec

echo [NetScan] Build selesai! File ada di folder dist/
pause
