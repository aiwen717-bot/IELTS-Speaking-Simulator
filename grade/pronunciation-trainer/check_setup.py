"""
测试脚本 - 检查项目是否配置正确
用于在安装依赖前验证文件结构
"""

import os
import json

def check_files():
    """检查必需的文件是否存在"""
    print("=" * 60)
    print("项目文件结构检查")
    print("=" * 60)
    
    files_to_check = {
        "参考文本": "databases/test.txt",
        "测试音频": "databases/test.wav",
        "主程序": "run_scorer.py",
        "核心模块": "pronunciationTrainer.py",
        "单词匹配": "WordMatching.py",
        "单词指标": "WordMetrics.py",
    }
    
    all_exist = True
    for name, path in files_to_check.items():
        exists = os.path.exists(path)
        status = "✓ 存在" if exists else "✗ 缺失"
        print(f"{name:12} [{path:40}] {status}")
        if not exists:
            all_exist = False
    
    # 检查输出目录
    output_dir = "output"
    if os.path.exists(output_dir):
        print(f"{'输出目录':12} [{output_dir:40}] ✓ 存在")
    else:
        print(f"{'输出目录':12} [{output_dir:40}] ! 将自动创建")
    
    print("=" * 60)
    
    if all_exist:
        print("✓ 所有必需文件都存在！")
    else:
        print("✗ 有文件缺失，请检查项目完整性")
    
    print("=" * 60)
    return all_exist


def check_reference_text():
    """显示参考文本内容"""
    text_file = "databases/test.txt"
    if os.path.exists(text_file):
        print("\n" + "=" * 60)
        print("参考文本内容:")
        print("=" * 60)
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("=" * 60)
        print(f"文本长度: {len(content)} 字符")
        print(f"单词数量: {len(content.split())} 个")
        print("=" * 60)
    else:
        print(f"\n! 找不到文件: {text_file}")


def show_expected_output():
    """显示预期的输出格式"""
    print("\n" + "=" * 60)
    print("预期输出格式 (output/output.json):")
    print("=" * 60)
    
    example_output = {
        "score": 85.5,
        "realtext": "hello world this is a test",
        "rectext": "hello world this is a test",
        "lambdascore": "11111 11111 1111 11 1 1111",
        "grade": ["excellent", "excellent", "good", "excellent", "excellent", "excellent"]
    }
    
    print(json.dumps(example_output, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    print("\n字段说明:")
    print("  • score: 发音准确度分数 (0-100)")
    print("  • realtext: 参考文本")
    print("  • rectext: 识别到的文本")
    print("  • lambdascore: 字母级别的正确性标记 (1=正确, 0=错误)")
    print("  • grade: 单词级别的评分等级")
    print("    - excellent: 优秀 (≥80%)")
    print("    - good: 良好 (60-79%)")
    print("    - needs_improvement: 需改进 (<60%)")
    print("=" * 60)


def check_dependencies():
    """检查Python依赖是否已安装"""
    print("\n" + "=" * 60)
    print("依赖包检查:")
    print("=" * 60)
    
    required_packages = [
        'torch',
        'torchaudio',
        'numpy',
        'transformers',
        'eng_to_ipa',
        'audioread'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package:20} 已安装")
        except ImportError:
            print(f"  ✗ {package:20} 未安装")
            missing_packages.append(package)
    
    print("=" * 60)
    
    if missing_packages:
        print("\n需要安装缺失的依赖:")
        print("  pip install -r requirements.txt")
        print("\n或单独安装:")
        print(f"  pip install {' '.join(missing_packages)}")
    else:
        print("\n✓ 所有依赖都已安装，可以运行程序！")
        print("\n运行命令:")
        print("  python run_scorer.py")
    
    print("=" * 60)
    
    return len(missing_packages) == 0


def main():
    """主函数"""
    print("\n🎤 AI 发音评分器 - 配置检查\n")
    
    # 检查文件
    files_ok = check_files()
    
    # 显示参考文本
    if files_ok:
        check_reference_text()
    
    # 显示预期输出
    show_expected_output()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 最终总结
    print("\n" + "=" * 60)
    print("总结:")
    print("=" * 60)
    if files_ok and deps_ok:
        print("✓ 项目配置完整，可以开始使用！")
        print("\n下一步:")
        print("  1. 确保 databases/test.wav 是你要评估的录音")
        print("  2. 运行: python run_scorer.py")
        print("  3. 查看结果: output/output.json")
    elif files_ok and not deps_ok:
        print("! 文件完整，但需要安装依赖")
        print("\n下一步:")
        print("  1. 安装依赖: pip install -r requirements.txt")
        print("  2. 运行: python run_scorer.py")
    else:
        print("✗ 项目配置不完整，请检查缺失的文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
