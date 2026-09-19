@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        EC 2.0 - BUILD EXECUTABLE
echo ========================================

echo.
echo [1/3] Comprobando Python...
python --version >nul 2>&1 || (
    echo ERROR: Python no esta instalado o no esta en PATH.
    exit /b 1
)

echo [2/3] Comprobando PyInstaller...
python -m PyInstaller --version >nul 2>&1 || (
    echo PyInstaller no esta instalado.
    echo Instala con: python -m pip install pyinstaller
    exit /b 1
)

echo [3/3] Generando ec.exe...
python -m PyInstaller --noconfirm --clean --onefile --name ec --icon ec.ico --console --paths . main.py

if errorlevel 1 (
    echo ERROR: No se pudo generar ec.exe
    exit /b 1
)

echo.
echo LISTO: dist\ec.exe
endlocal
