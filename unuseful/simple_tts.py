#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Coqui TTS调用脚本
快速上手使用
"""

import os
import sys
import torch

try:
    from TTS.api import TTS
except ImportError:
    print("❌ TTS库未安装，请运行: pip install TTS")
    sys.exit(1)


def main():
    """简单的TTS演示"""
    print("🐸 简化版 Coqui TTS 演示")
    print("=" * 40)
    
    # 检查设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    
    # 要转换的文本
    text = "Hello, this is a simple demonstration of text to speech synthesis using Coqui TTS."
    print(f"文本: {text}")
    
    try:
        # 初始化TTS模型（使用默认英语模型）
        print("\n正在加载TTS模型...")
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True).to(device)
        
        # 生成语音
        output_file = "simple_output.wav"
        print(f"\n正在生成语音...")
        tts.tts_to_file(text=text, file_path=output_file)
        
        print(f"\n✅ 成功！语音已保存到: {output_file}")
        
        # 如果在Windows上，尝试播放音频
        if os.name == 'nt':
            try:
                import winsound
                print("正在播放音频...")
                winsound.PlaySound(output_file, winsound.SND_FILENAME)
            except ImportError:
                print("无法播放音频（winsound不可用）")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
