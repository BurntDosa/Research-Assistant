#!/usr/bin/env python3
"""
API Key Manager
Handles user API key configuration and validation
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages API keys for the Research Assistant"""
    
    REQUIRED_KEYS = {
        'GEMINI_API_KEY': {
            'name': 'Google Gemini API Key',
            'description': 'Required for AI-powered features (literature review, gap analysis, feasibility assessment, LaTeX generation)',
            'get_url': 'https://makersuite.google.com/app/apikey',
            'validation_prefix': 'AIza'
        },
        'SERPAPI_KEY': {
            'name': 'SerpAPI Key',
            'description': 'Required for Google Scholar search',
            'get_url': 'https://serpapi.com/manage-api-key',
            'validation_prefix': None
        }
    }
    
    OPTIONAL_KEYS = {
        'OPENAI_API_KEY': {
            'name': 'OpenAI API Key',
            'description': 'Optional: For alternative AI features',
            'get_url': 'https://platform.openai.com/api-keys',
            'validation_prefix': 'sk-'
        }
    }
    
    # ========== ADMIN OVERRIDE FOR TESTING ==========
    # TODO: Remove this before production deployment
    # This allows developers to bypass API key configuration during development
    ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'
    
    def __init__(self, config_file: str = ".env"):
        """Initialize API Key Manager"""
        self.config_file = Path(config_file)
        self.keys = {}
        self.load_keys()
        
        # Admin override: Load keys from environment variables if ADMIN_MODE is enabled
        if self.ADMIN_MODE and not self.keys:
            self._load_from_environment()
            logger.warning("🔧 ADMIN MODE: Loading API keys from environment variables")
    
    def load_keys(self) -> None:
        """Load existing API keys from .env file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key in self.REQUIRED_KEYS or key in self.OPTIONAL_KEYS:
                                self.keys[key] = value
                logger.info(f"Loaded {len(self.keys)} API keys from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load keys: {e}")
    
    def _load_from_environment(self) -> None:
        """
        Load API keys from environment variables (ADMIN MODE ONLY)
        
        TODO: Remove before production deployment
        This is a developer convenience feature for testing
        """
        logger.warning("⚠️ LOADING KEYS FROM ENVIRONMENT - ADMIN MODE ACTIVE")
        
        for key_name in self.REQUIRED_KEYS:
            value = os.environ.get(key_name)
            if value:
                self.keys[key_name] = value
                logger.info(f"  ✓ Loaded {key_name} from environment")
        
        for key_name in self.OPTIONAL_KEYS:
            value = os.environ.get(key_name)
            if value:
                self.keys[key_name] = value
                logger.info(f"  ✓ Loaded {key_name} from environment")
        
        if self.keys:
            logger.warning(f"🔧 Admin mode loaded {len(self.keys)} keys from environment variables")
    
    def save_keys(self, keys_dict: Dict[str, str]) -> Tuple[bool, str]:
        """
        Save API keys to .env file
        
        Args:
            keys_dict: Dictionary of API keys
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate required keys
            missing_keys = []
            for key_name in self.REQUIRED_KEYS:
                if key_name not in keys_dict or not keys_dict[key_name].strip():
                    missing_keys.append(self.REQUIRED_KEYS[key_name]['name'])
            
            if missing_keys:
                return False, f"Missing required API keys: {', '.join(missing_keys)}"
            
            # Validate key formats
            validation_errors = []
            for key_name, key_value in keys_dict.items():
                if not key_value or not key_value.strip():
                    continue
                
                key_info = self.REQUIRED_KEYS.get(key_name) or self.OPTIONAL_KEYS.get(key_name)
                if key_info and key_info['validation_prefix']:
                    if not key_value.startswith(key_info['validation_prefix']):
                        validation_errors.append(
                            f"{key_info['name']} should start with '{key_info['validation_prefix']}'"
                        )
            
            if validation_errors:
                return False, "Invalid key format:\n" + "\n".join(validation_errors)
            
            # Create backup of existing .env
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.env.backup')
                import shutil
                shutil.copy2(self.config_file, backup_file)
            
            # Read existing .env to preserve other variables
            existing_lines = []
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key = line.split('=', 1)[0].strip()
                            # Skip lines with keys we're updating
                            if key in keys_dict:
                                continue
                        existing_lines.append(line)
            
            # Write new .env file
            with open(self.config_file, 'w') as f:
                # Write header
                f.write("# Research Assistant API Configuration\n")
                f.write("# Generated by API Key Manager\n\n")
                
                # Write required keys
                f.write("# Required API Keys\n")
                for key_name in self.REQUIRED_KEYS:
                    if key_name in keys_dict and keys_dict[key_name].strip():
                        f.write(f'{key_name}="{keys_dict[key_name].strip()}"\n')
                
                # Write optional keys
                f.write("\n# Optional API Keys\n")
                for key_name in self.OPTIONAL_KEYS:
                    if key_name in keys_dict and keys_dict[key_name].strip():
                        f.write(f'{key_name}="{keys_dict[key_name].strip()}"\n')
                
                # Write other existing variables
                if existing_lines:
                    f.write("\n# Other Configuration\n")
                    for line in existing_lines:
                        if line:
                            f.write(line + "\n")
            
            # Update environment variables
            for key_name, key_value in keys_dict.items():
                if key_value and key_value.strip():
                    os.environ[key_name] = key_value.strip()
                    self.keys[key_name] = key_value.strip()
            
            logger.info(f"Successfully saved {len(keys_dict)} API keys")
            return True, "API keys saved successfully! You can now use the Research Assistant."
            
        except Exception as e:
            logger.error(f"Failed to save keys: {e}")
            return False, f"Error saving API keys: {str(e)}"
    
    def validate_keys(self) -> Tuple[bool, str]:
        """
        Validate that all required keys are present
        
        Returns:
            Tuple of (valid: bool, message: str)
        """
        missing_keys = []
        for key_name, key_info in self.REQUIRED_KEYS.items():
            if key_name not in self.keys or not self.keys[key_name]:
                missing_keys.append(key_info['name'])
        
        if missing_keys:
            return False, f"Missing required API keys: {', '.join(missing_keys)}"
        
        return True, "All required API keys are configured"
    
    def get_key(self, key_name: str) -> Optional[str]:
        """Get a specific API key"""
        return self.keys.get(key_name)
    
    def has_all_required_keys(self) -> bool:
        """Check if all required keys are present"""
        valid, _ = self.validate_keys()
        return valid
    
    def get_configuration_status(self) -> Dict[str, bool]:
        """Get status of all API keys"""
        status = {}
        for key_name in self.REQUIRED_KEYS:
            status[key_name] = key_name in self.keys and bool(self.keys[key_name])
        for key_name in self.OPTIONAL_KEYS:
            status[key_name] = key_name in self.keys and bool(self.keys[key_name])
        return status
    
    def clear_keys(self) -> None:
        """Clear all API keys from memory (not from file)"""
        self.keys.clear()


if __name__ == "__main__":
    # Test the API Key Manager
    manager = APIKeyManager()
    print("API Key Configuration Status:")
    print(f"Has all required keys: {manager.has_all_required_keys()}")
    print(f"\nConfiguration status:")
    for key, status in manager.get_configuration_status().items():
        print(f"  {key}: {'✓' if status else '✗'}")
