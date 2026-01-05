@echo off
echo ========================================
echo Building Pet Factory Executable
echo ========================================
echo.

REM Install PyInstaller if not present
echo Installing/Updating PyInstaller...
pip install pyinstaller --upgrade

echo.
echo Building executable...
echo This may take a few minutes...
echo.

REM Build the executable with all dependencies
pyinstaller --onefile ^
    --name="PetFactory" ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --collect-all pytesseract ^
    --collect-all cv2 ^
    --collect-all PIL ^
    --collect-all pynput ^
    PetFactory.py

echo.
echo ========================================
echo Build complete!
echo.
echo Executable location: dist\PetFactory.exe
echo.
echo IMPORTANTE: Tu amigo necesita instalar Tesseract OCR
echo Descarga: https://github.com/UB-Mannheim/tesseract/wiki
echo Instalar en: C:\Program Files\Tesseract-OCR
echo ========================================
echo.
pause
