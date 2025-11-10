"""
IELTS Part 3 style question generator module.
"""
from typing import List, Dict, Any, Optional
import logging
import os
from .text_processor import TextProcessor
try:
    from .qwen_generator import QwenGenerator as Generator
except ImportError:
    from .llm_generator import LLMGenerator as Generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IELTSQuestionGenerator:
    """
    Generates IELTS Part 3 style questions based on input text.
    """
    
    def __init__(self, llm_generator: Optional[Any] = None, config_path: Optional[str] = None):
        """
        Initialize the IELTS Question Generator.
        
        Args:
            llm_generator: An instance of a language model generator
            config_path: Path to configuration file
        """
        self.text_processor = TextProcessor()
        # Ensure config path is passed correctly
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.llm_generator = llm_generator or Generator(config_path)
        
        # IELTS Part 3 question templates
        self.question_templates = [
            "What impact does {topic} have on society?",
            "How has {topic} changed in recent years?",
            "Do you think {topic} will become more important in the future? Why?",
            "What are the advantages and disadvantages of {topic}?",
            "How do different generations view {topic} differently?",
            "What role should the government play regarding {topic}?",
            "How does {topic} differ between urban and rural areas?",
            "What are some potential solutions to problems related to {topic}?",
            "How does {topic} affect people's daily lives?",
            "What cultural differences exist in how people approach {topic}?"
        ]
        
        # System prompt for IELTS Part 3 question generation
        self.system_prompt = """
        You are an IELTS examiner creating Part 3 questions for the speaking test.
        
        IELTS Speaking Part 3 questions:
        - Are abstract and require in-depth discussion
        - Ask about opinions, analysis, and evaluation
        - Cover broader social issues related to the topic
        - Require candidates to speculate, evaluate, and analyze
        - Often use phrases like "Why do you think...", "What factors...", "How far do you agree..."
        
        Generate thoughtful, challenging questions that:
        1. Require analytical thinking and detailed responses
        2. Explore social trends, causes and effects, comparisons, and future developments
        3. Are open-ended with no simple answers
        4. Connect the topic to broader themes like society, technology, education, or culture
        5. Avoid yes/no questions unless followed by "why" or "in what ways"
        
        IMPORTANT REQUIREMENTS:
        1. The questions MUST be directly related to the topics extracted from the text
        2. Analyze the text carefully and identify the main themes and subjects
        3. Do not generate generic questions - they should be specifically tailored to the text content
        4. Ensure questions reference specific elements or themes from the provided text
        5. Do NOT use generic placeholders or single words as topics in your questions
        6. Create questions that sound natural and conversational, as would be asked in an IELTS exam
        7. Questions should be sophisticated and require deep thinking, not simple factual answers
        8. Each question should explore a different aspect of the text's themes
        
        The questions should follow naturally from the topics provided and form a coherent set that explores the text's themes in depth.
        """
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """
        Generate IELTS Part 3 style questions based on the input text.
        
        Args:
            text: Input text to generate questions from
            num_questions: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        # Preprocess the text
        processed_text = self.text_processor.preprocess_text(text)
        
        # Extract topics from the text
        topics = self.text_processor.extract_topics(processed_text)
        topic_str = ", ".join(topics) if topics else "the text"
        
        # Create user prompt for the LLM
        user_prompt = f"""
        Based on the following text, generate {num_questions} challenging IELTS Speaking Part 3 questions.
        
        Text: "{processed_text}"
        
        Main topics identified: {topic_str}
        
        CAREFULLY ANALYZE THE TEXT: This text appears to be about {topic_str}. Make sure your questions are specifically related to the themes and content of this text.
        
        Generate {num_questions} different questions that explore these topics in depth, following IELTS Part 3 format.
        The questions must be directly relevant to the text content and themes.
        
        Your questions should:
        - Connect to real-world implications of the topics in the text
        - Encourage analytical and critical thinking
        - Explore social, cultural, or personal dimensions of the themes
        - Be sophisticated and natural-sounding
        - Avoid using single words as topics (like "going" or "meal")
        - Use complete phrases that capture the essence of the text's themes
        
        Return only the questions, numbered from 1 to {num_questions}.
        """
        
        try:
            # Generate questions using the LLM
            response = self.llm_generator.generate_with_system_prompt(
                self.system_prompt,
                user_prompt
            )
            
            # Process the response to extract questions
            questions = self._parse_questions(response, num_questions)
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            # Fallback to template-based questions if LLM fails
            return self._generate_template_questions(topics, num_questions)
    
    def _parse_questions(self, response: str, expected_count: int) -> List[str]:
        """
        Parse the LLM response to extract questions.
        
        Args:
            response: Raw response from the LLM
            expected_count: Expected number of questions
            
        Returns:
            List of parsed questions
        """
        lines = response.strip().split('\n')
        questions = []
        
        for line in lines:
            # Remove leading numbers, dots, and spaces
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a number followed by a dot or parenthesis
            if (line[0].isdigit() and len(line) > 1 and 
                (line[1] == '.' or line[1] == ')' or line[1] == '/')):
                # Remove the numbering
                question = line[2:].strip()
                questions.append(question)
            elif line[0].isdigit() and len(line) > 2 and line[1].isdigit() and line[2] in ['.', ')', '/']:
                # Handle double-digit numbering
                question = line[3:].strip()
                questions.append(question)
            elif not any(q in line.lower() for q in ["question", "questions", "example", "prompt"]):
                # If it looks like a question but doesn't have numbering
                if '?' in line:
                    questions.append(line)
        
        # If we couldn't parse enough questions, take lines with question marks
        if len(questions) < expected_count:
            questions = [line.strip() for line in lines if '?' in line]
            
        return questions[:expected_count]  # Limit to expected count
    
    def _generate_template_questions(self, topics: List[str], count: int) -> List[str]:
        """
        Generate questions using templates as a fallback method.
        
        Args:
            topics: List of topics extracted from the text
            count: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        import random
        
        questions = []
        
        # Use multiple topics if available to create diverse questions
        if not topics:
            topics = ["this topic"]
            
        # Create a mapping of templates to appropriate topics
        template_topic_pairs = []
        
        # Create pairs of templates and topics
        for i, topic in enumerate(topics):
            if i >= count:
                break
                
            # Select a template that fits well with this topic
            template_index = i % len(self.question_templates)
            template = self.question_templates[template_index]
            template_topic_pairs.append((template, topic))
        
        # If we need more questions than topics, add more template-topic pairs
        while len(template_topic_pairs) < count:
            # Pick a random topic and template
            topic = random.choice(topics)
            remaining_templates = [t for t in self.question_templates if not any(t == pair[0] for pair in template_topic_pairs)]
            
            if not remaining_templates:
                # If we've used all templates, just pick a random one
                template = random.choice(self.question_templates)
            else:
                # Otherwise, pick an unused template
                template = random.choice(remaining_templates)
                
            template_topic_pairs.append((template, topic))
        
        # Generate questions from template-topic pairs
        for template, topic in template_topic_pairs[:count]:
            question = template.format(topic=topic)
            questions.append(question)
            
        return questions
