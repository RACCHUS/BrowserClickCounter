# Browser Click Counter

A modern, always-on-top desktop app for Windows that counts mouse clicks within user-defined regions of Chrome or Edge browser windows. Features a sleek dark theme, intuitive UI, and comprehensive click tracking.

## ✨ Features
- **Modern Dark Theme**: Sleek Catppuccin-inspired color scheme
- **Smart Click Detection**: Only counts clicks in Chrome/Edge windows (optional)
- **Dual View Modes**: Compact and expanded interfaces
- **Real-time Statistics**: Click rate per hour and session duration
- **Region Management**: Draw, edit, and manage multiple click regions
- **Region Persistence**: Automatically saves and loads last used region
- **Smart Start Button**: Ready to start immediately with saved region
- **Persistent Settings**: Save/load configurations automatically
- **Always-on-top**: Stays visible while you work
- **Draggable Interface**: Easy window positioning
- **5-Minute Timer**: Built-in countdown timer with sound alerts

## 🎨 Modern UI Highlights
- **Catppuccin Color Palette**: Professional dark theme with excellent contrast
- **Segoe UI Typography**: Clean, modern fonts for better readability
- **Hover Effects**: Interactive buttons with visual feedback
- **Responsive Layout**: Optimized for both small and large screens
- **Visual Hierarchy**: Clear distinction between different UI elements

## 📋 Requirements
- Python 3.7+
- Windows OS
- [pynput](https://pypi.org/project/pynput/)
- [psutil](https://pypi.org/project/psutil/)
- [pywin32](https://pypi.org/project/pywin32/)
- tkinter (comes with Python)

Install dependencies:
```sh
pip install -r requirements.txt
```

## 🚀 Usage
1. **Launch**: `python main.py`
2. **Auto-Load**: App automatically loads your last used region (if any)
3. **Quick Start**: If region is already set, just click "Start" to begin
4. **Define New Regions**: Click "Draw" to create additional areas
5. **Monitor Stats**: View real-time click rates and session time
6. **Use Timer**: Set countdown timers with sound alerts
7. **Manage Regions**: Add, remove, or clear regions as needed
8. **Auto-Save**: Settings save automatically when regions change

## 🎛️ Controls
- **⚙ Expand Button**: Switch between compact/expanded views (compact mode)
- **▼ Title Bar Indicator**: Click to expand (compact mode only)
- **Ctrl+E**: Keyboard shortcut to toggle views
- **Start/Stop**: Control click counting
- **Reset**: Clear counter and session data
- **Draw**: Create new click regions
- **Manage**: Edit existing regions
- **Save/Load**: Persist settings to file
- **× Close**: Exit application

## 📱 Interface Modes
### Compact Mode (Default)
- **Clean, minimal interface** showing just the click count
- **Region status display** shows current region info
- **Smart button states**: Start enabled when region ready, Draw highlighted when needed
- **Quick access controls**: Start and Draw buttons for immediate use
- **Timer integration**: 5-minute countdown timer with controls
- **Perfect for monitoring** while working

### Expanded Mode
- **Full control panel** with all features
- **Real-time statistics** and session tracking
- **Region management** tools
- **Timer configuration** options
- **Settings persistence** options
- **Complete configuration** access

## 🎯 Performance Optimized
- Lightweight tkinter interface
- Efficient mouse event handling
- Minimal system resource usage
- Fast region detection algorithms
- Optimized redraw cycles

## 🔧 Troubleshooting
- **Import Errors**: `pip install pynput psutil pywin32`
- **Permission Issues**: Run as administrator for window detection
- **Settings Not Saving**: Ensure write permissions in app directory


## �️ Download & Installation

### For End Users

1. **Download**  
	Get the latest installer ZIP:  
	`BrowserClickCounter_Installer.zip`  
	(provided by the app author or from your download link)

2. **Extract**  
	Right-click the ZIP and select “Extract All…”  
	Open the extracted folder.

3. **Install**  
	Double-click `BrowserClickCounter_Installer.exe`  
	Follow the prompts to install.  
	(You may see a Windows SmartScreen or UAC prompt; click “More info” → “Run anyway” if you trust the source.)

4. **Run the App**  
	After install, find “Browser Click Counter” in your Start Menu or desktop shortcut.

### For Developers

- To build the installer yourself:
  1. Build the EXE with PyInstaller (see below).
  2. Run `build_installer.cmd` (requires Inno Setup 6).

---

## �📁 Project Structure
```
BrowserClickCounter/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── src/                       # Source code
│   ├── gui.py                 # Main Tkinter GUI
│   ├── click_logic.py         # Core click tracking logic
│   │
│   ├── timer/                 # Timer feature
│   │   ├── timer.py           # Timer logic (session + countdown)
│   │   └── timer_gui.py       # Timer UI widgets
│   │
│   ├── celebration/           # Celebration effects
│   │   ├── celebration.py     # Celebration manager
│   │   └── fireworks.py       # Particle effects
│   │
│   ├── region/                # Region management
│   │   ├── region_drawer.py   # Draw click regions
│   │   └── region_manager.py  # Manage regions dialog
│   │
│   └── audio/                 # Audio playback
│       └── sound_manager.py   # Sound effects manager
│
├── tests/                     # Test files
├── demos/                     # Demo scripts
├── docs/                      # Documentation
├── sounds/                    # Sound assets
│
├── dist/                      # PyInstaller output (EXE)
├── Output/                    # Inno Setup output (installer)
├── BrowserClickCounter.iss    # Inno Setup script
└── build_installer.cmd        # Installer build script
```

## 🛠️ Building from Source

- To run from source, see the “Requirements” and “Usage” sections above.
- To build a distributable EXE:
  1. Install requirements:  
	  `pip install -r requirements.txt pyinstaller`
  2. Build:  
	  `pyinstaller --onefile --noconsole --name BrowserClickCounter main.py`
  3. The EXE will be in the `dist` folder.
- To create an installer:  
  Run `build_installer.cmd` (requires Inno Setup 6).

---

## 🎨 Color Scheme
- **Background**: `#1e1e2e` (Dark blue-gray)
- **Accent**: `#89b4fa` (Blue)
- **Success**: `#a6e3a1` (Green)
- **Warning**: `#f9e2af` (Yellow)
- **Error**: `#f38ba8` (Red)
- **Text**: `#cdd6f4` (Light blue-white)

## 📝 License
MIT License - Free to use and modify

---

**Enjoy your modern click counting experience! 🎉**
