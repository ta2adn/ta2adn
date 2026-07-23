@echo off
title TA2ADN Dashboard Veri Guncelleme
set /p CALENDAR_ICS_URL=Google Takvim gizli iCal adresini yapistirin: 
python scripts\update_data.py
if errorlevel 1 (
  echo.
  echo Veri guncelleme sirasinda hata olustu.
  pause
  exit /b 1
)
echo.
echo Veriler guncellendi.
pause
