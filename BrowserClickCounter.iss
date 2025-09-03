; Inno Setup script for Browser Click Counter
; Save this file to the project root and compile with Inno Setup (ISCC.exe)

[Setup]
AppName=Browser Click Counter
AppVersion=1.0
DefaultDirName={pf}\Browser Click Counter
DefaultGroupName=Browser Click Counter
OutputBaseFilename=BrowserClickCounter_Installer
Compression=lzma
SolidCompression=yes

; You can change this to your app icon file if you have one
; SetupIconFile=app.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Pack the single EXE produced by PyInstaller (expects dist\BrowserClickCounter.exe in project root)
Source: "dist\\BrowserClickCounter.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Browser Click Counter"; Filename: "{app}\BrowserClickCounter.exe"
Name: "{group}\Uninstall Browser Click Counter"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\BrowserClickCounter.exe"; Description: "Launch Browser Click Counter"; Flags: nowait postinstall skipifsilent
