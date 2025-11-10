"""
Speech-to-text module for converting audio to text.

This module provides functionality to convert recorded audio files
or live microphone input to text using various speech recognition engines.
"""

import speech_recognition as sr
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Handles speech-to-text conversion using various recognition engines.
    """
    
    # Available recognition engines
    ENGINES = {
        'google': 'Google Speech Recognition',
        'google_cloud': 'Google Cloud Speech-to-Text',
        'whisper': 'OpenAI Whisper',
        'sphinx': 'CMU Sphinx (offline)',
        'wit': 'Wit.ai',
        'azure': 'Microsoft Azure Speech',
        'ibm': 'IBM Speech to Text'
    }
    
    def __init__(self, 
                 engine: str = 'google',
                 language: str = 'en-US',
                 api_key: Optional[str] = None):
        """
        Initialize the speech-to-text converter.
        
        Args:
            engine: Recognition engine to use
            language: Language code for recognition
            api_key: API key for cloud services (if required)
        """
        self.engine = engine
        self.language = language
        self.api_key = api_key
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        
        # Engine-specific settings
        self.engine_settings = {
            'google': {},
            'whisper': {'model': 'base'},  # Can be: tiny, base, small, medium, large
            'sphinx': {},
            'wit': {'key': api_key},
            'azure': {'key': api_key},
            'ibm': {'username': None, 'password': api_key},
            'google_cloud': {'credentials_json': api_key}
        }
        
        # Validate engine
        if engine not in self.ENGINES:
            raise ValueError(f"Unsupported engine: {engine}. Available: {list(self.ENGINES.keys())}")
        
        # Check if engine is available
        self._check_engine_availability()
    
    def _check_engine_availability(self) -> bool:
        """
        Check if the selected engine is available and properly configured.
        
        Returns:
            True if engine is available, False otherwise
        """
        try:
            if self.engine == 'whisper':
                try:
                    import whisper
                    logger.info("Whisper engine is available")
                    return True
                except ImportError:
                    logger.warning("Whisper not installed. Install with: pip install openai-whisper")
                    return False
            
            elif self.engine == 'google_cloud':
                if not self.api_key:
                    logger.warning("Google Cloud requires credentials JSON file path")
                    return False
                return True
            
            elif self.engine in ['wit', 'azure'] and not self.api_key:
                logger.warning(f"{self.engine} requires an API key")
                return False
            
            elif self.engine == 'ibm' and not self.api_key:
                logger.warning("IBM Speech to Text requires API key")
                return False
            
            # For google and sphinx, no additional checks needed
            return True
            
        except Exception as e:
            logger.error(f"Error checking engine availability: {e}")
            return False
    
    def _recognize_with_engine(self, audio_data: sr.AudioData) -> str:
        """
        Perform speech recognition using the selected engine.
        
        Args:
            audio_data: Audio data to recognize
            
        Returns:
            Recognized text
            
        Raises:
            sr.UnknownValueError: If speech is unintelligible
            sr.RequestError: If there's an error with the recognition service
        """
        if self.engine == 'google':
            return self.recognizer.recognize_google(audio_data, language=self.language)
        
        elif self.engine == 'google_cloud':
            return self.recognizer.recognize_google_cloud(
                audio_data, 
                credentials_json=self.api_key,
                language=self.language
            )
        
        elif self.engine == 'whisper':
            return self.recognizer.recognize_whisper(
                audio_data, 
                model=self.engine_settings['whisper']['model'],
                language=self.language.split('-')[0]  # Whisper uses 2-letter codes
            )
        
        elif self.engine == 'sphinx':
            return self.recognizer.recognize_sphinx(audio_data, language=self.language)
        
        elif self.engine == 'wit':
            return self.recognizer.recognize_wit(audio_data, key=self.api_key)
        
        elif self.engine == 'azure':
            return self.recognizer.recognize_azure(
                audio_data, 
                key=self.api_key,
                language=self.language
            )
        
        elif self.engine == 'ibm':
            return self.recognizer.recognize_ibm(
                audio_data,
                username=self.engine_settings['ibm']['username'],
                password=self.api_key,
                language=self.language
            )
        
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")
    
    def transcribe_file(self, audio_file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Transcribe audio from a file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Tuple of (success, transcribed_text, metadata)
        """
        if not os.path.exists(audio_file_path):
            return False, "", {"error": f"Audio file not found: {audio_file_path}"}
        
        try:
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio data
                audio_data = self.recognizer.record(source)
            
            # Perform recognition
            text = self._recognize_with_engine(audio_data)
            
            metadata = {
                "engine": self.engine,
                "language": self.language,
                "file_path": audio_file_path,
                "file_size": os.path.getsize(audio_file_path),
                "success": True
            }
            
            logger.info(f"Successfully transcribed: {audio_file_path}")
            return True, text, metadata
            
        except sr.UnknownValueError:
            error_msg = "Could not understand the audio"
            logger.warning(f"Recognition failed for {audio_file_path}: {error_msg}")
            return False, "", {"error": error_msg, "file_path": audio_file_path}
            
        except sr.RequestError as e:
            error_msg = f"Recognition service error: {str(e)}"
            logger.error(f"Service error for {audio_file_path}: {error_msg}")
            return False, "", {"error": error_msg, "file_path": audio_file_path}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for {audio_file_path}: {error_msg}")
            return False, "", {"error": error_msg, "file_path": audio_file_path}
    
    def transcribe_microphone(self, 
                             duration: Optional[float] = None,
                             timeout: float = 10.0,
                             phrase_timeout: float = 5.0) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Transcribe audio directly from microphone.
        
        Args:
            duration: Recording duration in seconds (None for automatic)
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time to wait for phrase to complete
            
        Returns:
            Tuple of (success, transcribed_text, metadata)
        """
        try:
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Listening for speech...")
                
                if duration:
                    # Record for specified duration
                    audio_data = self.recognizer.record(source, duration=duration)
                else:
                    # Listen for speech with timeout
                    audio_data = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_timeout
                    )
            
            logger.info("Processing speech...")
            
            # Perform recognition
            text = self._recognize_with_engine(audio_data)
            
            metadata = {
                "engine": self.engine,
                "language": self.language,
                "source": "microphone",
                "duration": duration,
                "success": True
            }
            
            logger.info("Successfully transcribed microphone input")
            return True, text, metadata
            
        except sr.WaitTimeoutError:
            error_msg = f"No speech detected within {timeout} seconds"
            logger.warning(error_msg)
            return False, "", {"error": error_msg, "source": "microphone"}
            
        except sr.UnknownValueError:
            error_msg = "Could not understand the audio from microphone"
            logger.warning(error_msg)
            return False, "", {"error": error_msg, "source": "microphone"}
            
        except sr.RequestError as e:
            error_msg = f"Recognition service error: {str(e)}"
            logger.error(error_msg)
            return False, "", {"error": error_msg, "source": "microphone"}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, "", {"error": error_msg, "source": "microphone"}
    
    def batch_transcribe(self, audio_files: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Transcribe multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Dictionary mapping file paths to transcription results
        """
        results = {}
        
        for audio_file in audio_files:
            logger.info(f"Processing: {audio_file}")
            success, text, metadata = self.transcribe_file(audio_file)
            
            results[audio_file] = {
                "success": success,
                "text": text,
                "metadata": metadata
            }
        
        return results
    
    def test_recognition(self) -> Tuple[bool, str]:
        """
        Test the speech recognition setup.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Test microphone access
            with sr.Microphone() as source:
                logger.info("Testing microphone access...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Test recognition engine
            if not self._check_engine_availability():
                return False, f"Engine '{self.engine}' is not properly configured"
            
            return True, f"Speech recognition test successful with engine: {self.engine}"
            
        except Exception as e:
            return False, f"Speech recognition test failed: {str(e)}"
    
    def get_available_engines(self) -> Dict[str, str]:
        """
        Get list of available recognition engines.
        
        Returns:
            Dictionary of engine codes and descriptions
        """
        available = {}
        
        for engine_code, description in self.ENGINES.items():
            # Create temporary instance to check availability
            try:
                temp_stt = SpeechToText(engine=engine_code, api_key=self.api_key)
                if temp_stt._check_engine_availability():
                    available[engine_code] = description
            except:
                pass  # Engine not available
        
        return available
    
    def set_engine(self, engine: str, api_key: Optional[str] = None) -> bool:
        """
        Change the recognition engine.
        
        Args:
            engine: New engine to use
            api_key: API key for the new engine (if required)
            
        Returns:
            True if engine was changed successfully, False otherwise
        """
        if engine not in self.ENGINES:
            logger.error(f"Unsupported engine: {engine}")
            return False
        
        old_engine = self.engine
        old_api_key = self.api_key
        
        self.engine = engine
        if api_key is not None:
            self.api_key = api_key
        
        if self._check_engine_availability():
            logger.info(f"Successfully changed engine from {old_engine} to {engine}")
            return True
        else:
            # Revert changes
            self.engine = old_engine
            self.api_key = old_api_key
            logger.error(f"Failed to change engine to {engine}")
            return False
    
    def configure_recognition_settings(self, **kwargs):
        """
        Configure recognition settings for the current engine.
        
        Args:
            **kwargs: Engine-specific settings
        """
        if self.engine in self.engine_settings:
            self.engine_settings[self.engine].update(kwargs)
            logger.info(f"Updated settings for {self.engine}: {kwargs}")
        else:
            logger.warning(f"No settings available for engine: {self.engine}")
