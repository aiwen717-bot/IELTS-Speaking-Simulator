"""
Voice-to-Questions integration module.

This module integrates speech recording, speech-to-text conversion,
question generation, and text-to-speech functionality into a complete
voice-driven question generation system.
"""

import os
import sys
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .speech_recorder import SpeechRecorder
from .speech_to_text import SpeechToText
from .question_generator import IELTSQuestionGenerator
from .tts_integration import TTSIntegration
from .text_processor import TextProcessor
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceToQuestions:
    """
    Complete voice-driven question generation system.
    
    This class orchestrates the entire pipeline:
    1. Record user's voice input
    2. Convert speech to text
    3. Generate IELTS questions from the text
    4. Convert questions to speech output
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 stt_engine: str = 'google',
                 stt_language: str = 'en-US',
                 stt_api_key: Optional[str] = None):
        """
        Initialize the voice-to-questions system.
        
        Args:
            config_path: Path to configuration file
            stt_engine: Speech-to-text engine to use
            stt_language: Language for speech recognition
            stt_api_key: API key for STT service (if required)
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Initialize components
        self.speech_recorder = SpeechRecorder()
        self.speech_to_text = SpeechToText(
            engine=stt_engine,
            language=stt_language,
            api_key=stt_api_key
        )
        self.question_generator = IELTSQuestionGenerator(config_path=config_path)
        self.tts_integration = TTSIntegration()
        self.text_processor = TextProcessor()
        
        # Processing settings from config
        self.temp_audio_dir = tempfile.mkdtemp(prefix='voice_to_questions_')
        
        # Load recording settings from config
        recording_config = self.config.get('speech_recording', {})
        self.recording_settings = {
            'sample_rate': recording_config.get('sample_rate', 16000),
            'channels': recording_config.get('channels', 1),
            'auto_stop_on_silence': recording_config.get('auto_stop_on_silence', True),
            'silence_duration': recording_config.get('silence_duration', 3.0),
            'silence_threshold': recording_config.get('silence_threshold', 300),
            'max_duration': recording_config.get('max_duration', 300)
        }
        
        # Apply settings to speech recorder
        if hasattr(self.speech_recorder, 'silence_threshold'):
            self.speech_recorder.silence_threshold = self.recording_settings['silence_threshold']
        if hasattr(self.speech_recorder, 'silence_duration'):
            self.speech_recorder.silence_duration = self.recording_settings['silence_duration']
        
        logger.info("VoiceToQuestions system initialized")
    
    def __del__(self):
        """Clean up temporary files."""
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Remove temporary audio files."""
        try:
            import shutil
            if os.path.exists(self.temp_audio_dir):
                shutil.rmtree(self.temp_audio_dir)
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")
    
    def test_system(self) -> Dict[str, Any]:
        """
        Test all components of the system.
        
        Returns:
            Dictionary with test results for each component
        """
        results = {
            'speech_recorder': {'available': False, 'message': ''},
            'speech_to_text': {'available': False, 'message': ''},
            'question_generator': {'available': False, 'message': ''},
            'tts_integration': {'available': False, 'message': ''},
            'overall': {'success': False, 'message': ''}
        }
        
        # Test speech recorder
        try:
            devices = self.speech_recorder.list_audio_devices()
            if devices:
                results['speech_recorder']['available'] = True
                results['speech_recorder']['message'] = f"Found {len(devices)} audio input devices"
            else:
                results['speech_recorder']['message'] = "No audio input devices found"
        except Exception as e:
            results['speech_recorder']['message'] = f"Speech recorder error: {str(e)}"
        
        # Test speech-to-text
        try:
            stt_success, stt_message = self.speech_to_text.test_recognition()
            results['speech_to_text']['available'] = stt_success
            results['speech_to_text']['message'] = stt_message
        except Exception as e:
            results['speech_to_text']['message'] = f"STT error: {str(e)}"
        
        # Test question generator
        try:
            test_text = "This is a test text for question generation."
            questions = self.question_generator.generate_questions(test_text, num_questions=1)
            if questions and len(questions) > 0:
                results['question_generator']['available'] = True
                results['question_generator']['message'] = "Question generation working"
            else:
                results['question_generator']['message'] = "Question generation failed"
        except Exception as e:
            results['question_generator']['message'] = f"Question generator error: {str(e)}"
        
        # Test TTS integration
        try:
            if self.tts_integration.tts_available:
                results['tts_integration']['available'] = True
                results['tts_integration']['message'] = "TTS system available"
            else:
                results['tts_integration']['message'] = "TTS system not available"
        except Exception as e:
            results['tts_integration']['message'] = f"TTS error: {str(e)}"
        
        # Overall system status
        all_available = all(results[component]['available'] for component in 
                           ['speech_recorder', 'speech_to_text', 'question_generator', 'tts_integration'])
        
        if all_available:
            results['overall']['success'] = True
            results['overall']['message'] = "All system components are working correctly"
        else:
            failed_components = [comp for comp in results.keys() 
                               if comp != 'overall' and not results[comp]['available']]
            results['overall']['message'] = f"Failed components: {', '.join(failed_components)}"
        
        return results
    
    def record_and_transcribe(self, 
                             duration: Optional[float] = None,
                             output_audio_path: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Record audio from microphone and transcribe to text.
        
        Args:
            duration: Recording duration in seconds (None for auto-stop)
            output_audio_path: Path to save recorded audio (None for temp file)
            
        Returns:
            Tuple of (success, transcribed_text, metadata)
        """
        # Determine output path
        if output_audio_path is None:
            output_audio_path = os.path.join(self.temp_audio_dir, 'recorded_audio.wav')
        
        try:
            # Record audio
            logger.info("Starting audio recording...")
            # If duration is specified, disable auto-stop on silence for manual control
            auto_stop = self.recording_settings['auto_stop_on_silence'] if duration is None else False
            if duration is not None:
                logger.info(f"Manual stop mode enabled: duration={duration}s, auto_stop_on_silence=False")
            
            record_success, record_message = self.speech_recorder.record_audio(
                output_path=output_audio_path,
                duration=duration,
                auto_stop_on_silence=auto_stop
            )
            
            if not record_success:
                return False, "", {"error": f"Recording failed: {record_message}"}
            
            logger.info("Audio recording completed, starting transcription...")
            
            # Transcribe audio
            transcribe_success, transcribed_text, transcribe_metadata = self.speech_to_text.transcribe_file(
                output_audio_path
            )
            
            if not transcribe_success:
                return False, "", {
                    "error": f"Transcription failed: {transcribe_metadata.get('error', 'Unknown error')}",
                    "audio_file": output_audio_path
                }
            
            # Combine metadata
            combined_metadata = {
                "recording_success": record_success,
                "transcription_success": transcribe_success,
                "audio_file": output_audio_path,
                "transcription_metadata": transcribe_metadata,
                "text_length": len(transcribed_text)
            }
            
            logger.info(f"Successfully transcribed {len(transcribed_text)} characters")
            return True, transcribed_text, combined_metadata
            
        except Exception as e:
            error_msg = f"Error in record_and_transcribe: {str(e)}"
            logger.error(error_msg)
            return False, "", {"error": error_msg}
    
    def process_voice_input(self, 
                           duration: Optional[float] = None,
                           num_questions: int = 5,
                           output_dir: str = './output',
                           generate_audio: bool = True,
                           save_transcript: bool = True) -> Dict[str, Any]:
        """
        Complete voice-to-questions processing pipeline.
        
        Args:
            duration: Recording duration in seconds (None for auto-stop)
            num_questions: Number of questions to generate
            output_dir: Directory to save output files
            generate_audio: Whether to generate audio files for questions
            save_transcript: Whether to save the transcribed text
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'success': False,
            'transcript': '',
            'questions': [],
            'audio_files': {},
            'output_files': [],
            'errors': []
        }
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Record and transcribe
            logger.info("Step 1: Recording and transcribing voice input...")
            record_success, transcript, record_metadata = self.record_and_transcribe(duration)
            
            if not record_success:
                results['errors'].append(f"Recording/transcription failed: {record_metadata.get('error', 'Unknown error')}")
                return results
            
            results['transcript'] = transcript
            logger.info(f"Transcription completed: {len(transcript)} characters")
            
            # Save transcript if requested
            if save_transcript:
                transcript_file = os.path.join(output_dir, 'voice_transcript.txt')
                try:
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    results['output_files'].append(transcript_file)
                    logger.info(f"Transcript saved to: {transcript_file}")
                except Exception as e:
                    results['errors'].append(f"Failed to save transcript: {str(e)}")
            
            # Step 2: Generate questions
            logger.info("Step 2: Generating IELTS questions...")
            try:
                questions = self.question_generator.generate_questions(
                    transcript, 
                    num_questions=num_questions
                )
                results['questions'] = questions
                logger.info(f"Generated {len(questions)} questions")
                
                # Save questions to file
                questions_file = os.path.join(output_dir, 'voice_generated_questions.txt')
                with open(questions_file, 'w', encoding='utf-8') as f:
                    for i, question in enumerate(questions):
                        f.write(f"{i+1}. {question}\n")
                results['output_files'].append(questions_file)
                logger.info(f"Questions saved to: {questions_file}")
                
            except Exception as e:
                error_msg = f"Question generation failed: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                return results
            
            # Step 3: Generate audio (if requested)
            if generate_audio and questions:
                logger.info("Step 3: Converting questions to speech...")
                try:
                    if not self.tts_integration.tts_available:
                        results['errors'].append("TTS system not available")
                    else:
                        tts_result = self.tts_integration.batch_process(
                            questions,
                            output_dir,
                            combined=True,
                            voice="en-US-Neural2-F"
                        )
                        
                        results['audio_files'] = tts_result['individual_files']
                        if tts_result['combined_file']:
                            results['audio_files']['combined'] = tts_result['combined_file']
                        
                        # Add audio files to output files list
                        for file_path in tts_result['individual_files'].values():
                            results['output_files'].append(file_path)
                        if tts_result['combined_file']:
                            results['output_files'].append(tts_result['combined_file'])
                        
                        logger.info(f"Generated {len(tts_result['individual_files'])} audio files")
                        
                except Exception as e:
                    error_msg = f"TTS generation failed: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            results['success'] = True
            logger.info("Voice-to-questions processing completed successfully")
            
        except Exception as e:
            error_msg = f"Unexpected error in process_voice_input: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def process_audio_file(self, 
                          audio_file_path: str,
                          num_questions: int = 5,
                          output_dir: str = './output',
                          generate_audio: bool = True,
                          save_transcript: bool = True) -> Dict[str, Any]:
        """
        Process an existing audio file through the question generation pipeline.
        
        Args:
            audio_file_path: Path to the audio file to process
            num_questions: Number of questions to generate
            output_dir: Directory to save output files
            generate_audio: Whether to generate audio files for questions
            save_transcript: Whether to save the transcribed text
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'success': False,
            'transcript': '',
            'questions': [],
            'audio_files': {},
            'output_files': [],
            'errors': []
        }
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Transcribe audio file
            logger.info(f"Step 1: Transcribing audio file: {audio_file_path}")
            transcribe_success, transcript, transcribe_metadata = self.speech_to_text.transcribe_file(
                audio_file_path
            )
            
            if not transcribe_success:
                results['errors'].append(f"Transcription failed: {transcribe_metadata.get('error', 'Unknown error')}")
                return results
            
            results['transcript'] = transcript
            logger.info(f"Transcription completed: {len(transcript)} characters")
            
            # Continue with the same process as voice input
            # Save transcript if requested
            if save_transcript:
                transcript_file = os.path.join(output_dir, 'audio_transcript.txt')
                try:
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    results['output_files'].append(transcript_file)
                    logger.info(f"Transcript saved to: {transcript_file}")
                except Exception as e:
                    results['errors'].append(f"Failed to save transcript: {str(e)}")
            
            # Generate questions and audio using the same logic as process_voice_input
            # (The rest follows the same pattern as in process_voice_input)
            
            # Step 2: Generate questions
            logger.info("Step 2: Generating IELTS questions...")
            try:
                questions = self.question_generator.generate_questions(
                    transcript, 
                    num_questions=num_questions
                )
                results['questions'] = questions
                logger.info(f"Generated {len(questions)} questions")
                
                # Save questions to file
                questions_file = os.path.join(output_dir, 'audio_generated_questions.txt')
                with open(questions_file, 'w', encoding='utf-8') as f:
                    for i, question in enumerate(questions):
                        f.write(f"{i+1}. {question}\n")
                results['output_files'].append(questions_file)
                logger.info(f"Questions saved to: {questions_file}")
                
            except Exception as e:
                error_msg = f"Question generation failed: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                return results
            
            # Step 3: Generate audio (if requested)
            if generate_audio and questions:
                logger.info("Step 3: Converting questions to speech...")
                try:
                    if not self.tts_integration.tts_available:
                        results['errors'].append("TTS system not available")
                    else:
                        tts_result = self.tts_integration.batch_process(
                            questions,
                            output_dir,
                            combined=True,
                            voice="en-US-Neural2-F"
                        )
                        
                        results['audio_files'] = tts_result['individual_files']
                        if tts_result['combined_file']:
                            results['audio_files']['combined'] = tts_result['combined_file']
                        
                        # Add audio files to output files list
                        for file_path in tts_result['individual_files'].values():
                            results['output_files'].append(file_path)
                        if tts_result['combined_file']:
                            results['output_files'].append(tts_result['combined_file'])
                        
                        logger.info(f"Generated {len(tts_result['individual_files'])} audio files")
                        
                except Exception as e:
                    error_msg = f"TTS generation failed: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            results['success'] = True
            logger.info("Audio file processing completed successfully")
            
        except Exception as e:
            error_msg = f"Unexpected error in process_audio_file: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the system configuration and capabilities.
        
        Returns:
            Dictionary with system information
        """
        info = {
            'speech_recorder': {
                'available_devices': self.speech_recorder.list_audio_devices(),
                'settings': self.recording_settings
            },
            'speech_to_text': {
                'current_engine': self.speech_to_text.engine,
                'language': self.speech_to_text.language,
                'available_engines': self.speech_to_text.get_available_engines()
            },
            'question_generator': {
                'config_loaded': self.question_generator is not None,
                'num_questions_default': self.config.get('num_questions', 5)
            },
            'tts_integration': {
                'available': self.tts_integration.tts_available
            },
            'temp_directory': self.temp_audio_dir
        }
        
        return info
