"""
LLM Generator module for interfacing with language models.
"""
import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    Handles interaction with Language Model APIs.
    Currently supports OpenAI's API, with extensibility for other models.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM Generator.
        
        Args:
            config_path: Path to configuration file with API keys and settings
        """
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 500
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
            
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update attributes from config
            if "api_key" in config:
                self.api_key = config["api_key"]
            if "model" in config:
                self.model = config["model"]
            if "temperature" in config:
                self.temperature = config["temperature"]
            if "max_tokens" in config:
                self.max_tokens = config["max_tokens"]
                
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
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using the configured LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated text response
            
        Raises:
            ValueError: If API key is not set
            RuntimeError: If there's an error with the API call
        """
        if not self.api_key:
            raise ValueError("API key not set. Set it via environment variable OPENAI_API_KEY or in the config file.")
        
        try:
            # OpenAI API call
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                raise RuntimeError(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
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
        if not self.api_key:
            raise ValueError("API key not set. Set it via environment variable OPENAI_API_KEY or in the config file.")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                raise RuntimeError(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise RuntimeError(f"Error generating text: {str(e)}")
