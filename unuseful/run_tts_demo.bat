@echo off
chcp 65001 >nul
echo 🐸 Coqui TTS 演示脚本启动器
echo ================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

echo ✅ Python已安装

REM 检查TTS是否安装
python -c "import TTS" >nul 2>&1
if errorlevel 1 (
    echo ❌ TTS库未安装
    echo 正在安装TTS...
    pip install TTS
    if errorlevel 1 (
        echo ❌ TTS安装失败
        pause
        exit /b 1
    )
)

echo ✅ TTS库已准备就绪
echo.

:menu
echo 请选择运行模式:
echo 1. 简单演示 (simple_tts.py)
echo 2. 完整演示 - 基础TTS
echo 3. 完整演示 - 列出所有模型
echo 4. 完整演示 - 中文TTS
echo 5. 创建示例音频文件
echo 0. 退出
echo.

set /p choice="请输入选择 (0-5): "

if "%choice%"=="1" (
    echo 运行简单演示...
    python simple_tts.py
    goto end
)

if "%choice%"=="2" (
    echo 运行基础TTS演示...
    python tts_demo.py --mode basic --text "Hello, this is a demonstration of Coqui TTS." --output output_basic.wav
    goto end
)

if "%choice%"=="3" (
    echo 列出所有可用模型...
    python tts_demo.py --mode list_models
    goto end
)

if "%choice%"=="4" (
    echo 运行中文TTS演示...
    python tts_demo.py --mode chinese --output output_chinese.wav
    goto end
)

if "%choice%"=="5" (
    echo 创建示例音频文件...
    python tts_demo.py --create_sample
    goto end
)

if "%choice%"=="0" (
    echo 退出程序
    goto end
)

echo 无效选择，请重新选择
goto menu

:end
echo.
echo 按任意键退出...
pause >nul
