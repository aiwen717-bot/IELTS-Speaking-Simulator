"""
Test script to diagnose Qwen question generation issues.
"""
import sys
import os
from llm_module.text_processor import TextProcessor
from llm_module.question_generator import IELTSQuestionGenerator

def test_topic_extraction(text):
    """Test the topic extraction functionality."""
    print("=== Testing Topic Extraction ===")
    processor = TextProcessor()
    topics = processor.extract_topics(text)
    print(f"Extracted topics: {topics}")
    return topics

def test_qwen_generation(text, num_questions=5):
    """Test the full Qwen generation process."""
    print("\n=== Testing Qwen Question Generation ===")
    
    try:
        # Initialize the question generator
        generator = IELTSQuestionGenerator()
        
        # Check which generator is being used
        generator_type = type(generator.llm_generator).__name__
        print(f"Using generator: {generator_type}")
        
        # Test topic extraction first
        topics = test_topic_extraction(text)
        
        # Generate questions
        print(f"\nGenerating {num_questions} questions...")
        questions = generator.generate_questions(text, num_questions)
        
        print(f"\nGenerated {len(questions)} questions:")
        for i, question in enumerate(questions):
            print(f"{i+1}. {question}")
            
        return questions
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_fallback_generation(text, num_questions=5):
    """Test the fallback template generation."""
    print("\n=== Testing Fallback Template Generation ===")
    
    try:
        processor = TextProcessor()
        generator = IELTSQuestionGenerator()
        
        topics = processor.extract_topics(text)
        print(f"Topics for fallback: {topics}")
        
        questions = generator._generate_template_questions(topics, num_questions)
        
        print(f"\nFallback generated {len(questions)} questions:")
        for i, question in enumerate(questions):
            print(f"{i+1}. {question}")
            
        return questions
        
    except Exception as e:
        print(f"Error during fallback generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    # Test text
    test_text = """I am going to talk about the unusual meal I had. The unusual meal I am going to tell you is what I ate with my best friend before graduation. He and I shared the same room and our beds were set together. During the college, we play basketball together, study together and even help each other find our true loves. Oh, a lot of happy memory. The meal was in the evening before graduation. Next day, we would pursue our own courses. He would go to Xia' men, a southern city in China, to teach in a university, while I would stay here and start my work. We were parted thousands of miles, so that meal was very likely to be our last meal in several years, and it is. Instead of eating in a restaurant, we bought some food and beer and came back to the dormitory where we lived for four years. We ate, drank and talked. We talked about our ambitions, expectations, lives, and paths ahead until about 4 o' clock in the morning. This article is from Laokaoya website. Do not copy or post it. Then we packed our baggage. He embarked on his way to Xia' men. I took a bus to my small rented room. In fact, the food that day was not so good, but I always remember this meal and it resurfaces in my memory now and then. After all, it symbolized the end of my college and precious friendship."""
    
    print("Testing IELTS Question Generation System")
    print("=" * 50)
    
    # Test 1: Topic extraction
    topics = test_topic_extraction(test_text)
    
    # Test 2: Fallback generation (to compare)
    fallback_questions = test_fallback_generation(test_text, 5)
    
    # Test 3: Full Qwen generation
    qwen_questions = test_qwen_generation(test_text, 5)
    
    # Compare results
    print("\n=== Comparison ===")
    print("Fallback questions vs Qwen questions:")
    
    if fallback_questions and qwen_questions:
        if fallback_questions == qwen_questions:
            print("WARNING: Questions are identical! This suggests Qwen API is not being used or is falling back to templates.")
        else:
            print("Questions are different, which is expected if Qwen API is working.")
    
    # Save results to file for comparison
    with open("test_results_comparison.txt", "w") as f:
        f.write("=== Topic Extraction Results ===\n")
        f.write(f"Topics: {topics}\n\n")
        
        f.write("=== Fallback Template Questions ===\n")
        for i, q in enumerate(fallback_questions):
            f.write(f"{i+1}. {q}\n")
        
        f.write("\n=== Qwen Generated Questions ===\n")
        for i, q in enumerate(qwen_questions):
            f.write(f"{i+1}. {q}\n")
    
    print("\nResults saved to test_results_comparison.txt")

if __name__ == "__main__":
    main()
