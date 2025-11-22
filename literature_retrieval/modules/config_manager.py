"""
Configuration management for literature retrieval system.
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for literature retrieval system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._override_with_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Load default config
        default_config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/default_config.yaml'
        )
        
        if os.path.exists(default_config_path):
            with open(default_config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Return minimal default config
        return {
            'search': {'sources': ['semantic_scholar', 'arxiv'], 'limit_per_source': 10},
            'relevance': {'scorer_type': 'simple', 'top_k': 10},
            'llm': {'enabled': False},
            'github': {'auto_create_pr': False},
            'general': {'log_level': 'INFO'}
        }
    
    def _override_with_env_vars(self):
        """Override config with environment variables."""
        # API keys
        if 'SEMANTIC_SCHOLAR_API_KEY' in os.environ:
            self.config.setdefault('semantic_scholar', {})
            self.config['semantic_scholar']['api_key'] = os.environ['SEMANTIC_SCHOLAR_API_KEY']
        
        if 'OPENAI_API_KEY' in os.environ:
            self.config.setdefault('llm', {})
            self.config['llm']['api_key'] = os.environ['OPENAI_API_KEY']
        
        if 'ANTHROPIC_API_KEY' in os.environ:
            self.config.setdefault('llm', {})
            self.config['llm']['api_key'] = os.environ['ANTHROPIC_API_KEY']
        
        if 'GITHUB_TOKEN' in os.environ:
            self.config.setdefault('github', {})
            self.config['github']['github_token'] = os.environ['GITHUB_TOKEN']
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            key: Dot-separated key path (e.g., 'search.limit_per_source')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by key path.
        
        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str):
        """
        Save configuration to YAML file.
        
        Args:
            path: Path to save configuration
        """
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {path}")
