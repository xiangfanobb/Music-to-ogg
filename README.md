# Music Converter Pro 🎵

一个功能强大的音频转换工具，支持任意音频格式转换和音量调节。特别适合用于SCP:SL服务器插件的音频使用。

## ✨ 特性

- **现代化黑色主题GUI** - 使用PySide6开发的现代化深色界面Windows应用程序
- **任意格式转换** - 支持MP3, OGG, WAV, FLAC, M4A, AAC, WMA, OPUS等格式互转
- **音量调节** - 可调节音频文件的音量大小 (0.1x - 3.0x)
- **批量转换** - 支持同时转换多个文件或整个文件夹
- **可调参数** - 可调整声道数、采样率、质量等参数
- **进度显示** - 实时显示转换进度和状态
- **便携版本** - 提供无需安装的便携版
- **安装程序** - 提供完整的安装程序

## 📦 安装

### 方法1: 使用预编译版本（推荐）

1. 从 [Releases](https://github.com/xiangfanobb/Music-to-ogg/releases) 页面下载最新版本
2. 运行 `Music-to-OGG_Setup.exe` 进行安装
3. 或使用便携版 `Music-to-OGG_Portable.zip`

### 方法2: 从源代码运行

```bash
# 克隆仓库
git clone https://github.com/xiangfanobb/Music-to-ogg.git
cd Music-to-ogg

# 安装依赖
pip install -r requirements.txt

# 运行GUI版本
python run.py

# 或运行命令行版本
python run.py cli --help
```

### 方法3: 自行构建

```bash
# 安装构建工具
pip install pyinstaller

# 构建可执行文件
python build.py
```

## 🚀 使用指南

### 黑色主题界面
应用程序采用现代化黑色主题设计，具有以下特点：
- **深色背景** (#121212)：减少视觉疲劳，适合长时间使用
- **高对比度**：白色文字在深色背景上清晰易读
- **彩色功能按钮**：开始(绿色)、停止(红色)、打开目录(蓝色)按钮
- **悬停效果**：所有交互元素都有明显的悬停状态
- **专业外观**：现代化深色设计，提升使用体验

### GUI版本（推荐）

1. 启动程序
2. 点击"添加文件"或"添加文件夹"选择要转换的音频文件
3. 设置输出目录和转换参数
4. 点击"开始转换"
5. 转换完成后，点击"打开输出目录"查看结果

### 命令行版本

```bash
# 转换单个文件为指定格式
python converter.py input.mp3 -f wav

# 转换并调节音量
python converter.py song.wav -f mp3 -v 1.5

# 仅调节音量，不转换格式
python converter.py audio.mp3 --volume-only -v 0.8 --keep-format

# 转换整个文件夹
python converter.py /path/to/folder -b -f ogg

# 自定义参数
python converter.py input.wav -o output_folder -f flac -c 2 -r 44100 -q 8 -v 1.2
```

#### 命令行参数

- `-f, --format`: 输出格式 (mp3, ogg, wav, flac, m4a, aac, wma, opus，默认ogg)
- `-o, --output`: 输出目录（默认为输入文件所在目录）
- `-c, --channels`: 声道数 (1=单声道, 2=立体声，默认1)
- `-r, --sample-rate`: 采样率 (默认48000)
- `-q, --quality`: 质量等级 0-10 (默认5)
- `-v, --volume`: 音量倍数 (0.5=一半音量，1.0=原音量，2.0=两倍音量，默认1.0)
- `-b, --batch`: 批量转换目录中的所有音频文件
- `--volume-only`: 仅调节音量，不转换格式
- `--keep-format`: 调节音量时保持原格式

## 🔧 系统要求

- **操作系统**: Windows 7/8/10/11 (推荐Windows 10+)
- **运行时**: 需要安装 [FFmpeg](https://ffmpeg.org/download.html)
- **Python** (仅源代码版本需要): Python 3.8+

### FFmpeg安装

1. 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载Windows版本
2. 解压到 `C:\ffmpeg` 或任意目录
3. 将 `bin` 目录添加到系统PATH环境变量
4. 或在程序设置中指定FFmpeg路径

## 📁 项目结构

```
Music-to-ogg/
├── main.py              # GUI主程序 (支持任意格式转换和音量调节)
├── converter.py         # 核心转换模块 (支持8种格式和音量调节)
├── run.py              # 启动脚本
├── build.py            # 构建脚本
├── requirements.txt    # Python依赖
├── app.ico            # 应用程序图标
├── README.md          # 说明文档
├── QUICKSTART.md      # 快速开始指南
├── PROJECT_SUMMARY.md # 项目总结
└── LICENSE            # 许可证文件
```

## 🛠️ 开发

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 运行测试

```bash
# 运行GUI测试
python main.py

# 运行命令行测试
python converter.py --help
```

### 构建发布

```bash
# 使用构建脚本
python build.py

# 或手动构建
pyinstaller --name=Music-to-OGG --windowed --icon=app.ico --onefile run.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 📞 支持

- 提交 [Issue](https://github.com/xiangfanobb/Music-to-ogg/issues)
- 查看 [Wiki](https://github.com/xiangfanobb/Music-to-ogg/wiki) 获取更多帮助

## 🙏 致谢

感谢以下开源项目：
- [FFmpeg](https://ffmpeg.org/) - 强大的多媒体框架
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt for Python
- [PyInstaller](https://www.pyinstaller.org/) - Python应用打包工具

---

**注意**: 首次运行时可能会被Windows Defender警告，这是因为PyInstaller打包的程序没有数字签名。请点击"更多信息"->"仍要运行"。

**SCP:SL服务器插件使用建议**: 使用单声道、48000Hz采样率可以获得最佳兼容性。

