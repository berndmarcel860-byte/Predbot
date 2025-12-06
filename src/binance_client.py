"""
Binance Futures API integration module.
Handles all interactions with Binance Futures API.
"""

import logging
from typing import Optional, List
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd

logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance Futures API client wrapper."""
    
    def __init__(self, api_key: str, api_secret: str, leverage: int = 20, margin_type: str = "CROSSED"):
        """
        Initialize the Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            leverage: Leverage multiplier (default: 20x)
            margin_type: Margin type - "CROSSED" or "ISOLATED" (default: CROSSED)
        """
        self.client = Client(api_key, api_secret)
        self.client.futures_ping()  # Test connection
        self.leverage = leverage
        self.margin_type = margin_type
        logger.info(f"Connected to Binance Futures API (Leverage: {leverage}x, Margin: {margin_type})")
    
    def set_leverage(self, symbol: str, leverage: int = None) -> bool:
        """
        Set leverage for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            leverage: Leverage multiplier (uses instance default if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            lev = leverage or self.leverage
            self.client.futures_change_leverage(symbol=symbol, leverage=lev)
            logger.info(f"Set leverage for {symbol} to {lev}x")
            return True
        except BinanceAPIException as e:
            logger.error(f"Failed to set leverage for {symbol}: {e}")
            return False
    
    def set_margin_type(self, symbol: str, margin_type: str = None) -> bool:
        """
        Set margin type for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            margin_type: "CROSSED" or "ISOLATED" (uses instance default if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mt = margin_type or self.margin_type
            self.client.futures_change_margin_type(symbol=symbol, marginType=mt)
            logger.info(f"Set margin type for {symbol} to {mt}")
            return True
        except BinanceAPIException as e:
            # Ignore if margin type is already set
            if "No need to change margin type" in str(e):
                logger.debug(f"Margin type for {symbol} already set to {mt}")
                return True
            logger.error(f"Failed to set margin type for {symbol}: {e}")
            return False
    
    def configure_symbol(self, symbol: str) -> bool:
        """
        Configure a symbol with leverage and margin type settings.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            True if successful, False otherwise
        """
        margin_ok = self.set_margin_type(symbol)
        leverage_ok = self.set_leverage(symbol)
        return margin_ok and leverage_ok
    
    def get_futures_symbols(self) -> List[str]:
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
    
    def get_24h_ticker(self, symbol: Optional[str] = None) -> List[dict]:
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
    ) -> List[dict]:
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
