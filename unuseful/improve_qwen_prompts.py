"""
This script updates the question_generator.py file to improve the prompts for Qwen model.
It makes the prompts more specific to generate high-quality IELTS Part 3 questions.
"""

import os
import re
import sys

def update_system_prompt():
    """Update the system prompt in question_generator.py to improve question quality."""
    file_path = os.path.join('llm_module', 'question_generator.py')
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return False
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the improved system prompt
    improved_system_prompt = '''
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
        '''
    
    # Define the improved user prompt
    improved_user_prompt = '''
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
        '''
    
    # Replace the system prompt
    pattern_system = r'self\.system_prompt = """.*?"""'
    replacement_system = f'self.system_prompt = """{improved_system_prompt}"""'
    new_content = re.sub(pattern_system, replacement_system, content, flags=re.DOTALL)
    
    # Replace the user prompt
    pattern_user = r'user_prompt = f""".*?"""'
    replacement_user = f'user_prompt = f"""{improved_user_prompt}"""'
    new_content = re.sub(pattern_user, replacement_user, new_content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated prompts in {file_path}")
    return True

def main():
    print("Improving Qwen prompts for better question generation...")
    if update_system_prompt():
        print("\nPrompts have been improved. The Qwen model should now generate higher quality questions.")
        print("Please run run_qwen_questions.bat to generate questions with the improved prompts.")
    else:
        print("\nFailed to update prompts. Please check the file structure.")

if __name__ == "__main__":
    main()
