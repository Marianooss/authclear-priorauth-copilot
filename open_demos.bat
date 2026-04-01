@echo off
echo Opening AuthClear Demo Pages (RESPONSIVE)...
echo.

REM Open architecture responsive
start "" "C:\Users\user\Desktop\devpost\video_assets\architecture_responsive.html"

timeout /t 2 /nobreak > nul

REM Open demo flow responsive
start "" "C:\Users\user\Desktop\devpost\video_assets\demo_flow_responsive.html"

timeout /t 1 /nobreak > nul

REM Open title card
start "" "C:\Users\user\Desktop\devpost\video_assets\title_card_final.html"

timeout /t 1 /nobreak > nul

REM Open compliance + ROI combined
start "" "C:\Users\user\Desktop\devpost\video_assets\compliance_roi_combined.html"

echo.
echo ========================================
echo All 3 demos opened in your browser!
echo ========================================
echo.
echo NEXT STEPS FOR RECORDING:
echo.
echo 1. Press F11 in each tab for fullscreen
echo 2. Press Win+G to start Game Bar recording
echo 3. Record each demo:
echo    - Title card: 30 seconds
echo    - Architecture: 20 seconds
echo    - Demo flow: 40 seconds
echo.
echo TIP: The demos auto-animate, just narrate over them!
echo.
pause
