"""
测试环境配置脚本
验证所有依赖是否正确安装和配置
"""

import sys
import os

def test_imports():
    """测试所有关键包的导入"""
    print("=" * 60)
    print("测试Python包导入")
    print("=" * 60)
    
    tests = []
    
    # 测试基础包
    try:
        import torch
        print(f"✓ torch {torch.__version__}")
        print(f"  路径: {torch.__file__}")
        tests.append(("torch", True))
    except Exception as e:
        print(f"✗ torch 导入失败: {e}")
        tests.append(("torch", False))
    
    try:
        import torchaudio
        print(f"✓ torchaudio {torchaudio.__version__}")
        tests.append(("torchaudio", True))
    except Exception as e:
        print(f"✗ torchaudio 导入失败: {e}")
        tests.append(("torchaudio", False))
    
    try:
        import numpy
        print(f"✓ numpy {numpy.__version__}")
        print(f"  路径: {numpy.__file__}")
        tests.append(("numpy", True))
    except Exception as e:
        print(f"✗ numpy 导入失败: {e}")
        tests.append(("numpy", False))
    
    try:
        import transformers
        print(f"✓ transformers {transformers.__version__}")
        print(f"  路径: {transformers.__file__}")
        tests.append(("transformers", True))
    except Exception as e:
        print(f"✗ transformers 导入失败: {e}")
        tests.append(("transformers", False))
    
    try:
        from transformers import pipeline
        print(f"✓ transformers.pipeline 导入成功")
        tests.append(("pipeline", True))
    except Exception as e:
        print(f"✗ transformers.pipeline 导入失败: {e}")
        tests.append(("pipeline", False))
    
    try:
        import flask
        print(f"✓ flask {flask.__version__}")
        tests.append(("flask", True))
    except Exception as e:
        print(f"✗ flask 导入失败: {e}")
        tests.append(("flask", False))
    
    try:
        import pyaudio
        print(f"✓ pyaudio")
        tests.append(("pyaudio", True))
    except Exception as e:
        print(f"✗ pyaudio 导入失败: {e}")
        tests.append(("pyaudio", False))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！环境配置正确。")
        return True
    else:
        print("✗ 部分测试失败，请检查上述错误信息。")
        return False

def test_whisper():
    """测试Whisper模型加载"""
    print("\n" + "=" * 60)
    print("测试Whisper模型")
    print("=" * 60)
    
    try:
        from transformers import pipeline
        print("正在加载Whisper模型（可能需要几秒钟）...")
        asr = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        print("✓ Whisper模型加载成功")
        return True
    except Exception as e:
        print(f"✗ Whisper模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment():
    """检查环境变量"""
    print("\n" + "=" * 60)
    print("环境信息")
    print("=" * 60)
    
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    pythonnousersite = os.environ.get("PYTHONNOUSERSITE", "未设置")
    print(f"PYTHONNOUSERSITE: {pythonnousersite}")
    
    if pythonnousersite == "1":
        print("✓ 已禁用用户site-packages，使用conda环境")
    else:
        print("⚠ 建议设置 PYTHONNOUSERSITE=1 以避免全局包干扰")
    
    print(f"\nPython搜索路径:")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"  {i}. {path}")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("IELTS Speaking Test 环境测试")
    print("=" * 60)
    
    check_environment()
    imports_ok = test_imports()
    
    if imports_ok:
        whisper_ok = test_whisper()
        
        if whisper_ok:
            print("\n" + "=" * 60)
            print("✓ 所有测试通过！可以启动服务器了。")
            print("=" * 60)
            print("\n运行以下命令启动服务器:")
            print("  cd web_interface")
            print("  start_server.bat")
        else:
            print("\n" + "=" * 60)
            print("✗ Whisper测试失败")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 导入测试失败，请先修复依赖问题")
        print("=" * 60)

if __name__ == "__main__":
    main()

