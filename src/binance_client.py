"""
Binance Futures API integration module.
Handles all interactions with Binance Futures API.
"""

import logging
from typing import Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd

logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance Futures API client wrapper."""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize the Binance client."""
        self.client = Client(api_key, api_secret)
        self.client.futures_ping()  # Test connection
        logger.info("Connected to Binance Futures API")
    
    def get_futures_symbols(self) -> list[str]:
        """Get all available USDT futures trading pairs."""
        try:
            exchange_info = self.client.futures_exchange_info()
            symbols = [
                s['symbol'] for s in exchange_info['symbols']
                if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING'
            ]
            logger.info(f"Found {len(symbols)} USDT futures pairs")
            return symbols
        except BinanceAPIException as e:
            logger.error(f"Failed to get futures symbols: {e}")
            return []
    
    def get_24h_ticker(self, symbol: Optional[str] = None) -> list[dict]:
        """Get 24h ticker data for futures."""
        try:
            if symbol:
                return [self.client.futures_ticker(symbol=symbol)]
            return self.client.futures_ticker()
        except BinanceAPIException as e:
            logger.error(f"Failed to get ticker data: {e}")
            return []
    
    def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        limit: int = 200
    ) -> pd.DataFrame:
        """
        Get candlestick/kline data for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '5m', '15m', '1h', '4h')
            limit: Number of candles to fetch (max 1500)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except BinanceAPIException as e:
            logger.error(f"Failed to get klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_top_volatile_coins(
        self, 
        count: int = 20, 
        min_volume: float = 10000000
    ) -> list[dict]:
        """
        Get the top volatile coins based on 24h price change.
        
        Args:
            count: Number of top coins to return
            min_volume: Minimum 24h volume in USDT
            
        Returns:
            List of dictionaries with symbol info sorted by volatility
        """
        try:
            tickers = self.get_24h_ticker()
            
            # Filter USDT pairs and minimum volume
            usdt_tickers = [
                {
                    'symbol': t['symbol'],
                    'price_change_percent': abs(float(t['priceChangePercent'])),
                    'last_price': float(t['lastPrice']),
                    'volume_24h': float(t['quoteVolume']),
                    'high_24h': float(t['highPrice']),
                    'low_24h': float(t['lowPrice'])
                }
                for t in tickers
                if t['symbol'].endswith('USDT') 
                and float(t['quoteVolume']) >= min_volume
            ]
            
            # Sort by volatility (price change percent)
            sorted_tickers = sorted(
                usdt_tickers, 
                key=lambda x: x['price_change_percent'], 
                reverse=True
            )
            
            top_coins = sorted_tickers[:count]
            logger.info(f"Found top {len(top_coins)} volatile coins")
            return top_coins
            
        except Exception as e:
            logger.error(f"Failed to get volatile coins: {e}")
            return []
