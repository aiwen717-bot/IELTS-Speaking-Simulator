"""
Integration module to connect LLM-generated questions with the TTS system.
"""
import os
import sys
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TTSIntegration:
    """
    Handles integration between the LLM question generator and TTS system.
    """
    
    def __init__(self, tts_path: Optional[str] = None):
        """
        Initialize the TTS integration module.
        
        Args:
            tts_path: Path to the TTS module directory
        """
        # Default to parent directory of llm_module
        if tts_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            tts_path = os.path.dirname(current_dir)
            
        self.tts_path = tts_path
        self._setup_tts_import()
    
    def _setup_tts_import(self) -> None:
        """
        Set up the import path for the TTS module.
        """
        if self.tts_path not in sys.path:
            sys.path.append(self.tts_path)
        
        # Try importing the TTS module
        try:
            import TTS
            self.tts_available = True
            logger.info("TTS module successfully imported")
        except ImportError:
            logger.warning("TTS module not found or could not be imported")
            self.tts_available = False
    
    def text_to_speech(self, text: str, output_path: str, voice: str = "en-US-Neural2-F") -> bool:
        """
        Convert text to speech using the TTS system.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the output audio file
            voice: Voice to use for TTS
            
        Returns:
            True if successful, False otherwise
        """
        if not self.tts_available:
            logger.error("TTS module not available")
            return False
            
        try:
            # Import TTS modules
            from TTS.api import TTS
            
            # Initialize TTS with a high-quality model
            # Try with a more natural sounding model first
            try:
                logger.info("Using high-quality TTS model: tts_models/en/ljspeech/glow-tts")
                tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")
                tts.tts_to_file(text=text, file_path=output_path)
            except Exception as e:
                logger.warning(f"Error with primary TTS model: {e}. Trying fallback model.")
                try:
                    # Fallback to VCTK model if available
                    tts = TTS(model_name="tts_models/en/vctk/vits")
                    speakers = tts.speakers
                    if speakers:
                        # Use the first speaker if available
                        speaker = speakers[0]
                        logger.info(f"Using speaker: {speaker}")
                        tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
                    else:
                        # Last resort - use basic model
                        logger.info("Switching to basic single-speaker model")
                        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                        tts.tts_to_file(text=text, file_path=output_path)
                except Exception as nested_e:
                    logger.error(f"Error with fallback TTS model: {nested_e}")
                    raise
            
            logger.info(f"Successfully generated speech at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return False
    
    def questions_to_speech(self, questions: List[str], output_dir: str, 
                           prefix: str = "question", voice: str = "en-US-Neural2-F") -> Dict[str, str]:
        """
        Convert a list of questions to speech files.
        
        Args:
            questions: List of questions to convert
            output_dir: Directory to save the output audio files
            prefix: Prefix for the output filenames
            voice: Voice to use for TTS
            
        Returns:
            Dictionary mapping question index to output file path
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        
        for i, question in enumerate(questions):
            output_path = os.path.join(output_dir, f"{prefix}_{i+1}.wav")
            success = self.text_to_speech(question, output_path, voice)
            
            if success:
                results[i] = output_path
                
        return results
    
    def batch_process(self, questions: List[str], output_dir: str, 
                     combined: bool = False, voice: str = "en-US-Neural2-F") -> Dict[str, Any]:
        """
        Process a batch of questions, converting them to speech.
        
        Args:
            questions: List of questions to convert
            output_dir: Directory to save the output audio files
            combined: Whether to also create a combined audio file
            voice: Voice to use for TTS
            
        Returns:
            Dictionary with results information
        """
        # Generate individual question audio files
        individual_files = self.questions_to_speech(questions, output_dir, "question", voice)
        
        result = {
            "individual_files": individual_files,
            "combined_file": None
        }
        
        # Generate combined audio if requested
        if combined and individual_files:
            try:
                import numpy as np
                from scipy.io import wavfile
                
                # Load all audio files
                audio_data = []
                sample_rate = None
                
                for _, file_path in sorted(individual_files.items()):
                    sr, data = wavfile.read(file_path)
                    
                    if sample_rate is None:
                        sample_rate = sr
                    elif sample_rate != sr:
                        logger.warning(f"Sample rate mismatch: {sample_rate} vs {sr}")
                        
                    # Add a second of silence between questions
                    silence = np.zeros(sample_rate, dtype=data.dtype)
                    audio_data.append(data)
                    audio_data.append(silence)
                
                # Combine audio data
                combined_audio = np.concatenate(audio_data)
                combined_path = os.path.join(output_dir, "combined_questions.wav")
                
                # Save combined audio
                wavfile.write(combined_path, sample_rate, combined_audio)
                result["combined_file"] = combined_path
                
            except Exception as e:
                logger.error(f"Error creating combined audio: {str(e)}")
        
        return result
