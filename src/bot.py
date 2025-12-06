"""
Predbot - Main Bot Module.
Orchestrates the crypto trading analysis bot for scalping.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

from .config import Config
from .binance_client import BinanceClient
from .indicators import TechnicalIndicators
from .patterns import ChartPatterns
from .trend_analyzer import TrendAnalyzer
from .telegram_notifier import TelegramNotifier
from .scalping_analyzer import ScalpingAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Predbot:
    """
    Main trading analysis bot for Binance Futures scalping.
    
    This bot:
    1. Identifies top volatile coins on Binance Futures
    2. Analyzes them using 10 indicators and 10 patterns
    3. Checks trend direction across multiple timeframes
    4. Generates scalping trades with 4 entries, 4 TPs, and stop loss
    5. Only sends high-probability trades to Telegram
    
    Note: This bot does NOT open trades, only identifies opportunities.
    """
    
    def __init__(self):
        """Initialize the bot."""
        self.config = Config
        self.binance: Optional[BinanceClient] = None
        self.telegram: Optional[TelegramNotifier] = None
        self.trend_analyzer = TrendAnalyzer(
            confirmation_threshold=Config.TREND_CONFIRMATION_THRESHOLD
        )
        self.scalping_analyzer = ScalpingAnalyzer()
        self.is_running = False
        self.scan_count = 0
    
    async def initialize(self) -> bool:
        """Initialize connections and validate configuration."""
        logger.info("Initializing Predbot Scalping Bot...")
        
        # Validate configuration
        if not Config.validate():
            logger.error("Configuration validation failed")
            return False
        
        # Initialize Binance client
        try:
            self.binance = BinanceClient(
                Config.BINANCE_API_KEY,
                Config.BINANCE_API_SECRET
            )
            logger.info("Binance client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            return False
        
        # Initialize Telegram notifier
        if Config.ENABLE_TELEGRAM:
            try:
                self.telegram = TelegramNotifier(
                    Config.TELEGRAM_BOT_TOKEN,
                    Config.TELEGRAM_CHAT_ID
                )
                await self.telegram.send_startup_message()
                logger.info("Telegram notifier initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram: {e}")
                return False
        
        return True
    
    async def analyze_symbol_for_scalping(self, symbol: str) -> Optional[dict]:
        """
        Perform full scalping analysis on a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Scalping trade setup or None if no valid trade
        """
        logger.info(f"Analyzing {symbol} for scalping...")
        
        try:
            # Fetch data for all timeframes
            timeframe_data = {}
            for tf in Config.TIMEFRAMES:
                df = self.binance.get_klines(symbol, tf, limit=250)
                if not df.empty:
                    timeframe_data[tf] = df
            
            if not timeframe_data:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Perform multi-timeframe analysis
            mtf_analysis = self.trend_analyzer.analyze_multi_timeframe(timeframe_data)
            
            # Skip if no clear direction
            if mtf_analysis['overall_direction'] == 'neutral':
                logger.debug(f"{symbol}: No clear direction")
                return None
            
            # Get current price
            ticker = self.binance.get_24h_ticker(symbol)
            current_price = float(ticker[0]['lastPrice']) if ticker else 0
            
            if current_price == 0:
                return None
            
            # Get indicator signals from primary timeframe
            primary_tf = '5m' if '5m' in timeframe_data else list(timeframe_data.keys())[0]
            primary_df = timeframe_data[primary_tf]
            primary_indicators = mtf_analysis['timeframe_results'].get(
                primary_tf, {}
            ).get('indicator_signals', {})
            
            # Get pattern target if available
            pattern_target = None
            pattern_confidence = 70
            for tf, result in mtf_analysis['timeframe_results'].items():
                for pattern_name, pattern_data in result.get('pattern_signals', {}).items():
                    if pattern_data.get('take_profit'):
                        pattern_target = pattern_data['take_profit']
                        pattern_confidence = pattern_data.get('confidence', 70)
                        break
            
            # Generate scalping trade
            scalping_trade = self.scalping_analyzer.generate_scalping_trade(
                symbol=symbol,
                current_price=current_price,
                direction=mtf_analysis['overall_direction'],
                df=primary_df,
                indicator_signals=primary_indicators,
                timeframe_alignment=mtf_analysis['alignment'] / 100,
                pattern_confidence=pattern_confidence,
                pattern_target=pattern_target
            )
            
            if scalping_trade:
                scalping_trade['timeframe_results'] = mtf_analysis['timeframe_results']
                scalping_trade['indicators'] = primary_indicators
                
            return scalping_trade
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} for scalping: {e}")
            return None
    
    async def analyze_symbol(self, symbol: str) -> Optional[dict]:
        """
        Perform full analysis on a symbol (legacy method).
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Analysis results or None if analysis failed
        """
        logger.info(f"Analyzing {symbol}...")
        
        try:
            # Fetch data for all timeframes
            timeframe_data = {}
            for tf in Config.TIMEFRAMES:
                df = self.binance.get_klines(symbol, tf, limit=250)
                if not df.empty:
                    timeframe_data[tf] = df
            
            if not timeframe_data:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Perform multi-timeframe analysis
            mtf_analysis = self.trend_analyzer.analyze_multi_timeframe(timeframe_data)
            
            # Get trade signal strength
            signal_info = self.trend_analyzer.get_trade_signal_strength(
                mtf_analysis,
                threshold=Config.SIGNAL_STRENGTH_THRESHOLD
            )
            
            # Get current price
            ticker = self.binance.get_24h_ticker(symbol)
            current_price = float(ticker[0]['lastPrice']) if ticker else 0
            
            # Compile detected patterns with entry prices
            detected_patterns = []
            for tf, result in mtf_analysis['timeframe_results'].items():
                for pattern_name, pattern_data in result.get('pattern_signals', {}).items():
                    pattern_info = {
                        'name': f"{pattern_name} ({tf})",
                        'signal': pattern_data['signal'],
                        'confidence': pattern_data['confidence'],
                        'status': pattern_data.get('status', 'none'),
                        'entry_price': pattern_data.get('entry_price'),
                        'stop_loss': pattern_data.get('stop_loss'),
                        'take_profit': pattern_data.get('take_profit'),
                        'breakout_level': pattern_data.get('breakout_level')
                    }
                    detected_patterns.append(pattern_info)
            
            # Sort patterns: 'ready' status first, then by confidence
            detected_patterns.sort(
                key=lambda x: (
                    0 if x.get('status') == 'ready' else 1 if x.get('status') == 'forming' else 2,
                    -x['confidence']
                )
            )
            
            # Get indicator signals from the primary timeframe (1h or first available)
            primary_tf = '1h' if '1h' in timeframe_data else list(timeframe_data.keys())[0]
            primary_indicators = mtf_analysis['timeframe_results'].get(
                primary_tf, {}
            ).get('indicator_signals', {})
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'direction': mtf_analysis['overall_direction'],
                'strength': mtf_analysis['overall_strength'],
                'alignment': mtf_analysis['alignment'],
                'trend_confirmed': mtf_analysis['trend_confirmed'],
                'is_strong_signal': signal_info['is_strong_signal'],
                'signal_strength': signal_info['signal_strength'],
                'recommendation': signal_info['recommendation'],
                'timeframe_results': mtf_analysis['timeframe_results'],
                'indicators': primary_indicators,
                'patterns': detected_patterns
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    async def scan_market(self) -> list[dict]:
        """
        Scan the market for scalping trade opportunities.
        
        Returns:
            List of high-probability scalping trades
        """
        self.scan_count += 1
        logger.info(f"Starting scalping market scan #{self.scan_count}...")
        
        # Get top volatile coins
        volatile_coins = self.binance.get_top_volatile_coins(
            count=Config.TOP_VOLATILE_COINS,
            min_volume=Config.MIN_VOLUME_USD
        )
        
        if not volatile_coins:
            logger.warning("No volatile coins found")
            return []
        
        logger.info(f"Found {len(volatile_coins)} volatile coins to analyze")
        
        # Analyze each coin for scalping
        high_probability_trades = []
        for coin in volatile_coins:
            symbol = coin['symbol']
            scalping_trade = await self.analyze_symbol_for_scalping(symbol)
            
            if scalping_trade and scalping_trade.get('is_high_probability'):
                high_probability_trades.append(scalping_trade)
                logger.info(
                    f"High-probability trade found: {symbol} - "
                    f"{scalping_trade['direction']} (Score: {scalping_trade['trade_score']})"
                )
                
                # Send Telegram alert
                if self.telegram:
                    await self.telegram.send_scalping_trade_alert(
                        trade=scalping_trade,
                        timeframe_results=scalping_trade.get('timeframe_results'),
                        indicators=scalping_trade.get('indicators')
                    )
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
        
        # Send scan summary
        if self.telegram:
            await self.telegram.send_scan_summary(
                coins_scanned=len(volatile_coins),
                signals_found=len(high_probability_trades),
                top_signals=[
                    {
                        'symbol': t['symbol'],
                        'direction': t['direction'],
                        'trade_score': t['trade_score']
                    }
                    for t in sorted(
                        high_probability_trades,
                        key=lambda x: x['trade_score'],
                        reverse=True
                    )
                ]
            )
        
        return high_probability_trades
    
    async def run(self, scan_interval: int = 300):
        """
        Run the bot continuously.
        
        Args:
            scan_interval: Seconds between scans (default: 5 minutes)
        """
        logger.info("Starting Predbot Scalping Bot...")
        
        if not await self.initialize():
            logger.error("Initialization failed. Exiting.")
            return
        
        self.is_running = True
        logger.info(f"Bot running. Scanning every {scan_interval} seconds.")
        
        try:
            while self.is_running:
                try:
                    await self.scan_market()
                except Exception as e:
                    logger.error(f"Error during scan: {e}")
                
                logger.info(f"Waiting {scan_interval} seconds until next scan...")
                await asyncio.sleep(scan_interval)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.is_running = False
            logger.info("Bot stopped")
    
    async def run_single_scan(self) -> list[dict]:
        """Run a single market scan (useful for testing)."""
        if not await self.initialize():
            logger.error("Initialization failed")
            return []
        
        return await self.scan_market()


async def main():
    """Main entry point."""
    bot = Predbot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
