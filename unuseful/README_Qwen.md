# 使用通义千问(Qwen)模型生成雅思问题

本项目使用阿里云通义千问(Qwen)大语言模型来生成雅思口语Part 3风格的问题，并可选择使用TTS系统将问题转换为语音。

## 功能特点

- 使用通义千问API代替OpenAI API
- 从用户输入或文件中读取英语文本
- 生成雅思Part 3风格的问题
- 可选择使用TTS系统将问题转换为语音
- 可配置问题数量和其他参数

## 系统要求

- Python 3.7+
- 阿里云通义千问API密钥
- 可选：TTS系统（用于语音合成）

## 设置步骤

1. 运行`set_qwen_key.bat`设置您的通义千问API密钥
   ```
   set_qwen_key.bat
   ```

2. 按照提示输入您的API密钥（从阿里云DashScope服务获取）

3. 运行`run_with_qwen.bat`生成雅思问题
   ```
   run_with_qwen.bat
   ```

## 获取通义千问API密钥

1. 访问阿里云DashScope服务：https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 在控制台创建API密钥
5. 复制API密钥并在`set_qwen_key.bat`中使用

## 使用方法

### 使用批处理文件

1. 运行`set_qwen_key.bat`设置API密钥
2. 运行`run_with_qwen.bat`生成问题和语音

### 使用命令行

```
# 使用配置文件生成问题
python generate_ielts_questions.py --text "你的英语文本" --config llm_module\config.json

# 生成问题并转换为语音
python generate_ielts_questions.py --text "你的英语文本" --config llm_module\config.json --tts

# 从文件生成问题
python generate_ielts_questions.py --file example_input.txt --config llm_module\config.json
```

## 常见问题解答

### 如果出现API错误怎么办？

- 检查您的API密钥是否正确
- 确认您的阿里云账户有足够的额度
- 检查网络连接是否正常

### 如果TTS生成失败怎么办？

- 确保已安装espeak-ng（Windows用户可运行`install_espeak.bat`）
- 或者使用`run_with_fallback_tts.bat`，它使用Windows自带的语音引擎

## 注意事项

- 通义千问API可能有使用限制和费用，请查阅阿里云官方文档
- 生成的问题质量取决于模型版本和输入文本质量
- TTS功能需要额外的依赖项
