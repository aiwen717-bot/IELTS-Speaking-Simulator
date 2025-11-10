#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动安装和运行TTS的脚本
"""

import subprocess
import sys
import os


def install_tts():
    """安装TTS库"""
    print("🔧 正在安装Coqui TTS...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "TTS"])
        print("✅ TTS安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ TTS安装失败: {e}")
        return False


def check_tts_installed():
    """检查TTS是否已安装"""
    try:
        import TTS
        print("✅ TTS已安装")
        return True
    except ImportError:
        print("❌ TTS未安装")
        return False


def run_simple_demo():
    """运行简单演示"""
    print("\n🚀 运行简单TTS演示...")
    
    try:
        import torch
        from TTS.api import TTS
        
        # 检查设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {device}")
        
        # 初始化TTS
        print("正在加载模型...")
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        
        # 生成语音
        text = "Hello! This is an automatic installation and demonstration of Coqui TTS."
        output_file = "auto_demo_output.wav"
        
        print("正在生成语音...")
        tts.tts_to_file(text=text, file_path=output_file)
        
        print(f"✅ 成功！语音已保存到: {output_file}")
        
        # 显示文件信息
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"文件大小: {file_size} 字节")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        return False


def main():
    """主函数"""
    print("🐸 Coqui TTS 自动安装和演示脚本")
    print("=" * 50)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 9):
        print("❌ 需要Python 3.9或更高版本")
        return False
    
    # 检查TTS是否已安装
    if not check_tts_installed():
        print("\n正在安装TTS...")
        if not install_tts():
            return False
    
    # 运行演示
    print("\n" + "=" * 50)
    success = run_simple_demo()
    
    if success:
        print("\n🎉 演示完成！")
        print("\n接下来您可以:")
        print("1. 运行 python simple_tts.py 进行简单演示")
        print("2. 运行 python tts_demo.py --help 查看更多选项")
        print("3. 在Windows上运行 run_tts_demo.bat 使用图形界面")
    else:
        print("\n❌ 演示失败，请检查错误信息")
    
    return success


if __name__ == "__main__":
    main()
