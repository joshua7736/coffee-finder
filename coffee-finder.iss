; Inno Setup script for Coffee Finder
; Download Inno Setup from: https://jrsoftware.org/isdl.php
; Build with: iscc coffee-finder.iss
; This creates an installer (coffee-finder-setup.exe) with uninstaller, shortcuts, etc.

#define MyAppName "Coffee Finder"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Coffee Finder Contributors"
#define MyAppExeName "coffee-finder-gui.exe"

[Setup]
; Basic settings
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=coffee-finder-setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

; License and info
LicenseFile=README.md
InfoBeforeFile=
InfoAfterFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked,skipifdoesntexist
Name: "run_gui"; Description: "Launch Coffee Finder"; GroupDescription: "After installation"

[Files]
; Copy console executable
Source: "dist\coffee-finder.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copy GUI executable
Source: "dist\coffee-finder-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copy tray executable
Source: "dist\coffee-finder-tray.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copy README
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
; Copy license if available
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion; Excludes: "LICENSE"

[Icons]
; Start Menu icons
Name: "{group}\{#MyAppName} (GUI)"; Filename: "{app}\{#MyAppExeName}"; IconIndex: 0
Name: "{group}\{#MyAppName} (Tray)"; Filename: "{app}\coffee-finder-tray.exe"; IconIndex: 0
Name: "{group}\README"; Filename: "{app}\README.md"; IconIndex: 0
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcuts
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconIndex: 0
Name: "{commonappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconIndex: 0

[Run]
; Run the GUI after installation if task is selected
Filename: "{app}\{#MyAppExeName}"; Parameters: ""; Tasks: run_gui; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove shortcuts
Type: files; Name: "{commondesktop}\{#MyAppName}.lnk"
Type: files; Name: "{commonappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}.lnk"

[Code]
// Optional: Add code here for custom installer logic
