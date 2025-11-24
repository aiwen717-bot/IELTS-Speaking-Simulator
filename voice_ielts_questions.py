#!/usr/bin/env python
"""
Voice-driven IELTS Question Generator

This script extends the original IELTS question generator to support voice input.
Users can speak their input instead of typing text, and the system will:
1. Record their voice
2. Convert speech to text
3. Generate IELTS questions from the text
4. Optionally convert questions back to speech

Usage:
    # Voice input mode (record from microphone)
    python voice_ielts_questions.py --voice-input --output_dir ./output

    # Process existing audio file
    python voice_ielts_questions.py --audio-file input.wav --output_dir ./output
    
    # Voice input with specific settings
    python voice_ielts_questions.py --voice-input --duration 30 --stt-engine whisper --num_questions 3
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any, Optional

# Add the current directory to the path so we can import the llm_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_module.voice_to_questions import VoiceToQuestions
from llm_module.config import Config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate IELTS Part 3 style questions from voice input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record voice input and generate questions
  python voice_ielts_questions.py --voice-input

  # Process existing audio file
  python voice_ielts_questions.py --audio-file recording.wav

  # Voice input with custom settings
  python voice_ielts_questions.py --voice-input --duration 60 --stt-engine whisper

  # Test system components
  python voice_ielts_questions.py --test-system
        """
    )
    
    # Input mode (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('--voice-input', action='store_true',
                            help='Record voice input from microphone')
    input_group.add_argument('--audio-file', type=str,
                            help='Path to audio file to process')
    input_group.add_argument('--test-system', action='store_true',
                            help='Test all system components')
    
    # Recording settings
    parser.add_argument('--duration', type=float,
                        help='Recording duration in seconds (default: auto-stop on silence)')
    parser.add_argument('--device-index', type=int,
                        help='Audio device index to use for recording')
    
    # Speech-to-text settings
    parser.add_argument('--stt-engine', type=str, default='google',
                        choices=['google', 'whisper', 'sphinx', 'wit', 'azure', 'ibm'],
                        help='Speech recognition engine (default: google)')
    parser.add_argument('--stt-language', type=str, default='en-US',
                        help='Language for speech recognition (default: en-US)')
    parser.add_argument('--stt-api-key', type=str,
                        help='API key for speech recognition service (if required)')
    
    # Question generation settings
    parser.add_argument('--config', type=str,
                        help='Path to configuration file')
    parser.add_argument('--num_questions', type=int, default=5,
                        help='Number of questions to generate (default: 5)')
    
    # Output settings
    parser.add_argument('--output_dir', type=str, default='./voice_output',
                        help='Directory to save output files (default: ./voice_output)')
    parser.add_argument('--no-audio', action='store_true',
                        help='Skip generating audio files for questions')
    parser.add_argument('--no-transcript', action='store_true',
                        help='Skip saving transcript file')
    
    # TTS settings
    parser.add_argument('--voice', type=str, default='en-US-Neural2-A',
                        help='Voice to use for TTS (default: en-US-Neural2-A)')
    
    # Utility options
    parser.add_argument('--list-devices', action='store_true',
                        help='List available audio input devices and exit')
    parser.add_argument('--list-engines', action='store_true',
                        help='List available speech recognition engines and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    return parser.parse_args()


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    import logging
    
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def list_audio_devices():
    """List available audio input devices."""
    try:
        from llm_module.speech_recorder import SpeechRecorder
        
        recorder = SpeechRecorder()
        devices = recorder.list_audio_devices()
        
        if not devices:
            print("No audio input devices found.")
            return
        
        print("Available audio input devices:")
        print("-" * 50)
        for device in devices:
            print(f"Index: {device['index']}")
            print(f"Name: {device['name']}")
            print(f"Channels: {device['channels']}")
            print(f"Sample Rate: {device['sample_rate']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error listing audio devices: {e}")


def list_speech_engines():
    """List available speech recognition engines."""
    try:
        from llm_module.speech_to_text import SpeechToText
        
        # Create a temporary instance to check available engines
        stt = SpeechToText()
        available_engines = stt.get_available_engines()
        
        if not available_engines:
            print("No speech recognition engines available.")
            return
        
        print("Available speech recognition engines:")
        print("-" * 50)
        for engine_code, description in available_engines.items():
            print(f"Code: {engine_code}")
            print(f"Description: {description}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error listing speech engines: {e}")


def test_system_components():
    """Test all system components."""
    print("Testing Voice-to-Questions system components...")
    print("=" * 60)
    
    try:
        # Initialize the system
        voice_system = VoiceToQuestions()
        
        # Run system test
        test_results = voice_system.test_system()
        
        # Display results
        for component, result in test_results.items():
            if component == 'overall':
                continue
                
            status = "[PASS]" if result['available'] else "[FAIL]"
            print(f"{component.replace('_', ' ').title()}: {status}")
            print(f"  Message: {result['message']}")
            print()
        
        # Overall status
        overall_status = "[PASS]" if test_results['overall']['success'] else "[FAIL]"
        print(f"Overall System Status: {overall_status}")
        print(f"Message: {test_results['overall']['message']}")
        
        return test_results['overall']['success']
        
    except Exception as e:
        print(f"System test failed: {e}")
        return False


def process_voice_input(args):
    """Process voice input and generate questions."""
    try:
        # Initialize the voice-to-questions system
        voice_system = VoiceToQuestions(
            config_path=args.config,
            stt_engine=args.stt_engine,
            stt_language=args.stt_language,
            stt_api_key=args.stt_api_key
        )
        
        print("Voice-to-Questions System Ready")
        print("=" * 40)
        
        if args.voice_input:
            print("Preparing to record voice input...")
            if args.duration:
                print(f"Recording duration: {args.duration} seconds")
            else:
                print("Recording will auto-stop on silence (2 seconds)")
            
            print("\nPress Enter to start recording, or Ctrl+C to cancel...")
            try:
                input()
            except KeyboardInterrupt:
                print("\nCancelled by user.")
                return False
            
            # Process voice input
            results = voice_system.process_voice_input(
                duration=args.duration,
                num_questions=args.num_questions,
                output_dir=args.output_dir,
                generate_audio=not args.no_audio,
                save_transcript=not args.no_transcript
            )
            
        elif args.audio_file:
            if not os.path.exists(args.audio_file):
                print(f"Error: Audio file not found: {args.audio_file}")
                return False
            
            print(f"Processing audio file: {args.audio_file}")
            
            # Process audio file
            results = voice_system.process_audio_file(
                audio_file_path=args.audio_file,
                num_questions=args.num_questions,
                output_dir=args.output_dir,
                generate_audio=not args.no_audio,
                save_transcript=not args.no_transcript
            )
        
        # Display results
        print("\nProcessing Results:")
        print("=" * 40)
        
        if results['success']:
            print("[SUCCESS] Processing completed successfully!")
            
            # Show transcript
            if results['transcript']:
                print(f"\nTranscript ({len(results['transcript'])} characters):")
                print("-" * 40)
                print(results['transcript'][:200] + "..." if len(results['transcript']) > 200 else results['transcript'])
            
            # Show questions
            if results['questions']:
                print(f"\nGenerated Questions ({len(results['questions'])}):")
                print("-" * 40)
                for i, question in enumerate(results['questions']):
                    print(f"{i+1}. {question}")
            
            # Show output files
            if results['output_files']:
                print(f"\nOutput Files:")
                print("-" * 40)
                for file_path in results['output_files']:
                    print(f"  {file_path}")
            
            # Show audio files
            if results['audio_files']:
                print(f"\nAudio Files:")
                print("-" * 40)
                for key, file_path in results['audio_files'].items():
                    if key == 'combined':
                        print(f"  Combined: {file_path}")
                    else:
                        print(f"  Question {key+1}: {file_path}")
        
        else:
            print("[FAILED] Processing failed!")
            if results['errors']:
                print("\nErrors:")
                for error in results['errors']:
                    print(f"  - {error}")
        
        return results['success']
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


def main():
    """Main function."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle utility commands
    if args.list_devices:
        list_audio_devices()
        return 0
    
    if args.list_engines:
        list_speech_engines()
        return 0
    
    if args.test_system:
        success = test_system_components()
        return 0 if success else 1
    
    # Ensure we have an input mode
    if not args.voice_input and not args.audio_file:
        print("Error: Please specify either --voice-input or --audio-file")
        print("Use --help for usage information")
        return 1
    
    # Process input
    success = process_voice_input(args)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
