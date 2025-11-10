"""
Generate audio file for Part 2 introduction text.
This script converts the text in part2_introduction.txt to an audio file.
"""

import os
import sys
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import TTS integration
from llm_module.tts_integration import TTSIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate audio for Part 2 introduction."""
    # Path for the introduction text and audio
    web_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_output')
    intro_text_path = os.path.join(web_output_dir, "part2_introduction.txt")
    intro_audio_path = os.path.join(web_output_dir, "part2_introduction.wav")
    
    # Check if the introduction text file exists
    if not os.path.exists(intro_text_path):
        logger.error(f"Introduction text file not found: {intro_text_path}")
        return False
    
    # Read the introduction text
    try:
        with open(intro_text_path, 'r', encoding='utf-8') as f:
            intro_text = f.read().strip()
        
        if not intro_text:
            logger.error("Introduction text file is empty")
            return False
        
        logger.info(f"Read introduction text: {intro_text[:50]}...")
    except Exception as e:
        logger.error(f"Error reading introduction text: {e}")
        return False
    
    # Initialize TTS integration
    try:
        tts = TTSIntegration()
        logger.info("TTS integration initialized")
    except Exception as e:
        logger.error(f"Error initializing TTS integration: {e}")
        return False
    
    # Generate audio
    try:
        logger.info(f"Generating audio for introduction text to {intro_audio_path}")
        success = tts.text_to_speech(intro_text, intro_audio_path)
        
        if success:
            logger.info(f"Successfully generated audio: {intro_audio_path}")
            return True
        else:
            logger.error("Failed to generate audio")
            return False
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting generation of Part 2 introduction audio")
    success = main()
    if success:
        logger.info("Successfully generated Part 2 introduction audio")
    else:
        logger.error("Failed to generate Part 2 introduction audio")
