#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG Converter - 核心转换模块
支持任意音频格式转换和音量调节
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, List


class AudioConverter:
    """音频转换器类"""
    
    # 支持的音频格式和对应的编码器
    SUPPORTED_FORMATS = {
        'mp3': {'ext': '.mp3', 'codec': 'libmp3lame', 'quality_param': '-q:a'},
        'ogg': {'ext': '.ogg', 'codec': 'libvorbis', 'quality_param': '-q:a'},
        'wav': {'ext': '.wav', 'codec': 'pcm_s16le', 'quality_param': None},
        'flac': {'ext': '.flac', 'codec': 'flac', 'quality_param': '-compression_level'},
        'm4a': {'ext': '.m4a', 'codec': 'aac', 'quality_param': '-b:a'},
        'aac': {'ext': '.aac', 'codec': 'aac', 'quality_param': '-b:a'},
        'wma': {'ext': '.wma', 'codec': 'wmav2', 'quality_param': '-b:a'},
        'opus': {'ext': '.opus', 'codec': 'libopus', 'quality_param': '-b:a'},
    }
    
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
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的输出格式列表"""
        return list(self.SUPPORTED_FORMATS.keys())
    
    def get_format_info(self, format_name: str) -> Optional[Dict]:
        """获取格式信息"""
        return self.SUPPORTED_FORMATS.get(format_name.lower())
    
    def convert_to_format(
        self,
        input_file: str,
        output_format: str,
        output_dir: Optional[str] = None,
        channels: int = 1,
        sample_rate: int = 48000,
        quality: int = 5,
        volume: float = 1.0,
        output_filename: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        转换音频文件为指定格式
        
        Args:
            input_file: 输入文件路径
            output_format: 输出格式 (mp3, ogg, wav, flac, m4a, aac, wma, opus)
            output_dir: 输出目录（默认为输入文件所在目录）
            channels: 声道数 (1=单声道, 2=立体声)
            sample_rate: 采样率
            quality: 质量 (0-10，不同格式含义不同)
            volume: 音量调节倍数 (0.5=一半音量，1.0=原音量，2.0=两倍音量)
            output_filename: 自定义输出文件名（不含扩展名）
            
        Returns:
            (成功状态, 消息)
        """
        if not self.ffmpeg_path:
            return False, "错误: 找不到 FFmpeg，请确保已正确安装"
        
        if not os.path.exists(input_file):
            return False, f"错误: 文件不存在 - {input_file}"
        
        # 检查输出格式是否支持
        format_info = self.get_format_info(output_format)
        if not format_info:
            supported = ", ".join(self.get_supported_formats())
            return False, f"错误: 不支持的输出格式 '{output_format}'。支持的格式: {supported}"
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.dirname(input_file)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        input_path = Path(input_file)
        if output_filename:
            base_name = output_filename
        else:
            base_name = f"{input_path.stem}_converted"
        
        output_file = os.path.join(output_dir, f"{base_name}{format_info['ext']}")
        
        # 构建FFmpeg命令基础部分
        cmd = [self.ffmpeg_path, '-i', input_file]
        
        # 添加音量调节
        if volume != 1.0:
            cmd.extend(['-af', f'volume={volume}'])
        
        # 添加音频参数
        cmd.extend(['-ac', str(channels)])
        cmd.extend(['-ar', str(sample_rate)])
        
        # 添加编码器和质量参数
        cmd.extend(['-c:a', format_info['codec']])
        
        if format_info['quality_param']:
            # 不同格式的质量参数处理
            if output_format in ['mp3', 'ogg']:
                # MP3和OGG使用0-10的质量等级
                quality_value = quality
            elif output_format in ['m4a', 'aac', 'wma', 'opus']:
                # 这些格式使用比特率，质量等级转换为比特率
                bitrates = ['64k', '96k', '128k', '160k', '192k', '256k', '320k']
                quality_idx = min(max(quality, 0), len(bitrates) - 1)
                quality_value = bitrates[quality_idx]
            elif output_format == 'flac':
                # FLAC使用压缩级别0-8
                quality_value = min(max(quality, 0), 8)
            else:
                quality_value = quality
            
            cmd.extend([format_info['quality_param'], str(quality_value)])
        
        # 添加覆盖选项和输出文件
        cmd.extend(['-y', output_file])
        
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
                    return True, f"转换成功: {os.path.basename(output_file)} ({size:.1f} KB)"
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
    
    def adjust_volume(
        self,
        input_file: str,
        volume: float,
        output_dir: Optional[str] = None,
        keep_format: bool = True
    ) -> Tuple[bool, str]:
        """
        调节音频文件音量
        
        Args:
            input_file: 输入文件路径
            volume: 音量调节倍数 (0.5=一半音量，1.0=原音量，2.0=两倍音量)
            output_dir: 输出目录（默认为输入文件所在目录）
            keep_format: 是否保持原格式
            
        Returns:
            (成功状态, 消息)
        """
        if not self.ffmpeg_path:
            return False, "错误: 找不到 FFmpeg，请确保已正确安装"
        
        if not os.path.exists(input_file):
            return False, f"错误: 文件不存在 - {input_file}"
        
        if volume <= 0:
            return False, "错误: 音量倍数必须大于0"
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.dirname(input_file)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        input_path = Path(input_file)
        if keep_format:
            output_ext = input_path.suffix
            output_filename = f"{input_path.stem}_volume_{volume}x{output_ext}"
        else:
            output_filename = f"{input_path.stem}_volume_{volume}x.mp3"
        
        output_file = os.path.join(output_dir, output_filename)
        
        # 构建FFmpeg命令
        cmd = [
            self.ffmpeg_path,
            '-i', input_file,
            '-af', f'volume={volume}',
            '-c:a', 'copy' if keep_format else 'libmp3lame',
            '-q:a', '2' if not keep_format else None,
            '-y',
            output_file
        ]
        
        # 移除None值
        cmd = [arg for arg in cmd if arg is not None]
        
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
                    return True, f"音量调节成功: {output_filename} ({size:.1f} KB)"
                else:
                    return False, "音量调节成功但输出文件未找到"
            else:
                # 提取错误信息
                error_lines = []
                for line in result.stderr.split('\n'):
                    if 'Error' in line or 'error' in line:
                        error_lines.append(line.strip())
                
                error_msg = error_lines[-1] if error_lines else result.stderr[:200]
                return False, f"音量调节失败: {error_msg}"
                
        except Exception as e:
            return False, f"音量调节异常: {str(e)}"
    
    # 向后兼容的OGG转换方法
    def convert(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        channels: int = 1,
        sample_rate: int = 48000,
        quality: int = 5
    ) -> Tuple[bool, str]:
        """
        转换音频文件为OGG格式（向后兼容）
        """
        return self.convert_to_format(
            input_file=input_file,
            output_format='ogg',
            output_dir=output_dir,
            channels=channels,
            sample_rate=sample_rate,
            quality=quality,
            volume=1.0
        )
    
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
    
    parser = argparse.ArgumentParser(description='Music Converter Pro - 音频转换器')
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-f', '--format', default='ogg', 
                       choices=['mp3', 'ogg', 'wav', 'flac', 'm4a', 'aac', 'wma', 'opus'],
                       help='输出格式 (默认: ogg)')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-c', '--channels', type=int, default=1, help='声道数 (1=单声道, 2=立体声)')
    parser.add_argument('-r', '--sample-rate', type=int, default=48000, help='采样率')
    parser.add_argument('-q', '--quality', type=int, default=5, help='质量 (0-10)')
    parser.add_argument('-v', '--volume', type=float, default=1.0, help='音量倍数 (0.5=一半, 1.0=原音量, 2.0=两倍)')
    parser.add_argument('-b', '--batch', action='store_true', help='批量转换目录中的所有音频文件')
    parser.add_argument('--volume-only', action='store_true', help='仅调节音量，不转换格式')
    parser.add_argument('--keep-format', action='store_true', help='调节音量时保持原格式')
    
    args = parser.parse_args()
    
    converter = AudioConverter()
    
    if args.batch and os.path.isdir(args.input):
        # 批量转换目录
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg', '.opus'}
        files = []
        
        for root, _, filenames in os.walk(args.input):
            for filename in filenames:
                if Path(filename).suffix.lower() in audio_extensions:
                    files.append(os.path.join(root, filename))
        
        if not files:
            print("错误: 目录中没有找到支持的音频文件")
            sys.exit(1)
        
        print(f"找到 {len(files)} 个音频文件")
        print(f"输出格式: {args.format}")
        print(f"音量调节: {args.volume}x")
        
        results = []
        for file in files:
            if args.volume_only:
                # 仅调节音量
                success, message = converter.adjust_volume(
                    file,
                    args.volume,
                    args.output or args.input,
                    args.keep_format
                )
            else:
                # 格式转换+音量调节
                success, message = converter.convert_to_format(
                    input_file=file,
                    output_format=args.format,
                    output_dir=args.output or args.input,
                    channels=args.channels,
                    sample_rate=args.sample_rate,
                    quality=args.quality,
                    volume=args.volume
                )
            results.append((file, success, message))
        
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
        
        if args.volume_only:
            # 仅调节音量
            success, message = converter.adjust_volume(
                args.input,
                args.volume,
                args.output,
                args.keep_format
            )
        else:
            # 格式转换+音量调节
            success, message = converter.convert_to_format(
                input_file=args.input,
                output_format=args.format,
                output_dir=args.output,
                channels=args.channels,
                sample_rate=args.sample_rate,
                quality=args.quality,
                volume=args.volume
            )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            sys.exit(1)