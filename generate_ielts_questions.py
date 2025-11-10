#!/usr/bin/env python
"""
IELTS Question Generator Demo Script

This script demonstrates how to use the LLM module to generate IELTS Part 3 style questions
based on input text, and optionally convert them to speech using the TTS system.

Usage:
    python generate_ielts_questions.py --text "Your input text here"
    python generate_ielts_questions.py --file input.txt
    python generate_ielts_questions.py --file input.txt --tts --output_dir ./output
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import the llm_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_module.text_processor import TextProcessor
from llm_module.llm_generator import LLMGenerator
from llm_module.question_generator import IELTSQuestionGenerator
from llm_module.tts_integration import TTSIntegration
from llm_module.config import Config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate IELTS Part 3 style questions from text')
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', type=str, help='Input text to generate questions from')
    input_group.add_argument('--file', type=str, help='Path to input text file')
    
    # Configuration
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--num_questions', type=int, default=5, 
                        help='Number of questions to generate (default: 5)')
    
    # TTS options
    parser.add_argument('--tts', action='store_true', help='Convert questions to speech')
    parser.add_argument('--output_dir', type=str, default='./output', 
                        help='Directory to save output files (default: ./output)')
    parser.add_argument('--voice', type=str, default='en-US-Neural2-F',
                        help='Voice to use for TTS (default: en-US-Neural2-F)')
    parser.add_argument('--combined', action='store_true', 
                        help='Create a combined audio file with all questions')
    
    return parser.parse_args()


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = Config(args.config)
    
    # Override config with command line arguments
    if args.num_questions:
        config.set('num_questions', args.num_questions)
    
    # Initialize text processor
    text_processor = TextProcessor()
    
    # Get input text
    if args.text:
        input_text = args.text
    else:
        try:
            input_text = text_processor.read_from_file(args.file)
        except (FileNotFoundError, IOError) as e:
            print(f"Error reading input file: {e}")
            return 1
    
    # Initialize LLM generator and question generator
    # Use QwenGenerator if config file is provided, otherwise use default
    if args.config:
        question_generator = IELTSQuestionGenerator(config_path=args.config)
    else:
        # Fallback to default configuration
        question_generator = IELTSQuestionGenerator()
    
    # Generate questions
    try:
        print(f"Generating {config.get('num_questions')} IELTS Part 3 questions...")
        questions = question_generator.generate_questions(
            input_text, 
            num_questions=config.get('num_questions')
        )
        
        # Print generated questions
        print("\nGenerated Questions:")
        for i, question in enumerate(questions):
            print(f"{i+1}. {question}")
        
        # Save questions to file
        os.makedirs(args.output_dir, exist_ok=True)
        questions_file = os.path.join(args.output_dir, 'ielts_questions.txt')
        
        with open(questions_file, 'w', encoding='utf-8') as f:
            for i, question in enumerate(questions):
                f.write(f"{i+1}. {question}\n")
        
        print(f"\nQuestions saved to: {questions_file}")
        
        # Convert to speech if requested
        if args.tts:
            print("\nConverting questions to speech...")
            tts_integration = TTSIntegration()
            
            if not tts_integration.tts_available:
                print("Error: TTS module not available")
                return 1
            
            result = tts_integration.batch_process(
                questions,
                args.output_dir,
                combined=args.combined,
                voice=args.voice
            )
            
            # Print results
            print("\nGenerated audio files:")
            for i, file_path in sorted(result['individual_files'].items()):
                print(f"Question {i+1}: {file_path}")
            
            if result['combined_file']:
                print(f"\nCombined audio: {result['combined_file']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
