"""
Speech recording module for capturing user voice input.

This module provides functionality to record audio from the microphone
and save it to WAV files for further processing.
"""

import pyaudio
import wave
import threading
import time
import logging
from typing import Optional, Tuple
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpeechRecorder:
    """
    Handles audio recording from microphone with various recording modes.
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 audio_format: int = pyaudio.paInt16):
        """
        Initialize the speech recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1 for mono, 2 for stereo)
            chunk_size: Size of audio chunks to read at once
            audio_format: PyAudio format for audio data
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        
        self.audio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
        
        # Silence detection parameters
        self.silence_threshold = 300  # Amplitude threshold for silence detection (lowered for better sensitivity)
        self.silence_duration = 3.0   # Seconds of silence before auto-stop (increased)
        self.min_recording_duration = 3.0  # Minimum recording duration before silence detection kicks in
        
    def _initialize_audio(self) -> bool:
        """
        Initialize PyAudio instance.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.audio = pyaudio.PyAudio()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False
    
    def _cleanup_audio(self):
        """Clean up PyAudio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if self.audio:
            self.audio.terminate()
            self.audio = None
    
    def list_audio_devices(self) -> list:
        """
        List available audio input devices.
        
        Returns:
            List of dictionaries containing device information
        """
        if not self._initialize_audio():
            return []
        
        devices = []
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")
        finally:
            self._cleanup_audio()
            
        return devices
    
    def _detect_silence(self, audio_data: bytes) -> bool:
        """
        Detect if audio data contains silence.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            True if silence detected, False otherwise
        """
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate RMS (Root Mean Square) amplitude
        rms = np.sqrt(np.mean(audio_array**2))
        
        return rms < self.silence_threshold
    
    def _recording_loop(self, output_path: str, max_duration: Optional[float], 
                       auto_stop_on_silence: bool, device_index: Optional[int]):
        """
        Main recording loop running in a separate thread.
        
        Args:
            output_path: Path to save the recorded audio
            max_duration: Maximum recording duration in seconds
            auto_stop_on_silence: Whether to auto-stop on silence
            device_index: Index of audio device to use
        """
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Recording started...")
            start_time = time.time()
            silence_start = None
            
            while self.is_recording:
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
                
                current_time = time.time()
                recording_duration = current_time - start_time
                
                # Check for maximum duration
                if max_duration and recording_duration >= max_duration:
                    logger.info(f"Maximum duration ({max_duration}s) reached")
                    break
                
                # Check for silence if auto-stop is enabled and minimum duration has passed
                if auto_stop_on_silence and recording_duration >= self.min_recording_duration:
                    if self._detect_silence(data):
                        if silence_start is None:
                            silence_start = current_time
                            logger.info(f"Silence detected after {recording_duration:.1f}s of recording...")
                        elif (current_time - silence_start) >= self.silence_duration:
                            logger.info(f"Silence detected for {self.silence_duration}s, stopping recording")
                            break
                    else:
                        if silence_start is not None:
                            logger.info("Speech resumed, continuing recording...")
                        silence_start = None
            
            # Save recorded audio
            self._save_recording(output_path)
            logger.info(f"Recording saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error during recording: {e}")
        finally:
            self.is_recording = False
    
    def _save_recording(self, output_path: str):
        """
        Save recorded frames to WAV file.
        
        Args:
            output_path: Path to save the audio file
        """
        try:
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
        except Exception as e:
            logger.error(f"Error saving recording: {e}")
            raise
    
    def start_recording(self, 
                       output_path: str,
                       max_duration: Optional[float] = None,
                       auto_stop_on_silence: bool = True,
                       device_index: Optional[int] = None) -> bool:
        """
        Start recording audio.
        
        Args:
            output_path: Path to save the recorded audio
            max_duration: Maximum recording duration in seconds (None for unlimited)
            auto_stop_on_silence: Whether to automatically stop on silence
            device_index: Index of audio device to use (None for default)
            
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False
        
        if not self._initialize_audio():
            return False
        
        # Reset frames
        self.frames = []
        self.is_recording = True
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(
            target=self._recording_loop,
            args=(output_path, max_duration, auto_stop_on_silence, device_index)
        )
        self.recording_thread.start()
        
        return True
    
    def stop_recording(self) -> bool:
        """
        Stop the current recording.
        
        Returns:
            True if recording stopped successfully, False otherwise
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return False
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=5.0)
            if self.recording_thread.is_alive():
                logger.warning("Recording thread did not stop gracefully")
        
        self._cleanup_audio()
        return True
    
    def record_audio(self, 
                    output_path: str,
                    duration: Optional[float] = None,
                    auto_stop_on_silence: bool = True,
                    device_index: Optional[int] = None) -> Tuple[bool, str]:
        """
        Record audio with automatic stop conditions.
        
        Args:
            output_path: Path to save the recorded audio
            duration: Recording duration in seconds (None for manual stop)
            auto_stop_on_silence: Whether to auto-stop on silence
            device_index: Index of audio device to use
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # If duration is specified, disable auto-stop on silence for manual control
            if duration is not None:
                auto_stop_on_silence = False
                logger.info(f"Manual stop mode: duration={duration}s, auto_stop_on_silence disabled")
            
            if not self.start_recording(output_path, duration, auto_stop_on_silence, device_index):
                return False, "Failed to start recording"
            
            if duration:
                # Wait for specified duration or manual interrupt
                print(f"Recording for up to {duration} seconds... Press Ctrl+C to stop early")
                try:
                    elapsed = 0
                    while self.is_recording and elapsed < duration:
                        time.sleep(0.5)
                        elapsed += 0.5
                        # Show progress every 10 seconds
                        if int(elapsed) % 10 == 0 and elapsed > 0:
                            remaining = duration - elapsed
                            print(f"Recording... {remaining:.0f} seconds remaining (Press Ctrl+C to stop)")
                except KeyboardInterrupt:
                    print("\nStopping recording manually...")
            else:
                # Wait for manual stop or auto-stop
                print("Recording... Press Ctrl+C to stop manually")
                try:
                    while self.is_recording:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nStopping recording...")
            
            self.stop_recording()
            return True, f"Recording completed and saved to {output_path}"
            
        except Exception as e:
            self.stop_recording()
            return False, f"Recording failed: {str(e)}"
    
    def test_microphone(self, duration: float = 3.0) -> Tuple[bool, str]:
        """
        Test microphone functionality.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Tuple of (success, message)
        """
        import tempfile
        import os
        
        # Create temporary file for test
        temp_file = tempfile.mktemp(suffix='.wav')
        
        try:
            success, message = self.record_audio(temp_file, duration, auto_stop_on_silence=False)
            
            if success and os.path.exists(temp_file):
                # Check file size to ensure audio was recorded
                file_size = os.path.getsize(temp_file)
                if file_size > 1000:  # At least 1KB
                    return True, f"Microphone test successful. Recorded {file_size} bytes."
                else:
                    return False, "Microphone test failed: No audio data recorded"
            else:
                return False, f"Microphone test failed: {message}"
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
