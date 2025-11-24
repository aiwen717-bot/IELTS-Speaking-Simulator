// IELTS Speaking Test Simulator - API Client

class IELTSApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
        this.apiEndpoint = `${this.baseUrl}/api`;
    }
    
    // Check system status
    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiEndpoint}/system-status`);
            return await response.json();
        } catch (error) {
            console.error('Error checking system status:', error);
            return {
                status: 'error',
                message: 'Failed to connect to the server'
            };
        }
    }
    
    // Convert text to speech
    async textToSpeech(text, voice = 'en-US-Neural2-A') {
        try {
            const response = await fetch(`${this.apiEndpoint}/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text, voice })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error converting text to speech:', error);
            return {
                status: 'error',
                message: 'Failed to convert text to speech'
            };
        }
    }
    
    // Process audio recording
    async processRecording(audioBlob, numQuestions = 3) {
        try {
            // Convert blob to base64
            const base64Audio = await this._blobToBase64(audioBlob);
            
            const response = await fetch(`${this.apiEndpoint}/process-recording`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio: base64Audio,
                    num_questions: numQuestions
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error processing recording:', error);
            return {
                status: 'error',
                message: 'Failed to process recording'
            };
        }
    }
    
    // Generate questions from text
    async generateQuestions(text, numQuestions = 3, generateAudio = true) {
        try {
            const response = await fetch(`${this.apiEndpoint}/generate-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text,
                    num_questions: numQuestions,
                    generate_audio: generateAudio
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error generating questions:', error);
            return {
                status: 'error',
                message: 'Failed to generate questions'
            };
        }
    }
    
    // Get Part 2 introduction audio
    async getPart2Introduction() {
        try {
            const response = await fetch(`${this.apiEndpoint}/get-part2-introduction`);
            return await response.json();
        } catch (error) {
            console.error('Error getting Part 2 introduction:', error);
            return {
                status: 'error',
                message: 'Failed to get Part 2 introduction'
            };
        }
    }
    
    // Get Part 2 question
    async getPart2Question() {
        try {
            const response = await fetch(`${this.apiEndpoint}/get-part2-question`);
            return await response.json();
        } catch (error) {
            console.error('Error getting Part 2 question:', error);
            return {
                status: 'error',
                message: 'Failed to get Part 2 question'
            };
        }
    }
    
    // Get IELTS speaking score report
    async getReport() {
        try {
            const response = await fetch(`${this.apiEndpoint}/get-report`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting report:', error);
            return {
                status: 'error',
                message: 'Failed to load report'
            };
        }
    }
    
    // Generate Part 2 audio
    async generatePart2Audio(questionData) {
        try {
            const response = await fetch(`${this.apiEndpoint}/generate-part2-audio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: questionData })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error generating Part 2 audio:', error);
            return {
                status: 'error',
                message: 'Failed to generate Part 2 audio'
            };
        }
    }
    
    // Save Part 3 recording
    async savePart3Recording(audioBlob, questionNumber) {
        try {
            const base64Audio = await this._blobToBase64(audioBlob);
            
            const response = await fetch(`${this.apiEndpoint}/save-part3-recording`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio: base64Audio,
                    question_number: questionNumber
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error saving Part 3 recording:', error);
            return {
                status: 'error',
                message: 'Failed to save Part 3 recording'
            };
        }
    }
    
    // Helper method to convert Blob to base64
    async _blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
    
    // Get audio URL
    getAudioUrl(audioPath, cacheBuster = null) {
        if (!audioPath) return null;
        
        // If it's already a full URL, return it
        if (audioPath.startsWith('http')) {
            return audioPath;
        }
        
        // Extract the filename from the path (handle both / and \ for Windows paths)
        const filename = audioPath.split(/[\/\\]/).pop();
        
        // Add cache buster parameter if provided
        const url = `${this.apiEndpoint}/audio/${filename}`;
        return cacheBuster ? `${url}?v=${cacheBuster}` : url;
    }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IELTSApiClient;
}
