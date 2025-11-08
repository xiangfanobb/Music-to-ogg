import os
import sys
import subprocess

def get_ffmpeg_path():
    """获取 FFmpeg 的完整路径"""
    # 尝试在常见安装位置查找
    possible_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",  # 你的安装位置
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Tools\ffmpeg\bin\ffmpeg.exe",
    ]
    
    # 首先尝试从系统PATH中查找
    try:
        result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    # 如果PATH中找不到，尝试已知路径
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果都找不到，返回None
    return None

def simple_convert(input_file):
    """简单的音频转换函数"""
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        return False
    
    # 获取FFmpeg路径
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("错误: 找不到 FFmpeg，请确保已正确安装")
        return False
    
    print(f"使用 FFmpeg: {ffmpeg_path}")
    
    # 生成输出文件名
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_converted.ogg"
    
    # FFmpeg命令
    cmd = [
        ffmpeg_path,
        '-i', input_file,
        '-ac', '1',           # 单声道
        '-ar', '48000',       # 48000Hz采样率
        '-c:a', 'libvorbis',  # OGG编码器
        '-y',                 # 覆盖输出文件
        output_file
    ]
    
    print(f"正在转换: {input_file} -> {output_file}")
    
    try:
        # 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("转换成功!")
        print(f"输出文件: {output_file}")
        
        # 显示文件信息
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"文件大小: {size:.2f} KB")
        
        return True
    except subprocess.CalledProcessError as e:
        print("转换失败!")
        if e.stderr:
            # 提取错误信息
            for line in e.stderr.split('\n'):
                if 'Error' in line or 'error' in line:
                    print(f"错误: {line}")
        return False

if __name__ == "__main__":
    test_file = r"C:\Users\edma\Desktop\76561199491290836@steam.mp3"
    
    if os.path.exists(test_file):
        print(f"找到测试文件: {test_file}")
        simple_convert(test_file)
    else:
        print("测试文件不存在，请手动指定文件路径")
        if len(sys.argv) > 1:
            simple_convert(sys.argv[1])
        else:
            print("用法: python converter.py 音频文件路径")
