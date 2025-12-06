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
    
    def format_scalping_trade_alert(
        self,
        trade: dict,
        timeframe_results: dict = None,
        indicators: dict = None
    ) -> str:
        """
        Format a scalping trade alert with 4 entries, 4 TPs, and stop loss.
        
        Args:
            trade: Scalping trade setup from ScalpingAnalyzer
            timeframe_results: Optional timeframe analysis results
            indicators: Optional indicator signals
            
        Returns:
            Formatted message string
        """
        direction = trade['direction']
        emoji = "🟢" if direction == "LONG" else "🔴"
        
        # Trade quality indicator - stricter thresholds
        score = trade.get('trade_score', 0)
        if score >= 85:
            quality = "⭐⭐⭐ EXCELLENT"
        elif score >= 75:
            quality = "⭐⭐ HIGH PROBABILITY"
        else:
            quality = "⭐ MODERATE"
        
        # Calculate average entry for DCA
        entries = trade['entries']
        avg_entry = sum(entries) / len(entries)
        
        # Get leverage and margin info
        leverage = trade.get('leverage', 20)
        margin_type = trade.get('margin_type', 'CROSSED')
        
        message = f"""
{emoji} <b>SCALPING TRADE: {trade['symbol']}</b> {emoji}

📊 <b>Direction:</b> {direction}
⚡ <b>Leverage:</b> {leverage}x {margin_type}
🏆 <b>Trade Quality:</b> {quality}
💯 <b>Score:</b> {score}/100
💰 <b>Current Price:</b> ${trade['current_price']:,.4f}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

<b>📍 DCA ENTRY LEVELS (25% each):</b>
  Entry 1 (25%): ${trade['entries'][0]:,.4f}
  Entry 2 (25%): ${trade['entries'][1]:,.4f}
  Entry 3 (25%): ${trade['entries'][2]:,.4f}
  Entry 4 (25%): ${trade['entries'][3]:,.4f}
  <b>📊 Avg Entry:</b> ${avg_entry:,.4f}

<b>🎯 TAKE PROFIT LEVELS (Scale Out):</b>
  TP1 (25%): ${trade['take_profits'][0]:,.4f}
  TP2 (25%): ${trade['take_profits'][1]:,.4f}
  TP3 (25%): ${trade['take_profits'][2]:,.4f}
  TP4 (25%): ${trade['take_profits'][3]:,.4f}

<b>🛑 STOP LOSS:</b> ${trade['stop_loss']:,.4f}

<b>📈 TRADE METRICS:</b>
  Risk: {trade['risk_percent']:.2f}%
  Reward: {trade['reward_percent']:.2f}%
  R:R Ratio: 1:{trade['risk_reward_ratio']:.1f}
  Indicators Aligned: {trade['indicators_aligned']}/10
"""
        
        # Add support/resistance levels
        if trade.get('support') or trade.get('resistance'):
            message += "\n<b>📊 KEY LEVELS:</b>\n"
            if trade.get('support'):
                message += f"  Support: ${trade['support']:,.4f}\n"
            if trade.get('resistance'):
                message += f"  Resistance: ${trade['resistance']:,.4f}\n"
        
        # Add timeframe analysis
        if timeframe_results:
            message += "\n<b>📈 Timeframe Analysis:</b>\n"
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
        
        message += """
<b>💡 DCA EXECUTION STRATEGY:</b>
• Place 25% of position at each entry level
• Wait for price to reach each level before adding
• Average entry price improves with each DCA fill
• Take 25% profit at each TP level
• Move stop to breakeven after TP1 hits

⚠️ <i>This is not financial advice. Always manage your risk.</i>
"""
        
        return message
    
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
        """Format a trade alert message with entry prices."""
        
        emoji = "🟢" if direction == "bullish" else "🔴" if direction == "bearish" else "⚪"
        direction_text = direction.upper()
        recommendation = "LONG" if direction == "bullish" else "SHORT" if direction == "bearish" else "WAIT"
        
        # Build the message
        message = f"""
{emoji} <b>TRADE ALERT: {symbol}</b> {emoji}

📊 <b>Signal:</b> {recommendation}
💪 <b>Strength:</b> {signal_strength}%
💰 <b>Current Price:</b> ${current_price:,.4f}
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
        
        # Add detected patterns with entry prices
        if patterns:
            message += "\n<b>📐 Patterns Detected:</b>\n"
            for pattern in patterns[:3]:
                pattern_emoji = "🟢" if pattern['signal'] == 1 else "🔴"
                status_emoji = "⏳" if pattern.get('status') == 'forming' else "✅" if pattern.get('status') == 'ready' else "🔔"
                status_text = pattern.get('status', 'unknown').upper()
                message += f"  {pattern_emoji} {pattern['name']}: {status_text} ({pattern['confidence']}%)\n"
                
                # Add entry levels if available
                if pattern.get('entry_price'):
                    message += f"     📍 Entry: ${pattern['entry_price']:,.4f}\n"
                if pattern.get('stop_loss'):
                    message += f"     🛑 Stop Loss: ${pattern['stop_loss']:,.4f}\n"
                if pattern.get('take_profit'):
                    message += f"     🎯 Take Profit: ${pattern['take_profit']:,.4f}\n"
                if pattern.get('breakout_level'):
                    message += f"     ⚡ Breakout Level: ${pattern['breakout_level']:,.4f}\n"
        
        message += "\n⚠️ <i>This is not financial advice. Always do your own research.</i>"
        
        return message
    
    async def send_scalping_trade_alert(
        self,
        trade: dict,
        timeframe_results: dict = None,
        indicators: dict = None
    ) -> bool:
        """Send a scalping trade alert."""
        if not self.enabled:
            logger.info("Telegram notifications disabled")
            return False
        
        message = self.format_scalping_trade_alert(
            trade=trade,
            timeframe_results=timeframe_results,
            indicators=indicators
        )
        
        return await self.send_message(message)
    
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
🤖 <b>Predbot Scalping Bot Started</b>

📊 Binance Futures Scalping Analysis Bot is now running.
⏰ Scanning for high-probability scalping opportunities...

Bot will send alerts with:
• 4 Entry levels for scaling in
• 4 Take Profit levels for scaling out
• Stop Loss level
• Trade quality score

Only verified high-probability trades will be sent.
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
📊 <b>Scalping Scan Summary</b>

🔍 Coins Scanned: {coins_scanned}
📈 High-Probability Trades Found: {signals_found}

"""
        
        if top_signals:
            message += "<b>Top Scalping Opportunities:</b>\n"
            for i, signal in enumerate(top_signals[:5], 1):
                emoji = "🟢" if signal['direction'] == 'LONG' else "🔴"
                message += f"{i}. {emoji} {signal['symbol']}: {signal['direction']} (Score: {signal.get('trade_score', 0)})\n"
        else:
            message += "No high-probability trades detected in this scan."
        
        message += f"\n⏰ Next scan in progress..."
        
        return await self.send_message(message)
