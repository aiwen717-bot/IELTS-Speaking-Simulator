# IELTS Speaking Test Simulator - Web Interface

This module provides a web-based user interface for the IELTS Speaking Test simulation system, integrating with the existing voice processing capabilities.

## Features

- 🎭 Realistic IELTS speaking test simulation with examiner interface
- 🎤 Audio recording with visual feedback
- 🔊 Text-to-speech for examiner questions
- 📊 Visual progress tracking
- 📝 Complete IELTS test structure (Parts 1, 2, and 3)
- 🔄 Integration with existing voice-to-questions module

## Requirements

- Python 3.7+
- Flask and Flask-CORS
- Modern web browser with microphone access
- TTS-dev system (for speech synthesis)

## Installation

1. Ensure you have the TTS-dev system installed
2. Install required Python packages:
   ```
   pip install flask flask-cors
   ```

## Usage

### Starting the Web Server

Run the provided batch file:
```
run_server.bat
```

Or start manually with Python:
```
python server.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

### Using the Interface

1. Click "Begin Test" to start the IELTS speaking test simulation
2. Listen to the examiner's questions (click "Play Audio" if needed)
3. Click "Start Recording" to record your response
4. Click "Stop Recording" when finished
5. The system will automatically proceed through the test parts

## Test Structure

The interface simulates a complete IELTS speaking test:

- **Introduction**: Basic identification questions
- **Part 1**: General questions on familiar topics
- **Part 2**: Long-turn speaking on a given topic (with preparation time)
- **Part 3**: Discussion of more abstract issues related to the Part 2 topic

## Integration with Existing System

This web interface integrates with the existing voice-to-questions module to:

1. Record user voice input
2. Process recordings to generate follow-up questions
3. Convert questions to speech using the TTS system

## Technical Architecture

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask Python server
- **API**: RESTful endpoints for voice processing
- **Integration**: Connection to existing voice_to_questions module

## Directory Structure

```
web_interface/
├── css/
│   ├── styles.css
│   └── ielts-test.css
├── images/
│   └── examiner.jpg
├── js/
│   ├── app.js
│   ├── api-client.js
│   └── ielts-test-flow.js
├── index.html
├── server.py
├── run_server.bat
└── README.md
```

## Customization

- Add different examiner photos in the `images` directory
- Modify test questions and structure in `ielts-test-flow.js`
- Adjust the UI appearance in the CSS files

## Troubleshooting

- If the server fails to start, check that all required Python packages are installed
- If audio recording doesn't work, ensure your browser has permission to access the microphone
- If TTS doesn't work, the system will fall back to browser-based speech synthesis
