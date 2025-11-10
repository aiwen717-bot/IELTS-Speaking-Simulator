"""
Test script for topic extraction from text.
"""
from llm_module.text_processor import TextProcessor
from llm_module.question_generator import IELTSQuestionGenerator
import sys
import os

def main():
    # Ensure output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Get text from command line argument
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = """I am going to talk about the unusual meal I had. The unusual meal I am going to tell you is what I ate with my best friend before graduation. He and I shared the same room and our beds were set together. During the college, we play basketball together, study together and even help each other find our true loves. Oh, a lot of happy memory. The meal was in the evening before graduation. Next day, we would pursue our own courses. He would go to Xia' men, a southern city in China, to teach in a university, while I would stay here and start my work. We were parted thousands of miles, so that meal was very likely to be our last meal in several years, and it is. Instead of eating in a restaurant, we bought some food and beer and came back to the dormitory where we lived for four years. We ate, drank and talked. We talked about our ambitions, expectations, lives, and paths ahead until about 4 o' clock in the morning. This article is from Laokaoya website. Do not copy or post it. Then we packed our baggage. He embarked on his way to Xia' men. I took a bus to my small rented room. In fact, the food that day was not so good, but I always remember this meal and it resurfaces in my memory now and then. After all, it symbolized the end of my college and precious friendship."""
    
    # Initialize text processor
    tp = TextProcessor()
    
    # Extract topics
    topics = tp.extract_topics(text)
    print("Extracted topics:", topics)
    
    # Initialize question generator
    qg = IELTSQuestionGenerator()
    
    # Generate template questions
    questions = qg._generate_template_questions(topics, 5)
    print("\nGenerated questions:")
    for i, q in enumerate(questions):
        print(f"{i+1}. {q}")
    
    # Save results to file
    with open("output/improved_topics.txt", "w") as f:
        f.write(f"Extracted topics: {topics}\n\n")
        f.write("Generated template questions:\n")
        for i, q in enumerate(questions):
            f.write(f"{i+1}. {q}\n")

if __name__ == "__main__":
    main()
