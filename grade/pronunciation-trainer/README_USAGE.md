# Pronunciation Trainer

## 安装依赖

在运行之前，请确保安装所有必需的依赖包：

```bash
pip install -r requirements.txt
```

如果遇到 torch 安装问题，可以单独安装：

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## 文件结构

```
ai-pronunciation-trainer-main/
├── run_scorer.py           # 主运行文件
├── pronunciationTrainer.py # 发音训练器核心模块（已修改，仅支持英语）
├── databases/
│   ├── test.txt           # 参考文本文件
│   └── test.wav           # 用户录音文件
└── output/
    └── output.json        # 输出结果文件（自动生成）
```

## 使用方法

### 方式一：使用测试文件运行

直接运行脚本，使用默认的测试文件：

```bash
python run_scorer.py
```

程序会自动：

- 读取 `databases/test.txt` 作为参考文本
- 读取 `databases/test.wav` 作为用户录音
- 将结果保存到 `output/output.json`

## 输出格式

`output/output.json` 包含以下字段：

```json
{
  "score": 85.5,
  "realtext": "hello world this is a test",
  "rectext": "hello world this is a test",
  "lambdascore": "11111 11111 1111 11 1 1111",
  "grade": [
    "excellent",
    "excellent",
    "good",
    "excellent",
    "excellent",
    "excellent"
  ]
}
```

### 字段说明

- **score**: 发音准确度分数（0-100），数值越高表示发音越准确
- **realtext**: 参考文本（原始文本）
- **rectext**: 语音识别到的文本
- **lambdascore**: 逐字母的正确性标记
  - `1` 表示该字母发音正确
  - `0` 表示该字母发音错误
  - 空格分隔不同单词
- **grade**: 每个单词的准确度等级列表
  - `"excellent"`: 优秀（≥80%）
  - `"good"`: 良好（60-79%）
  - `"needs_improvement"`: 需要改进（<60%）

## 评分标准

### 准确度计算方法

1. **音标转换**: 将文本和识别结果都转换为 IPA 音标
2. **编辑距离**: 计算音标之间的编辑距离（Levenshtein 距离）
3. **准确度公式**:
   ```
   准确度 = (总音标数 - 错误音标数) / 总音标数 × 100%
   ```

### 评分等级

| 准确度范围 | 等级              | 描述               |
| ---------- | ----------------- | ------------------ |
| ≥80%       | excellent         | 发音优秀，基本无误 |
| 60-79%     | good              | 发音良好，有小错误 |
| <60%       | needs_improvement | 需要改进           |

## 音频文件要求

- **格式**: WAV, OGG 或其他音频格式（推荐 WAV）
- **采样率**: 任意（程序会自动重采样到 16kHz）
- **声道**: 单声道或立体声（程序会自动转换为单声道）
- **时长**: 建议不超过 30 秒

## 参考文本要求

- **格式**: 纯文本文件（UTF-8 编码）
- **内容**: 英文句子或段落
- **标点**: 可以包含标点符号（评分时会忽略）

## 示例

### 示例 1：评估单个句子

1. 准备参考文本 `databases/test.txt`:

   ```
   Hello, this is a pronunciation test.
   ```

2. 准备录音文件 `databases/test.wav`（用户朗读上述句子）

3. 运行评分器:

   ```bash
   python run_scorer.py
   ```

4. 查看结果 `output/output.json`:
   ```json
   {
     "score": 92.3,
     "realtext": "hello this is a pronunciation test",
     "rectext": "hello this is a pronunciation test",
     "lambdascore": "11111 1111 11 1 111111111111 1111",
     "grade": [
       "excellent",
       "excellent",
       "excellent",
       "excellent",
       "excellent",
       "excellent"
     ]
   }
   ```

## 注意事项

1. 首次运行时，程序会下载 Whisper 模型，可能需要几分钟
2. 确保音频文件质量良好，背景噪音较少
3. 参考文本应与录音内容完全一致
4. 程序会自动创建 `output/` 目录（如果不存在）
