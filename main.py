#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG Converter - 主程序
现代化的音频转换工具，支持批量转换和多种格式
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QProgressBar, QMessageBox, QGroupBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QSlider, QComboBox, QTextEdit, QSplitter, QStyleFactory
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor


class ConverterWorker(QThread):
    """转换工作线程"""
    progress_updated = Signal(int, str)  # 进度百分比, 当前文件
    conversion_finished = Signal(bool, str)  # 成功状态, 消息
    file_converted = Signal(str, bool, str)  # 文件名, 成功状态, 消息
    
    def __init__(self, files: List[str], output_dir: str, settings: Dict[str, Any]):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.settings = settings
        self._is_running = True
        
    def run(self):
        """执行转换任务"""
        total_files = len(self.files)
        
        for i, input_file in enumerate(self.files):
            if not self._is_running:
                break
                
            # 更新进度
            progress = int((i / total_files) * 100)
            self.progress_updated.emit(progress, f"正在处理: {os.path.basename(input_file)}")
            
            # 执行转换
            success, message = self.convert_file(input_file)
            self.file_converted.emit(input_file, success, message)
            
            # 短暂暂停，让UI有机会更新
            time.sleep(0.1)
        
        self.conversion_finished.emit(True, "转换完成!")
        
    def convert_file(self, input_file: str) -> (bool, str):
        """转换单个文件"""
        try:
            # 导入converter模块
            from converter import AudioConverter
            
            # 创建转换器实例
            converter = AudioConverter()
            
            # 使用新的convert_to_format方法
            success, message = converter.convert_to_format(
                input_file=input_file,
                output_format=self.settings.get('format', 'ogg'),
                output_dir=self.output_dir,
                channels=self.settings.get('channels', 1),
                sample_rate=self.settings.get('sample_rate', 48000),
                quality=self.settings.get('quality', 5),
                volume=self.settings.get('volume', 1.0)
            )
            
            return success, message
                
        except Exception as e:
            return False, f"转换异常: {str(e)}"
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """获取FFmpeg路径"""
        # 尝试从系统PATH中查找
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ["where", "ffmpeg"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    ["which", "ffmpeg"],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # 尝试已知路径
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Tools\ffmpeg\bin\ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def stop(self):
        """停止转换"""
        self._is_running = False


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.files_to_convert = []
        self.converter_worker = None
        self.settings = {
            'format': 'ogg',
            'channels': 1,
            'sample_rate': 48000,
            'quality': 5,
            'volume': 1.0,
            'output_dir': str(Path.home() / "Music" / "Converted")
        }
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Music Converter Pro - 音频转换器")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置应用图标
        if os.path.exists("app.ico"):
            self.setWindowIcon(QIcon("app.ico"))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("🎵 Music Converter Pro - 音频转换器")
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # 分隔线
        main_layout.addWidget(self.create_horizontal_line())
        
        # 文件选择区域
        file_group = QGroupBox("📁 文件选择")
        file_layout = QVBoxLayout()
        
        # 按钮行
        button_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("➕ 添加文件")
        self.add_files_btn.setMinimumHeight(40)
        self.add_files_btn.clicked.connect(self.add_files)
        
        self.add_folder_btn = QPushButton("📂 添加文件夹")
        self.add_folder_btn.setMinimumHeight(40)
        self.add_folder_btn.clicked.connect(self.add_folder)
        
        self.clear_list_btn = QPushButton("🗑️ 清空列表")
        self.clear_list_btn.setMinimumHeight(40)
        self.clear_list_btn.clicked.connect(self.clear_file_list)
        
        button_layout.addWidget(self.add_files_btn)
        button_layout.addWidget(self.add_folder_btn)
        button_layout.addWidget(self.clear_list_btn)
        button_layout.addStretch()
        
        file_layout.addLayout(button_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        file_layout.addWidget(self.file_list)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 设置区域
        settings_group = QGroupBox("⚙️ 转换设置")
        settings_layout = QVBoxLayout()
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        
        self.output_dir_label = QLabel(self.settings['output_dir'])
        self.output_dir_label.setStyleSheet("""
            padding: 5px; 
            background-color: #2d2d2d; 
            border-radius: 3px;
            border: 1px solid #444444;
            color: #cccccc;
        """)
        output_layout.addWidget(self.output_dir_label, 1)
        
        self.browse_output_btn = QPushButton("浏览...")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_output_btn)
        
        settings_layout.addLayout(output_layout)
        
        # 音频设置 - 第一行
        audio_row1_layout = QHBoxLayout()
        
        # 输出格式
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "OGG", "WAV", "FLAC", "M4A", "AAC", "WMA", "OPUS"])
        self.format_combo.setCurrentIndex(1)  # 默认OGG
        self.format_combo.currentIndexChanged.connect(self.update_format)
        format_layout.addWidget(self.format_combo)
        audio_row1_layout.addLayout(format_layout)
        
        # 声道数
        channels_layout = QVBoxLayout()
        channels_layout.addWidget(QLabel("声道数:"))
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["单声道 (1)", "立体声 (2)"])
        self.channels_combo.setCurrentIndex(0)
        self.channels_combo.currentIndexChanged.connect(self.update_channels)
        channels_layout.addWidget(self.channels_combo)
        audio_row1_layout.addLayout(channels_layout)
        
        # 采样率
        sample_rate_layout = QVBoxLayout()
        sample_rate_layout.addWidget(QLabel("采样率:"))
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["44100 Hz", "48000 Hz", "96000 Hz"])
        self.sample_rate_combo.setCurrentIndex(1)
        self.sample_rate_combo.currentIndexChanged.connect(self.update_sample_rate)
        sample_rate_layout.addWidget(self.sample_rate_combo)
        audio_row1_layout.addLayout(sample_rate_layout)
        
        audio_row1_layout.addStretch()
        settings_layout.addLayout(audio_row1_layout)
        
        # 音频设置 - 第二行
        audio_row2_layout = QHBoxLayout()
        
        # 质量
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("质量 (0-10):"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(0, 10)
        self.quality_spin.setValue(5)
        self.quality_spin.valueChanged.connect(self.update_quality)
        quality_layout.addWidget(self.quality_spin)
        audio_row2_layout.addLayout(quality_layout)
        
        # 音量调节
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("音量倍数:"))
        volume_control_layout = QHBoxLayout()
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(10, 300)  # 0.1x 到 3.0x
        self.volume_slider.setValue(100)  # 1.0x
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(50)
        self.volume_slider.valueChanged.connect(self.update_volume_from_slider)
        
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.1, 3.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(1.0)
        self.volume_spin.setDecimals(1)
        self.volume_spin.valueChanged.connect(self.update_volume_from_spin)
        
        volume_control_layout.addWidget(self.volume_slider)
        volume_control_layout.addWidget(self.volume_spin)
        
        volume_layout.addLayout(volume_control_layout)
        audio_row2_layout.addLayout(volume_layout)
        
        # 音量预设按钮
        volume_preset_layout = QVBoxLayout()
        volume_preset_layout.addWidget(QLabel("预设:"))
        preset_buttons_layout = QHBoxLayout()
        
        self.volume_half_btn = QPushButton("½")
        self.volume_half_btn.setToolTip("一半音量 (0.5x)")
        self.volume_half_btn.clicked.connect(lambda: self.set_volume_preset(0.5))
        
        self.volume_normal_btn = QPushButton("1")
        self.volume_normal_btn.setToolTip("正常音量 (1.0x)")
        self.volume_normal_btn.clicked.connect(lambda: self.set_volume_preset(1.0))
        
        self.volume_double_btn = QPushButton("2")
        self.volume_double_btn.setToolTip("双倍音量 (2.0x)")
        self.volume_double_btn.clicked.connect(lambda: self.set_volume_preset(2.0))
        
        preset_buttons_layout.addWidget(self.volume_half_btn)
        preset_buttons_layout.addWidget(self.volume_normal_btn)
        preset_buttons_layout.addWidget(self.volume_double_btn)
        
        volume_preset_layout.addLayout(preset_buttons_layout)
        audio_row2_layout.addLayout(volume_preset_layout)
        
        audio_row2_layout.addStretch()
        settings_layout.addLayout(audio_row2_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # 进度区域
        progress_group = QGroupBox("📊 转换进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setTextVisible(True)
        
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            padding: 5px; 
            color: #cccccc;
            background-color: #2d2d2d;
            border-radius: 3px;
            border: 1px solid #444444;
        """)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: Consolas, 'Courier New', monospace;
            }
        """)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.log_text)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 开始转换")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #1e8449;
            }
            QPushButton:hover {
                background-color: #219653;
                border: 1px solid #196f3d;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
                border: 1px solid #333333;
            }
        """)
        self.start_btn.clicked.connect(self.start_conversion)
        
        self.stop_btn = QPushButton("⏹️ 停止转换")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #c0392b;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border: 1px solid #a93226;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
                border: 1px solid #333333;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_conversion)
        
        self.open_output_btn = QPushButton("📂 打开输出目录")
        self.open_output_btn.setMinimumHeight(50)
        self.open_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border: 1px solid #2471a3;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)
        self.open_output_btn.clicked.connect(self.open_output_directory)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.open_output_btn)
        
        main_layout.addLayout(control_layout)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 应用样式
        self.apply_stylesheet()
        
    def create_horizontal_line(self):
        """创建水平分隔线"""
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #444444;")
        return line
        
    def apply_stylesheet(self):
        """应用黑色主题样式表"""
        self.setStyleSheet("""
            /* 主窗口 */
            QMainWindow {
                background-color: #121212;
            }
            
            /* 分组框 */
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #333333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            
            /* 按钮 */
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                border: 1px solid #444444;
                background-color: #2d2d2d;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #666666;
                border: 1px solid #333333;
            }
            
            /* 下拉框和微调框 */
            QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #444444;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #3498db;
                border: 1px solid #444444;
            }
            
            /* 标签 */
            QLabel {
                color: #ffffff;
            }
            
            /* 进度条 */
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 3px;
                text-align: center;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            /* 文本编辑框 */
            QTextEdit {
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: Consolas, 'Courier New', monospace;
            }
            
            /* 状态栏 */
            QStatusBar {
                background-color: #1e1e1e;
                color: #cccccc;
            }
        """)
        
    def load_settings(self):
        """加载设置"""
        # 这里可以添加从配置文件加载设置的逻辑
        pass
        
    def save_settings(self):
        """保存设置"""
        # 这里可以添加保存设置到配置文件的逻辑
        pass
        
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音频文件",
            str(Path.home()),
            "音频文件 (*.mp3 *.wav *.flac *.m4a *.aac *.wma);;所有文件 (*.*)"
        )
        
        if files:
            for file in files:
                if file not in self.files_to_convert:
                    self.files_to_convert.append(file)
                    item = QListWidgetItem(f"📄 {os.path.basename(file)}")
                    item.setData(Qt.UserRole, file)
                    self.file_list.addItem(item)
            
            self.update_status(f"已添加 {len(files)} 个文件")
            
    def add_folder(self):
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            str(Path.home())
        )
        
        if folder:
            # 支持的音频格式
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg'}
            added_count = 0
            
            for root, _, files in os.walk(folder):
                for file in files:
                    if Path(file).suffix.lower() in audio_extensions:
                        file_path = os.path.join(root, file)
                        if file_path not in self.files_to_convert:
                            self.files_to_convert.append(file_path)
                            item = QListWidgetItem(f"📁 {file}")
                            item.setData(Qt.UserRole, file_path)
                            self.file_list.addItem(item)
                            added_count += 1
            
            self.update_status(f"从文件夹添加了 {added_count} 个文件")
            
    def clear_file_list(self):
        """清空文件列表"""
        self.files_to_convert.clear()
        self.file_list.clear()
        self.update_status("文件列表已清空")
        
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.settings['output_dir']
        )
        
        if directory:
            self.settings['output_dir'] = directory
            self.output_dir_label.setText(directory)
            
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            
    def update_channels(self, index):
        """更新声道数设置"""
        self.settings['channels'] = 1 if index == 0 else 2
        
    def update_sample_rate(self, index):
        """更新采样率设置"""
        rates = [44100, 48000, 96000]
        self.settings['sample_rate'] = rates[index]
        
    def update_quality(self, value):
        """更新质量设置"""
        self.settings['quality'] = value
    
    def update_format(self, index):
        """更新输出格式设置"""
        formats = ['mp3', 'ogg', 'wav', 'flac', 'm4a', 'aac', 'wma', 'opus']
        self.settings['format'] = formats[index]
        
    def update_volume_from_slider(self, value):
        """从滑块更新音量设置"""
        volume = value / 100.0  # 转换为0.1-3.0范围
        self.settings['volume'] = volume
        # 更新微调框，但不触发其valueChanged信号
        self.volume_spin.blockSignals(True)
        self.volume_spin.setValue(volume)
        self.volume_spin.blockSignals(False)
        
    def update_volume_from_spin(self, value):
        """从微调框更新音量设置"""
        self.settings['volume'] = value
        # 更新滑块，但不触发其valueChanged信号
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(int(value * 100))
        self.volume_slider.blockSignals(False)
        
    def set_volume_preset(self, volume):
        """设置音量预设"""
        self.settings['volume'] = volume
        # 更新滑块和微调框
        self.volume_slider.setValue(int(volume * 100))
        self.volume_spin.setValue(volume)
        
    def start_conversion(self):
        """开始转换"""
        if not self.files_to_convert:
            QMessageBox.warning(self, "警告", "请先添加要转换的文件!")
            return
            
        # 检查输出目录
        output_dir = self.settings['output_dir']
        if not output_dir:
            QMessageBox.warning(self, "警告", "请先设置输出目录!")
            return
            
        # 创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建输出目录: {str(e)}")
            return
            
        # 检查FFmpeg
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            reply = QMessageBox.question(
                self,
                "FFmpeg未找到",
                "未找到FFmpeg，是否继续？\n\n请确保FFmpeg已安装并添加到系统PATH中。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.add_files_btn.setEnabled(False)
        self.add_folder_btn.setEnabled(False)
        self.clear_list_btn.setEnabled(False)
        
        # 清空日志
        self.log_text.clear()
        self.log("开始转换任务...")
        self.log(f"输出目录: {output_dir}")
        self.log(f"文件数量: {len(self.files_to_convert)}")
        
        # 创建并启动工作线程
        self.converter_worker = ConverterWorker(
            self.files_to_convert,
            output_dir,
            self.settings
        )
        
        # 连接信号
        self.converter_worker.progress_updated.connect(self.update_progress)
        self.converter_worker.file_converted.connect(self.on_file_converted)
        self.converter_worker.conversion_finished.connect(self.on_conversion_finished)
        
        # 启动线程
        self.converter_worker.start()
        
    def stop_conversion(self):
        """停止转换"""
        if self.converter_worker and self.converter_worker.isRunning():
            self.converter_worker.stop()
            self.log("正在停止转换...")
            
    def on_file_converted(self, filename, success, message):
        """处理单个文件转换完成"""
        basename = os.path.basename(filename)
        if success:
            self.log(f"✅ {basename}: {message}")
        else:
            self.log(f"❌ {basename}: {message}")
            
    def on_conversion_finished(self, success, message):
        """处理转换完成"""
        if success:
            self.log(f"🎉 {message}")
            QMessageBox.information(self, "完成", "所有文件转换完成!")
        else:
            self.log(f"⚠️ {message}")
            
        # 恢复UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.add_files_btn.setEnabled(True)
        self.add_folder_btn.setEnabled(True)
        self.clear_list_btn.setEnabled(True)
        
        self.progress_bar.setValue(100)
        self.status_label.setText("转换完成")
        
    def update_progress(self, progress, status):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def get_ffmpeg_path(self):
        """获取FFmpeg路径（简化版）"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ["where", "ffmpeg"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    ["which", "ffmpeg"],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        return None
        
    def open_output_directory(self):
        """打开输出目录"""
        output_dir = self.settings['output_dir']
        if os.path.exists(output_dir):
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', output_dir])
            else:
                subprocess.run(['xdg-open', output_dir])
        else:
            QMessageBox.warning(self, "警告", "输出目录不存在!")
            
    def update_status(self, message):
        """更新状态栏"""
        self.statusBar().showMessage(message)
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.converter_worker and self.converter_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "转换正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.converter_worker.stop()
                self.converter_worker.wait(2000)  # 等待2秒
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle(QStyleFactory.create("Fusion"))
    
    # 设置应用程序信息
    app.setApplicationName("Music-to-OGG Converter")
    app.setOrganizationName("Music-to-OGG")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()