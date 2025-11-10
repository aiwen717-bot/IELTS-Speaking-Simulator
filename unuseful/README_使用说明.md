# IELTS问题生成器使用说明

本项目在TTS-dev系统基础上添加了一个新模块，该模块使用大型语言模型(LLM)根据输入的英语文本生成雅思口语Part 3风格的问题。

## 功能特点

- 从用户输入或文件中读取英语文本
- 使用语言模型生成雅思Part 3风格的问题
- 使用TTS系统将生成的问题转换为语音
- 可配置问题数量和其他参数
- 批处理功能，可选择生成合并的音频输出

## 系统要求

- Python 3.7+
- OpenAI API密钥（用于使用GPT模型）
- TTS-dev系统（用于语音合成）

## 安装方法

1. 确保已安装TTS-dev系统
2. 将OpenAI API密钥设置为环境变量：
   ```
   set OPENAI_API_KEY=你的API密钥
   ```
   或创建配置文件（参见配置部分）

## 使用方法

### 使用批处理文件

1. 运行`run_ielts_questions.bat`从文本输入生成问题
2. 运行`run_ielts_questions_tts.bat`生成问题并将其转换为语音
3. 运行`run_ielts_file_example.bat`使用示例文件生成问题

### 使用命令行

```
# 从文本生成问题
python generate_ielts_questions.py --text "你的英语文本" --num_questions 5

# 从文件生成问题
python generate_ielts_questions.py --file input.txt --num_questions 5

# 生成问题并转换为语音
python generate_ielts_questions.py --text "你的英语文本" --tts --output_dir ./output

# 生成问题并创建合并的音频文件
python generate_ielts_questions.py --text "你的英语文本" --tts --combined
```

## 配置说明

您可以创建配置文件来设置默认参数：

```json
{
    "api_key": "你的API密钥",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "num_questions": 5,
    "tts_integration": {
        "enabled": true,
        "voice": "en-US-Neural2-F"
    }
}
```

然后使用以下命令：

```
python generate_ielts_questions.py --text "你的文本" --config 你的配置文件.json
```

## 模块结构

- `llm_module/`: 主模块目录
  - `__init__.py`: 模块初始化
  - `text_processor.py`: 文本读取和预处理
  - `llm_generator.py`: LLM API集成
  - `question_generator.py`: 雅思问题生成
  - `tts_integration.py`: 与TTS系统集成
  - `config.py`: 配置管理
  - `default_config.json`: 默认配置

## 示例

输入文本：
```
Technology has transformed education in recent years. Students now have access to online resources, virtual classrooms, and digital tools that enhance learning experiences.
```

生成的问题：
1. 技术如何改变了学生与教师在教育环境中的互动方式？
2. 在教育中过度依赖技术可能带来哪些潜在的缺点？
3. 你认为传统的教学方法最终会被基于技术的方法所取代吗？为什么？
4. 数字鸿沟如何影响世界不同地区获得平等教育的机会？
5. 政府在监管教育机构的技术使用方面应该扮演什么角色？