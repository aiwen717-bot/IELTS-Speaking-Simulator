#!/usr/bin/env python
"""
Test script to help debug and adjust recording settings.
"""

import os
import sys
import time
import argparse

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_module.speech_recorder import SpeechRecorder
from llm_module.speech_to_text import SpeechToText


def test_microphone_levels():
    """Test microphone input levels to help adjust silence threshold."""
    print("Testing microphone input levels...")
    print("This will help you determine the right silence threshold.")
    print("Speak normally into your microphone for 10 seconds.")
    print("Press Enter to start...")
    input()
    
    recorder = SpeechRecorder()
    
    if not recorder._initialize_audio():
        print("Failed to initialize audio")
        return
    
    try:
        # Open audio stream
        stream = recorder.audio.open(
            format=recorder.audio_format,
            channels=recorder.channels,
            rate=recorder.sample_rate,
            input=True,
            frames_per_buffer=recorder.chunk_size
        )
        
        print("Recording for 10 seconds... Speak normally!")
        start_time = time.time()
        levels = []
        
        while time.time() - start_time < 10:
            data = stream.read(recorder.chunk_size, exception_on_overflow=False)
            
            # Calculate RMS level
            import numpy as np
            audio_array = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array**2))
            levels.append(rms)
            
            # Print current level
            print(f"Current level: {rms:.0f}", end='\r')
            time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        
        # Analyze levels
        import numpy as np
        levels = np.array(levels)
        
        print(f"\n\nAnalysis:")
        print(f"Average level: {np.mean(levels):.0f}")
        print(f"Maximum level: {np.max(levels):.0f}")
        print(f"Minimum level: {np.min(levels):.0f}")
        print(f"Standard deviation: {np.std(levels):.0f}")
        
        # Suggest threshold
        suggested_threshold = np.mean(levels) * 0.3  # 30% of average
        print(f"\nSuggested silence threshold: {suggested_threshold:.0f}")
        print(f"Current default threshold: {recorder.silence_threshold}")
        
        if suggested_threshold < recorder.silence_threshold:
            print("⚠️  Your microphone might be too quiet. Consider:")
            print("   - Increasing microphone volume in system settings")
            print("   - Moving closer to the microphone")
            print(f"   - Using a lower threshold like {suggested_threshold:.0f}")
        elif suggested_threshold > recorder.silence_threshold * 2:
            print("⚠️  Your microphone might be too loud or noisy. Consider:")
            print("   - Decreasing microphone volume in system settings")
            print("   - Using a quieter environment")
            print(f"   - Using a higher threshold like {suggested_threshold:.0f}")
        else:
            print("✅ Your microphone levels look good!")
            
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        recorder._cleanup_audio()


def test_recording_with_settings(threshold=300, duration=4.0, min_duration=3.0):
    """Test recording with specific settings."""
    print(f"\nTesting recording with:")
    print(f"- Silence threshold: {threshold}")
    print(f"- Silence duration: {duration}s")
    print(f"- Minimum recording duration: {min_duration}s")
    print("\nPress Enter to start recording...")
    input()
    
    recorder = SpeechRecorder()
    recorder.silence_threshold = threshold
    recorder.silence_duration = duration
    recorder.min_recording_duration = min_duration
    
    output_file = "test_recording.wav"
    
    print("Recording started... Speak into your microphone!")
    success, message = recorder.record_audio(
        output_path=output_file,
        auto_stop_on_silence=True
    )
    
    if success:
        print(f"✅ {message}")
        
        # Test transcription
        print("Testing transcription...")
        stt = SpeechToText(engine='google')  # Use Google for quick test
        success, text, metadata = stt.transcribe_file(output_file)
        
        if success:
            print(f"✅ Transcription: '{text}'")
        else:
            print(f"❌ Transcription failed: {metadata.get('error', 'Unknown error')}")
        
        # Clean up
        try:
            os.remove(output_file)
        except:
            pass
    else:
        print(f"❌ {message}")


def main():
    parser = argparse.ArgumentParser(description='Test recording settings')
    parser.add_argument('--test-levels', action='store_true', 
                       help='Test microphone input levels')
    parser.add_argument('--test-recording', action='store_true',
                       help='Test recording with current settings')
    parser.add_argument('--threshold', type=int, default=300,
                       help='Silence threshold to test')
    parser.add_argument('--silence-duration', type=float, default=4.0,
                       help='Silence duration to test')
    parser.add_argument('--min-duration', type=float, default=3.0,
                       help='Minimum recording duration')
    
    args = parser.parse_args()
    
    if args.test_levels:
        test_microphone_levels()
    
    if args.test_recording:
        test_recording_with_settings(
            threshold=args.threshold,
            duration=args.silence_duration,
            min_duration=args.min_duration
        )
    
    if not args.test_levels and not args.test_recording:
        print("Recording Settings Test Tool")
        print("=" * 30)
        print("Choose a test:")
        print("1. Test microphone levels (recommended first)")
        print("2. Test recording with current settings")
        print("3. Both")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            test_microphone_levels()
        
        if choice in ['2', '3']:
            test_recording_with_settings()


if __name__ == "__main__":
    main()
