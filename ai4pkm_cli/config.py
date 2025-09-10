"""Configuration management for AI4PKM CLI."""

import json
import os
from typing import Dict, Any


class Config:
    """Handles configuration for AI4PKM CLI."""
    
    DEFAULT_CONFIG = {
        "default-agent": "claude_code",  # Options: claude_code, gemini_cli, codex_cli
        "agents-config": {
            "claude_code": {
                "permission_mode": "bypassPermissions"
            },
            "gemini_cli": {
                "command": "gemini"  # CLI command name
            },
            "codex_cli": {
                "command": "codex"  # CLI command name
            }
        },
        "cron_jobs": []
    }
    
    def __init__(self, config_file=None):
        """Initialize configuration."""
        if config_file is None:
            # Use current working directory for config file
            self.config_file = os.path.join(os.getcwd(), "ai4pkm_cli.json")
        else:
            self.config_file = config_file
            
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"⚠️  Error loading config, using defaults: {e}")
                return self.DEFAULT_CONFIG
        else:
            # Create config file with defaults
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
            
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")
            
    def get(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key: str, value: Any):
        """Set configuration value and save."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)
        
    def get_agent(self) -> str:
        """Get current default agent selection."""
        return self.get('default-agent', 'claude_code')
        
    def set_agent(self, agent: str):
        """Set current default agent and save."""
        if agent not in ['claude_code', 'gemini_cli', 'codex_cli']:
            raise ValueError(f"Invalid agent: {agent}. Must be one of: claude_code, gemini_cli, codex_cli")
        self.set('default-agent', agent)
        
    def get_cron_jobs(self) -> list:
        """Get cron jobs from configuration."""
        return self.get('cron_jobs', [])
        
    def get_agent_config(self, agent: str = None) -> Dict[str, Any]:
        """Get configuration for specific agent."""
        if agent is None:
            agent = self.get_agent()
        return self.get(f'agents-config.{agent}', {})
