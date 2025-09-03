@echo off
REM Build installer using Inno Setup's ISCC.exe. Adjust the path to ISCC if needed.
SET ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
IF NOT EXIST %ISCC% (
  echo Inno Setup compiler not found at %ISCC%.
  echo Please install Inno Setup and update build_installer.cmd with the correct path.
  exit /b 1
)

REM Compile the .iss script. Output will be in the same folder as this script.
%ISCC% BrowserClickCounter.iss
IF %ERRORLEVEL% NEQ 0 (
  echo Inno Setup compilation failed.
  exit /b %ERRORLEVEL%
)
echo Installer built successfully.
pause
