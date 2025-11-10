import sys
from llm_module.question_generator import IELTSQuestionGenerator

class MockGenerator:
    def generate_with_system_prompt(self, system_prompt, user_prompt):
        """Mock LLM that returns predefined questions based on the text."""
        return '''
1. How do you think shared experiences like meals influence the development of close friendships?
2. In what ways have social gatherings around food changed in recent years compared to traditional practices?
3. What factors make certain memories, like your graduation meal, particularly significant in people's lives?
4. How do you think technology has affected the way people maintain long-distance friendships compared to your experience?
5. What role do you think educational institutions should play in fostering meaningful friendships among students?
        '''

# Create question generator with mock LLM
generator = IELTSQuestionGenerator(MockGenerator())

# Test with the input text
test_text = sys.argv[1]
num_questions = int(sys.argv[2])

# Generate questions
questions = generator.generate_questions(test_text, num_questions)

# Print results
print("Generated IELTS Part 3 questions:")
for i, question in enumerate(questions):
    print(f"{i+1}. {question}")

# Save to file
with open("output/ielts_questions.txt", "w") as f:
    for i, question in enumerate(questions):
        f.write(f"{i+1}. {question}\n")
