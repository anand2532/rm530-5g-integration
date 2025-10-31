"""Configuration loader with YAML support."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from rm530_5g_integration.config.defaults import (
    DEFAULT_CARRIERS,
    DEFAULT_NETWORK_SETTINGS,
    DEFAULT_MODEM_SETTINGS,
)
from rm530_5g_integration.config.validator import validate_config, ConfigValidator
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Load and manage configuration from files and defaults."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._load()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = Path.home() / ".rm530"
        config_dir.mkdir(exist_ok=True, mode=0o755)
        return str(config_dir / "config.yaml")
    
    def _load(self) -> None:
        """Load configuration from file or use defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    if YAML_AVAILABLE:
                        self.config = yaml.safe_load(f) or {}
                    else:
                        logger.warning("PyYAML not installed, using default config")
                        self.config = {}
            except Exception as e:
                logger.warning(f"Error loading config file: {e}, using defaults")
                self.config = {}
        
        # Merge with defaults
        self.config.setdefault("carriers", DEFAULT_CARRIERS)
        self.config.setdefault("defaults", DEFAULT_NETWORK_SETTINGS)
        self.config.setdefault("modem", DEFAULT_MODEM_SETTINGS)
        
        # Validate configuration
        try:
            validate_config(self.config)
        except Exception as e:
            logger.warning(f"Configuration validation warning: {e}")
            # Don't raise, but log warning
    
    def get_carrier_config(self, carrier: str) -> Dict[str, Any]:
        """
        Get configuration for a specific carrier.
        
        Args:
            carrier: Carrier name (e.g., 'airtel', 'jio')
        
        Returns:
            Carrier configuration dictionary
        """
        carriers = self.config.get("carriers", DEFAULT_CARRIERS)
        return carriers.get(carrier.lower(), {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default network settings."""
        return self.config.get("defaults", DEFAULT_NETWORK_SETTINGS)
    
    def get_modem_settings(self) -> Dict[str, Any]:
        """Get modem communication settings."""
        return self.config.get("modem", DEFAULT_MODEM_SETTINGS)


def load_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to config file (optional)
    
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path)


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "carriers": DEFAULT_CARRIERS,
        "defaults": DEFAULT_NETWORK_SETTINGS,
        "modem": DEFAULT_MODEM_SETTINGS,
    }

