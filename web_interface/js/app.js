// IELTS Speaking Test Simulator - Main Application (Part 2 & Part 3 Focus)

// DOM Elements
const beginBtn = document.getElementById('begin-btn');
const playBtn = document.getElementById('play-btn');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const examinerStatus = document.getElementById('examiner-status');
const currentPart = document.getElementById('current-part');
const partDescription = document.getElementById('part-description');
const questionDisplay = document.getElementById('question-display');
const timerElement = document.getElementById('timer');
const progressIndicator = document.getElementById('progress-indicator');
const visualizer = document.getElementById('visualizer');
const examinerImage = document.getElementById('examiner-image');

// Audio Context for recording and visualization
let audioContext;
let mediaRecorder;
let audioChunks = [];
let recordingStream;
let analyser;
let visualizerContext = visualizer.getContext('2d');
let recordingStartTime;
let timerInterval;
let isRecording = false;
let isPlaying = false;

// Initialize API client
const apiClient = new IELTSApiClient();

// Test state
const testState = {
    phase: 'waiting', // waiting, part2_intro, part2_playing, part2_recording, part3_playing, part3_recording, review
    part2Question: null,
    part3Questions: [],
    currentPart3Index: 0,
    recordings: {},
    transcripts: {},
    audioFiles: {},
    systemReady: false,
    part3StartTime: null,
    part3TotalTimeLimit: 8 * 60 * 1000, // 8 minutes in milliseconds
    part3QuestionTimeLimit: 2 * 60 * 1000 // 2 minutes per question in milliseconds
};

// Initialize the application
async function init() {
    setupEventListeners();
    setupVisualizer();
    await checkSystemStatus();
}

// Check system status
async function checkSystemStatus() {
    updateExaminerStatus('Checking system status...');
    
    try {
        const response = await apiClient.checkSystemStatus();
        
        if (response.status === 'success') {
            testState.systemReady = true;
            updateExaminerStatus('Ready to begin the test');
            console.log('System status:', response);
        } else {
            updateExaminerStatus('System not ready. Check console for details.');
            console.error('System status error:', response.message);
        }
    } catch (error) {
        updateExaminerStatus('Failed to connect to server');
        console.error('Connection error:', error);
        
        // Enable fallback mode (browser TTS)
        testState.systemReady = true;
        console.log('Using fallback mode with browser TTS');
    }
}

// Set up event listeners for buttons
function setupEventListeners() {
    beginBtn.addEventListener('click', beginTest);
    playBtn.addEventListener('click', playAudio);
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
}

// Setup audio visualizer
function setupVisualizer() {
    visualizer.width = visualizer.offsetWidth;
}

// Begin the test - Play introduction, then load and play Part 2 question
async function beginTest() {
    if (!testState.systemReady) {
        alert('System is not ready. Please wait for initialization to complete.');
        return;
    }
    
    beginBtn.disabled = true;
    updateExaminerStatus('Starting the test...');
    
    try {
        // First play the Part 2 introduction
        await playPart2Introduction();
        
        // Then load and play the Part 2 question
        await loadAndPlayPart2Question();
    } catch (error) {
        updateExaminerStatus('Error starting test');
        console.error('Error in beginTest:', error);
        beginBtn.disabled = false;
    }
}

// Sleep function for waiting
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Play the Part 2 introduction audio
async function playPart2Introduction() {
    // Set the phase to part2_intro
    testState.phase = 'part2_intro';
    updateTestDisplay();
    updateExaminerStatus('Playing Part 2 introduction...');
    
    try {
        // Get the Part 2 introduction audio
        const response = await apiClient.getPart2Introduction();
        
        if (response.status === 'success') {
            // Play the introduction audio directly from web_output directory
            // Use cache_buster to force reload new audio
            const audioUrl = apiClient.getAudioUrl(response.audio_path, response.cache_buster);
            console.log('Playing Part 2 introduction from:', audioUrl);
            await playAudioFromUrl(audioUrl);
            
            // Wait for 1 second after introduction audio finishes
            updateExaminerStatus('Preparing Part 2 question...');
            await sleep(1000);
            
            return true;
        } else {
            console.error('Failed to get Part 2 introduction:', response.message);
            // Continue even if introduction fails
            return false;
        }
    } catch (error) {
        console.error('Error playing Part 2 introduction:', error);
        // Continue even if introduction fails
        return false;
    }
}

// Load the Part 2 question and play audio
async function loadAndPlayPart2Question() {
    updateExaminerStatus('Loading Part 2 question...');
    
    try {
        // Get Part 2 question
        const response = await apiClient.getPart2Question();
        
        if (response.status === 'success') {
            testState.part2Question = response.question;
            testState.phase = 'part2_playing';
            
            // Update UI to show the question
            updateTestDisplay();
            
            // Generate and play Part 2 audio
            await playPart2Audio();
        } else {
            updateExaminerStatus('Failed to load question');
            console.error('Error loading Part 2 question:', response.message);
            beginBtn.disabled = false;
        }
    } catch (error) {
        updateExaminerStatus('Error loading question');
        console.error('Error in loadAndPlayPart2Question:', error);
        beginBtn.disabled = false;
    }
}

// Update the test display based on current state
function updateTestDisplay() {
    switch(testState.phase) {
        case 'part2_intro':
            currentPart.textContent = 'Part 2';
            partDescription.textContent = 'Introduction to Part 2';
            questionDisplay.innerHTML = `<p class="question-hidden">The examiner is introducing Part 2 of the test...</p>`;
            progressIndicator.style.width = '20%';
            break;
            
        case 'part2_playing':
        case 'part2_recording':
            currentPart.textContent = 'Part 2';
            partDescription.textContent = 'Long-turn speaking: You will have 1 minute to prepare and then speak for 1-2 minutes.';
            
            if (testState.part2Question) {
                questionDisplay.innerHTML = formatPart2Question(testState.part2Question);
            }
            
            progressIndicator.style.width = '25%';
            break;
            
        case 'part3_playing':
            currentPart.textContent = 'Part 3';
            partDescription.textContent = 'Discussion: Answer questions related to the Part 2 topic.';
            
            // Hide question text during Part 3 playing phase
            questionDisplay.innerHTML = `<p class="question-hidden">Listen carefully to the question...</p>`;
            
            progressIndicator.style.width = `${50 + (testState.currentPart3Index / testState.part3Questions.length) * 50}%`;
            break;
            
        case 'part3_recording':
            currentPart.textContent = 'Part 3';
            partDescription.textContent = 'Discussion: Answer questions related to the Part 2 topic.';
            
            // Show question text during recording so user can refer to it
            if (testState.part3Questions.length > 0) {
                const currentQuestion = testState.part3Questions[testState.currentPart3Index];
                questionDisplay.innerHTML = `<p class="question">Question ${testState.currentPart3Index + 1}: ${currentQuestion}</p>`;
            }
            
            progressIndicator.style.width = `${50 + (testState.currentPart3Index / testState.part3Questions.length) * 50}%`;
            break;
            
        case 'review':
            currentPart.textContent = 'Test Review';
            partDescription.textContent = 'Review your responses and listen to the questions and answers.';
            
            displayReviewPage();
            
            progressIndicator.style.width = '100%';
            break;
    }
}

// Format Part 2 question for display
function formatPart2Question(questionData) {
    let html = `<div class="cue-card">
        <h4>${questionData.topic}</h4>
        <p>You should say:</p>
        <ul>`;
        
    questionData.points.forEach(point => {
        html += `<li>${point}</li>`;
    });
    
    html += `</ul></div>`;
    return html;
}

// Play Part 2 audio
async function playPart2Audio() {
    if (!testState.part2Question) return;
    
    updateExaminerStatus('Generating Part 2 audio...');
    
    try {
        const response = await apiClient.generatePart2Audio(testState.part2Question);
        
        if (response.status === 'success') {
            const audioUrl = apiClient.getAudioUrl(response.audio_path);
            await playAudioFromUrl(audioUrl);
            
            // After Part 2 audio finishes, enable recording
            updateExaminerStatus('You may now start recording your Part 2 response');
            recordBtn.disabled = false;
            playBtn.disabled = true; // Disable replay for Part 2
            testState.phase = 'part2_recording';
        } else {
            console.error('Failed to generate Part 2 audio:', response.message);
            // Fallback to browser TTS
            await playPart2WithBrowserTTS();
        }
    } catch (error) {
        console.error('Error playing Part 2 audio:', error);
        await playPart2WithBrowserTTS();
    }
}

// Fallback Part 2 audio using browser TTS
async function playPart2WithBrowserTTS() {
    if (!testState.part2Question) return;
    
    const text = `Here's your topic for Part 2. ${testState.part2Question.topic}. You should say: ${testState.part2Question.points.join(', ')}. You have one minute to prepare. You can make notes if you wish.`;
    
    await useSpeechSynthesis(text);
    
    updateExaminerStatus('You may now start recording your Part 2 response');
    recordBtn.disabled = false;
    playBtn.disabled = true;
    testState.phase = 'part2_recording';
}

// Play audio from URL
function playAudioFromUrl(audioUrl) {
    return new Promise((resolve, reject) => {
        const audio = new Audio(audioUrl);
        
        isPlaying = true;
        updateExaminerStatus('Speaking...');
        examinerImage.parentElement.classList.add('speaking');
        
        audio.onended = () => {
            isPlaying = false;
            examinerImage.parentElement.classList.remove('speaking');
            resolve();
        };
        
        audio.onerror = () => {
            isPlaying = false;
            examinerImage.parentElement.classList.remove('speaking');
            reject(new Error('Audio playback failed'));
        };
        
        audio.play().catch(reject);
    });
}

// Use speech synthesis as a fallback for TTS
function useSpeechSynthesis(text) {
    return new Promise((resolve) => {
        if ('speechSynthesis' in window) {
            isPlaying = true;
            updateExaminerStatus('Speaking...');
            examinerImage.parentElement.classList.add('speaking');
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            
            utterance.onend = () => {
                isPlaying = false;
                examinerImage.parentElement.classList.remove('speaking');
                resolve();
            };
            
            speechSynthesis.speak(utterance);
        } else {
            console.error('Speech synthesis not supported');
            resolve();
        }
    });
}

// Play audio (for Part 3 questions)
async function playAudio() {
    if (testState.phase !== 'part3_playing') return;
    
    if (testState.part3Questions.length === 0) {
        alert('No Part 3 questions available. Please complete Part 2 first.');
        return;
    }
    
    const currentQuestion = testState.part3Questions[testState.currentPart3Index];
    
    try {
        const response = await apiClient.textToSpeech(currentQuestion);
        
        if (response.status === 'success') {
            const audioUrl = apiClient.getAudioUrl(response.audio_path);
            await playAudioFromUrl(audioUrl);
        } else {
            await useSpeechSynthesis(currentQuestion);
        }
        
        // After playing, enable recording
        updateExaminerStatus(`Waiting for your answer to question ${testState.currentPart3Index + 1}`);
        recordBtn.disabled = false;
        testState.phase = 'part3_recording';
        
    } catch (error) {
        console.error('Error playing Part 3 audio:', error);
        await useSpeechSynthesis(currentQuestion);
        updateExaminerStatus(`Waiting for your answer to question ${testState.currentPart3Index + 1}`);
        recordBtn.disabled = false;
        testState.phase = 'part3_recording';
    }
}

// Start recording
async function startRecording() {
    if (isRecording) return;
    
    try {
        // Request microphone access
        recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Setup audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(recordingStream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        
        // Setup media recorder
        mediaRecorder = new MediaRecorder(recordingStream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = handleRecordingStopped;
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        recordBtn.classList.add('recording');
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        playBtn.disabled = true;
        updateExaminerStatus('Listening to your response...');
        examinerImage.parentElement.classList.add('listening');
        
        // Start timer
        recordingStartTime = Date.now();
        startTimer();
        
        // Start visualizer
        drawVisualizer();
        
        // Set up auto-stop timers based on current phase
        if (testState.phase === 'part2_recording') {
            // Part 2: 4 minutes maximum
            setTimeout(() => {
                if (isRecording) {
                    console.log('Part 2 recording auto-stopped after 4 minutes');
                    stopRecording();
                }
            }, 240000); // 4 minutes
        } else if (testState.phase === 'part3_recording') {
            // Part 3: 2 minutes per question maximum
            setTimeout(() => {
                if (isRecording) {
                    console.log('Part 3 recording auto-stopped after 2 minutes');
                    stopRecording();
                }
            }, 120000); // 2 minutes
            
            // Also check total Part 3 time limit
            if (testState.part3StartTime) {
                const timeElapsed = Date.now() - testState.part3StartTime;
                const timeRemaining = testState.part3TotalTimeLimit - timeElapsed;
                
                if (timeRemaining <= 0) {
                    console.log('Part 3 total time limit reached');
                    stopRecording();
                    finishTest();
                    return;
                } else if (timeRemaining < 120000) {
                    // Less than 2 minutes remaining, set shorter timeout
                    setTimeout(() => {
                        if (isRecording) {
                            console.log('Part 3 recording auto-stopped due to total time limit');
                            stopRecording();
                            finishTest();
                        }
                    }, timeRemaining);
                }
            }
        }
        
    } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Error accessing microphone. Please ensure your browser has permission to use the microphone.');
    }
}

// Stop recording
function stopRecording() {
    if (!isRecording) return;
    
    mediaRecorder.stop();
    recordingStream.getTracks().forEach(track => track.stop());
    
    // Update UI
    isRecording = false;
    recordBtn.classList.remove('recording');
    stopBtn.disabled = true;
    updateExaminerStatus('Processing your response...');
    
    // Stop timer
    stopTimer();
    
    // Stop visualizer
    cancelAnimationFrame(drawVisualizer);
}

// Handle recording stopped
async function handleRecordingStopped() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    
    if (testState.phase === 'part2_recording') {
        // Process Part 2 recording and generate Part 3 questions
        await processPart2Recording(audioBlob);
    } else if (testState.phase === 'part3_recording') {
        // Save Part 3 recording
        await savePart3Recording(audioBlob);
    }
}

// Process Part 2 recording and generate Part 3 questions
async function processPart2Recording(audioBlob) {
    updateExaminerStatus('Saving recording, please wait...');
    
    try {
        // 添加延迟，确保录音文件被完全保存
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        updateExaminerStatus('Processing recording and generating Part 3 questions, please wait...');
        
        // 使用processRecording API，该API集成了run_voice_manual_4min.bat的功能
        const response = await apiClient.processRecording(audioBlob, 3);
        
        // 添加额外的处理时间，确保后端有足够时间处理录音和生成问题
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        if (response.status === 'success' && response.questions && response.questions.length > 0) {
            testState.part3Questions = response.questions;
            testState.currentPart3Index = 0;
            testState.phase = 'part3_playing';
            testState.part3StartTime = Date.now(); // 开始Part 3计时器
            
            // 存储转录文本以供回顾
            if (response.transcript) {
                testState.transcripts['part2'] = response.transcript;
            }
            
            // 存储音频文件路径
            if (response.audio_files) {
                // 保存Part2回答的音频路径
                testState.audioFiles['part2'] = 'part2_answer.wav';
                
                // 保存Part3问题的音频路径
                for (const key in response.audio_files) {
                    testState.audioFiles[key] = response.audio_files[key];
                }
            }
            
            // 更新UI
            updateTestDisplay();
            updateExaminerStatus('Part 3 questions generated. Click "Play Audio" to hear the first question.');
            
            // 启用播放按钮
            playBtn.disabled = false;
            recordBtn.disabled = true;
            
            console.log('生成的Part 3问题:', testState.part3Questions);
            console.log('音频文件:', testState.audioFiles);
            
        } else {
            console.error('生成Part 3问题失败:', response.message || '没有返回问题');
            updateExaminerStatus('Failed to generate Part 3 questions. Using default questions.');
            
            // 使用与常见话题相关的默认Part 3问题
            testState.part3Questions = [
                'What do you think are the main benefits of this topic to society?',
                'What changes have occurred in this area in your country in recent years?',
                'What role do you think technology plays in this field?',
                'Do you think this will become more or less important in the future? Why?',
                'How might this topic affect future generations?'
            ];
            testState.currentPart3Index = 0;
            testState.phase = 'part3_playing';
            testState.part3StartTime = Date.now();
            
            updateTestDisplay();
            playBtn.disabled = false;
            recordBtn.disabled = true;
        }
    } catch (error) {
        console.error('处理Part 2录音时出错:', error);
        updateExaminerStatus('Error processing recording. Please try again.');
        recordBtn.disabled = false;
    }
}

// Save Part 3 recording
async function savePart3Recording(audioBlob) {
    const questionNumber = testState.currentPart3Index + 1;
    
    try {
        // 添加状态更新，告知用户正在保存录音
        updateExaminerStatus(`Saving answer to question ${questionNumber}, please wait...`);
        
        // 添加延迟，确保录音文件被完全保存
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 调用API保存录音
        const response = await apiClient.savePart3Recording(audioBlob, questionNumber);
        
        // 添加额外的处理时间，确保后端有足够时间处理录音
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (response.status === 'success') {
            console.log(`Part 3回答${questionNumber}已保存:`, response.message);
            
            // 存储转录文本和音频信息以供回顾
            if (response.transcript) {
                testState.transcripts[`part3_q${questionNumber}`] = response.transcript;
            }
            
            // 存储音频文件路径 - 使用固定的文件名格式，而不是依赖响应中的路径
            const audioFileName = `part3_answer_${questionNumber}.wav`;
            testState.audioFiles[`part3_q${questionNumber}`] = audioFileName;
            console.log(`保存Part3回答${questionNumber}的音频路径:`, audioFileName);
            
            // 检查时间限制
            const timeElapsed = Date.now() - testState.part3StartTime;
            const timeRemaining = testState.part3TotalTimeLimit - timeElapsed;
            
            // 移至下一个问题或结束
            testState.currentPart3Index++;
            
            if (testState.currentPart3Index < testState.part3Questions.length && timeRemaining > 30000) {
                // 还有更多问题可用，且剩余时间充足（至少30秒）
                testState.phase = 'part3_playing';
                updateTestDisplay();
                
                const remainingMinutes = Math.floor(timeRemaining / 60000);
                updateExaminerStatus(`Question ${questionNumber} saved. ${remainingMinutes} minutes remaining. Click "Play Audio" to hear the next question.`);
                playBtn.disabled = false;
                recordBtn.disabled = true;
            } else {
                // 所有问题已完成或时间限制已到
                finishTest();
            }
        } else {
            console.error('保存Part 3录音失败:', response.message);
            updateExaminerStatus('Failed to save recording. Please try again.');
            recordBtn.disabled = false;
        }
    } catch (error) {
        console.error('保存Part 3录音时出错:', error);
        updateExaminerStatus('Error saving recording. Please try again.');
        recordBtn.disabled = false;
    }
}

// Finish the test and show review page
function finishTest() {
    testState.phase = 'review';
    updateTestDisplay();
    updateExaminerStatus('Test completed! Review your responses below.');
    
    // Disable all control buttons
    playBtn.disabled = true;
    recordBtn.disabled = true;
    stopBtn.disabled = true;
}

// Display the review page
function displayReviewPage() {
    // Create two-column layout: left for Q&A review, right for score report
    let reviewHTML = '<div class="review-wrapper">';
    
    // Left panel: Q&A Review
    reviewHTML += '<div class="review-left-panel">';
    reviewHTML += '<div class="review-panel-header"><h3>Your Responses</h3></div>';
    reviewHTML += '<div class="review-panel-content">';
    
    // Part 2 Review
    if (testState.part2Question) {
        reviewHTML += '<div class="review-section">';
        reviewHTML += '<h3>Part 2 - Long Turn</h3>';
        reviewHTML += formatPart2Question(testState.part2Question);
        
        reviewHTML += `<button class="play-question-btn" onclick="playQuestionAudio('${testState.part2Question.topic}')">🔊 Play Question</button>`;
        
        if (testState.transcripts['part2']) {
            reviewHTML += '<div class="answer-section">';
            reviewHTML += '<h4>Your Response:</h4>';
            reviewHTML += `<p class="transcript">${testState.transcripts['part2']}</p>`;
            reviewHTML += '<button class="play-answer-btn" onclick="playUserRecording(\'part2\')">🔊 Play Your Answer</button>';
            reviewHTML += '</div>';
        }
        reviewHTML += '</div>';
    }
    
    // Part 3 Review
    if (testState.part3Questions.length > 0) {
        reviewHTML += '<div class="review-section">';
        reviewHTML += '<h3>Part 3 - Discussion</h3>';
        
        for (let i = 0; i < testState.currentPart3Index; i++) {
            const questionNum = i + 1;
            reviewHTML += '<div class="qa-pair">';
            reviewHTML += `<div class="question-review">`;
            reviewHTML += `<h4>Question ${questionNum}:</h4>`;
            reviewHTML += `<p>${testState.part3Questions[i]}</p>`;
            reviewHTML += `<button class="play-question-btn" onclick="playQuestionAudio('${testState.part3Questions[i]}')">🔊 Play Question</button>`;
            reviewHTML += '</div>';
            
            if (testState.transcripts[`part3_q${questionNum}`]) {
                reviewHTML += '<div class="answer-review">';
                reviewHTML += '<h4>Your Response:</h4>';
                reviewHTML += `<p class="transcript">${testState.transcripts[`part3_q${questionNum}`]}</p>`;
                reviewHTML += `<button class="play-answer-btn" onclick="playUserRecording('part3_q${questionNum}')">🔊 Play Your Answer</button>`;
                reviewHTML += '</div>';
            }
            reviewHTML += '</div>';
        }
        reviewHTML += '</div>';
    }
    
    reviewHTML += '</div>'; // end review-panel-content
    reviewHTML += '</div>'; // end review-left-panel
    
    // Right panel: Score Report
    reviewHTML += '<div class="review-right-panel">';
    reviewHTML += '<div class="review-panel-header"><h3>Score Report</h3></div>';
    reviewHTML += '<div class="review-panel-content" id="report-content-panel">';
    reviewHTML += '<div class="report-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading report...</p></div>';
    reviewHTML += '</div>'; // end review-panel-content
    reviewHTML += '</div>'; // end review-right-panel
    
    reviewHTML += '</div>'; // end review-wrapper
    
    questionDisplay.innerHTML = reviewHTML;
    
    // Load and display the report
    loadAndDisplayReport();
}

// Play question audio using TTS
async function playQuestionAudio(questionText) {
    try {
        const response = await apiClient.textToSpeech(questionText);
        if (response.status === 'success') {
            const audioUrl = apiClient.getAudioUrl(response.audio_path);
            const audio = new Audio(audioUrl);
            audio.play();
        } else {
            // Fallback to browser TTS
            const utterance = new SpeechSynthesisUtterance(questionText);
            utterance.rate = 0.9;
            speechSynthesis.speak(utterance);
        }
    } catch (error) {
        console.error('Error playing question audio:', error);
        // Fallback to browser TTS
        const utterance = new SpeechSynthesisUtterance(questionText);
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
    }
}

// Play user recording
function playUserRecording(recordingKey) {
    if (testState.audioFiles[recordingKey]) {
        const audioUrl = apiClient.getAudioUrl(testState.audioFiles[recordingKey]);
        const audio = new Audio(audioUrl);
        audio.play();
    } else {
        console.error('Audio file not found for:', recordingKey);
        alert('Audio file not available for playback.');
    }
}

// Update the examiner status
function updateExaminerStatus(status) {
    examinerStatus.textContent = status;
}

// Start timer
function startTimer() {
    timerElement.textContent = '00:00';
    
    timerInterval = setInterval(() => {
        const elapsedTime = Date.now() - recordingStartTime;
        const minutes = Math.floor(elapsedTime / 60000);
        const seconds = Math.floor((elapsedTime % 60000) / 1000);
        
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// Stop timer
function stopTimer() {
    clearInterval(timerInterval);
}

// Draw audio visualizer
function drawVisualizer() {
    if (!isRecording) return;
    
    requestAnimationFrame(drawVisualizer);
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);
    
    visualizerContext.clearRect(0, 0, visualizer.width, visualizer.height);
    visualizerContext.fillStyle = '#3498db';
    
    const barWidth = (visualizer.width / bufferLength) * 2.5;
    let x = 0;
    
    for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * visualizer.height;
        
        visualizerContext.fillRect(x, visualizer.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
    }
}

// Load and display the IELTS score report
async function loadAndDisplayReport() {
    const reportPanel = document.getElementById('report-content-panel');
    
    if (!reportPanel) {
        console.error('Report panel not found');
        return;
    }
    
    try {
        // Show loading state
        reportPanel.innerHTML = '<div class="report-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading report...</p></div>';
        
        // Fetch the report
        const response = await apiClient.getReport();
        
        if (response.status === 'success') {
            // Format and display the report
            const formattedHTML = formatReportContent(response.content);
            reportPanel.innerHTML = `<div class="report-content">${formattedHTML}</div>`;
        } else if (response.status === 'not_found') {
            // Report not found
            reportPanel.innerHTML = `
                <div class="report-empty">
                    <i class="fas fa-file-alt"></i>
                    <p>Report not available yet</p>
                    <p class="report-hint">Complete the test and wait for the system to generate your score report.</p>
                </div>
            `;
        } else if (response.status === 'empty') {
            // Report is being generated
            reportPanel.innerHTML = `
                <div class="report-generating">
                    <i class="fas fa-clock"></i>
                    <p>Report is being generated</p>
                    <p class="report-hint">Please wait a moment...</p>
                    <button class="btn primary-btn" onclick="loadAndDisplayReport()" style="margin-top: 15px;">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            `;
        } else {
            // Error occurred
            reportPanel.innerHTML = `
                <div class="report-error">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Failed to load report</p>
                    <button class="btn primary-btn" onclick="loadAndDisplayReport()" style="margin-top: 15px;">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading report:', error);
        reportPanel.innerHTML = `
            <div class="report-error">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load report</p>
                <button class="btn primary-btn" onclick="loadAndDisplayReport()" style="margin-top: 15px;">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }
}

// Format markdown-like report content to HTML
function formatReportContent(text) {
    if (!text) return '';
    
    let html = '';
    const lines = text.split('\n');
    let inList = false;
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        
        // Skip empty lines
        if (!line.trim()) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += '<br>';
            continue;
        }
        
        // Handle headings
        if (line.startsWith('# ')) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<h1>${line.substring(2)}</h1>`;
        } else if (line.startsWith('## ')) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<h2>${line.substring(3)}</h2>`;
        } else if (line.startsWith('### ')) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<h3>${line.substring(4)}</h3>`;
        }
        // Handle horizontal rules
        else if (line.trim() === '---') {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += '<hr>';
        }
        // Handle list items
        else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
            if (!inList) {
                html += '<ul>';
                inList = true;
            }
            let content = line.trim().substring(2);
            content = formatInlineStyles(content);
            html += `<li>${content}</li>`;
        }
        // Handle numbered lists
        else if (/^\d+\.\s/.test(line.trim())) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            let content = line.trim().replace(/^\d+\.\s/, '');
            content = formatInlineStyles(content);
            html += `<p class="numbered-item">${content}</p>`;
        }
        // Regular paragraph
        else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            let content = formatInlineStyles(line);
            html += `<p>${content}</p>`;
        }
    }
    
    if (inList) {
        html += '</ul>';
    }
    
    return html;
}

// Format inline styles (bold, code, etc.)
function formatInlineStyles(text) {
    // Bold text: **text**
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Highlight scores (e.g., "7.5分", "8分")
    text = text.replace(/(\d+\.?\d*分)/g, '<span class="score-highlight">$1</span>');
    
    // Preserve indentation
    const leadingSpaces = text.match(/^(\s+)/);
    if (leadingSpaces) {
        const indent = leadingSpaces[1].length;
        text = '<span style="margin-left: ' + (indent * 8) + 'px;">' + text.trim() + '</span>';
    }
    
    return text;
}

// Initialize the application when the page loads
window.addEventListener('load', init);