#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TTS安装和基本功能的脚本
"""

import sys
import importlib


def test_python_version():
    """测试Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 9) and version < (3, 12):
        print("✅ Python版本符合要求 (3.9-3.11)")
        return True
    else:
        print("❌ Python版本不符合要求，需要3.9-3.11")
        return False


def test_import(module_name, description):
    """测试模块导入"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description} - 已安装")
        return True
    except ImportError:
        print(f"❌ {description} - 未安装")
        return False


def test_torch_cuda():
    """测试PyTorch和CUDA"""
    try:
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA可用，设备数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   设备 {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("ℹ️  CUDA不可用，将使用CPU")
        
        return True
    except ImportError:
        print("❌ PyTorch未安装")
        return False


def test_tts_basic():
    """测试TTS基本功能"""
    print("\n🧪 测试TTS基本功能...")
    try:
        from TTS.api import TTS
        
        # 尝试初始化TTS（不下载模型）
        print("✅ TTS API导入成功")
        
        # 尝试列出模型
        try:
            tts_temp = TTS()
            models = tts_temp.list_models()
            if models:
                print("✅ 模型列表获取成功")
                # 显示一些模型示例
                tts_models = models.get('tts_models', [])
                if tts_models:
                    print(f"   发现 {len(tts_models)} 个TTS模型")
                    print("   示例模型:")
                    for i, model in enumerate(tts_models[:3]):
                        print(f"     {i+1}. {model}")
            else:
                print("⚠️  无法获取模型列表")
        except Exception as e:
            print(f"⚠️  获取模型列表时出错: {e}")
        
        return True
        
    except ImportError:
        print("❌ TTS库未安装")
        return False
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🐸 Coqui TTS 安装测试")
    print("=" * 50)
    
    tests = [
        ("Python版本", test_python_version),
        ("PyTorch", lambda: test_import("torch", "PyTorch")),
        ("TorchAudio", lambda: test_import("torchaudio", "TorchAudio")),
        ("NumPy", lambda: test_import("numpy", "NumPy")),
        ("SciPy", lambda: test_import("scipy", "SciPy")),
        ("Librosa", lambda: test_import("librosa", "Librosa")),
        ("SoundFile", lambda: test_import("soundfile", "SoundFile")),
        ("TTS", lambda: test_import("TTS", "Coqui TTS")),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 {test_name} 时出错: {e}")
            results.append((test_name, False))
    
    # 如果基础库都安装了，测试CUDA和TTS功能
    if all(result for _, result in results):
        print(f"\n📋 测试: PyTorch CUDA支持")
        test_torch_cuda()
        
        print(f"\n📋 测试: TTS基本功能")
        test_tts_basic()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！TTS环境准备就绪。")
        print("\n接下来您可以:")
        print("   python simple_tts.py           # 运行简单演示")
        print("   python tts_demo.py --help      # 查看完整选项")
        print("   python install_and_run.py      # 自动安装和演示")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查安装。")
        print("\n建议运行以下命令安装缺失的依赖:")
        print("   pip install TTS")
        print("   pip install torch torchaudio")
    
    return passed == total


if __name__ == "__main__":
    main()
