
# IELTS 口语测试模拟器 / IELTS Speaking Test Simulator

一个基于 AI 的雅思口语考试模拟系统，提供完整的语音交互体验，包括问题生成、语音识别、文本转语音和评分功能。

An AI-powered IELTS speaking test simulation system with complete voice interaction, including question generation, speech recognition, text-to-speech, and scoring features.


## 🌟 主要特性 / Key Features

- **🎤 语音交互测试**：支持完整的语音输入输出，模拟真实考试场景
- **🤖 智能问题生成**：基于 LLM（大语言模型）生成符合雅思标准的问题
- **🗣️ 文本转语音**：使用先进的 TTS 技术朗读考官问题
- **📝 语音识别**：支持多种语音识别引擎（Google、Whisper 等）
- **🌐 Web 界面**：提供友好的浏览器界面进行测试
- **📊 自动评分**：对回答进行评分并生成详细报告
- **📋 完整测试流程**：涵盖雅思口语 Part 1、Part 2 和 Part 3

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Python 3.7 或更高版本
- Windows 操作系统（推荐）
- 麦克风（用于语音输入）
- 稳定的网络连接（用于 API 调用）

### 安装步骤 / Installation

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/aiwen717-bot/IELTS-Speaking-Simulator.git
   cd IELTS-Speaking-Simulator
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirement.txt
   pip install -r requirements_voice.txt
   ```
   
   使用批处理文件：
   ```bash
   install_voice_dependencies.bat
   ```

3. **配置 API 密钥**
   
   设置 Qwen API 密钥（用于问题生成）：
   ```bash
   set_qwen_key.bat
   ```
   
   按提示输入您的 Qwen API 密钥。

4. **测试环境**
   ```bash
   python test_environment.py
   ```

### 🎯 使用 Web 界面（推荐）

**这是最简单和推荐的使用方式！**

1. **启动 Web 服务器**
   ```bash
   cd web_interface
   run_server.bat
   ```
   
   或者：
   ```bash
   python web_interface/server.py
   ```

2. **打开浏览器**
   
   访问：`http://localhost:5000`

3. **开始测试**
   - 点击 "Begin Test" 开始测试
   - 点击 "Play Audio" 播放考官问题
   - 点击 "Start Recording" 开始录音
   - 点击 "Stop Recording" 停止录音
   - 系统会自动生成下一个问题


## 📁 项目结构 / Project Structure

```
IELTS-Speaking-Simulator/
├── web_interface/          # Web 界面（主要使用方式）
│   ├── server.py          # Flask 服务器
│   ├── index.html         # 前端界面
│   ├── run_server.bat     # 启动脚本
│   └── css/, js/, images/ # 前端资源
│
├── llm_module/            # 核心模块
│   ├── voice_to_questions.py    # 语音转问题核心逻辑
│   ├── speech_recorder.py       # 语音录制
│   ├── speech_to_text.py        # 语音识别
│   ├── question_generator.py    # 问题生成
│   ├── qwen_generator.py        # Qwen LLM 集成
│   ├── tts_integration.py       # 文本转语音
│   ├── text_processor.py        # 文本处理
│   └── config.py                # 配置管理
│
├── grade/                 # 评分模块
│   ├── report_runner.py   # 评分报告生成
│   └── pronunciation-trainer/  # 发音评估
│
├── output/                # 输出文件夹
├── voice_output/          # 语音输出文件夹
├── web_output/            # Web 界面输出
│
├── requirement.txt        # Python 依赖
├── requirements_voice.txt # 语音相关依赖
├── test_environment.py    # 环境测试脚本
│
└── 批处理脚本 / Batch Scripts
    ├── run_server.bat     # 启动 Web 服务器 ⭐ 推荐
    ├── run_voice_manual_4min.bat  # 4分钟语音录制
    ├── run_voice_with_whisper.bat # Whisper 语音识别
    ├── run_qwen_questions.bat     # Qwen 问题生成
    ├── set_qwen_key.bat          # 设置 API 密钥
    └── install_voice_dependencies.bat  # 安装依赖
```


### 语音识别引擎

支持多种语音识别引擎：

- **Google Speech Recognition**（默认）：免费，需要网络
- **Whisper**：离线运行，更准确，需要较高的计算资源
- 其他：Azure、IBM Watson 等（需要额外配置）

在 `llm_module/config.json` 中配置：
```json
{
    "stt_engine": "google",  // 或 "whisper"
    "stt_language": "en-US"
}
```

## 📊 输出文件 / Output Files

测试完成后，系统会生成以下文件：
  
- **web_output/** - Web 界面专用输出
  - 测试记录和音频文件
  - `ielts_speaking_report.txt` - 评分报告


## 🎓 IELTS 测试流程 / Test Flow

系统模拟完整的雅思口语测试流程：

1. **Introduction（介绍）**
   - 考官自我介绍
   - 确认考生身份

2. **Part 1（第一部分）** - 4-5 分钟
   - 日常话题问答
   - 个人信息、家庭、工作等

3. **Part 2（第二部分）** - 3-4 分钟
   - 话题卡描述
   - 1 分钟准备时间
   - 1-2 分钟陈述

4. **Part 3（第三部分）** - 4-5 分钟
   - 深度讨论
   - 与 Part 2 相关的抽象话题


## 📚 技术栈 / Tech Stack

- **后端框架**：Flask（Python Web 框架）
- **前端**：HTML5、CSS3、JavaScript
- **语音识别**：Google Speech API、OpenAI Whisper
- **文本转语音**：TTS-dev（自定义 TTS 引擎）
- **LLM**：Qwen（通义千问）
- **音频处理**：PyAudio、Librosa、SoundFile
- **机器学习**：PyTorch、Transformers

## 🤝 贡献 / Contributing

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证 / License

请参阅项目根目录下的 LICENSE 文件。

## 📧 联系方式 / Contact

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送 Pull Request

## 🔄 更新日志 / Changelog

### 最新版本
- ✅ 完整的 Web 界面
- ✅ 支持多种语音识别引擎
- ✅ 自动评分功能
- ✅ Qwen LLM 集成
- ✅ 完整的 IELTS 测试流程

---

## ⚡ 快速命令参考 / Quick Command Reference

| 功能 | 命令 |
|------|------|
| 启动 Web 界面（推荐） | `cd web_interface && run_server.bat` |
| 4分钟语音录制 | `run_voice_manual_4min.bat` |
| Whisper 语音识别 | `run_voice_with_whisper.bat` |
| 仅问题生成 | `run_qwen_questions.bat` |
| 设置 API 密钥 | `set_qwen_key.bat` |
| 安装依赖 | `install_voice_dependencies.bat` |
| 测试环境 | `python test_environment.py` |

---

**开始使用：最简单的方式是运行 `web_interface\run_server.bat` 然后在浏览器中访问 `http://localhost:5000`！**

**Get Started: The easiest way is to run `web_interface\run_server.bat` and visit `http://localhost:5000` in your browser!**

## Character Mode

环境配置，可以参考reference_environment.yaml以及characters_third_party/Musetalk中的Readme.md

运行:
```bash
cd characters_third_party/Musetalk
python ielts_app.py
```

# Citation
```bib
@article{musetalk,
  title={MuseTalk: Real-Time High-Fidelity Video Dubbing via Spatio-Temporal Sampling},
  author={Zhang, Yue and Zhong, Zhizhou and Liu, Minhao and Chen, Zhaokang and Wu, Bin and Zeng, Yubin and Zhan, Chao and He, Yingjie and Huang, Junxin and Zhou, Wenjiang},
  journal={arxiv},
  year={2025}
}

@misc{ielts-speaking-simulator,
  title     = {IELTS Speaking Simulator: A Multimodal Avatar-LLM-driven Framework for IELTS Speaking Assessment and Practice},
  author    = {Aiwen LU, Jingxuan Chen, Baiyu Huang, Yini Huang, Yantong Liu},
  year      = {2025},
  note      = {INFH5000, HKUST(GZ)}
}
```

