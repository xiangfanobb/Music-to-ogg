# Music-to-OGG 快速开始指南

## 🚀 立即开始

### 选项1：使用预编译版本（最简单）
1. 从 [Releases](https://github.com/xiangfanobb/Music-to-ogg/releases) 下载最新版本
2. 运行 `Music-to-OGG.exe`（便携版）或安装 `Music-to-OGG_Setup.exe`

### 选项2：从源代码运行
```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 运行GUI版本
python run.py

# 3. 或运行命令行版本
python run.py cli --help
```

### 选项3：构建自己的版本
```bash
# 1. 安装构建工具
pip install pyinstaller

# 2. 运行构建脚本
python build.py

# 3. 选择构建选项（推荐选项2或3）
```

## 📋 系统要求

### 必需
- **Windows 7/8/10/11**（推荐Windows 10+）
- **[FFmpeg](https://ffmpeg.org/download.html)**（必须安装并添加到PATH）

### 可选（源代码版本需要）
- **Python 3.8+**
- **pip**（Python包管理器）

## 🔧 FFmpeg安装指南

### Windows用户
1. 访问 https://ffmpeg.org/download.html
2. 下载Windows版本（推荐"Windows builds from gyan.dev"）
3. 解压到 `C:\ffmpeg`
4. 将 `C:\ffmpeg\bin` 添加到系统PATH环境变量
5. 重启命令行或电脑

### 验证安装
```bash
# 打开命令提示符或PowerShell
ffmpeg -version
```
应该显示FFmpeg版本信息。

## 🎯 使用示例

### GUI版本
1. 启动 `Music-to-OGG.exe`
2. 点击"添加文件"选择音频文件
3. 设置输出目录（默认为用户音乐文件夹）
4. 调整参数（声道数、采样率、质量）
5. 点击"开始转换"
6. 转换完成后点击"打开输出目录"

### 命令行版本
```bash
# 转换单个文件
python converter.py input.mp3

# 转换整个文件夹
python converter.py C:\Music\ -b

# 自定义参数
python converter.py song.wav -o C:\Output -c 2 -r 44100 -q 8
```

## 🛠️ 故障排除

### 问题1：找不到FFmpeg
**症状**：程序提示"找不到FFmpeg"
**解决**：
1. 确认FFmpeg已安装：在命令行运行 `ffmpeg -version`
2. 如果未安装，参考上面的FFmpeg安装指南
3. 如果已安装但程序找不到，尝试重启电脑

### 问题2：转换失败
**症状**：转换过程中出现错误
**解决**：
1. 检查输入文件是否损坏
2. 尝试降低质量参数（-q 3）
3. 检查输出目录是否有写入权限

### 问题3：GUI无法启动
**症状**：双击exe无反应或闪退
**解决**：
1. 安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. 以管理员身份运行
3. 检查防病毒软件是否阻止了程序

## 📞 获取帮助

- **GitHub Issues**: https://github.com/xiangfanobb/Music-to-ogg/issues
- **查看完整文档**: [README.md](README.md)

## ⚡ 小贴士

1. **SCP:SL服务器使用**：建议使用单声道、48000Hz采样率
2. **批量转换**：使用"添加文件夹"功能可以一次性转换整个文件夹
3. **质量设置**：质量越高文件越大，5-7是较好的平衡点
4. **输出目录**：建议使用专用文件夹，避免与原始文件混淆

---

**注意**：首次运行时可能会被Windows Defender警告，这是因为PyInstaller打包的程序没有数字签名。点击"更多信息"->"仍要运行"即可。