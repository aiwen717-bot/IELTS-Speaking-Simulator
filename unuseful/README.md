# IELTS Question Generator

This project extends the TTS-dev system with a new module that uses a Large Language Model (LLM) to generate IELTS Part 3 style questions from English text input.

## Features

- Read English text from user input or files
- Generate IELTS Part 3 style questions using a language model
- Convert generated questions to speech using the TTS system
- Configurable number of questions and other parameters
- Batch processing with optional combined audio output

## Requirements

- Python 3.7+
- OpenAI API key (for using GPT models)
- TTS-dev system (for speech synthesis)

## Installation

1. Ensure you have the TTS-dev system installed
2. Set your OpenAI API key as an environment variable:
   ```
   set OPENAI_API_KEY=your_api_key_here
   ```
   Or create a config file (see Configuration section)

## Usage

### Using Batch Files

1. Run `run_ielts_questions.bat` to generate questions from text input
2. Run `run_ielts_questions_tts.bat` to generate questions and convert them to speech

### Using Command Line

```
# Generate questions from text
python generate_ielts_questions.py --text "Your English text here" --num_questions 5

# Generate questions from a file
python generate_ielts_questions.py --file input.txt --num_questions 5

# Generate questions and convert to speech
python generate_ielts_questions.py --text "Your English text here" --tts --output_dir ./output

# Generate questions with combined audio file
python generate_ielts_questions.py --text "Your English text here" --tts --combined
```

## Configuration

You can create a configuration file to set default parameters:

```json
{
    "api_key": "your_api_key_here",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "num_questions": 5,
    "tts_integration": {
        "enabled": true,
        "voice": "en-US-Neural2-F"
    }
}
```

Then use it with:

```
python generate_ielts_questions.py --text "Your text" --config your_config.json
```

## Module Structure

- `llm_module/`: Main module directory
  - `__init__.py`: Module initialization
  - `text_processor.py`: Text reading and preprocessing
  - `llm_generator.py`: LLM API integration
  - `question_generator.py`: IELTS question generation
  - `tts_integration.py`: Integration with TTS system
  - `config.py`: Configuration management
  - `default_config.json`: Default configuration

## Example

Input text:
```
Technology has transformed education in recent years. Students now have access to online resources, virtual classrooms, and digital tools that enhance learning experiences.
```

Generated questions:
1. How has technology changed the way students interact with teachers in educational settings?
2. What are the potential disadvantages of relying too heavily on technology in education?
3. Do you think traditional teaching methods will eventually be replaced by technology-based approaches? Why or why not?
4. How might the digital divide affect equal access to education in different parts of the world?
5. What role should governments play in regulating technology use in educational institutions?
