"""
Technical Indicators Module.
Implements 10 key technical indicators for trading analysis.
"""

import logging
import pandas as pd
import numpy as np
import ta

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Technical Indicators Calculator.
    
    Implements 10 key indicators:
    1. RSI (Relative Strength Index)
    2. MACD (Moving Average Convergence Divergence)
    3. Bollinger Bands
    4. EMA (Exponential Moving Average)
    5. SMA (Simple Moving Average)
    6. Stochastic Oscillator
    7. ADX (Average Directional Index)
    8. CCI (Commodity Channel Index)
    9. Williams %R
    10. OBV (On Balance Volume)
    """
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        return ta.momentum.RSIIndicator(df['close'], window=period).rsi()
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame) -> dict:
        """Calculate MACD indicator."""
        macd = ta.trend.MACD(df['close'])
        return {
            'macd': macd.macd(),
            'signal': macd.macd_signal(),
            'histogram': macd.macd_diff()
        }
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20) -> dict:
        """Calculate Bollinger Bands."""
        bb = ta.volatility.BollingerBands(df['close'], window=period)
        return {
            'upper': bb.bollinger_hband(),
            'middle': bb.bollinger_mavg(),
            'lower': bb.bollinger_lband(),
            'width': bb.bollinger_wband()
        }
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods: list = None) -> dict:
        """Calculate EMA for multiple periods."""
        if periods is None:
            periods = [9, 21, 50, 200]
        emas = {}
        for period in periods:
            emas[f'ema_{period}'] = ta.trend.EMAIndicator(
                df['close'], window=period
            ).ema_indicator()
        return emas
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, periods: list = None) -> dict:
        """Calculate SMA for multiple periods."""
        if periods is None:
            periods = [20, 50, 100, 200]
        smas = {}
        for period in periods:
            smas[f'sma_{period}'] = ta.trend.SMAIndicator(
                df['close'], window=period
            ).sma_indicator()
        return smas
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, period: int = 14) -> dict:
        """Calculate Stochastic Oscillator."""
        stoch = ta.momentum.StochasticOscillator(
            df['high'], df['low'], df['close'], window=period
        )
        return {
            'k': stoch.stoch(),
            'd': stoch.stoch_signal()
        }
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> dict:
        """Calculate ADX (Average Directional Index)."""
        adx = ta.trend.ADXIndicator(
            df['high'], df['low'], df['close'], window=period
        )
        return {
            'adx': adx.adx(),
            'di_plus': adx.adx_pos(),
            'di_minus': adx.adx_neg()
        }
    
    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate CCI (Commodity Channel Index)."""
        return ta.trend.CCIIndicator(
            df['high'], df['low'], df['close'], window=period
        ).cci()
    
    @staticmethod
    def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Williams %R."""
        return ta.momentum.WilliamsRIndicator(
            df['high'], df['low'], df['close'], lbp=period
        ).williams_r()
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """Calculate OBV (On Balance Volume)."""
        return ta.volume.OnBalanceVolumeIndicator(
            df['close'], df['volume']
        ).on_balance_volume()
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame) -> dict:
        """Calculate all indicators and return as dictionary."""
        if df.empty or len(df) < 200:
            logger.warning("Insufficient data for indicator calculation")
            return {}
        
        try:
            indicators = {
                'rsi': cls.calculate_rsi(df),
                'macd': cls.calculate_macd(df),
                'bollinger': cls.calculate_bollinger_bands(df),
                'ema': cls.calculate_ema(df),
                'sma': cls.calculate_sma(df),
                'stochastic': cls.calculate_stochastic(df),
                'adx': cls.calculate_adx(df),
                'cci': cls.calculate_cci(df),
                'williams_r': cls.calculate_williams_r(df),
                'obv': cls.calculate_obv(df)
            }
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    @classmethod
    def get_indicator_signals(cls, df: pd.DataFrame) -> dict:
        """
        Analyze indicators and return buy/sell signals.
        
        Returns:
            Dictionary with indicator signals (-1: sell, 0: neutral, 1: buy)
        """
        signals = {}
        indicators = cls.calculate_all(df)
        
        if not indicators:
            return signals
        
        try:
            # Get latest values
            latest_close = df['close'].iloc[-1]
            
            # RSI Signal
            rsi = indicators['rsi'].iloc[-1]
            if rsi < 30:
                signals['rsi'] = 1  # Oversold - Buy signal
            elif rsi > 70:
                signals['rsi'] = -1  # Overbought - Sell signal
            else:
                signals['rsi'] = 0
            
            # MACD Signal
            macd = indicators['macd']['macd'].iloc[-1]
            macd_signal = indicators['macd']['signal'].iloc[-1]
            macd_hist = indicators['macd']['histogram'].iloc[-1]
            macd_hist_prev = indicators['macd']['histogram'].iloc[-2]
            
            if macd > macd_signal and macd_hist > 0 and macd_hist > macd_hist_prev:
                signals['macd'] = 1
            elif macd < macd_signal and macd_hist < 0 and macd_hist < macd_hist_prev:
                signals['macd'] = -1
            else:
                signals['macd'] = 0
            
            # Bollinger Bands Signal
            bb_upper = indicators['bollinger']['upper'].iloc[-1]
            bb_lower = indicators['bollinger']['lower'].iloc[-1]
            
            if latest_close <= bb_lower:
                signals['bollinger'] = 1  # Price at lower band - Buy
            elif latest_close >= bb_upper:
                signals['bollinger'] = -1  # Price at upper band - Sell
            else:
                signals['bollinger'] = 0
            
            # EMA Signal (EMA crossover)
            ema_9 = indicators['ema']['ema_9'].iloc[-1]
            ema_21 = indicators['ema']['ema_21'].iloc[-1]
            ema_50 = indicators['ema']['ema_50'].iloc[-1]
            
            if ema_9 > ema_21 > ema_50:
                signals['ema'] = 1  # Bullish alignment
            elif ema_9 < ema_21 < ema_50:
                signals['ema'] = -1  # Bearish alignment
            else:
                signals['ema'] = 0
            
            # SMA Signal
            sma_50 = indicators['sma']['sma_50'].iloc[-1]
            sma_200 = indicators['sma']['sma_200'].iloc[-1]
            
            if latest_close > sma_50 and sma_50 > sma_200:
                signals['sma'] = 1  # Golden cross territory
            elif latest_close < sma_50 and sma_50 < sma_200:
                signals['sma'] = -1  # Death cross territory
            else:
                signals['sma'] = 0
            
            # Stochastic Signal
            stoch_k = indicators['stochastic']['k'].iloc[-1]
            stoch_d = indicators['stochastic']['d'].iloc[-1]
            
            if stoch_k < 20 and stoch_k > stoch_d:
                signals['stochastic'] = 1  # Oversold with bullish crossover
            elif stoch_k > 80 and stoch_k < stoch_d:
                signals['stochastic'] = -1  # Overbought with bearish crossover
            else:
                signals['stochastic'] = 0
            
            # ADX Signal (trend strength)
            adx = indicators['adx']['adx'].iloc[-1]
            di_plus = indicators['adx']['di_plus'].iloc[-1]
            di_minus = indicators['adx']['di_minus'].iloc[-1]
            
            if adx > 25:  # Strong trend
                if di_plus > di_minus:
                    signals['adx'] = 1  # Strong uptrend
                else:
                    signals['adx'] = -1  # Strong downtrend
            else:
                signals['adx'] = 0  # Weak trend
            
            # CCI Signal
            cci = indicators['cci'].iloc[-1]
            if cci < -100:
                signals['cci'] = 1  # Oversold
            elif cci > 100:
                signals['cci'] = -1  # Overbought
            else:
                signals['cci'] = 0
            
            # Williams %R Signal
            williams = indicators['williams_r'].iloc[-1]
            if williams < -80:
                signals['williams_r'] = 1  # Oversold
            elif williams > -20:
                signals['williams_r'] = -1  # Overbought
            else:
                signals['williams_r'] = 0
            
            # OBV Signal (volume trend)
            obv = indicators['obv']
            obv_sma = obv.rolling(window=20).mean()
            
            if obv.iloc[-1] > obv_sma.iloc[-1]:
                signals['obv'] = 1  # Volume supporting upward move
            elif obv.iloc[-1] < obv_sma.iloc[-1]:
                signals['obv'] = -1  # Volume supporting downward move
            else:
                signals['obv'] = 0
            
        except Exception as e:
            logger.error(f"Error calculating indicator signals: {e}")
        
        return signals
