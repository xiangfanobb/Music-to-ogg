#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG 构建脚本
用于打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("未找到PyInstaller，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except:
            print("无法安装PyInstaller")
            return False


def build_exe():
    """构建可执行文件"""
    if not check_pyinstaller():
        return False
    
    print("开始构建 Music-to-OGG 可执行文件...")
    
    # 清理之前的构建
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Music-to-OGG",
        "--windowed",  # 不显示控制台窗口
        "--icon=app.ico",
        "--add-data=app.ico;.",  # 包含图标文件
        "--clean",
        "--onefile",  # 打包成单个exe文件
        "run.py"
    ]
    
    try:
        print("正在打包... (这可能需要几分钟)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功!")
            
            # 检查生成的文件
            exe_path = dist_dir / "Music-to-OGG.exe"
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"生成文件: {exe_path}")
                print(f"文件大小: {size:.2f} MB")
                
                # 创建便携版zip
                create_portable_version(exe_path)
                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
        else:
            print("❌ 构建失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False


def create_portable_version(exe_path):
    """创建便携版"""
    print("\n创建便携版...")
    
    portable_dir = Path("Music-to-OGG_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制exe文件
    shutil.copy2(exe_path, portable_dir / "Music-to-OGG.exe")
    
    # 创建说明文件
    readme_content = """Music-to-OGG 便携版
====================

这是一个便携版的音频转换工具，无需安装即可使用。

使用方法:
1. 双击运行 "Music-to-OGG.exe"
2. 选择要转换的音频文件
3. 设置输出选项
4. 点击"开始转换"

系统要求:
- Windows 7/8/10/11
- 需要安装 FFmpeg (可以从 https://ffmpeg.org 下载)

注意事项:
- 首次运行可能会被Windows Defender警告，请点击"更多信息"->"仍要运行"
- 确保FFmpeg已添加到系统PATH环境变量中

作者: xiangfanobb
GitHub: https://github.com/xiangfanobb/Music-to-ogg
"""
    
    with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 创建批处理脚本，用于自动添加FFmpeg到PATH
    batch_content = """@echo off
echo Music-to-OGG 便携版启动器
echo.
echo 正在检查FFmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    echo FFmpeg已找到，启动程序...
    start "" "Music-to-OGG.exe"
) else (
    echo 警告: 未找到FFmpeg!
    echo 请从 https://ffmpeg.org 下载并安装FFmpeg
    echo 或将其添加到系统PATH环境变量中
    pause
)
"""
    
    with open(portable_dir / "Start.bat", "w", encoding="gbk") as f:
        f.write(batch_content)
    
    # 创建zip压缩包
    import zipfile
    
    zip_path = Path("Music-to-OGG_Portable.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in portable_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(portable_dir)
                zipf.write(file, arcname)
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ 便携版创建完成: {zip_path} ({zip_size:.2f} MB)")
    
    # 清理临时目录
    shutil.rmtree(portable_dir)


def create_installer():
    """创建安装程序（使用Inno Setup）"""
    print("\n创建安装程序...")
    
    # 检查Inno Setup是否可用
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
        print("⚠️  未找到Inno Setup，跳过安装程序创建")
        print("提示: 可以从 https://jrsoftware.org/isinfo.php 下载Inno Setup")
        return
    
    # 创建ISS脚本
    iss_content = f"""; Music-to-OGG 安装脚本
#define MyAppName "Music-to-OGG"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "xiangfanobb"
#define MyAppURL "https://github.com/xiangfanobb/Music-to-ogg"
#define MyAppExeName "Music-to-OGG.exe"

[Setup]
AppId={{{{E8C4A3B1-1234-5678-90AB-CDEF12345678}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=Music-to-OGG_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\Music-to-OGG.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion isreadme

[Icons]
Name: "{{group}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; IconFilename: "{{app}}\app.ico"
Name: "{{group}}\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; IconFilename: "{{app}}\app.ico"; Tasks: desktopicon

[Run]
Filename: "{{app}}\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  // 检查FFmpeg
  if not Exec('where', 'ffmpeg', '', SW_HIDE, ewWait, ResultCode) or (ResultCode <> 0) then
  begin
    if MsgBox('未检测到FFmpeg。Music-to-OGG需要FFmpeg才能正常工作。'#13#13'是否要打开FFmpeg下载页面？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://ffmpeg.org/download.html', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
  Result := True;
end;
"""
    
    iss_file = Path("setup.iss")
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    try:
        print("正在编译安装程序...")
        subprocess.run([inno_exe, str(iss_file)], check=True)
        
        output_dir = Path("Output")
        if output_dir.exists():
            setup_files = list(output_dir.glob("*.exe"))
            if setup_files:
                setup_file = setup_files[0]
                size = setup_file.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ 安装程序创建完成: {setup_file} ({size:.2f} MB)")
            else:
                print("❌ 未找到生成的安装程序")
        else:
            print("❌ 输出目录不存在")
            
    except Exception as e:
        print(f"❌ 创建安装程序失败: {e}")
    
    # 清理ISS文件
    if iss_file.exists():
        iss_file.unlink()


def main():
    """主函数"""
    print("=" * 50)
    print("Music-to-OGG 构建工具")
    print("=" * 50)
    
    # 检查是否在Windows上
    if sys.platform != "win32":
        print("⚠️  警告: 此构建脚本主要针对Windows平台")
        print("在其他平台上可能无法正常工作")
        print()
    
    # 构建选项
    print("请选择构建选项:")
    print("1. 仅构建可执行文件")
    print("2. 构建可执行文件 + 便携版")
    print("3. 构建可执行文件 + 安装程序 (需要Inno Setup)")
    print("4. 全部构建")
    print()
    
    try:
        choice = input("请输入选项 (1-4): ").strip()
        
        if choice == "1":
            build_exe()
        elif choice == "2":
            if build_exe():
                # 便携版已在build_exe中创建
                pass
        elif choice == "3":
            if build_exe():
                create_installer()
        elif choice == "4":
            if build_exe():
                create_installer()
        else:
            print("❌ 无效选项")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n用户取消")
        return 1
    
    print("\n构建完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())