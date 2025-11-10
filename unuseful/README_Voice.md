# 语音驱动的IELTS问题生成器

这个模块扩展了原有的IELTS问题生成功能，增加了语音输入支持。用户现在可以通过语音输入来生成问题，实现完整的语音到语音的处理流程。

## 功能特性

### 🎤 语音录制
- 从麦克风录制用户语音
- 自动静音检测和停止录音
- 支持手动控制录音时长
- 多种音频设备支持

### 🔤 语音转文本
- 支持多种语音识别引擎：
  - Google Speech Recognition（在线，免费）
  - OpenAI Whisper（离线，高精度）
  - Microsoft Azure Speech
  - IBM Watson Speech to Text
  - Wit.ai
  - CMU Sphinx（离线）
- 多语言支持
- 可配置的识别参数

### 📝 问题生成
- 基于语音转换的文本生成IELTS Part 3风格问题
- 集成现有的LLM问题生成功能
- 支持自定义问题数量

### 🔊 文本转语音
- 将生成的问题转换为语音输出
- 支持多种语音选择
- 可生成单独或合并的音频文件

## 安装和设置

### 1. 安装依赖项

运行安装脚本：
```bash
install_voice_dependencies.bat
```

或手动安装：
```bash
pip install -r requirements_voice.txt
```

### 2. 可选：安装Whisper（推荐）

Whisper提供离线、高精度的语音识别：
```bash
pip install openai-whisper
```

### 3. 测试系统

运行系统测试：
```bash
test_voice_system.bat
```

或使用Python：
```bash
python voice_ielts_questions.py --test-system
```

## 使用方法

### 基本语音输入模式

最简单的使用方式：
```bash
run_voice_questions.bat
```

或使用Python：
```bash
python voice_ielts_questions.py --voice-input
```

### 使用Whisper引擎（推荐）

```bash
run_voice_with_whisper.bat
```

或：
```bash
python voice_ielts_questions.py --voice-input --stt-engine whisper
```

### 处理现有音频文件

```bash
python voice_ielts_questions.py --audio-file your_recording.wav
```

### 高级选项

```bash
# 指定录音时长（秒）
python voice_ielts_questions.py --voice-input --duration 60

# 生成特定数量的问题
python voice_ielts_questions.py --voice-input --num_questions 3

# 使用特定语音识别引擎
python voice_ielts_questions.py --voice-input --stt-engine google --stt-language zh-CN

# 自定义输出目录
python voice_ielts_questions.py --voice-input --output_dir ./my_output

# 不生成音频文件（仅文本）
python voice_ielts_questions.py --voice-input --no-audio
```

## 命令行参数详解

### 输入模式
- `--voice-input`: 从麦克风录制语音输入
- `--audio-file PATH`: 处理现有音频文件
- `--test-system`: 测试所有系统组件

### 录音设置
- `--duration SECONDS`: 录音时长（默认：自动停止）
- `--device-index INDEX`: 指定音频设备索引

### 语音识别设置
- `--stt-engine ENGINE`: 语音识别引擎（google, whisper, sphinx等）
- `--stt-language LANG`: 识别语言（如en-US, zh-CN）
- `--stt-api-key KEY`: API密钥（某些引擎需要）

### 问题生成设置
- `--config PATH`: 配置文件路径
- `--num_questions N`: 生成问题数量（默认：5）

### 输出设置
- `--output_dir DIR`: 输出目录（默认：./voice_output）
- `--no-audio`: 不生成问题音频文件
- `--no-transcript`: 不保存转录文本
- `--voice VOICE`: TTS语音选择

### 实用工具
- `--list-devices`: 列出可用音频设备
- `--list-engines`: 列出可用语音识别引擎
- `--verbose`: 详细日志输出

## 配置文件

可以创建JSON配置文件来保存常用设置：

```json
{
    "speech_recognition": {
        "engine": "whisper",
        "language": "en-US",
        "timeout": 10.0,
        "phrase_timeout": 5.0
    },
    "speech_recording": {
        "sample_rate": 16000,
        "channels": 1,
        "auto_stop_on_silence": true,
        "silence_duration": 2.0,
        "max_duration": 300
    },
    "num_questions": 5,
    "tts_integration": {
        "enabled": true,
        "voice": "en-US-Neural2-F"
    }
}
```

使用配置文件：
```bash
python voice_ielts_questions.py --voice-input --config my_config.json
```

## 处理流程

1. **语音录制**: 系统从麦克风录制用户语音
2. **语音转文本**: 使用选定的引擎将语音转换为文本
3. **问题生成**: 基于转录文本生成IELTS问题
4. **文本转语音**: 将问题转换为音频文件（可选）
5. **文件保存**: 保存所有输出文件到指定目录

## 输出文件

系统会在输出目录中生成以下文件：

- `voice_transcript.txt` 或 `audio_transcript.txt`: 语音转录文本
- `voice_generated_questions.txt` 或 `audio_generated_questions.txt`: 生成的问题
- `question_1.wav`, `question_2.wav`, ...: 各问题的音频文件
- `combined_questions.wav`: 合并的音频文件（如果启用）

## 故障排除

### PyAudio安装问题

如果PyAudio安装失败，尝试以下方法：

1. 使用conda：
   ```bash
   conda install pyaudio
   ```

2. 使用pipwin：
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

3. 从官方网站下载预编译的wheel文件

### 麦克风权限问题

确保应用程序有访问麦克风的权限：
- Windows: 检查隐私设置 > 麦克风
- 确保麦克风未被其他应用程序占用

### 语音识别精度问题

1. 使用Whisper引擎获得更好的离线识别效果
2. 确保录音环境安静
3. 说话清晰，语速适中
4. 调整麦克风音量和位置

### 网络连接问题

- Google Speech Recognition需要网络连接
- 使用Whisper或Sphinx进行离线识别
- 检查防火墙设置

## 支持的语音识别引擎

| 引擎 | 类型 | 精度 | 需要网络 | 需要API密钥 |
|------|------|------|----------|-------------|
| Google | 在线 | 高 | 是 | 否 |
| Whisper | 离线 | 很高 | 否 | 否 |
| Azure | 在线 | 高 | 是 | 是 |
| IBM Watson | 在线 | 高 | 是 | 是 |
| Wit.ai | 在线 | 中 | 是 | 是 |
| Sphinx | 离线 | 中 | 否 | 否 |

## 环境变量

可以通过环境变量设置默认值：

```bash
set STT_ENGINE=whisper
set STT_LANGUAGE=en-US
set STT_API_KEY=your_api_key_here
```

## 示例使用场景

### 场景1：快速语音输入
```bash
# 说话30秒，生成3个问题，使用Whisper
python voice_ielts_questions.py --voice-input --duration 30 --num_questions 3 --stt-engine whisper
```

### 场景2：处理录音文件
```bash
# 处理已有的录音文件
python voice_ielts_questions.py --audio-file interview.wav --num_questions 5
```

### 场景3：仅生成文本
```bash
# 不生成音频文件，仅生成问题文本
python voice_ielts_questions.py --voice-input --no-audio
```

## 技术架构

```
用户语音输入
    ↓
语音录制模块 (speech_recorder.py)
    ↓
语音转文本模块 (speech_to_text.py)
    ↓
问题生成模块 (question_generator.py)
    ↓
文本转语音模块 (tts_integration.py)
    ↓
输出文件
```

## 贡献和反馈

如果您遇到问题或有改进建议，请：
1. 运行系统测试确定问题所在
2. 检查日志输出获取详细错误信息
3. 提供系统信息和错误复现步骤

## 许可证

本项目遵循与主项目相同的许可证。
