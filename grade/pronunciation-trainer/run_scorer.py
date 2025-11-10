"""
AI Pronunciation Scorer - Standalone Version
用于评估英语发音准确度的独立运行程序
"""

import torch
import json
import os
import time
import numpy as np
from torchaudio.transforms import Resample
import torchaudio
import pronunciationTrainer
import WordMatching as wm

# 设置路径
DATABASE_DIR = "databases"
OUTPUT_DIR = "output"
TEST_TEXT_FILE = os.path.join(DATABASE_DIR, "test.txt")
TEST_AUDIO_FILE = os.path.join(DATABASE_DIR, "test.wav")
OUTPUT_JSON_FILE = os.path.join(OUTPUT_DIR, "output.json")

# Web模块输出路径
WEB_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web_output")
WEB_TEXT_FILE = os.path.join(WEB_OUTPUT_DIR, "part23_answers.txt")
WEB_AUDIO_FILE = os.path.join(WEB_OUTPUT_DIR, "part23_answers.wav")
WEB_OUTPUT_JSON_FILE = os.path.join(WEB_OUTPUT_DIR, "pronunciation_score.json")


def load_reference_text(text_file_path):
    """
    加载参考文本
    
    Args:
        text_file_path: 文本文件路径
        
    Returns:
        str: 参考文本内容
    """
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    return text


def load_audio(audio_file_path, target_sample_rate=16000):
    """
    加载音频文件并重采样到目标采样率
    
    Args:
        audio_file_path: 音频文件路径
        target_sample_rate: 目标采样率
        
    Returns:
        torch.Tensor: 音频张量
    """
    # 加载音频文件 - 使用 soundfile backend 避免 torchcodec 依赖
    try:
        signal, original_sample_rate = torchaudio.load(audio_file_path, backend="soundfile")
    except Exception as e:
        # 如果 soundfile 失败，尝试使用 sox_io backend
        try:
            signal, original_sample_rate = torchaudio.load(audio_file_path, backend="sox_io")
        except Exception:
            # 最后尝试不指定 backend（使用默认）
            import soundfile as sf
            data, original_sample_rate = sf.read(audio_file_path)
            signal = torch.from_numpy(data).float()
            if len(signal.shape) == 1:
                signal = signal.unsqueeze(0)
            else:
                signal = signal.T
    
    # 如果是多声道，转换为单声道
    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)
    
    # 重采样到目标采样率
    if original_sample_rate != target_sample_rate:
        resampler = Resample(orig_freq=original_sample_rate, new_freq=target_sample_rate)
        signal = resampler(signal)
    
    return signal


def calculate_letter_correctness(real_text, matched_text):
    """
    计算每个字母的正确性标记
    
    Args:
        real_text: 真实文本
        matched_text: 匹配的文本
        
    Returns:
        str: 正确性标记字符串 (例如: "11010 11101")
    """
    words_real = real_text.lower().split()
    mapped_words = matched_text.split()
    
    is_letter_correct_all_words = ''
    for idx, word_real in enumerate(words_real):
        if idx >= len(mapped_words):
            # 如果识别的单词不够，标记为全错
            is_letter_correct_all_words += '0' * len(word_real) + ' '
        else:
            mapped_letters, mapped_letters_indices = wm.get_best_mapped_words(
                mapped_words[idx], word_real)
            
            is_letter_correct = wm.getWhichLettersWereTranscribedCorrectly(
                word_real, mapped_letters)
            
            is_letter_correct_all_words += ''.join([str(is_correct)
                                                    for is_correct in is_letter_correct]) + ' '
    
    return is_letter_correct_all_words.strip()


def get_grade_from_categories(categories):
    """
    将类别转换为等级描述
    
    Args:
        categories: 类别列表 [0, 1, 2]
        
    Returns:
        list: 等级描述列表 ["excellent", "good", "needs_improvement"]
    """
    grade_map = {
        0: "excellent",      # ≥80%
        1: "good",          # 60-79%
        2: "needs_improvement"  # <60%
    }
    return [grade_map[cat] for cat in categories]


def run_pronunciation_scorer(reference_text, audio_file_path, output_json_path, language='en'):
    """
    运行发音评分器
    
    Args:
        reference_text: 参考文本
        audio_file_path: 音频文件路径
        output_json_path: 输出JSON文件路径
        language: 语言代码 (默认: 'en')
        
    Returns:
        dict: 评分结果
    """
    print("=" * 60)
    print("AI Pronunciation Scorer")
    print("=" * 60)
    print(f"\n参考文本: {reference_text}")
    print(f"音频文件: {audio_file_path}")
    print(f"输出文件: {output_json_path}\n")
    
    # 初始化训练器
    print("正在初始化模型...")
    start_time = time.time()
    trainer = pronunciationTrainer.getTrainer(language)
    print(f"模型初始化完成 (耗时: {time.time() - start_time:.2f}秒)\n")
    
    # 加载音频
    print("正在加载音频文件...")
    start_time = time.time()
    audio_signal = load_audio(audio_file_path)
    print(f"音频加载完成 (耗时: {time.time() - start_time:.2f}秒)")
    print(f"音频形状: {audio_signal.shape}, 采样率: 16000Hz\n")
    
    # 处理音频并评分
    print("正在进行语音识别和发音评估...")
    start_time = time.time()
    result = trainer.processAudioForGivenText(audio_signal, reference_text)
    print(f"评估完成 (耗时: {time.time() - start_time:.2f}秒)\n")
    
    # 提取结果
    real_transcripts = ' '.join([word[0] for word in result['real_and_transcribed_words']])
    matched_transcripts = ' '.join([word[1] for word in result['real_and_transcribed_words']])
    
    # 计算字母级别的正确性标记
    letter_correctness = calculate_letter_correctness(real_transcripts, matched_transcripts)
    
    # 获取等级描述
    grades = get_grade_from_categories(result['pronunciation_categories'])
    
    # 构建输出结果
    output_result = {
        "score": float(result['pronunciation_accuracy']),
        "realtext": real_transcripts,
        "rectext": matched_transcripts,
        "lambdascore": letter_correctness,
        "grade": grades
    }
    
    # 保存到JSON文件
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_result, f, ensure_ascii=False, indent=2)
    
    # 打印结果
    print("=" * 60)
    print("评估结果:")
    print("=" * 60)
    print(f"发音准确度分数: {output_result['score']:.1f}%")
    print(f"\n参考文本: {output_result['realtext']}")
    print(f"识别文本: {output_result['rectext']}")
    print(f"\n正确性标记: {output_result['lambdascore']}")
    print(f"单词等级: {output_result['grade']}")
    print(f"\n结果已保存到: {output_json_path}")
    print("=" * 60)
    
    return output_result


def main():
    """
    主函数
    """
    try:
        # 检查是否存在Web模块输出的文件
        if os.path.exists(WEB_TEXT_FILE) and os.path.exists(WEB_AUDIO_FILE):
            print(f"检测到Web模块输出文件，使用Web模块路径")
            # 加载参考文本
            reference_text = load_reference_text(WEB_TEXT_FILE)
            
            # 运行评分器
            result = run_pronunciation_scorer(
                reference_text=reference_text,
                audio_file_path=WEB_AUDIO_FILE,
                output_json_path=WEB_OUTPUT_JSON_FILE,
                language='en'
            )
            return
            
        # 如果没有Web模块输出文件，则使用默认测试文件
        print(f"未检测到Web模块输出文件，使用默认测试文件路径")
        
        # 检查文件是否存在
        if not os.path.exists(TEST_TEXT_FILE):
            print(f"错误: 找不到参考文本文件 {TEST_TEXT_FILE}")
            return
        
        if not os.path.exists(TEST_AUDIO_FILE):
            print(f"错误: 找不到音频文件 {TEST_AUDIO_FILE}")
            return
        
        # 加载参考文本
        reference_text = load_reference_text(TEST_TEXT_FILE)
        
        # 运行评分器
        result = run_pronunciation_scorer(
            reference_text=reference_text,
            audio_file_path=TEST_AUDIO_FILE,
            output_json_path=OUTPUT_JSON_FILE,
            language='en'
        )
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置环境变量，避免OpenMP重复加载问题
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    main()
