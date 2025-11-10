"""
IELTS Speaking Test Web Interface Server

This module provides a web server for the IELTS Speaking Test Simulator,
integrating the web interface with the existing voice_to_questions module.
"""

import os
import sys
import json
import base64
import logging
import tempfile
import random
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the voice_to_questions module
from llm_module.voice_to_questions import VoiceToQuestions
from llm_module.tts_integration import TTSIntegration

# Add grade directories to system path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'grade', 'pronunciation-trainer'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'grade'))
import run_scorer
import report_runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize VoiceToQuestions system
voice_to_questions = None
tts_integration = None

# Temporary directory for audio files
TEMP_DIR = tempfile.mkdtemp(prefix='ielts_web_')

# Use the same output directory as run_voice_manual_4min.bat
VOICE_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'voice_output')
os.makedirs(VOICE_OUTPUT_DIR, exist_ok=True)
OUTPUT_DIR = VOICE_OUTPUT_DIR  # 使用voice_output作为主要输出目录

# Also use the web_output directory for persistent storage
WEB_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web_output')
os.makedirs(WEB_OUTPUT_DIR, exist_ok=True)

# Clean up any existing files in web_output directory at startup
def clean_web_output():
    """Clean up files in web_output directory at startup."""
    try:
        # List of files to keep (don't delete these)
        files_to_keep = ['part2_introduction.txt', 'part2_introduction.wav']
        
        for file in os.listdir(WEB_OUTPUT_DIR):
            file_path = os.path.join(WEB_OUTPUT_DIR, file)
            if os.path.isfile(file_path) and file not in files_to_keep:
                os.remove(file_path)
                logger.info(f"Removed old file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning web_output directory: {e}")

# Clean up at startup
clean_web_output()


def initialize_system():
    """Initialize the voice_to_questions system."""
    global voice_to_questions, tts_integration
    
    try:
        # Initialize VoiceToQuestions
        voice_to_questions = VoiceToQuestions()
        
        # Initialize TTSIntegration
        tts_integration = TTSIntegration()
        
        # Generate Part 2 introduction audio if needed
        generate_part2_introduction_audio()
        
        # 初始化时尝试合并现有的回答文件
        try:
            merge_answer_files()
            logger.info("Merged existing answer files")
        except Exception as merge_error:
            logger.warning(f"Failed to merge answer files during initialization: {merge_error}")
        
        logger.info("Voice-to-questions system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize voice-to-questions system: {e}")
        return False

def generate_part2_introduction_audio():
    """Generate Part 2 introduction audio if it doesn't exist."""
    try:
        # Path for the introduction text and audio
        intro_text_path = os.path.join(WEB_OUTPUT_DIR, "part2_introduction.txt")
        intro_audio_path = os.path.join(WEB_OUTPUT_DIR, "part2_introduction.wav")
        
        # Check if audio already exists
        if os.path.exists(intro_audio_path):
            logger.info(f"Part 2 introduction audio already exists: {intro_audio_path}")
            return True
        
        # Check if text exists
        if not os.path.exists(intro_text_path):
            logger.error(f"Part 2 introduction text not found: {intro_text_path}")
            return False
        
        # Read the introduction text
        with open(intro_text_path, 'r', encoding='utf-8') as f:
            intro_text = f.read().strip()
        
        if not intro_text:
            logger.error("Part 2 introduction text is empty")
            return False
        
        logger.info(f"Generating audio for Part 2 introduction: {intro_text[:50]}...")
        
        # Generate audio
        success = tts_integration.text_to_speech(intro_text, intro_audio_path)
        
        if success:
            logger.info(f"Successfully generated Part 2 introduction audio: {intro_audio_path}")
            return True
        else:
            logger.error("Failed to generate Part 2 introduction audio")
            return False
    except Exception as e:
        logger.error(f"Error generating Part 2 introduction audio: {e}")
        return False


def load_part2_questions():
    """Load Part 2 questions from the text file."""
    questions_file = os.path.join(os.path.dirname(__file__), 'part2_questions.txt')
    questions = []
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Split by double newlines to separate questions
        question_blocks = content.split('\n\n')
        
        for block in question_blocks:
            if block.strip():
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if lines:
                    # First line is the main question, rest are bullet points
                    main_question = lines[0]
                    if main_question.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                        main_question = main_question[2:].strip()  # Remove number prefix
                    
                    bullet_points = lines[1:] if len(lines) > 1 else []
                    
                    questions.append({
                        'topic': main_question,
                        'points': bullet_points
                    })
        
        logger.info(f"Loaded {len(questions)} Part 2 questions")
        return questions
    except Exception as e:
        logger.error(f"Error loading Part 2 questions: {e}")
        # Return default questions if file loading fails
        return [{
            'topic': 'Describe a place you would like to visit',
            'points': [
                'Where it is',
                'How you know about this place',
                'What you would do there',
                'And explain why you would like to visit this place'
            ]
        }]


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('.', filename)


@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Get the status of the voice-to-questions system."""
    if not voice_to_questions:
        return jsonify({
            'status': 'error',
            'message': 'System not initialized'
        }), 500
    
    try:
        # Get system info
        system_info = voice_to_questions.get_system_info()
        
        # Run a simple test
        test_results = voice_to_questions.test_system()
        
        return jsonify({
            'status': 'success',
            'system_info': system_info,
            'test_results': test_results
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using voice_ielts_questions.py script directly."""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'No text provided'
            }), 400
        
        # Generate a unique filename for the text and output
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
        temp_text_file = os.path.join(TEMP_DIR, f"text_{text_hash}.txt")
        
        # Save text to a temporary file
        with open(temp_text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Use voice_ielts_questions.py script directly
        try:
            import subprocess
            
            # Get the path to voice_ielts_questions.py
            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'voice_ielts_questions.py')
            
            # Create a temporary directory for output
            temp_output_dir = os.path.join(TEMP_DIR, f"tts_output_{text_hash}")
            os.makedirs(temp_output_dir, exist_ok=True)
            
            # Create a file with the text to use as input
            input_text_file = os.path.join(TEMP_DIR, f"input_{text_hash}.txt")
            with open(input_text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Run the script with appropriate arguments
            cmd = [
                'python', 
                script_path,
                '--file', input_text_file,  # Use text file as input
                '--num_questions', '1',  # Generate just one item
                '--output_dir', temp_output_dir,
                '--tts'  # Enable TTS
            ]
            
            logger.info(f"Running TTS command: {' '.join(cmd)}")
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check if the command was successful
            if process.returncode != 0:
                logger.error(f"Error running voice_ielts_questions.py for TTS: {process.stderr}")
                raise Exception(f"Script execution failed: {process.stderr}")
            
            # Look for generated audio file
            output_file = os.path.join(temp_output_dir, "question_1.wav")
            
            if os.path.exists(output_file):
                logger.info(f"Successfully generated audio using voice_ielts_questions.py: {output_file}")
                return jsonify({
                    'status': 'success',
                    'audio_path': output_file
                })
            
            # If we can't find the expected file, look for any .wav file
            wav_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.wav')]
            if wav_files:
                output_file = os.path.join(temp_output_dir, wav_files[0])
                logger.info(f"Found alternative audio file: {output_file}")
                return jsonify({
                    'status': 'success',
                    'audio_path': output_file
                })
            
            # If script ran but no audio file was found, try direct TTS method
            logger.warning("Script ran successfully but no audio file was found. Trying direct TTS.")
            
            # Try direct TTS API method
            output_file = os.path.join(TEMP_DIR, f"tts_{text_hash}.wav")
            from TTS.api import TTS as TTSApi
            
            # Try several models in order of preference
            tts_models = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/en/ljspeech/fast_pitch"
            ]
            
            for model_name in tts_models:
                try:
                    logger.info(f"Trying TTS model: {model_name}")
                    tts = TTSApi(model_name=model_name)
                    tts.tts_to_file(text=text, file_path=output_file)
                    
                    if os.path.exists(output_file):
                        logger.info(f"Generated audio with {model_name} at {output_file}")
                        return jsonify({
                            'status': 'success',
                            'audio_path': output_file
                        })
                except Exception as model_error:
                    logger.warning(f"TTS model {model_name} failed: {model_error}")
                    continue
            
            # If all direct methods failed, try using the TTS integration as fallback
            if tts_integration:
                success = tts_integration.text_to_speech(text, output_file)
                if success:
                    logger.info(f"Generated audio with TTS integration at {output_file}")
                    return jsonify({
                        'status': 'success',
                        'audio_path': output_file
                    })
            
            # If we got here, all methods failed
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate audio with all available methods'
            }), 500
            
        except Exception as script_error:
            logger.error(f"Error in script-based TTS: {script_error}")
            
            # Try direct TTS API method as fallback
            output_file = os.path.join(TEMP_DIR, f"tts_{text_hash}.wav")
            try:
                from TTS.api import TTS as TTSApi
                tts = TTSApi(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                tts.tts_to_file(text=text, file_path=output_file)
                
                if os.path.exists(output_file):
                    return jsonify({
                        'status': 'success',
                        'audio_path': output_file
                    })
            except Exception as tts_error:
                logger.error(f"Direct TTS also failed: {tts_error}")
                
                # Last resort: TTS integration
                if tts_integration:
                    try:
                        success = tts_integration.text_to_speech(text, output_file)
                        if success:
                            return jsonify({
                                'status': 'success',
                                'audio_path': output_file
                            })
                    except Exception as fallback_error:
                        logger.error(f"TTS integration also failed: {fallback_error}")
            
            return jsonify({
                'status': 'error',
                'message': f'Failed to convert text to speech: {script_error}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/process-recording', methods=['POST'])
def process_recording():
    """Process a recorded audio and generate questions directly within the server."""
    try:
        data = request.json
        audio_data = data.get('audio')  # Base64 encoded audio data
        num_questions = int(data.get('num_questions', 3))
        
        if not audio_data:
            return jsonify({
                'status': 'error',
                'message': 'No audio data provided'
            }), 400
        
        # Decode base64 audio data
        try:
            # Remove the data URL prefix if present
            if 'base64,' in audio_data:
                audio_data = audio_data.split('base64,')[1]
            
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            logger.error(f"Error decoding audio data: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid audio data format'
            }), 400
        
        # Save audio to temporary file
        input_audio_path = os.path.join(TEMP_DIR, 'recorded_audio.wav')
        with open(input_audio_path, 'wb') as f:
            f.write(audio_bytes)
            
        # Also save a copy to web_output directory for persistence
        web_output_audio_path = os.path.join(WEB_OUTPUT_DIR, 'part2_answer.wav')
        try:
            with open(web_output_audio_path, 'wb') as f:
                f.write(audio_bytes)
            logger.info(f"Saved Part 2 answer to web_output directory")
        except Exception as web_save_error:
            logger.error(f"Error saving to web_output directory: {web_save_error}")
        
        # 验证文件是否存在且大小正常
        if not os.path.exists(input_audio_path) or os.path.getsize(input_audio_path) == 0:
            logger.error("Audio file was not saved correctly or is empty")
            return jsonify({
                'status': 'error',
                'message': 'Failed to save audio file properly'
            }), 500
            
        # 同样检查web_output目录中的文件
        if not os.path.exists(web_output_audio_path) or os.path.getsize(web_output_audio_path) == 0:
            logger.warning("Audio file in web_output directory was not saved correctly or is empty")
        
        # 直接使用voice_to_questions模块处理音频文件
        logger.info(f"Processing audio file directly: {input_audio_path}")
        
        # 确保voice_to_questions已初始化
        if not voice_to_questions:
            logger.error("Voice-to-questions system not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Voice-to-questions system not initialized'
            }), 500
        
        # 将录音文件转换为正确格式并保存到voice_output目录
        voice_output_audio_path = os.path.join(VOICE_OUTPUT_DIR, 'recorded_audio.wav')
        try:
            # 使用ffmpeg转换音频格式
            try:
                import subprocess
                logger.info(f"尝试使用ffmpeg转换音频格式")
                
                # 创建ffmpeg命令
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-y',  # 覆盖输出文件
                    '-i', web_output_audio_path,  # 输入文件
                    '-acodec', 'pcm_s16le',  # PCM 16-bit编码
                    '-ar', '16000',  # 16kHz采样率
                    '-ac', '1',  # 单声道
                    voice_output_audio_path  # 输出文件
                ]
                
                # 执行命令
                process = subprocess.run(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    logger.info(f"音频格式转换成功: {voice_output_audio_path}")
                else:
                    logger.error(f"ffmpeg转换失败: {process.stderr}")
                    # 如果ffmpeg失败，尝试直接复制
                    import shutil
                    shutil.copy2(web_output_audio_path, voice_output_audio_path)
                    logger.info(f"复制录音文件到voice_output目录: {voice_output_audio_path}")
            except Exception as convert_error:
                logger.error(f"音频格式转换失败: {convert_error}")
                # 如果转换失败，尝试直接复制
                import shutil
                shutil.copy2(web_output_audio_path, voice_output_audio_path)
                logger.info(f"复制录音文件到voice_output目录: {voice_output_audio_path}")
        except Exception as copy_error:
            logger.error(f"复制录音文件失败: {copy_error}")
            # 如果复制失败，继续使用原始文件
            voice_output_audio_path = web_output_audio_path
        
        # 直接使用voice_to_questions模块处理音频文件
        logger.info(f"开始处理音频文件: {voice_output_audio_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(voice_output_audio_path)
        logger.info(f"音频文件大小: {file_size} 字节")
        
        # 确保文件已完全写入
        import time
        time.sleep(3)  # 额外等待3秒，确保文件完全写入
        
        # 再次检查文件大小，确认文件已稳定
        new_file_size = os.path.getsize(voice_output_audio_path)
        logger.info(f"等待后音频文件大小: {new_file_size} 字节")
        
        # 处理音频文件 - 使用voice_output目录作为输出目录
        results = voice_to_questions.process_audio_file(
            audio_file_path=voice_output_audio_path,  # 使用voice_output目录中的文件
            num_questions=num_questions,
            output_dir=OUTPUT_DIR,  # 现在OUTPUT_DIR已经是VOICE_OUTPUT_DIR
            generate_audio=True,
            save_transcript=True
        )
        
        logger.info(f"音频处理结果: {results['success']}")
        if not results['success']:
            logger.error(f"处理错误: {results['errors']}")
        
        if not results['success']:
            logger.error(f"Failed to process audio: {results['errors']}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to process audio',
                'errors': results['errors']
            }), 500
        
        # 准备响应
        response = {
            'status': 'success',
            'transcript': results['transcript'],
            'questions': results['questions'],
            'audio_files': {}
        }
        
        # 添加音频文件路径
        for idx, path in results['audio_files'].items():
            if idx == 'combined':
                response['audio_files']['combined'] = path
            else:
                response['audio_files'][f'question_{idx+1}'] = path
        
        # 由于我们现在直接使用voice_output目录，文件已经保存在正确的位置
        # 我们仍然复制一份到web_output目录，以便网页界面可以访问
        
        # 复制转录文本到web_output
        if results['transcript']:
            # 源文件路径 - voice_output/audio_transcript.txt (注意这里是audio_transcript.txt，不是voice_transcript.txt)
            source_transcript_path = os.path.join(VOICE_OUTPUT_DIR, 'audio_transcript.txt')
            web_output_transcript_path = os.path.join(WEB_OUTPUT_DIR, 'part2_answer_transcript.txt')
            try:
                import shutil
                if os.path.exists(source_transcript_path):
                    shutil.copy2(source_transcript_path, web_output_transcript_path)
                    logger.info(f"Copied transcript to web_output: {web_output_transcript_path}")
                else:
                    # 如果源文件不存在，直接写入
                    with open(web_output_transcript_path, 'w', encoding='utf-8') as f:
                        f.write(results['transcript'])
                    logger.info(f"Saved transcript to web_output: {web_output_transcript_path}")
            except Exception as web_transcript_error:
                logger.error(f"Error handling transcript: {web_transcript_error}")
        
        # 复制问题到web_output
        if results['questions']:
            # 源文件路径 - voice_output/audio_generated_questions.txt (注意这里是audio_generated_questions.txt，不是voice_generated_questions.txt)
            source_questions_path = os.path.join(VOICE_OUTPUT_DIR, 'audio_generated_questions.txt')
            web_output_questions_path = os.path.join(WEB_OUTPUT_DIR, 'part3_questions.txt')
            try:
                import shutil
                if os.path.exists(source_questions_path):
                    shutil.copy2(source_questions_path, web_output_questions_path)
                    logger.info(f"Copied questions to web_output: {web_output_questions_path}")
                else:
                    # 如果源文件不存在，直接写入
                    with open(web_output_questions_path, 'w', encoding='utf-8') as f:
                        for i, q in enumerate(results['questions']):
                            f.write(f"{i+1}. {q}\n")
                    logger.info(f"Saved questions to web_output: {web_output_questions_path}")
            except Exception as web_questions_error:
                logger.error(f"Error handling questions: {web_questions_error}")
        
        # 复制音频文件到web_output
        for idx, path in results['audio_files'].items():
            if idx == 'combined':
                dest_path = os.path.join(WEB_OUTPUT_DIR, 'part3_combined_questions.wav')
            else:
                dest_path = os.path.join(WEB_OUTPUT_DIR, f'part3_question_{idx+1}.wav')
            
            try:
                import shutil
                if os.path.exists(path):
                    shutil.copy2(path, dest_path)
                    logger.info(f"Copied audio file to web_output: {dest_path}")
            except Exception as copy_error:
                logger.error(f"Error copying audio file to web_output: {copy_error}")
        
        # 合并回答文件
        merge_answer_files()
        
        return jsonify(response)
            
    except Exception as e:
        logger.error(f"Error processing recording: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/merge-answers', methods=['POST'])
def api_merge_answers():
    """API端点，手动触发合并回答文件。"""
    try:
        # 执行合并操作
        merge_answer_files()
        
        # 检查合并后的文件是否存在
        part23_text_path = os.path.join(WEB_OUTPUT_DIR, 'part23_answers.txt')
        part23_audio_path = os.path.join(WEB_OUTPUT_DIR, 'part23_answers.wav')
        part3_text_path = os.path.join(WEB_OUTPUT_DIR, 'part3_answers.txt')
        
        result = {
            'status': 'success',
            'message': 'Answer files merged successfully',
            'files': {}
        }
        
        if os.path.exists(part23_text_path):
            result['files']['part23_text'] = part23_text_path
        
        if os.path.exists(part23_audio_path):
            result['files']['part23_audio'] = part23_audio_path
        
        if os.path.exists(part3_text_path):
            result['files']['part3_text'] = part3_text_path
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in merge-answers API: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files."""
    try:
        # Handle absolute paths (convert to just filename)
        filename = os.path.basename(filename)
        
        # Check if the file exists in TEMP_DIR
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.exists(file_path):
            return send_from_directory(TEMP_DIR, filename)
        
        # Check if the file exists in OUTPUT_DIR
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            return send_from_directory(OUTPUT_DIR, filename)
        
        # Check voice_output directory as well (used by voice_ielts_questions.py)
        voice_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'voice_output')
        file_path = os.path.join(voice_output_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(voice_output_dir, filename)
            
        # Check web_output directory as well
        file_path = os.path.join(WEB_OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            return send_from_directory(WEB_OUTPUT_DIR, filename)
        
        # File not found
        logger.error(f"Audio file not found: {filename}")
        return jsonify({
            'status': 'error',
            'message': 'Audio file not found'
        }), 404
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """Generate questions from text."""
    if not voice_to_questions:
        return jsonify({
            'status': 'error',
            'message': 'System not initialized'
        }), 500
    
    try:
        data = request.json
        text = data.get('text', '')
        num_questions = int(data.get('num_questions', 3))
        generate_audio = data.get('generate_audio', True)
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'No text provided'
            }), 400
        
        # Generate questions
        questions = voice_to_questions.question_generator.generate_questions(
            text, 
            num_questions=num_questions
        )
        
        response = {
            'status': 'success',
            'questions': questions,
            'audio_files': {}
        }
        
        # Generate audio if requested
        if generate_audio and questions:
            tts_result = tts_integration.batch_process(
                questions,
                OUTPUT_DIR,
                combined=True
            )
            
            # Add audio file paths
            for idx, path in tts_result['individual_files'].items():
                response['audio_files'][f'question_{idx+1}'] = path
            
            if tts_result['combined_file']:
                response['audio_files']['combined'] = tts_result['combined_file']
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/get-part2-introduction', methods=['GET'])
def get_part2_introduction():
    """Get the Part 2 introduction audio."""
    try:
        intro_audio_path = os.path.join(WEB_OUTPUT_DIR, "part2_introduction.wav")
        
        if not os.path.exists(intro_audio_path):
            # Try to generate it if it doesn't exist
            if not generate_part2_introduction_audio():
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to generate Part 2 introduction audio'
                }), 500
        
        return jsonify({
            'status': 'success',
            'audio_path': intro_audio_path
        })
    except Exception as e:
        logger.error(f"Error getting Part 2 introduction: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/get-part2-question', methods=['GET'])
def get_part2_question():
    """Get a random Part 2 question."""
    try:
        questions = load_part2_questions()
        selected_question = random.choice(questions)
        
        return jsonify({
            'status': 'success',
            'question': selected_question
        })
    except Exception as e:
        logger.error(f"Error getting Part 2 question: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/get-report', methods=['GET'])
def get_report():
    """Get the IELTS speaking score report."""
    try:
        # 报告文件路径 - 使用web_output目录下的报告
        report_path = os.path.join(WEB_OUTPUT_DIR, 'ielts_speaking_report.txt')
        
        # 检查文件是否存在
        if not os.path.exists(report_path):
            return jsonify({
                'status': 'not_found',
                'message': 'Report not available yet'
            }), 404
        
        # 读取报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # 检查文件是否为空
        if not report_content.strip():
            return jsonify({
                'status': 'empty',
                'message': 'Report is being generated'
            }), 202
        
        return jsonify({
            'status': 'success',
            'content': report_content
        })
        
    except Exception as e:
        logger.error(f"Error reading report: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load report'
        }), 500


@app.route('/api/generate-part2-audio', methods=['POST'])
def generate_part2_audio():
    """Generate audio for Part 2 question."""
    try:
        data = request.json
        question_data = data.get('question')
        
        if not question_data:
            return jsonify({
                'status': 'error',
                'message': 'No question data provided'
            }), 400
        
        # Format the question text for TTS
        text_parts = [
            "Here's your topic for Part 2.",
            question_data['topic'],
            "You should say:"
        ]
        
        # Add bullet points
        for point in question_data['points']:
            text_parts.append(point)
        
        text_parts.append("You have one minute to prepare. You can make notes if you wish.")
        
        full_text = " ".join(text_parts)
        
        # Generate a unique filename for the audio based on the question content
        import hashlib
        question_hash = hashlib.md5(full_text.encode()).hexdigest()[:10]
        output_file = os.path.join(TEMP_DIR, f"part2_question_{question_hash}.wav")
        
        # Also save the question text to a file with the same hash for reference
        question_text_file = os.path.join(TEMP_DIR, f"part2_question_{question_hash}.txt")
        with open(question_text_file, 'w', encoding='utf-8') as f:
            f.write(f"Topic: {question_data['topic']}\nYou should say:\n")
            for point in question_data['points']:
                f.write(f"- {point}\n")
        
        # Generate audio
        success = tts_integration.text_to_speech(full_text, output_file)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate audio'
            }), 500
            
        # Also save a copy to web_output directory for persistence
        web_output_file = os.path.join(WEB_OUTPUT_DIR, "part2_question.wav")
        try:
            import shutil
            shutil.copy2(output_file, web_output_file)
            
            # Also save the question text
            web_output_text_file = os.path.join(WEB_OUTPUT_DIR, "part2_question.txt")
            with open(web_output_text_file, 'w', encoding='utf-8') as f:
                f.write(f"Topic: {question_data['topic']}\nYou should say:\n")
                for point in question_data['points']:
                    f.write(f"- {point}\n")
                    
            # Save just the topic for easy reference
            web_output_topic_file = os.path.join(WEB_OUTPUT_DIR, "part2_topic.txt")
            with open(web_output_topic_file, 'w', encoding='utf-8') as f:
                f.write(f"Part 2 Topic: {question_data['topic']}")
                
            logger.info(f"Saved part2 question and audio to web_output directory")
        except Exception as copy_error:
            logger.error(f"Error saving to web_output directory: {copy_error}")
        
        return jsonify({
            'status': 'success',
            'audio_path': output_file,
            'question': question_data
        })
    except Exception as e:
        logger.error(f"Error generating Part 2 audio: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/save-part3-recording', methods=['POST'])
def save_part3_recording():
    """Save Part 3 recording without generating new questions."""
    try:
        data = request.json
        audio_data = data.get('audio')
        question_number = data.get('question_number', 1)
        
        if not audio_data:
            return jsonify({
                'status': 'error',
                'message': 'No audio data provided'
            }), 400
        
        # Decode base64 audio data
        try:
            if 'base64,' in audio_data:
                audio_data = audio_data.split('base64,')[1]
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            logger.error(f"Error decoding audio data: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid audio data format'
            }), 400
        
        # 确保voice_to_questions已初始化
        if not voice_to_questions:
            logger.error("Voice-to-questions system not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Voice-to-questions system not initialized'
            }), 500
        
        # 直接保存到web_output目录，确保持久性
        audio_filename = f'part3_answer_{question_number}.wav'
        web_output_audio_path = os.path.join(WEB_OUTPUT_DIR, audio_filename)
        
        try:
            with open(web_output_audio_path, 'wb') as f:
                f.write(audio_bytes)
            logger.info(f"Saved Part 3 answer {question_number} to web_output directory")
        except Exception as web_save_error:
            logger.error(f"Error saving to web_output directory: {web_save_error}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to save audio file: {str(web_save_error)}'
            }), 500
        
        # 验证文件是否存在且大小正常
        if not os.path.exists(web_output_audio_path) or os.path.getsize(web_output_audio_path) == 0:
            logger.error("Part 3 audio file was not saved correctly or is empty")
            return jsonify({
                'status': 'error',
                'message': 'Failed to save Part 3 audio file properly'
            }), 500
        
        # 将录音文件转换为正确格式以便进行转录
        voice_output_audio_path = os.path.join(VOICE_OUTPUT_DIR, f'part3_answer_{question_number}.wav')
        try:
            # 使用ffmpeg转换音频格式
            try:
                import subprocess
                logger.info(f"Converting audio format for Part 3 answer {question_number}")
                
                # 创建ffmpeg命令
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-y',  # 覆盖输出文件
                    '-i', web_output_audio_path,  # 输入文件
                    '-acodec', 'pcm_s16le',  # PCM 16-bit编码
                    '-ar', '16000',  # 16kHz采样率
                    '-ac', '1',  # 单声道
                    voice_output_audio_path  # 输出文件
                ]
                
                # 执行命令
                process = subprocess.run(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    logger.info(f"Audio format conversion successful: {voice_output_audio_path}")
                    # 使用转换后的文件进行转录
                    audio_to_transcribe = voice_output_audio_path
                else:
                    logger.error(f"ffmpeg conversion failed: {process.stderr}")
                    # 如果ffmpeg失败，尝试直接复制
                    import shutil
                    shutil.copy2(web_output_audio_path, voice_output_audio_path)
                    logger.info(f"Copied audio file to voice_output directory: {voice_output_audio_path}")
                    audio_to_transcribe = voice_output_audio_path
            except Exception as convert_error:
                logger.error(f"Audio format conversion failed: {convert_error}")
                # 如果转换失败，尝试直接复制
                import shutil
                shutil.copy2(web_output_audio_path, voice_output_audio_path)
                logger.info(f"Copied audio file to voice_output directory: {voice_output_audio_path}")
                audio_to_transcribe = voice_output_audio_path
        except Exception as copy_error:
            logger.error(f"Failed to copy audio file: {copy_error}")
            # 如果复制失败，继续使用原始文件
            audio_to_transcribe = web_output_audio_path
        
        # 检查文件大小
        file_size = os.path.getsize(audio_to_transcribe)
        logger.info(f"Audio file size: {file_size} bytes")
        
        # 确保文件已完全写入
        import time
        time.sleep(1)  # 等待1秒，确保文件完全写入
        
        # 使用voice_to_questions模块的speech_to_text组件进行转录
        transcript = ""
        try:
            # 使用转换后的音频文件进行转录
            transcribe_success, transcript, _ = voice_to_questions.speech_to_text.transcribe_file(audio_to_transcribe)
            
            if transcribe_success:
                # 保存转录文本到web_output目录
                transcript_filename = f'part3_answer_{question_number}.txt'
                web_output_transcript_path = os.path.join(WEB_OUTPUT_DIR, transcript_filename)
                
                with open(web_output_transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                
                logger.info(f"Saved Part 3 answer {question_number} transcript to {web_output_transcript_path}")
            else:
                logger.warning(f"Failed to transcribe Part 3 answer {question_number}")
                # 如果转录失败，创建一个占位符文本文件
                transcript = "[Transcription unavailable]"
                transcript_filename = f'part3_answer_{question_number}.txt'
                web_output_transcript_path = os.path.join(WEB_OUTPUT_DIR, transcript_filename)
                
                with open(web_output_transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                
                logger.info(f"Created placeholder transcript for Part 3 answer {question_number}")
        except Exception as e:
            logger.error(f"Error transcribing Part 3 answer: {e}")
            # 即使转录失败，我们仍然可以返回成功，因为音频已保存
            # 创建一个占位符文本文件
            transcript = "[Transcription error occurred]"
            transcript_filename = f'part3_answer_{question_number}.txt'
            web_output_transcript_path = os.path.join(WEB_OUTPUT_DIR, transcript_filename)
            
            try:
                with open(web_output_transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                logger.info(f"Created error placeholder transcript for Part 3 answer {question_number}")
            except Exception as write_error:
                logger.error(f"Failed to create placeholder transcript: {write_error}")
        
        # 合并回答文件
        merge_answer_files()
        
        return jsonify({
            'status': 'success',
            'audio_path': web_output_audio_path,
            'transcript': transcript,
            'message': f'Part 3 answer {question_number} saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving Part 3 recording: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def merge_audio_files(audio_files, output_file):
    """合并多个音频文件为一个文件。
    
    Args:
        audio_files (list): 要合并的音频文件路径列表
        output_file (str): 输出文件路径
        
    Returns:
        bool: 是否成功合并
    """
    try:
        # 检查所有输入文件是否存在
        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return False
        
        # 使用ffmpeg合并音频文件
        try:
            import subprocess
            
            # 创建一个临时文件列表
            temp_list_file = os.path.join(TEMP_DIR, "audio_files_list.txt")
            with open(temp_list_file, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    f.write(f"file '{os.path.abspath(audio_file)}'\n")
            
            # 使用ffmpeg的concat demuxer合并音频文件
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # 覆盖输出文件
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_list_file,
                '-acodec', 'pcm_s16le',  # 使用PCM 16-bit编码
                '-ar', '16000',  # 16kHz采样率
                '-ac', '1',  # 单声道
                output_file
            ]
            
            logger.info(f"Running ffmpeg command to merge audio files: {' '.join(ffmpeg_cmd)}")
            
            # 执行命令
            process = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 检查命令是否成功执行
            if process.returncode == 0:
                logger.info(f"Successfully merged audio files to: {output_file}")
                return True
            else:
                logger.error(f"ffmpeg merge failed: {process.stderr}")
                
                # 如果ffmpeg失败，尝试使用pydub
                try:
                    from pydub import AudioSegment
                    
                    logger.info("Trying to merge audio files using pydub")
                    
                    # 读取第一个文件作为基础
                    combined = AudioSegment.from_wav(audio_files[0])
                    
                    # 添加其他文件
                    for audio_file in audio_files[1:]:
                        sound = AudioSegment.from_wav(audio_file)
                        combined += sound
                    
                    # 导出合并后的文件
                    combined.export(output_file, format="wav")
                    
                    logger.info(f"Successfully merged audio files using pydub to: {output_file}")
                    return True
                except Exception as pydub_error:
                    logger.error(f"pydub merge also failed: {pydub_error}")
                    return False
        except Exception as merge_error:
            logger.error(f"Error merging audio files: {merge_error}")
            return False
    except Exception as e:
        logger.error(f"Error in merge_audio_files: {e}")
        return False

def merge_answer_files():
    """合并回答文件到汇总文件。
    
    创建文件：
    1. part3_answers.txt - 包含所有part3回答
    2. part23_answers.txt - 包含part2和所有part3回答
    3. part23_answers.wav - 合并part2和part3的音频文件
    """
    try:
        # 检查必要的文件是否存在
        part2_path = os.path.join(WEB_OUTPUT_DIR, 'part2_answer_transcript.txt')
        part2_audio_path = os.path.join(WEB_OUTPUT_DIR, 'part2_answer.wav')
        part3_files = []
        part3_audio_files = []
        
        # 查找所有part3回答文件
        for i in range(1, 6):  # 假设最多有5个part3回答
            part3_path = os.path.join(WEB_OUTPUT_DIR, f'part3_answer_{i}.txt')
            part3_audio_path = os.path.join(WEB_OUTPUT_DIR, f'part3_answer_{i}.wav')
            
            if os.path.exists(part3_path):
                part3_files.append(part3_path)
            
            if os.path.exists(part3_audio_path):
                part3_audio_files.append(part3_audio_path)
        
        # 如果没有part3文件，则不需要合并
        if not part3_files:
            logger.warning("No Part 3 answer files found, skipping merge operation")
            return
        
        # 创建part3_answers.txt文件
        part3_combined_path = os.path.join(WEB_OUTPUT_DIR, 'part3_answers.txt')
        with open(part3_combined_path, 'w', encoding='utf-8') as outfile:
            for i, file_path in enumerate(part3_files):
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    outfile.write(f"Part 3 Answer {i+1}:\n{content}\n\n")
        
        logger.info(f"Successfully created merged Part 3 answers file: {part3_combined_path}")
        
        # 创建part23_answers.txt文件
        part23_combined_path = None
        if os.path.exists(part2_path):
            part23_combined_path = os.path.join(WEB_OUTPUT_DIR, 'part23_answers.txt')
            with open(part23_combined_path, 'w', encoding='utf-8') as outfile:
                # 首先添加Part 2回答
                with open(part2_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    outfile.write(f"Part 2 Answer:\n{content}\n\n")
                
                # 然后添加所有Part 3回答
                for i, file_path in enumerate(part3_files):
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read().strip()
                        outfile.write(f"Part 3 Answer {i+1}:\n{content}\n\n")
            
            logger.info(f"Successfully created merged Part 2+3 answers file: {part23_combined_path}")
        else:
            logger.warning(f"Part 2 answer file not found: {part2_path}, skipping part23_answers.txt creation")
        
        # 合并音频文件
        part23_audio_path = None
        if os.path.exists(part2_audio_path) and part3_audio_files:
            # 准备要合并的音频文件列表
            audio_files_to_merge = [part2_audio_path] + part3_audio_files
            part23_audio_path = os.path.join(WEB_OUTPUT_DIR, 'part23_answers.wav')
            
            # 调用音频合并函数
            if merge_audio_files(audio_files_to_merge, part23_audio_path):
                logger.info(f"Successfully created merged Part 2+3 audio file: {part23_audio_path}")
            else:
                logger.error("Failed to merge audio files")
                part23_audio_path = None
        else:
            if not os.path.exists(part2_audio_path):
                logger.warning(f"Part 2 audio file not found: {part2_audio_path}")
            if not part3_audio_files:
                logger.warning("No Part 3 audio files found")
            logger.warning("Skipping audio merge operation")
        
        # 检查是否生成了part23_answers.txt和part23_answers.wav文件，如果是则运行发音评分
        if part23_combined_path and part23_audio_path and os.path.exists(part23_combined_path) and os.path.exists(part23_audio_path):
            try:
                # 加载参考文本
                reference_text = run_scorer.load_reference_text(part23_combined_path)
                # 运行评分器
                result = run_scorer.run_pronunciation_scorer(
                    reference_text=reference_text,
                    audio_file_path=part23_audio_path,
                    output_json_path=os.path.join(WEB_OUTPUT_DIR, 'pronunciation_score.json'),
                    language='en'
                )
                logger.info("发音评分完成，结果已保存到pronunciation_score.json")
                
                # 运行IELTS综合评分报告
                try:
                    logger.info("开始生成IELTS综合评分报告...")
                    success = report_runner.run_ielts_report(verbose=False)
                    if success:
                        logger.info("IELTS综合评分报告生成成功，已保存到ielts_speaking_report.txt")
                    else:
                        logger.error("IELTS综合评分报告生成失败")
                except Exception as report_error:
                    logger.error(f"生成IELTS综合评分报告时出错: {report_error}")
            except Exception as e:
                logger.error(f"发音评分失败: {e}")
    
    except Exception as e:
        logger.error(f"Error merging answer files: {e}")

def cleanup_temp_files():
    """Clean up temporary files when the server shuts down."""
    try:
        import shutil
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            logger.info(f"Cleaned up temporary directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")


if __name__ == '__main__':
    try:
        # Initialize the system
        if initialize_system():
            logger.info("Starting web server...")
            
            # Register cleanup function
            import atexit
            atexit.register(cleanup_temp_files)
            
            # Start the server
            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            logger.error("Failed to initialize system. Exiting.")
    except Exception as e:
        logger.error(f"Error starting server: {e}")

