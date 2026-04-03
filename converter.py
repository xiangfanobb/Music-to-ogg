#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG Converter - 核心转换模块
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class AudioConverter:
    """音频转换器类"""
    
    def __init__(self):
        self.ffmpeg_path = self.get_ffmpeg_path()
        
    def get_ffmpeg_path(self) -> Optional[str]:
        """获取FFmpeg的完整路径"""
        # 尝试在常见安装位置查找
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Tools\ffmpeg\bin\ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
        ]
        
        # 首先尝试从系统PATH中查找
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
        
        # 如果PATH中找不到，尝试已知路径
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def convert(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        channels: int = 1,
        sample_rate: int = 48000,
        quality: int = 5
    ) -> Tuple[bool, str]:
        """
        转换音频文件为OGG格式
        
        Args:
            input_file: 输入文件路径
            output_dir: 输出目录（默认为输入文件所在目录）
            channels: 声道数 (1=单声道, 2=立体声)
            sample_rate: 采样率
            quality: 质量 (0-10)
            
        Returns:
            (成功状态, 消息)
        """
        if not self.ffmpeg_path:
            return False, "错误: 找不到 FFmpeg，请确保已正确安装"
        
        if not os.path.exists(input_file):
            return False, f"错误: 文件不存在 - {input_file}"
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.dirname(input_file)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        input_path = Path(input_file)
        output_filename = f"{input_path.stem}_converted.ogg"
        output_file = os.path.join(output_dir, output_filename)
        
        # 构建FFmpeg命令
        cmd = [
            self.ffmpeg_path,
            '-i', input_file,
            '-ac', str(channels),
            '-ar', str(sample_rate),
            '-c:a', 'libvorbis',
            '-q:a', str(quality),
            '-y',  # 覆盖输出文件
            output_file
        ]
        
        try:
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                # 检查输出文件
                if os.path.exists(output_file):
                    size = os.path.getsize(output_file) / 1024
                    return True, f"转换成功: {output_filename} ({size:.1f} KB)"
                else:
                    return False, "转换成功但输出文件未找到"
            else:
                # 提取错误信息
                error_lines = []
                for line in result.stderr.split('\n'):
                    if 'Error' in line or 'error' in line:
                        error_lines.append(line.strip())
                
                error_msg = error_lines[-1] if error_lines else result.stderr[:200]
                return False, f"转换失败: {error_msg}"
                
        except Exception as e:
            return False, f"转换异常: {str(e)}"
    
    def batch_convert(
        self,
        files: list,
        output_dir: str,
        channels: int = 1,
        sample_rate: int = 48000,
        quality: int = 5
    ) -> list:
        """
        批量转换文件
        
        Args:
            files: 文件路径列表
            output_dir: 输出目录
            channels: 声道数
            sample_rate: 采样率
            quality: 质量
            
        Returns:
            转换结果列表 [(文件路径, 成功状态, 消息), ...]
        """
        results = []
        
        for file in files:
            success, message = self.convert(
                file,
                output_dir,
                channels,
                sample_rate,
                quality
            )
            results.append((file, success, message))
        
        return results


def simple_convert(input_file: str) -> bool:
    """简单的音频转换函数（兼容旧版本）"""
    converter = AudioConverter()
    success, message = converter.convert(input_file)
    
    if success:
        print(f"转换成功! {message}")
    else:
        print(f"转换失败! {message}")
    
    return success


if __name__ == "__main__":
    # 命令行接口
    import argparse
    
    parser = argparse.ArgumentParser(description='Music-to-OGG 音频转换器')
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-c', '--channels', type=int, default=1, help='声道数 (1=单声道, 2=立体声)')
    parser.add_argument('-r', '--sample-rate', type=int, default=48000, help='采样率')
    parser.add_argument('-q', '--quality', type=int, default=5, help='质量 (0-10)')
    parser.add_argument('-b', '--batch', action='store_true', help='批量转换目录中的所有音频文件')
    
    args = parser.parse_args()
    
    converter = AudioConverter()
    
    if args.batch and os.path.isdir(args.input):
        # 批量转换目录
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg'}
        files = []
        
        for root, _, filenames in os.walk(args.input):
            for filename in filenames:
                if Path(filename).suffix.lower() in audio_extensions:
                    files.append(os.path.join(root, filename))
        
        if not files:
            print("错误: 目录中没有找到支持的音频文件")
            sys.exit(1)
        
        print(f"找到 {len(files)} 个音频文件")
        results = converter.batch_convert(
            files,
            args.output or args.input,
            args.channels,
            args.sample_rate,
            args.quality
        )
        
        success_count = sum(1 for _, success, _ in results if success)
        print(f"\n转换完成: {success_count}/{len(files)} 个文件成功")
        
        for file, success, message in results:
            status = "✅" if success else "❌"
            print(f"{status} {os.path.basename(file)}: {message}")
            
    else:
        # 单个文件转换
        if not os.path.exists(args.input):
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)
        
        success, message = converter.convert(
            args.input,
            args.output,
            args.channels,
            args.sample_rate,
            args.quality
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            sys.exit(1)