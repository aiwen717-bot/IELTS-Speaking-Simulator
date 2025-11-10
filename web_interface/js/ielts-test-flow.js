// IELTS Speaking Test Flow Manager
// This module handles the specific flow of an IELTS speaking test

class IELTSTestFlow {
    constructor() {
        this.parts = {
            intro: {
                name: "Introduction",
                description: "The examiner will introduce themselves and ask you to identify yourself.",
                duration: 1, // minutes
                questions: [
                    "Can you tell me your full name, please?",
                    "How may I address you?",
                    "Could you tell me where you're from?"
                ]
            },
            part1: {
                name: "Part 1",
                description: "Part 1 consists of general questions about familiar topics such as home, family, work, studies and interests.",
                duration: 4, // minutes
                topics: [
                    {
                        name: "Work/Studies",
                        questions: [
                            "What do you do? Do you work or are you a student?",
                            "Why did you choose that job/subject?",
                            "What do you enjoy most about your work/studies?",
                            "Would you like to change your job/subject in the future?"
                        ]
                    },
                    {
                        name: "Hometown",
                        questions: [
                            "Let's talk about your hometown. Where is your hometown?",
                            "What do you like most about your hometown?",
                            "How has your hometown changed in recent years?",
                            "Would you like to live in your hometown in the future?"
                        ]
                    },
                    {
                        name: "Accommodation",
                        questions: [
                            "Can you describe the place where you live?",
                            "What do you like most about living there?",
                            "How long have you lived there?",
                            "Would you like to move to a different home in the future?"
                        ]
                    }
                ]
            },
            part2: {
                name: "Part 2",
                description: "In Part 2, you will be given a topic card. You have 1 minute to prepare and then should speak for 1-2 minutes on the topic.",
                preparationTime: 1, // minutes
                speakingTime: 2, // minutes
                cueCards: [
                    {
                        topic: "Describe a skill that took you a long time to learn",
                        points: [
                            "what the skill is",
                            "when you learned it",
                            "why it took a long time to learn",
                            "and explain how you felt when you finally learned it"
                        ]
                    },
                    {
                        topic: "Describe a place you visited that has been affected by pollution",
                        points: [
                            "where it is",
                            "when you visited this place",
                            "what kind of pollution you saw there",
                            "and explain how this place could be improved"
                        ]
                    },
                    {
                        topic: "Describe an important decision you made",
                        points: [
                            "what the decision was",
                            "when you made this decision",
                            "how you made your decision",
                            "and explain why it was important"
                        ]
                    }
                ]
            },
            part3: {
                name: "Part 3",
                description: "Part 3 involves a discussion of more abstract issues related to the Part 2 topic.",
                duration: 5, // minutes
                topicSets: [
                    {
                        // Related to "skill that took time to learn"
                        name: "Skills and Learning",
                        questions: [
                            "What kinds of skills do you think are most important for young people to learn nowadays?",
                            "Do you think the skills needed for success have changed compared to the past? In what ways?",
                            "How do you think technology has changed the way people learn new skills?",
                            "Do you think schools focus too much on academic skills rather than practical skills? Why?",
                            "What role do you think persistence plays in mastering difficult skills?"
                        ]
                    },
                    {
                        // Related to "place affected by pollution"
                        name: "Environment and Pollution",
                        questions: [
                            "What do you think are the main causes of pollution in cities today?",
                            "How do you think pollution affects people's quality of life?",
                            "What responsibility do you think governments have in controlling pollution?",
                            "Do you think individuals can make a significant difference in reducing pollution? How?",
                            "How might environmental problems affect future generations?"
                        ]
                    },
                    {
                        // Related to "important decision"
                        name: "Decision Making",
                        questions: [
                            "What factors do you think people should consider when making important life decisions?",
                            "Do you think young people today face more difficult decisions than previous generations?",
                            "How do you think cultural background influences the way people make decisions?",
                            "What role do you think emotions should play in decision making?",
                            "How might technology help or hinder people in making important decisions?"
                        ]
                    }
                ]
            }
        };
        
        this.currentPart = null;
        this.currentTopicIndex = 0;
        this.currentQuestionIndex = 0;
        this.selectedCueCard = null;
        this.selectedPart3Set = null;
    }
    
    // Initialize the test
    initTest() {
        // Start with introduction
        this.currentPart = 'intro';
        this.currentQuestionIndex = 0;
        return this.getCurrentQuestion();
    }
    
    // Get current question based on test state
    getCurrentQuestion() {
        switch(this.currentPart) {
            case 'intro':
                return {
                    part: 'intro',
                    partName: this.parts.intro.name,
                    description: this.parts.intro.description,
                    question: this.parts.intro.questions[this.currentQuestionIndex],
                    isLastQuestionInPart: this.currentQuestionIndex >= this.parts.intro.questions.length - 1
                };
                
            case 'part1':
                const currentTopic = this.parts.part1.topics[this.currentTopicIndex];
                return {
                    part: 'part1',
                    partName: this.parts.part1.name,
                    description: this.parts.part1.description,
                    topic: currentTopic.name,
                    question: currentTopic.questions[this.currentQuestionIndex],
                    isLastQuestionInTopic: this.currentQuestionIndex >= currentTopic.questions.length - 1,
                    isLastTopic: this.currentTopicIndex >= this.parts.part1.topics.length - 1
                };
                
            case 'part2':
                if (!this.selectedCueCard) {
                    // Randomly select a cue card if none is selected
                    const randomIndex = Math.floor(Math.random() * this.parts.part2.cueCards.length);
                    this.selectedCueCard = this.parts.part2.cueCards[randomIndex];
                }
                
                return {
                    part: 'part2',
                    partName: this.parts.part2.name,
                    description: this.parts.part2.description,
                    preparationTime: this.parts.part2.preparationTime,
                    speakingTime: this.parts.part2.speakingTime,
                    topic: this.selectedCueCard.topic,
                    points: this.selectedCueCard.points,
                    isPreparing: this.currentQuestionIndex === 0,
                    isSpeaking: this.currentQuestionIndex === 1
                };
                
            case 'part3':
                if (!this.selectedPart3Set) {
                    // Select the part3 question set that matches the part2 cue card theme
                    // For simplicity, we'll just use the same index
                    const cueCardIndex = this.parts.part2.cueCards.indexOf(this.selectedCueCard);
                    this.selectedPart3Set = this.parts.part3.topicSets[cueCardIndex];
                }
                
                return {
                    part: 'part3',
                    partName: this.parts.part3.name,
                    description: this.parts.part3.description,
                    topic: this.selectedPart3Set.name,
                    question: this.selectedPart3Set.questions[this.currentQuestionIndex],
                    isLastQuestion: this.currentQuestionIndex >= this.selectedPart3Set.questions.length - 1
                };
                
            case 'complete':
                return {
                    part: 'complete',
                    partName: 'Test Complete',
                    description: 'You have completed the IELTS Speaking Test.',
                    question: 'Thank you. That is the end of the speaking test.'
                };
                
            default:
                return null;
        }
    }
    
    // Move to the next question
    nextQuestion() {
        switch(this.currentPart) {
            case 'intro':
                if (this.currentQuestionIndex < this.parts.intro.questions.length - 1) {
                    this.currentQuestionIndex++;
                } else {
                    // Move to Part 1
                    this.currentPart = 'part1';
                    this.currentTopicIndex = 0;
                    this.currentQuestionIndex = 0;
                }
                break;
                
            case 'part1':
                const currentTopic = this.parts.part1.topics[this.currentTopicIndex];
                if (this.currentQuestionIndex < currentTopic.questions.length - 1) {
                    this.currentQuestionIndex++;
                } else if (this.currentTopicIndex < this.parts.part1.topics.length - 1) {
                    // Move to next topic in Part 1
                    this.currentTopicIndex++;
                    this.currentQuestionIndex = 0;
                } else {
                    // Move to Part 2
                    this.currentPart = 'part2';
                    this.currentQuestionIndex = 0; // 0 = preparation phase
                }
                break;
                
            case 'part2':
                if (this.currentQuestionIndex === 0) {
                    // Move from preparation to speaking
                    this.currentQuestionIndex = 1;
                } else {
                    // Move to Part 3
                    this.currentPart = 'part3';
                    this.currentQuestionIndex = 0;
                }
                break;
                
            case 'part3':
                if (this.currentQuestionIndex < this.selectedPart3Set.questions.length - 1) {
                    this.currentQuestionIndex++;
                } else {
                    // End of test
                    this.currentPart = 'complete';
                }
                break;
        }
        
        return this.getCurrentQuestion();
    }
    
    // Format the Part 2 cue card for display
    formatCueCard(cueCard) {
        let html = `<div class="cue-card">
            <h4>${cueCard.topic}</h4>
            <p>You should say:</p>
            <ul>`;
            
        cueCard.points.forEach(point => {
            html += `<li>${point}</li>`;
        });
        
        html += `</ul></div>`;
        return html;
    }
    
    // Get the progress percentage based on current test state
    getProgressPercentage() {
        switch(this.currentPart) {
            case 'intro':
                return 5 + (this.currentQuestionIndex / this.parts.intro.questions.length * 15);
            case 'part1':
                const part1Progress = (this.currentTopicIndex * this.parts.part1.topics[0].questions.length + this.currentQuestionIndex) / 
                                     (this.parts.part1.topics.length * this.parts.part1.topics[0].questions.length);
                return 20 + (part1Progress * 25);
            case 'part2':
                return 45 + (this.currentQuestionIndex * 15);
            case 'part3':
                return 60 + (this.currentQuestionIndex / this.selectedPart3Set.questions.length * 35);
            case 'complete':
                return 100;
            default:
                return 0;
        }
    }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IELTSTestFlow;
}
