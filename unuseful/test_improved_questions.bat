@echo off
REM Test script for improved question generation

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist output mkdir output

REM Set the test text
set test_text=I am going to talk about the unusual meal I had. The unusual meal I am going to tell you is what I ate with my best friend before graduation. He and I shared the same room and our beds were set together. During the college, we play basketball together, study together and even help each other find our true loves. Oh, a lot of happy memory. The meal was in the evening before graduation. Next day, we would pursue our own courses. He would go to Xia' men, a southern city in China, to teach in a university, while I would stay here and start my work. We were parted thousands of miles, so that meal was very likely to be our last meal in several years, and it is. Instead of eating in a restaurant, we bought some food and beer and came back to the dormitory where we lived for four years. We ate, drank and talked. We talked about our ambitions, expectations, lives, and paths ahead until about 4 o' clock in the morning. This article is from Laokaoya website. Do not copy or post it. Then we packed our baggage. He embarked on his way to Xia' men. I took a bus to my small rented room. In fact, the food that day was not so good, but I always remember this meal and it resurfaces in my memory now and then. After all, it symbolized the end of my college and precious friendship.

echo Testing improved question generation with the meal and friendship text...
echo.

REM Generate questions using fallback method (no API needed)
python -c "from llm_module.text_processor import TextProcessor; from llm_module.question_generator import IELTSQuestionGenerator; tp = TextProcessor(); topics = tp.extract_topics('%test_text%'); print('Extracted topics:', topics); qg = IELTSQuestionGenerator(); questions = qg._generate_template_questions(topics, 5); print('\nGenerated questions:'); [print(f'{i+1}. {q}') for i, q in enumerate(questions)]" > output\improved_topics.txt

echo Questions generated using improved topic extraction.
echo Results saved to output\improved_topics.txt
echo.

REM Create a Python script to test the full generation with mock LLM
echo import sys> test_question_gen.py
echo from llm_module.text_processor import TextProcessor>> test_question_gen.py
echo from llm_module.question_generator import IELTSQuestionGenerator>> test_question_gen.py
echo.>> test_question_gen.py
echo class MockGenerator:>> test_question_gen.py
echo     def generate_with_system_prompt(self, system_prompt, user_prompt):>> test_question_gen.py
echo         """Mock LLM that returns predefined questions based on the text.""">> test_question_gen.py
echo         return '''>> test_question_gen.py
echo 1. How do you think shared experiences like meals influence the development of close friendships?>> test_question_gen.py
echo 2. In what ways have social gatherings around food changed in recent years compared to traditional practices?>> test_question_gen.py
echo 3. What factors make certain memories, like your graduation meal, particularly significant in people's lives?>> test_question_gen.py
echo 4. How do you think technology has affected the way people maintain long-distance friendships compared to your experience?>> test_question_gen.py
echo 5. What role do you think educational institutions should play in fostering meaningful friendships among students?>> test_question_gen.py
echo         '''>> test_question_gen.py
echo.>> test_question_gen.py
echo # Create question generator with mock LLM>> test_question_gen.py
echo generator = IELTSQuestionGenerator(MockGenerator())>> test_question_gen.py
echo.>> test_question_gen.py
echo # Test with the meal text>> test_question_gen.py
echo test_text = sys.argv[1]>> test_question_gen.py
echo.>> test_question_gen.py
echo # Generate questions>> test_question_gen.py
echo questions = generator.generate_questions(test_text, 5)>> test_question_gen.py
echo.>> test_question_gen.py
echo # Print results>> test_question_gen.py
echo print("Generated IELTS Part 3 questions:")>> test_question_gen.py
echo for i, question in enumerate(questions):>> test_question_gen.py
echo     print(f"{i+1}. {question}")>> test_question_gen.py
echo.>> test_question_gen.py
echo # Save to file>> test_question_gen.py
echo with open("output/improved_questions.txt", "w") as f:>> test_question_gen.py
echo     for i, question in enumerate(questions):>> test_question_gen.py
echo         f.write(f"{i+1}. {question}\n")>> test_question_gen.py

REM Run the test script
python test_question_gen.py "%test_text%" > output\test_results.txt

echo Full question generation test completed.
echo Results saved to output\improved_questions.txt and output\test_results.txt
echo.

REM Clean up
del test_question_gen.py

echo Press any key to exit...
pause >nul
