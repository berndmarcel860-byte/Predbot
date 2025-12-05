"""
Configuration module for Predbot.
Loads settings from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the trading bot."""
    
    # Binance API
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Bot Configuration
    TOP_VOLATILE_COINS = int(os.getenv("TOP_VOLATILE_COINS", "20"))
    VOLATILITY_PERIOD = int(os.getenv("VOLATILITY_PERIOD", "24"))  # hours
    MIN_VOLUME_USD = float(os.getenv("MIN_VOLUME_USD", "10000000"))
    
    # Timeframes
    TIMEFRAMES = os.getenv("TIMEFRAMES", "5m,15m,1h,4h").split(",")
    
    # Analysis thresholds
    TREND_CONFIRMATION_THRESHOLD = float(os.getenv("TREND_CONFIRMATION_THRESHOLD", "0.7"))
    SIGNAL_STRENGTH_THRESHOLD = int(os.getenv("SIGNAL_STRENGTH_THRESHOLD", "60"))
    
    # Notification settings
    ENABLE_TELEGRAM = os.getenv("ENABLE_TELEGRAM", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []
        
        if not cls.BINANCE_API_KEY:
            errors.append("BINANCE_API_KEY is required")
        if not cls.BINANCE_API_SECRET:
            errors.append("BINANCE_API_SECRET is required")
        if cls.ENABLE_TELEGRAM:
            if not cls.TELEGRAM_BOT_TOKEN:
                errors.append("TELEGRAM_BOT_TOKEN is required when Telegram is enabled")
            if not cls.TELEGRAM_CHAT_ID:
                errors.append("TELEGRAM_CHAT_ID is required when Telegram is enabled")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        return True
