"""
Test the generate_ielts_questions.py script to ensure it uses Qwen API correctly.
"""
import subprocess
import sys
import os

def test_generate_script():
    """Test the main generation script with Qwen config."""
    
    test_text = """I am going to talk about the unusual meal I had. The unusual meal I am going to tell you is what I ate with my best friend before graduation. He and I shared the same room and our beds were set together. During the college, we play basketball together, study together and even help each other find our true loves. Oh, a lot of happy memory. The meal was in the evening before graduation. Next day, we would pursue our own courses. He would go to Xia' men, a southern city in China, to teach in a university, while I would stay here and start my work. We were parted thousands of miles, so that meal was very likely to be our last meal in several years, and it is. Instead of eating in a restaurant, we bought some food and beer and came back to the dormitory where we lived for four years. We ate, drank and talked. We talked about our ambitions, expectations, lives, and paths ahead until about 4 o' clock in the morning. This article is from Laokaoya website. Do not copy or post it. Then we packed our baggage. He embarked on his way to Xia' men. I took a bus to my small rented room. In fact, the food that day was not so good, but I always remember this meal and it resurfaces in my memory now and then. After all, it symbolized the end of my college and precious friendship."""
    
    print("Testing generate_ielts_questions.py with Qwen config...")
    
    # Run the script with Qwen config
    cmd = [
        sys.executable, 
        "generate_ielts_questions.py",
        "--text", test_text,
        "--num_questions", "5",
        "--config", "llm_module/config.json",
        "--output_dir", "test_output"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        # Check if output file was created
        output_file = "test_output/ielts_questions.txt"
        if os.path.exists(output_file):
            print(f"\nOutput file created: {output_file}")
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print("Generated questions:")
            print(content)
            
            # Check if questions look like high-quality Qwen output
            if "emotional significance" in content.lower() or "shared activities" in content.lower():
                print("✅ Questions appear to be high-quality Qwen generated!")
            else:
                print("❌ Questions appear to be template generated.")
        else:
            print("❌ No output file created.")
            
    except Exception as e:
        print(f"Error running script: {str(e)}")

if __name__ == "__main__":
    test_generate_script()
