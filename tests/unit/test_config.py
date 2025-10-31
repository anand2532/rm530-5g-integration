"""Unit tests for config module."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from rm530_5g_integration.config.loader import ConfigLoader
from rm530_5g_integration.config.defaults import DEFAULT_CARRIERS, DEFAULT_NETWORK_SETTINGS


class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_config_loader_default_path(self):
        """Test default config path."""
        with patch('pathlib.Path.home', return_value=Path('/home/test')):
            loader = ConfigLoader()
            expected = Path('/home/test/.rm530/config.yaml')
            assert loader.config_path == str(expected)
    
    def test_config_loader_custom_path(self):
        """Test custom config path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('carriers:\n  test:\n    apn: test.apn')
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path=config_path)
            assert loader.config_path == config_path
        finally:
            os.unlink(config_path)
    
    def test_config_loader_no_file(self):
        """Test loading when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'nonexistent.yaml')
            loader = ConfigLoader(config_path=config_path)
            
            # Should use defaults
            assert loader.config['carriers'] == DEFAULT_CARRIERS
            assert loader.config['defaults'] == DEFAULT_NETWORK_SETTINGS
    
    def test_get_carrier_config_existing(self, sample_config):
        """Test getting existing carrier config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(sample_config, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path=config_path)
            carrier_config = loader.get_carrier_config('airtel')
            assert carrier_config['apn'] == 'airtelgprs.com'
            assert carrier_config['preferred_interface'] == 'usb0'
        finally:
            os.unlink(config_path)
    
    def test_get_carrier_config_not_found(self):
        """Test getting non-existent carrier config."""
        loader = ConfigLoader()
        carrier_config = loader.get_carrier_config('nonexistent')
        assert carrier_config == {}
    
    def test_get_defaults(self, sample_config):
        """Test getting default settings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(sample_config, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.get_defaults()
            assert defaults['route_metric'] == 100
            assert defaults['autoconnect'] is True
        finally:
            os.unlink(config_path)

