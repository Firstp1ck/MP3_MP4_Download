@echo off
:: Überprüfen, ob die Pakete bereits installiert ist
python -m pip list | findstr /C:"pytube" > nul
python -m pip list | findstr /C:"moviepy" > nul

:: Wenn das Paket nicht gefunden wurde, führe die Installation aus
if errorlevel 1 (
    echo Pakete werden installiert...
    python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pytube moviepy
) else (
    echo Pakete sind bereits installiert.
)

:: Führen Sie Ihr Python-Skript aus. Ersetzen Sie 'APP.py' durch den Namen Ihres Skripts.
python Youtube_down_con_01.py

echo.
echo Skript wurde ausgeführt. Fenster schließen oder weitere Befehle eingeben.
pause
