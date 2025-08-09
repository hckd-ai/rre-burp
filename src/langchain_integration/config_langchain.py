#!/usr/bin/env python3
"""
Configuration for LangChain RRE Integration
-------------------------------------------

This file contains configuration settings for the LangChain RRE application,
including model settings, analysis parameters, and customization options.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LangChainConfig:
    """Configuration class for LangChain RRE application"""
    
    # OpenAI Configuration
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.1
    openai_max_tokens: Optional[int] = None
    
    # RRE Analysis Configuration
    entropy_threshold: float = 3.0
    max_analysis_depth: int = 10
    auto_discover_limit: int = 10
    
    # HAR Collection Configuration
    default_wait_time: float = 5.0
    default_timeout: int = 45000
    headless_default: bool = True
    
    # Output Configuration
    output_dir: Path = Path("./output")
    log_level: str = "INFO"
    
    # Analysis Modes
    enabled_analysis_modes: list = None
    custom_patterns: Dict[str, str] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.enabled_analysis_modes is None:
            self.enabled_analysis_modes = [
                "pattern_recognition",
                "dependency_mapping", 
                "vulnerability_scanning",
                "api_analysis",
                "authentication_analysis"
            ]
        
        if self.custom_patterns is None:
            self.custom_patterns = {
                "jwt_tokens": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
                "api_keys": r"[A-Za-z0-9]{20,}",
                "session_ids": r"[a-f0-9]{32,}",
                "user_ids": r"\b\d{6,}\b"
            }
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

class ConfigManager:
    """Manager for configuration loading and validation"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> LangChainConfig:
        """Load configuration from file or environment variables"""
        
        # Start with defaults
        config = LangChainConfig()
        
        # Override with environment variables
        config.openai_model = os.getenv("LANGCHAIN_MODEL", config.openai_model)
        config.openai_temperature = float(os.getenv("LANGCHAIN_TEMPERATURE", config.openai_temperature))
        
        if os.getenv("LANGCHAIN_MAX_TOKENS"):
            config.openai_max_tokens = int(os.getenv("LANGCHAIN_MAX_TOKENS"))
        
        config.entropy_threshold = float(os.getenv("RRE_ENTROPY_THRESHOLD", config.entropy_threshold))
        config.max_analysis_depth = int(os.getenv("RRE_MAX_DEPTH", config.max_analysis_depth))
        
        # Load from config file if specified
        if self.config_file and Path(self.config_file).exists():
            config = self._load_from_file(config, self.config_file)
        
        return config
    
    def _load_from_file(self, config: LangChainConfig, file_path: str) -> LangChainConfig:
        """Load configuration from a file"""
        try:
            import yaml
            
            with open(file_path, 'r') as f:
                file_config = yaml.safe_load(f)
            
            # Update config with file values
            for key, value in file_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
        except ImportError:
            print("PyYAML not installed, skipping config file loading")
        except Exception as e:
            print(f"Error loading config file: {e}")
        
        return config
    
    def get_config(self) -> LangChainConfig:
        """Get the current configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def save_config(self, file_path: str) -> None:
        """Save current configuration to file"""
        try:
            import yaml
            
            config_dict = {
                key: getattr(self.config, key) 
                for key in self.config.__annotations__
            }
            
            with open(file_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                
        except ImportError:
            print("PyYAML not installed, cannot save config file")
        except Exception as e:
            print(f"Error saving config file: {e}")

# Default configuration instance
default_config = LangChainConfig()

# Configuration manager instance
config_manager = ConfigManager()

def get_config() -> LangChainConfig:
    """Get the current configuration"""
    return config_manager.get_config()

def update_config(**kwargs) -> None:
    """Update configuration values"""
    config_manager.update_config(**kwargs)

def save_config(file_path: str) -> None:
    """Save current configuration to file"""
    config_manager.save_config(file_path)

# Example configuration file template
CONFIG_TEMPLATE = """
# LangChain RRE Configuration
# Copy this to config.yaml and modify as needed

# OpenAI Configuration
openai_model: "gpt-4-turbo-preview"
openai_temperature: 0.1
openai_max_tokens: null

# RRE Analysis Configuration
entropy_threshold: 3.0
max_analysis_depth: 10
auto_discover_limit: 10

# HAR Collection Configuration
default_wait_time: 5.0
default_timeout: 45000
headless_default: true

# Output Configuration
output_dir: "./output"
log_level: "INFO"

# Analysis Modes
enabled_analysis_modes:
  - pattern_recognition
  - dependency_mapping
  - vulnerability_scanning
  - api_analysis
  - authentication_analysis

# Custom Patterns
custom_patterns:
  jwt_tokens: "eyJ[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*"
  api_keys: "[A-Za-z0-9]{20,}"
  session_ids: "[a-f0-9]{32,}"
  user_ids: "\\b\\d{6,}\\b"
"""

if __name__ == "__main__":
    # Print current configuration
    config = get_config()
    print("Current Configuration:")
    print("=" * 30)
    for key, value in config.__dict__.items():
        print(f"{key}: {value}")
    
    print("\nConfiguration Template:")
    print("=" * 30)
    print(CONFIG_TEMPLATE) 