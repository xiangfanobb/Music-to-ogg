#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG Build Script
Package the application into executable
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("PyInstaller not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except:
            print("Failed to install PyInstaller")
            return False


def build_exe():
    """Build executable file"""
    if not check_pyinstaller():
        return False
    
    print("Building Music-to-OGG executable...")
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Music-to-OGG",
        "--windowed",
        "--icon=app.ico",
        "--add-data=app.ico;.",
        "--clean",
        "--onefile",
        "run.py"
    ]
    
    try:
        print("Packaging... (this may take a few minutes)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Build successful!")
            
            exe_path = dist_dir / "Music-to-OGG.exe"
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)
                print(f"Output: {exe_path}")
                print(f"Size: {size:.2f} MB")
                create_portable_version(exe_path)
                return True
            else:
                print("[FAIL] Exe file not found")
                return False
        else:
            print(f"[FAIL] Build failed!\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Build error: {e}")
        return False


def create_portable_version(exe_path):
    """Create portable version"""
    print("\nCreating portable version...")
    
    portable_dir = Path("Music-to-OGG_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copy exe
    shutil.copy2(exe_path, portable_dir / "Music-to-OGG.exe")
    
    # README for portable version
    readme = """Music-to-OGG Portable Version
============================

Usage:
1. Double-click "Music-to-OGG.exe" to run
2. Make sure FFmpeg is installed and in system PATH

System Requirements:
- Windows 7/8/10/11
- FFmpeg (download from https://ffmpeg.org)

Note: First run may trigger Windows Defender - click "More info" -> "Run anyway"

Author: xiangfanobb
GitHub: https://github.com/xiangfanobb/Music-to-ogg
"""
    
    (portable_dir / "README.txt").write_text(readme, encoding="utf-8")
    
    # Batch script
    batch = """@echo off
echo Checking FFmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    start "" "Music-to-OGG.exe"
) else (
    echo FFmpeg not found! Please install from https://ffmpeg.org
    pause
)
"""
    
    (portable_dir / "Start.bat").write_text(batch, encoding="gbk")
    
    # Create zip
    import zipfile
    zip_path = Path("Music-to-OGG_Portable.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in portable_dir.rglob("*"):
            if file.is_file():
                zipf.write(file, file.relative_to(portable_dir))
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Portable version: {zip_path} ({zip_size:.2f} MB)")
    
    shutil.rmtree(portable_dir)


def create_installer():
    """Create installer using Inno Setup"""
    print("\nCreating installer...")
    
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    inno_exe = None
    for path in inno_paths:
        if os.path.exists(path):
            inno_exe = path
            break
    
    if not inno_exe:
        print("[WARN] Inno Setup not found, skipping installer")
        print("Download from: https://jrsoftware.org/isinfo.php")
        return
    
    # English-only ISS script (no Chinese language file dependency)
    # Note: {} in AppId must be doubled to escape them in ISS
    iss_content = """[Setup]
AppId={{E8C4A3B1-1234-5678-90AB-CDEF12345678}}
AppName=Music-to-OGG
AppVersion=1.0.0
AppPublisher=xiangfanobb
AppPublisherURL=https://github.com/xiangfanobb/Music-to-ogg
DefaultDirName={{autopf}}\\Music-to-OGG
DefaultGroupName=Music-to-OGG
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=Music-to-OGG_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\Music-to-OGG.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\Music-to-OGG"; Filename: "{{app}}\\Music-to-OGG.exe"; IconFilename: "{{app}}\\app.ico"
Name: "{{group}}\\Uninstall Music-to-OGG"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\Music-to-OGG"; Filename: "{{app}}\\Music-to-OGG.exe"; IconFilename: "{{app}}\\app.ico"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\Music-to-OGG.exe"; Description: "{{cm:LaunchProgram,Music-to-OGG}}"; Flags: nowait postinstall skipifsilent
"""
    
    iss_file = Path("setup.iss")
    try:
        iss_file.write_text(iss_content, encoding="utf-8")
        print("Compiling installer...")
        result = subprocess.run(
            [inno_exe, str(iss_file.absolute())],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            output_dir = Path("Output")
            if output_dir.exists():
                setup_files = list(output_dir.glob("*.exe"))
                if setup_files:
                    setup_file = setup_files[0]
                    size = setup_file.stat().st_size / (1024 * 1024)
                    print(f"[OK] Installer: {setup_file} ({size:.2f} MB)")
                    return
            print("[WARN] No installer exe found")
        else:
            print(f"[FAIL] Inno Setup error:\n{result.stderr}")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    finally:
        if iss_file.exists():
            iss_file.unlink()


def main():
    print("=" * 50)
    print("Music-to-OGG Build Tool")
    print("=" * 50)
    
    if sys.platform != "win32":
        print("WARNING: This script is designed for Windows")
        print()
    
    print("Build options:")
    print("1. Build exe only")
    print("2. Build exe + portable version")
    print("3. Build exe + installer (requires Inno Setup)")
    print("4. Build all")
    print()
    
    try:
        choice = input("Enter option (1-4): ").strip()
        
        if choice == "1":
            build_exe()
        elif choice == "2":
            build_exe()
        elif choice == "3":
            if build_exe():
                create_installer()
        elif choice == "4":
            if build_exe():
                create_installer()
        else:
            print("Invalid option")
            return 1
            
    except KeyboardInterrupt:
        print("\nCancelled")
        return 1
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
