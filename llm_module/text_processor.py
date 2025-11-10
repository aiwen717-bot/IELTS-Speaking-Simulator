"""
Text processing utilities for the LLM module.
"""
import os
import re
from typing import List, Optional, Dict, Any


class TextProcessor:
    """
    Handles reading and preprocessing text for the LLM module.
    """
    
    def __init__(self):
        """Initialize the text processor."""
        pass
        
    def read_from_file(self, file_path: str) -> str:
        """
        Read text content from a file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            String containing the file content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Try UTF-8 first
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content
            except UnicodeDecodeError:
                # If UTF-8 fails, try with different encodings
                encodings = ['utf-8-sig', 'gbk', 'cp1252', 'latin1']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            content = file.read()
                        return content
                    except UnicodeDecodeError:
                        continue
                # If all encodings fail, read as binary and decode with error handling
                with open(file_path, 'rb') as file:
                    raw_content = file.read()
                    content = raw_content.decode('utf-8', errors='ignore')
                return content
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess the input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Trim whitespace
        text = text.strip()
        return text
    
    def extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics from the text for question generation.
        
        Args:
            text: Input text
            
        Returns:
            List of main topics extracted from the text
        """
        # More robust implementation to extract meaningful topics
        
        # Common English stop words to filter out
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
        
        # Split text into sentences
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Extract noun phrases and potential topics
        word_counts = {}
        
        # Process each sentence to find important words
        for sentence in sentences:
            # Remove punctuation and convert to lowercase
            clean_sentence = re.sub(r'[^\w\s]', ' ', sentence.lower())
            words = clean_sentence.split()
            
            # Count words that are not stop words and have sufficient length
            for word in words:
                if word not in stop_words and len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find phrases (adjacent words that appear together frequently)
        phrases = []
        for i in range(len(sentences)):
            clean_sentence = re.sub(r'[^\w\s]', ' ', sentences[i].lower())
            words = clean_sentence.split()
            
            for j in range(len(words) - 1):
                if (words[j] not in stop_words and words[j+1] not in stop_words and 
                    len(words[j]) > 3 and len(words[j+1]) > 3):
                    phrase = f"{words[j]} {words[j+1]}"
                    phrases.append(phrase)
        
        # Find the most common words and phrases
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Extract main topics - prioritize meaningful phrases over single words
        topics = []
        
        # First, try to find meaningful phrases
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Add top phrases first (they are more meaningful than single words)
        top_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        for phrase, count in top_phrases:
            if len(topics) < 3:  # Limit to 3 phrases
                topics.append(phrase)
        
        # If we need more topics, add some single words but make them more meaningful
        if len(topics) < 5:
            # Only add words that are likely to be meaningful topics
            meaningful_words = []
            for word, count in top_words:
                if count > 1 and word not in ['meal', 'together', 'room']:  # Avoid generic words
                    # Check if this word represents a meaningful concept
                    if any(theme in word for theme in ['friend', 'graduat', 'memor', 'college', 'univers']):
                        meaningful_words.append(word)
            
            # Add meaningful words to topics
            for word in meaningful_words:
                if len(topics) < 5 and word not in topics:
                    topics.append(word)
        
        # If we still don't have enough topics, extract from the first and last sentences
        if len(topics) < 2:
            if sentences:
                # Extract from first sentence (often contains the main topic)
                first_sentence = re.sub(r'[^\w\s]', ' ', sentences[0].lower())
                words = first_sentence.split()
                for word in words:
                    if (word not in stop_words and len(word) > 3 and 
                        word not in topics and len(topics) < 5):
                        topics.append(word)
                
                # Extract from last sentence (often contains a conclusion)
                if len(sentences) > 1:
                    last_sentence = re.sub(r'[^\w\s]', ' ', sentences[-1].lower())
                    words = last_sentence.split()
                    for word in words:
                        if (word not in stop_words and len(word) > 3 and 
                            word not in topics and len(topics) < 5):
                            topics.append(word)
        
        # If we still don't have topics, extract meaningful phrases from key sentences
        if not topics:
            # Focus on extracting meaningful phrases instead of single words
            key_phrases = []
            
            # Look for patterns that indicate important concepts
            for sentence in sentences:
                clean_sentence = re.sub(r'[^\w\s]', ' ', sentence.lower())
                words = clean_sentence.split()
                
                # Extract 2-3 word phrases that don't start with stop words
                for i in range(len(words) - 1):
                    if (words[i] not in stop_words and words[i+1] not in stop_words and
                        len(words[i]) > 3 and len(words[i+1]) > 3):
                        phrase = f"{words[i]} {words[i+1]}"
                        if phrase not in key_phrases:
                            key_phrases.append(phrase)
                
                # Extract 3-word phrases
                for i in range(len(words) - 2):
                    if (words[i] not in stop_words and words[i+1] not in stop_words and 
                        words[i+2] not in stop_words and len(words[i]) > 3 and 
                        len(words[i+1]) > 3 and len(words[i+2]) > 3):
                        phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                        if phrase not in key_phrases:
                            key_phrases.append(phrase)
            
            # Add the best phrases as topics
            topics.extend(key_phrases[:3])
        
        # If still no topics, extract from the main theme of the text
        if not topics:
            # Analyze the overall theme based on sentence structure
            theme_indicators = []
            
            for sentence in sentences:
                # Look for sentences that describe experiences, relationships, or events
                if any(indicator in sentence.lower() for indicator in 
                       ['friend', 'memory', 'experience', 'relationship', 'together', 
                        'shared', 'remember', 'important', 'special', 'meaningful']):
                    # Extract the main concept from these sentences
                    clean_sentence = re.sub(r'[^\w\s]', ' ', sentence.lower())
                    words = [w for w in clean_sentence.split() if w not in stop_words and len(w) > 3]
                    if words:
                        theme_indicators.extend(words[:2])  # Take first 2 meaningful words
            
            if theme_indicators:
                # Create meaningful topic phrases from theme indicators
                unique_indicators = list(dict.fromkeys(theme_indicators))  # Remove duplicates while preserving order
                for i in range(0, len(unique_indicators), 2):
                    if i + 1 < len(unique_indicators):
                        topics.append(f"{unique_indicators[i]} {unique_indicators[i+1]}")
                    else:
                        topics.append(unique_indicators[i])
        
        # Final fallback: use general themes based on text analysis
        if not topics:
            topics = ["personal experiences", "relationships", "memorable moments"]
        
        return topics[:5]  # Return up to 5 topics
    
    def segment_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        Segment text into smaller chunks if it's too long.
        
        Args:
            text: Input text
            max_length: Maximum length of each segment
            
        Returns:
            List of text segments
        """
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences to avoid cutting in the middle of a sentence
        sentences = re.split(r'([.!?])', text)
        
        # Recombine sentence with its punctuation
        complete_sentences = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                complete_sentences.append(sentences[i] + sentences[i+1])
            else:
                complete_sentences.append(sentences[i])
        
        segments = []
        current_segment = ""
        
        for sentence in complete_sentences:
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
            
        return segments
