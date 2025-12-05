"""
Telegram Notification Service.
Sends trade alerts to Telegram.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional
import telegram
from telegram import Bot

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram notification service for trade alerts."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize the Telegram notifier.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.enabled = True
    
    async def send_message(self, message: str) -> bool:
        """Send a message to Telegram."""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Telegram message sent successfully")
            return True
        except telegram.error.TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def format_trade_alert(
        self,
        symbol: str,
        direction: str,
        signal_strength: float,
        current_price: float,
        timeframe_results: dict,
        indicators: dict,
        patterns: list
    ) -> str:
        """Format a trade alert message."""
        
        emoji = "🟢" if direction == "bullish" else "🔴" if direction == "bearish" else "⚪"
        direction_text = direction.upper()
        recommendation = "LONG" if direction == "bullish" else "SHORT" if direction == "bearish" else "WAIT"
        
        # Build the message
        message = f"""
{emoji} <b>TRADE ALERT: {symbol}</b> {emoji}

📊 <b>Signal:</b> {recommendation}
💪 <b>Strength:</b> {signal_strength}%
💰 <b>Price:</b> ${current_price:,.4f}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

<b>📈 Timeframe Analysis:</b>
"""
        
        # Add timeframe results
        for tf, result in timeframe_results.items():
            tf_emoji = "🟢" if result['direction'] == 'bullish' else "🔴" if result['direction'] == 'bearish' else "⚪"
            message += f"  {tf_emoji} {tf}: {result['direction'].upper()} ({result['strength']}%)\n"
        
        # Add key indicators
        if indicators:
            message += "\n<b>🔧 Key Indicators:</b>\n"
            for name, signal in list(indicators.items())[:5]:
                ind_emoji = "🟢" if signal == 1 else "🔴" if signal == -1 else "⚪"
                signal_text = "BUY" if signal == 1 else "SELL" if signal == -1 else "NEUTRAL"
                message += f"  {ind_emoji} {name.upper()}: {signal_text}\n"
        
        # Add detected patterns
        if patterns:
            message += "\n<b>📐 Patterns Detected:</b>\n"
            for pattern in patterns[:3]:
                pattern_emoji = "🟢" if pattern['signal'] == 1 else "🔴"
                message += f"  {pattern_emoji} {pattern['name']}: {pattern['confidence']}% confidence\n"
        
        message += "\n⚠️ <i>This is not financial advice. Always do your own research.</i>"
        
        return message
    
    async def send_trade_alert(
        self,
        symbol: str,
        direction: str,
        signal_strength: float,
        current_price: float,
        timeframe_results: dict,
        indicators: dict = None,
        patterns: list = None
    ) -> bool:
        """Send a formatted trade alert."""
        if not self.enabled:
            logger.info("Telegram notifications disabled")
            return False
        
        message = self.format_trade_alert(
            symbol=symbol,
            direction=direction,
            signal_strength=signal_strength,
            current_price=current_price,
            timeframe_results=timeframe_results,
            indicators=indicators or {},
            patterns=patterns or []
        )
        
        return await self.send_message(message)
    
    async def send_startup_message(self) -> bool:
        """Send a startup notification."""
        message = """
🤖 <b>Predbot Started</b>

📊 Binance Futures Trading Analysis Bot is now running.
⏰ Scanning for high-potential trade opportunities...

Bot will send alerts when strong signals are detected.
"""
        return await self.send_message(message)
    
    async def send_scan_summary(
        self,
        coins_scanned: int,
        signals_found: int,
        top_signals: list
    ) -> bool:
        """Send a summary of the scan results."""
        message = f"""
📊 <b>Scan Summary</b>

🔍 Coins Scanned: {coins_scanned}
📈 Strong Signals Found: {signals_found}

"""
        
        if top_signals:
            message += "<b>Top Opportunities:</b>\n"
            for i, signal in enumerate(top_signals[:5], 1):
                emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
                message += f"{i}. {emoji} {signal['symbol']}: {signal['direction'].upper()} ({signal['strength']}%)\n"
        else:
            message += "No strong signals detected in this scan."
        
        message += f"\n⏰ Next scan in progress..."
        
        return await self.send_message(message)
