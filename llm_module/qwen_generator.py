"""
Qwen Generator module for interfacing with Alibaba Cloud Qwen language models.
"""
import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QwenGenerator:
    """
    Handles interaction with Alibaba Cloud Qwen API.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Qwen Generator.
        
        Args:
            config_path: Path to configuration file with API keys and settings
        """
        # Default configuration
        self.api_key = os.environ.get("QWEN_API_KEY", "")
        self.model = "qwen-max"  # Default model
        self.temperature = 0.7
        self.max_tokens = 500
        self.api_base = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
            
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Update attributes from config
            if "qwen_api_key" in config:
                self.api_key = config["qwen_api_key"]
                logger.info("Qwen API key loaded from config file")
            if "qwen_model" in config:
                self.model = config["qwen_model"]
            if "temperature" in config:
                self.temperature = config["temperature"]
            if "max_tokens" in config:
                self.max_tokens = config["max_tokens"]
            if "qwen_api_base" in config:
                self.api_base = config["qwen_api_base"]
                
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
    
    def configure(self, **kwargs) -> None:
        """
        Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        if "model" in kwargs:
            self.model = kwargs["model"]
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
        if "max_tokens" in kwargs:
            self.max_tokens = kwargs["max_tokens"]
        if "api_base" in kwargs:
            self.api_base = kwargs["api_base"]
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using Qwen API.
        
        Args:
            prompt: The prompt to send to the Qwen model
            
        Returns:
            Generated text response
            
        Raises:
            ValueError: If API key is not set
            RuntimeError: If there's an error with the API call
        """
        if not self.api_key:
            raise ValueError("Qwen API key not set. Set it via environment variable QWEN_API_KEY or in the config file.")
        
        try:
            # Qwen API call
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            }
            
            response = requests.post(
                self.api_base,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                raise RuntimeError(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            # Extract the generated text from the response
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"].strip()
            else:
                logger.error(f"Unexpected API response format: {result}")
                raise RuntimeError(f"Unexpected API response format: {result}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise RuntimeError(f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise RuntimeError(f"Error generating text: {str(e)}")
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text with separate system and user prompts.
        
        Args:
            system_prompt: Instructions for the AI system
            user_prompt: User's input prompt
            
        Returns:
            Generated text response
        """
        # For Qwen API, combine the system and user prompts
        combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        return self.generate_text(combined_prompt)
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3, delay: float = 2.0) -> str:
        """
        Generate text with retry mechanism for handling API errors.
        
        Args:
            prompt: The prompt to send to the model
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
            
        Returns:
            Generated text response
        """
        for attempt in range(max_retries):
            try:
                return self.generate_text(prompt)
            except RuntimeError as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit hit. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                elif attempt < max_retries - 1:
                    logger.warning(f"API error: {str(e)}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
