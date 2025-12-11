@echo off
echo Building Sticky Notes...

REM Convert SVG to ICO if needed (PyInstaller needs .ico)
REM For now, we'll use logo.png and convert to ico

REM Install dependencies
pip install pyinstaller pillow

REM Convert PNG to ICO
python -c "from PIL import Image; img = Image.open('logo.png'); img.save('logo.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])"

REM Build the executable
pyinstaller --name "Sticky Notes" ^
    --windowed ^
    --onefile ^
    --icon=logo.ico ^
    --add-data "logo.ico;." ^
    main.py

echo Build complete! Check the 'dist' folder.
pause
