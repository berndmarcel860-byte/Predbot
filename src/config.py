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
    
    # Futures Trading Configuration
    LEVERAGE = int(os.getenv("LEVERAGE", "20"))  # Default 20x leverage
    MARGIN_TYPE = os.getenv("MARGIN_TYPE", "CROSSED")  # CROSSED or ISOLATED
    
    # Timeframes
    TIMEFRAMES = os.getenv("TIMEFRAMES", "5m,15m,1h,4h").split(",")
    
    # Analysis thresholds - STRICTER for better trade quality
    TREND_CONFIRMATION_THRESHOLD = float(os.getenv("TREND_CONFIRMATION_THRESHOLD", "0.75"))  # 75% for high probability
    SIGNAL_STRENGTH_THRESHOLD = int(os.getenv("SIGNAL_STRENGTH_THRESHOLD", "70"))  # Minimum 70% signal
    
    # Scalping trade quality thresholds - STRICTER to avoid loss trades
    MIN_RISK_REWARD_RATIO = float(os.getenv("MIN_RISK_REWARD_RATIO", "2.0"))  # Minimum 1:2 R/R
    MIN_INDICATOR_ALIGNMENT = int(os.getenv("MIN_INDICATOR_ALIGNMENT", "7"))  # At least 7/10 indicators
    MIN_TIMEFRAME_ALIGNMENT = float(os.getenv("MIN_TIMEFRAME_ALIGNMENT", "0.7"))  # 70% timeframe alignment
    MIN_PROFIT_POTENTIAL = float(os.getenv("MIN_PROFIT_POTENTIAL", "1.0"))  # Minimum 1% profit potential
    
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
        
        # Validate leverage
        if cls.LEVERAGE < 1 or cls.LEVERAGE > 125:
            errors.append("LEVERAGE must be between 1 and 125")
        
        # Validate margin type
        if cls.MARGIN_TYPE not in ["CROSSED", "ISOLATED"]:
            errors.append("MARGIN_TYPE must be CROSSED or ISOLATED")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        return True
