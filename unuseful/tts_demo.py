#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coqui TTS 调用演示脚本
支持多种TTS功能：基础文本转语音、多语言、语音克隆、语音转换等
"""

import os
import sys
import argparse
import torch
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from TTS.api import TTS
except ImportError:
    logger.error("TTS库未安装，请运行: pip install TTS")
    sys.exit(1)


class TTSDemo:
    """TTS演示类"""
    
    def __init__(self, gpu=False):
        """初始化TTS演示"""
        self.device = "cuda" if gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {self.device}")
        self.tts = None
        
    def list_models(self):
        """列出所有可用的TTS模型"""
        logger.info("获取可用模型列表...")
        try:
            # 使用TTS内置的ModelManager
            from TTS.utils.manage import ModelManager
            from TTS.api import TTS
            
            # 使用TTS内置的模型文件路径
            models_file = TTS.get_models_file_path()
            logger.info(f"使用模型文件: {models_file}")
            
            # 创建ModelManager实例
            manager = ModelManager(models_file=models_file, progress_bar=False, verbose=False)
            
            print("\n=== 可用的TTS模型 ===")
            print("格式: 类型/语言/数据集/模型名称")
            print("-" * 50)
            
            # 获取模型列表
            models_list = manager.list_models()
            
            # 按类型分组显示
            tts_models = [m for m in models_list if m.startswith('tts_models')]
            vocoder_models = [m for m in models_list if m.startswith('vocoder_models')]
            vc_models = [m for m in models_list if m.startswith('voice_conversion_models')]
            
            if tts_models:
                print(f"\n[TTS] TTS模型 ({len(tts_models)}个):")
                for i, model in enumerate(tts_models[:20], 1):  # 只显示前20个
                    print(f"  {i:2d}. {model}")
                if len(tts_models) > 20:
                    print(f"     ... 还有 {len(tts_models) - 20} 个模型")
            
            if vocoder_models:
                print(f"\n[VOC] 声码器模型 ({len(vocoder_models)}个):")
                for i, model in enumerate(vocoder_models[:10], 1):  # 只显示前10个
                    print(f"  {i:2d}. {model}")
                if len(vocoder_models) > 10:
                    print(f"     ... 还有 {len(vocoder_models) - 10} 个模型")
            
            if vc_models:
                print(f"\n[VC] 语音转换模型 ({len(vc_models)}个):")
                for i, model in enumerate(vc_models, 1):
                    print(f"  {i:2d}. {model}")
            
            print(f"\n[总计] {len(models_list)} 个模型")
            
            return models_list
            
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            logger.info("显示常用模型列表作为备用...")
            
            # 备用方案：显示一些常用模型
            print("\n=== 常用TTS模型（备用列表）===")
            common_models = {
                "英文TTS模型": [
                    "tts_models/en/ljspeech/tacotron2-DDC",
                    "tts_models/en/ljspeech/glow-tts",
                    "tts_models/en/ljspeech/speedy-speech",
                    "tts_models/en/vctk/vits",
                ],
                "多语言TTS模型": [
                    "tts_models/multilingual/multi-dataset/your_tts",
                    "tts_models/multilingual/multi-dataset/xtts_v2",
                ],
                "中文TTS模型": [
                    "tts_models/zh/fairseq/vits",
                ],
                "语音转换模型": [
                    "voice_conversion_models/multilingual/vctk/freevc24"
                ]
            }
            
            for category, models in common_models.items():
                print(f"\n{category}:")
                for i, model in enumerate(models, 1):
                    print(f"  {i}. {model}")
            
            # 返回扁平化的模型列表
            all_models = []
            for models in common_models.values():
                all_models.extend(models)
            
            return all_models
    
    def basic_tts(self, text, output_path="output_basic.wav", model_name=None):
        """基础文本转语音"""
        logger.info("执行基础文本转语音...")
        
        try:
            # 使用默认英语模型或指定模型
            if model_name is None:
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            
            logger.info(f"加载模型: {model_name}")
            self.tts = TTS(model_name=model_name, progress_bar=True).to(self.device)
            
            # 生成语音
            logger.info(f"生成语音: {text}")
            self.tts.tts_to_file(text=text, file_path=output_path)
            
            logger.info(f"语音已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"基础TTS失败: {e}")
            return False
    
    def multilingual_tts(self, text, language="en", output_path="output_multilingual.wav", 
                        speaker_wav=None):
        """多语言TTS（支持语音克隆）"""
        logger.info("执行多语言TTS...")
        
        try:
            # 使用XTTS v2多语言模型
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            logger.info(f"加载多语言模型: {model_name}")
            
            self.tts = TTS(model_name=model_name, progress_bar=True).to(self.device)
            
            # 检查是否提供了参考语音进行语音克隆
            if speaker_wav and os.path.exists(speaker_wav):
                logger.info(f"使用语音克隆，参考音频: {speaker_wav}")
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
            else:
                logger.warning("未提供有效的参考音频，使用默认说话人")
                # 对于XTTS，需要提供speaker_wav，这里创建一个示例
                logger.error("XTTS模型需要提供speaker_wav参数进行语音克隆")
                return False
            
            logger.info(f"多语言语音已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"多语言TTS失败: {e}")
            return False
    
    def voice_conversion(self, source_wav, target_wav, output_path="output_vc.wav"):
        """语音转换"""
        logger.info("执行语音转换...")
        
        try:
            if not os.path.exists(source_wav):
                logger.error(f"源音频文件不存在: {source_wav}")
                return False
            
            if not os.path.exists(target_wav):
                logger.error(f"目标音频文件不存在: {target_wav}")
                return False
            
            # 使用FreeVC模型进行语音转换
            model_name = "voice_conversion_models/multilingual/vctk/freevc24"
            logger.info(f"加载语音转换模型: {model_name}")
            
            self.tts = TTS(model_name=model_name, progress_bar=True).to(self.device)
            
            # 执行语音转换
            logger.info(f"转换语音: {source_wav} -> {target_wav}")
            self.tts.voice_conversion_to_file(
                source_wav=source_wav,
                target_wav=target_wav,
                file_path=output_path
            )
            
            logger.info(f"转换后的语音已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"语音转换失败: {e}")
            return False
    
    def tts_with_voice_conversion(self, text, speaker_wav, output_path="output_tts_vc.wav"):
        """TTS + 语音转换（伪语音克隆）"""
        logger.info("执行TTS + 语音转换...")
        
        try:
            if not os.path.exists(speaker_wav):
                logger.error(f"参考音频文件不存在: {speaker_wav}")
                return False
            
            # 使用基础TTS模型
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            logger.info(f"加载TTS模型: {model_name}")
            
            self.tts = TTS(model_name=model_name, progress_bar=True).to(self.device)
            
            # 执行TTS + 语音转换
            logger.info(f"生成语音并转换为目标说话人: {speaker_wav}")
            self.tts.tts_with_vc_to_file(
                text=text,
                speaker_wav=speaker_wav,
                file_path=output_path
            )
            
            logger.info(f"语音已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"TTS + 语音转换失败: {e}")
            return False
    
    def chinese_tts_demo(self, text="你好，这是一个中文语音合成的演示。", output_path="output_chinese.wav"):
        """中文TTS演示"""
        logger.info("执行中文TTS演示...")
        
        try:
            # 尝试使用支持中文的模型
            # 注意：可能需要根据实际可用的模型调整
            model_candidates = [
                "tts_models/zh-CN/baker/tacotron2-DDC",
                "tts_models/multilingual/multi-dataset/your_tts",
                "tts_models/multilingual/multi-dataset/xtts_v2"
            ]
            
            for model_name in model_candidates:
                try:
                    logger.info(f"尝试加载中文模型: {model_name}")
                    self.tts = TTS(model_name=model_name, progress_bar=True).to(self.device)
                    
                    if "xtts" in model_name.lower():
                        # XTTS需要参考音频，这里跳过或使用默认处理
                        logger.warning("XTTS模型需要参考音频，跳过此模型")
                        continue
                    
                    # 生成中文语音
                    self.tts.tts_to_file(text=text, file_path=output_path)
                    logger.info(f"中文语音已保存到: {output_path}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"模型 {model_name} 加载失败: {e}")
                    continue
            
            logger.error("所有中文模型都加载失败")
            return False
            
        except Exception as e:
            logger.error(f"中文TTS失败: {e}")
            return False


def create_sample_audio():
    """创建示例音频文件（用于测试）"""
    sample_text = "This is a sample audio for testing voice cloning and conversion."
    output_path = "sample_reference.wav"
    
    try:
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        tts.tts_to_file(text=sample_text, file_path=output_path)
        logger.info(f"示例音频已创建: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"创建示例音频失败: {e}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Coqui TTS 演示脚本")
    parser.add_argument("--mode", type=str, default="basic", 
                       choices=["basic", "multilingual", "voice_conversion", "tts_vc", "chinese", "list_models"],
                       help="运行模式")
    parser.add_argument("--text", type=str, default="Hello, this is a test of text to speech synthesis.",
                       help="要转换的文本")
    parser.add_argument("--output", type=str, default="output.wav",
                       help="输出音频文件路径")
    parser.add_argument("--model", type=str, default=None,
                       help="指定TTS模型名称")
    parser.add_argument("--language", type=str, default="en",
                       help="语言代码（用于多语言模式）")
    parser.add_argument("--speaker_wav", type=str, default=None,
                       help="参考音频文件路径（用于语音克隆）")
    parser.add_argument("--source_wav", type=str, default=None,
                       help="源音频文件路径（用于语音转换）")
    parser.add_argument("--target_wav", type=str, default=None,
                       help="目标音频文件路径（用于语音转换）")
    parser.add_argument("--gpu", action="store_true",
                       help="使用GPU加速")
    parser.add_argument("--create_sample", action="store_true",
                       help="创建示例音频文件")
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化TTS演示
    demo = TTSDemo(gpu=args.gpu)
    
    # 创建示例音频（如果需要）
    if args.create_sample:
        create_sample_audio()
        return
    
    # 根据模式执行相应功能
    if args.mode == "list_models":
        demo.list_models()
        
    elif args.mode == "basic":
        success = demo.basic_tts(args.text, args.output, args.model)
        if success:
            print(f"\n✅ 基础TTS完成！输出文件: {args.output}")
        else:
            print("\n❌ 基础TTS失败！")
            
    elif args.mode == "multilingual":
        if not args.speaker_wav:
            logger.error("多语言模式需要提供 --speaker_wav 参数")
            return
        
        success = demo.multilingual_tts(args.text, args.language, args.output, args.speaker_wav)
        if success:
            print(f"\n✅ 多语言TTS完成！输出文件: {args.output}")
        else:
            print("\n❌ 多语言TTS失败！")
            
    elif args.mode == "voice_conversion":
        if not args.source_wav or not args.target_wav:
            logger.error("语音转换模式需要提供 --source_wav 和 --target_wav 参数")
            return
        
        success = demo.voice_conversion(args.source_wav, args.target_wav, args.output)
        if success:
            print(f"\n✅ 语音转换完成！输出文件: {args.output}")
        else:
            print("\n❌ 语音转换失败！")
            
    elif args.mode == "tts_vc":
        if not args.speaker_wav:
            logger.error("TTS+语音转换模式需要提供 --speaker_wav 参数")
            return
        
        success = demo.tts_with_voice_conversion(args.text, args.speaker_wav, args.output)
        if success:
            print(f"\n✅ TTS+语音转换完成！输出文件: {args.output}")
        else:
            print("\n❌ TTS+语音转换失败！")
            
    elif args.mode == "chinese":
        chinese_text = args.text if args.text != "Hello, this is a test of text to speech synthesis." else "你好，这是一个中文语音合成的演示。"
        success = demo.chinese_tts_demo(chinese_text, args.output)
        if success:
            print(f"\n✅ 中文TTS完成！输出文件: {args.output}")
        else:
            print("\n❌ 中文TTS失败！")


if __name__ == "__main__":
    print("Coqui TTS Demo Script")
    print("=" * 50)
    
    # 检查依赖
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA设备数量: {torch.cuda.device_count()}")
    except ImportError:
        print("警告: PyTorch未安装")
    
    print("=" * 50)
    
    main()
