"""
Test only the topic extraction to debug the issue.
"""
from llm_module.text_processor import TextProcessor

def test_topic_extraction():
    text = """I am going to talk about the unusual meal I had. The unusual meal I am going to tell you is what I ate with my best friend before graduation. He and I shared the same room and our beds were set together. During the college, we play basketball together, study together and even help each other find our true loves. Oh, a lot of happy memory. The meal was in the evening before graduation. Next day, we would pursue our own courses. He would go to Xia' men, a southern city in China, to teach in a university, while I would stay here and start my work. We were parted thousands of miles, so that meal was very likely to be our last meal in several years, and it is. Instead of eating in a restaurant, we bought some food and beer and came back to the dormitory where we lived for four years. We ate, drank and talked. We talked about our ambitions, expectations, lives, and paths ahead until about 4 o' clock in the morning. This article is from Laokaoya website. Do not copy or post it. Then we packed our baggage. He embarked on his way to Xia' men. I took a bus to my small rented room. In fact, the food that day was not so good, but I always remember this meal and it resurfaces in my memory now and then. After all, it symbolized the end of my college and precious friendship."""
    
    processor = TextProcessor()
    
    # Test the updated topic extraction
    topics = processor.extract_topics(text)
    print("Extracted topics:", topics)
    
    # Let's also test the word counting part
    import re
    
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
        'when', 'where', 'how', 'why', 'which', 'who', 'whom', 'this', 'that',
        'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would',
        'should', 'could', 'ought', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'their', 'his', 'her', 'its', 'our', 'your', 'my', 'mine', 'yours', 'ours',
        'theirs', 'to', 'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'will', 'just', 'don', 'dont',
        'going', 'about', 'after', 'before', 'with', 'without', 'above', 'below',
        'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'up', 'down', 'for', 'of', 'by', 'at'
    }
    
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    word_counts = {}
    
    for sentence in sentences:
        clean_sentence = re.sub(r'[^\w\s]', ' ', sentence.lower())
        words = clean_sentence.split()
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1
    
    print("\nWord frequency analysis:")
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for word, count in top_words:
        print(f"  {word}: {count}")

if __name__ == "__main__":
    test_topic_extraction()
