"""
Configuration Manager
Handles loading and managing application configuration
"""

import json
import os
import logging
from typing import Dict, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found at {self.config_path}")
                self.config = self._get_default_config()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def _get_default_config(self) -> Dict:
        """
        Get default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            "job_search": {
                "keywords": ["python developer", "software engineer", "data scientist"],
                "locations": ["Remote", "New York, NY", "San Francisco, CA"],
                "job_sources": ["indeed", "glassdoor", "linkedin"],
                "pages_to_scrape": 5
            },
            "application_settings": {
                "auto_apply": True,
                "max_applications_per_day": 20,
                "delay_between_applications": 3,
                "apply_to_all_matching": False
            },
            "resume": {
                "base_resume_path": "resumes/resume.docx",
                "customize_for_job": True,
                "create_versions": True
            },
            "filters": {
                "exclude_keywords": ["contract", "temporary", "freelance"],
                "required_keywords": [],
                "min_salary": 0,
                "exclude_companies": []
            },
            "database": {
                "type": "sqlite",
                "path": "data/jobs.db"
            },
            "logging": {
                "level": "INFO",
                "log_file": "logs/automation.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dots, e.g., 'job_search.keywords')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
            
            return value
            
        except KeyError:
            logger.warning(f"Configuration key not found: {key}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports nested keys with dots)
            value: Value to set
            
        Returns:
            True if successful
        """
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            logger.info(f"Set configuration {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        """
        try:
            required_sections = ['job_search', 'application_settings', 'resume']
            
            for section in required_sections:
                if section not in self.config:
                    logger.warning(f"Missing configuration section: {section}")
                    return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def get_all_config(self) -> Dict:
        """
        Get entire configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
