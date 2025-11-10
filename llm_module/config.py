"""
Configuration utilities for the LLM module.
"""
import os
import json
from typing import Dict, Any, Optional


class Config:
    """
    Configuration manager for the LLM module.
    """
    
    DEFAULT_CONFIG = {
        "api_key": "",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 500,
        "num_questions": 5,
        "tts_integration": {
            "enabled": True,
            "voice": "en-US-Neural2-F"
        },
        "speech_recognition": {
            "engine": "google",
            "language": "en-US",
            "api_key": "",
            "timeout": 10.0,
            "phrase_timeout": 5.0
        },
        "speech_recording": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "auto_stop_on_silence": True,
            "silence_threshold": 500,
            "silence_duration": 2.0,
            "max_duration": 300
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration, optionally loading from a file.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Try to load from environment variables first
        self._load_from_env()
        
        # Then load from file if provided (overrides env vars)
        if config_path:
            self.load_from_file(config_path)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if os.environ.get("OPENAI_API_KEY"):
            self.config["api_key"] = os.environ.get("OPENAI_API_KEY")
        
        if os.environ.get("LLM_MODEL"):
            self.config["model"] = os.environ.get("LLM_MODEL")
            
        if os.environ.get("LLM_TEMPERATURE"):
            try:
                self.config["temperature"] = float(os.environ.get("LLM_TEMPERATURE"))
            except (ValueError, TypeError):
                pass
                
        if os.environ.get("LLM_MAX_TOKENS"):
            try:
                self.config["max_tokens"] = int(os.environ.get("LLM_MAX_TOKENS"))
            except (ValueError, TypeError):
                pass
                
        if os.environ.get("LLM_NUM_QUESTIONS"):
            try:
                self.config["num_questions"] = int(os.environ.get("LLM_NUM_QUESTIONS"))
            except (ValueError, TypeError):
                pass
        
        # Speech recognition environment variables
        if os.environ.get("STT_ENGINE"):
            self.config["speech_recognition"]["engine"] = os.environ.get("STT_ENGINE")
            
        if os.environ.get("STT_LANGUAGE"):
            self.config["speech_recognition"]["language"] = os.environ.get("STT_LANGUAGE")
            
        if os.environ.get("STT_API_KEY"):
            self.config["speech_recognition"]["api_key"] = os.environ.get("STT_API_KEY")
            
        if os.environ.get("STT_TIMEOUT"):
            try:
                self.config["speech_recognition"]["timeout"] = float(os.environ.get("STT_TIMEOUT"))
            except (ValueError, TypeError):
                pass
    
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                
            # Update config with values from file
            for key, value in file_config.items():
                if key in self.config:
                    self.config[key] = value
                    
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Invalid JSON in configuration file: {config_path}", "", 0)
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to a JSON file.
        
        Args:
            config_path: Path to save the configuration file
            
        Raises:
            IOError: If there's an error writing to the file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
                
        except IOError as e:
            raise IOError(f"Error writing configuration to {config_path}: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
