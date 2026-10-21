@echo off
setlocal
cd /d "%~dp0.."

rem Keep cache inside this repository (for example D:\Arknights-Lore\.cache\prts-v2)
set "PRTS_ROUGHCARD_CACHE=%CD%\.cache\prts-v2"

echo [1/3] Checking Python...
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  set PY=python
)

%PY% --version || goto :error

echo [2/3] Installing/updating dependencies...
%PY% -m pip install -r tools\requirements-prts-roughcard.txt || goto :error

echo.
echo Choose mode:
echo   1 = Rich test: Exusiai / SilverAsh / Saria / Skadi / Mostima
echo   2 = Full build (all canonical catalogs)
echo   3 = Full build + local git commit
echo.
set /p MODE=Enter 1, 2 or 3: 

if "%MODE%"=="1" (
  %PY% tools\prts_roughcard_builder.py --scope operators --names "能天使,银灰,塞雷娅,斯卡蒂,莫斯提马" --refresh
  goto :done
)
if "%MODE%"=="2" (
  %PY% tools\prts_roughcard_builder.py --scope all
  goto :done
)
if "%MODE%"=="3" (
  %PY% tools\prts_roughcard_builder.py --scope all --commit
  goto :done
)

echo Invalid choice.
goto :end

:error
echo.
echo ERROR: command failed. See messages above.
pause
exit /b 1

:done
echo.
echo Done. Check build\rough-worldbook\ and build\rough-worldbook\QA-fetch-errors.json.
echo Cache: %PRTS_ROUGHCARD_CACHE%
pause

:end
endlocal
