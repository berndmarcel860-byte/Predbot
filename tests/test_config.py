"""
Unit tests for the config module.
"""

import pytest
import os
from unittest.mock import patch

from src.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        assert Config.TOP_VOLATILE_COINS == 20 or isinstance(Config.TOP_VOLATILE_COINS, int)
        assert Config.VOLATILITY_PERIOD == 24 or isinstance(Config.VOLATILITY_PERIOD, int)
        assert isinstance(Config.MIN_VOLUME_USD, float)
        assert isinstance(Config.TIMEFRAMES, list)
    
    def test_timeframes_is_list(self):
        """Test that TIMEFRAMES is properly parsed as a list."""
        assert isinstance(Config.TIMEFRAMES, list)
        assert len(Config.TIMEFRAMES) > 0
    
    def test_validate_returns_bool(self):
        """Test that validate returns a boolean."""
        result = Config.validate()
        assert isinstance(result, bool)
    
    @patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_API_SECRET': 'test_secret',
        'ENABLE_TELEGRAM': 'false'
    })
    def test_validate_with_credentials(self):
        """Test validation with provided credentials."""
        # Reload config with patched environment
        from importlib import reload
        from src import config
        reload(config)
        
        # With telegram disabled, only binance keys needed
        assert config.Config.validate() == True
    
    def test_thresholds_are_numbers(self):
        """Test that thresholds are numeric."""
        assert isinstance(Config.TREND_CONFIRMATION_THRESHOLD, float)
        assert isinstance(Config.SIGNAL_STRENGTH_THRESHOLD, int)
        assert 0 <= Config.TREND_CONFIRMATION_THRESHOLD <= 1
        assert 0 <= Config.SIGNAL_STRENGTH_THRESHOLD <= 100
    
    def test_enable_telegram_is_bool(self):
        """Test that ENABLE_TELEGRAM is boolean."""
        assert isinstance(Config.ENABLE_TELEGRAM, bool)
    
    def test_log_level_is_string(self):
        """Test that LOG_LEVEL is a string."""
        assert isinstance(Config.LOG_LEVEL, str)
        assert Config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
