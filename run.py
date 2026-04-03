#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music-to-OGG 启动脚本
提供GUI和命令行两种运行方式
"""

import os
import sys
import argparse


def check_dependencies():
    """检查依赖"""
    try:
        import PySide6
        return True
    except ImportError:
        print("未找到PySide6，正在尝试安装...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyside6"])
            print("PySide6安装成功!")
            return True
        except:
            print("无法安装PySide6，请手动安装: pip install pyside6")
            return False


def run_gui():
    """运行GUI版本"""
    if not check_dependencies():
        print("无法启动GUI版本，请使用命令行版本")
        return 1
    
    try:
        from main import main
        return main()
    except Exception as e:
        print(f"启动GUI失败: {e}")
        return 1


def run_cli():
    """运行命令行版本"""
    try:
        from converter import simple_convert
        
        if len(sys.argv) > 2:
            # 使用converter.py的命令行参数
            from converter import __file__ as converter_file
            os.execl(sys.executable, sys.executable, converter_file, *sys.argv[2:])
        else:
            print("用法: python run.py cli <音频文件路径>")
            print("或: python run.py cli --help 查看完整选项")
            return 1
    except Exception as e:
        print(f"启动CLI失败: {e}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Music-to-OGG 音频转换器')
    parser.add_argument('mode', choices=['gui', 'cli'], nargs='?', default='gui',
                       help='运行模式: gui (图形界面) 或 cli (命令行)')
    
    # 如果提供了模式参数，解析它
    if len(sys.argv) > 1 and sys.argv[1] in ['gui', 'cli']:
        args = parser.parse_args()
    else:
        # 默认使用GUI
        args = argparse.Namespace(mode='gui')
    
    if args.mode == 'gui':
        return run_gui()
    else:
        return run_cli()


if __name__ == "__main__":
    sys.exit(main())