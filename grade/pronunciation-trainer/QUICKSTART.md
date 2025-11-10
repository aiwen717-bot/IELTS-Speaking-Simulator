# 快速开始指南

## ✅ 项目修改完成！

### 已完成的修改

1. ✅ **移除Web界面** - 不再需要 Flask 和浏览器
2. ✅ **移除德语支持** - 只保留英语评分功能
3. ✅ **创建独立运行文件** - `run_scorer.py`
4. ✅ **输出格式规范** - `output/output.json` 包含所需的所有字段
5. ✅ **音频加载修复** - 兼容最新版本的 torchaudio

---

## 🚀 如何使用

### 一键运行
```bash
python run_scorer.py
```

### 输入文件
- **参考文本**: `databases/test.txt`
- **用户录音**: `databases/test.wav`

### 输出文件
- **评分结果**: `output/output.json`

---

## 📄 输出格式

```json
{
  "score": 83.0,                    // 发音准确度分数 (0-100)
  "realtext": "原始文本...",         // 参考文本
  "rectext": "识别文本...",          // ASR识别结果
  "lambdascore": "11010 1101...",   // 字母正确性 (1=对, 0=错)
  "grade": ["excellent", ...]       // 单词评分等级
}
```

### 评分等级
- **excellent**: 优秀 (≥80%)
- **good**: 良好 (60-79%)
- **needs_improvement**: 需改进 (<60%)

---

## 📊 测试结果

使用 `databases/test.txt` 和 `databases/test.wav` 运行成功：

```
============================================================
评估结果:
============================================================
发音准确度分数: 83.0%

参考文本: Um well that is a it's a difficult question...
识别文本: Well, - that is - - a difficult question...

正确性标记: 00 0000 1111 11 0 0010 1 111111111...
单词等级: ['needs_improvement', 'needs_improvement', 'excellent'...]

结果已保存到: output/output.json
============================================================
```

---

## 🔧 自定义使用

### 方法1: 修改默认文件路径

编辑 `run_scorer.py` 中的路径变量：

```python
TEST_TEXT_FILE = os.path.join(DATABASE_DIR, "your_text.txt")
TEST_AUDIO_FILE = os.path.join(DATABASE_DIR, "your_audio.wav")
OUTPUT_JSON_FILE = os.path.join(OUTPUT_DIR, "your_output.json")
```

### 方法2: 直接调用函数

```python
from run_scorer import run_pronunciation_scorer

result = run_pronunciation_scorer(
    reference_text="Your custom text",
    audio_file_path="path/to/audio.wav",
    output_json_path="path/to/output.json",
    language='en'
)

print(f"Score: {result['score']}%")
```

---

## 📁 项目结构

```
ai-pronunciation-trainer-main/
├── run_scorer.py              ⭐ 主运行文件
├── check_setup.py             🔍 配置检查工具
├── pronunciationTrainer.py    🛠️ 核心模块（已修改）
├── databases/
│   ├── test.txt              📝 参考文本
│   └── test.wav              🎤 测试音频
└── output/
    ├── output.json           📊 评分结果
    └── output_example.json   📄 示例输出
```

---

## ⚙️ 技术细节

### 评分算法
1. **语音识别**: Whisper ASR 模型
2. **音标转换**: 文本 → IPA 音标
3. **单词匹配**: 动态规划算法
4. **准确度计算**: 基于编辑距离

### 准确度公式
```
准确度 = (总音标数 - 错误音标数) / 总音标数 × 100%
```

### 音频要求
- 格式: WAV, OGG 等
- 采样率: 任意（自动重采样到 16kHz）
- 声道: 单/多声道（自动转换）

---

## 🐛 已修复的问题

### 问题: torchcodec 模块缺失
**错误**: `ModuleNotFoundError: No module named 'torchcodec'`

**解决方案**: 修改 `load_audio()` 函数，使用 soundfile backend：
```python
signal, sr = torchaudio.load(audio_file_path, backend="soundfile")
```

---

## 📚 相关文档

- **详细使用说明**: `README_USAGE.md`
- **修改总结**: `MODIFICATION_SUMMARY.md`
- **配置检查**: `python check_setup.py`

---

## ✨ 特性

- ✅ 无需Web界面，命令行直接运行
- ✅ 自动化评分流程
- ✅ 详细的字母级别反馈
- ✅ JSON格式输出，易于集成
- ✅ 支持自定义文本和音频
- ✅ 兼容最新版本依赖

---

## 🎯 下一步

### 基础使用
1. 准备你的参考文本和录音文件
2. 放在 `databases/` 目录
3. 运行 `python run_scorer.py`
4. 查看 `output/output.json` 结果

### 高级集成
```python
# 在你的项目中导入使用
from run_scorer import run_pronunciation_scorer

# 批量处理
texts = ["text1", "text2", "text3"]
audios = ["audio1.wav", "audio2.wav", "audio3.wav"]

for text, audio in zip(texts, audios):
    result = run_pronunciation_scorer(text, audio, f"output_{i}.json")
    print(f"Score: {result['score']}%")
```

---

## 💡 提示

- 首次运行会下载 Whisper 模型（约5-10分钟）
- 确保音频质量良好，背景噪音少
- 参考文本应与录音内容一致
- 输出目录会自动创建

---

**版本**: 2.0 (命令行版)  
**最后更新**: 2025-11-06  
**状态**: ✅ 已测试通过
