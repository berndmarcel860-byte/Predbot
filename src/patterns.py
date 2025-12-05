"""
Chart Patterns Module.
Implements 10 key chart patterns for trading analysis.
"""

import logging
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

logger = logging.getLogger(__name__)


class ChartPatterns:
    """
    Chart Pattern Detector.
    
    Implements 10 key patterns:
    1. Double Top
    2. Double Bottom
    3. Head and Shoulders
    4. Inverse Head and Shoulders
    5. Ascending Triangle
    6. Descending Triangle
    7. Symmetrical Triangle
    8. Rising Wedge
    9. Falling Wedge
    10. Bullish/Bearish Engulfing
    """
    
    @staticmethod
    def find_local_extrema(df: pd.DataFrame, order: int = 5) -> tuple:
        """Find local maxima and minima in price data."""
        highs = argrelextrema(df['high'].values, np.greater, order=order)[0]
        lows = argrelextrema(df['low'].values, np.less, order=order)[0]
        return highs, lows
    
    @staticmethod
    def detect_double_top(df: pd.DataFrame, tolerance: float = 0.02) -> dict:
        """
        Detect Double Top pattern (bearish reversal).
        Two peaks at similar price levels with a valley between.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            highs, _ = ChartPatterns.find_local_extrema(df, order=10)
            
            if len(highs) < 2:
                return result
            
            # Check last two peaks
            peak1_idx, peak2_idx = highs[-2], highs[-1]
            peak1_price = df['high'].iloc[peak1_idx]
            peak2_price = df['high'].iloc[peak2_idx]
            
            # Check if peaks are at similar levels
            price_diff = abs(peak1_price - peak2_price) / peak1_price
            
            if price_diff <= tolerance:
                # Find the valley between peaks
                valley_slice = df['low'].iloc[peak1_idx:peak2_idx]
                if len(valley_slice) > 0:
                    valley_idx = valley_slice.idxmin()
                    current_price = df['close'].iloc[-1]
                    # Pattern confirmed if price breaks below valley
                    valley_price = df['low'].loc[valley_idx]
                    
                    if current_price < valley_price:
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['confidence'] = min(90, 70 + (1 - price_diff) * 20)
                    elif current_price < peak2_price * 0.98:
                        result['detected'] = True
                        result['signal'] = -1
                        result['confidence'] = 60
                        
        except Exception as e:
            logger.debug(f"Double Top detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_double_bottom(df: pd.DataFrame, tolerance: float = 0.02) -> dict:
        """
        Detect Double Bottom pattern (bullish reversal).
        Two troughs at similar price levels with a peak between.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            _, lows = ChartPatterns.find_local_extrema(df, order=10)
            
            if len(lows) < 2:
                return result
            
            # Check last two troughs
            trough1_idx, trough2_idx = lows[-2], lows[-1]
            trough1_price = df['low'].iloc[trough1_idx]
            trough2_price = df['low'].iloc[trough2_idx]
            
            # Check if troughs are at similar levels
            price_diff = abs(trough1_price - trough2_price) / trough1_price
            
            if price_diff <= tolerance:
                # Find the peak between troughs
                peak_slice = df['high'].iloc[trough1_idx:trough2_idx]
                if len(peak_slice) > 0:
                    peak_idx = peak_slice.idxmax()
                    current_price = df['close'].iloc[-1]
                    peak_price = df['high'].loc[peak_idx]
                    
                    if current_price > peak_price:
                        result['detected'] = True
                        result['signal'] = 1  # Bullish
                        result['confidence'] = min(90, 70 + (1 - price_diff) * 20)
                    elif current_price > trough2_price * 1.02:
                        result['detected'] = True
                        result['signal'] = 1
                        result['confidence'] = 60
                        
        except Exception as e:
            logger.debug(f"Double Bottom detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_head_and_shoulders(df: pd.DataFrame, tolerance: float = 0.03) -> dict:
        """
        Detect Head and Shoulders pattern (bearish reversal).
        Three peaks with the middle one being the highest.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            highs, _ = ChartPatterns.find_local_extrema(df, order=8)
            
            if len(highs) < 3:
                return result
            
            # Check last three peaks
            left_idx, head_idx, right_idx = highs[-3], highs[-2], highs[-1]
            left_price = df['high'].iloc[left_idx]
            head_price = df['high'].iloc[head_idx]
            right_price = df['high'].iloc[right_idx]
            
            # Head should be higher than both shoulders
            if head_price > left_price and head_price > right_price:
                # Shoulders should be at similar levels
                shoulder_diff = abs(left_price - right_price) / left_price
                
                if shoulder_diff <= tolerance:
                    # Calculate neckline (connect the lows between peaks)
                    low1 = df['low'].iloc[left_idx:head_idx].min()
                    low2 = df['low'].iloc[head_idx:right_idx].min()
                    neckline = (low1 + low2) / 2
                    
                    current_price = df['close'].iloc[-1]
                    
                    if current_price < neckline:
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['confidence'] = min(90, 70 + (1 - shoulder_diff) * 20)
                        
        except Exception as e:
            logger.debug(f"Head and Shoulders detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_inverse_head_and_shoulders(df: pd.DataFrame, tolerance: float = 0.03) -> dict:
        """
        Detect Inverse Head and Shoulders pattern (bullish reversal).
        Three troughs with the middle one being the lowest.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            _, lows = ChartPatterns.find_local_extrema(df, order=8)
            
            if len(lows) < 3:
                return result
            
            # Check last three troughs
            left_idx, head_idx, right_idx = lows[-3], lows[-2], lows[-1]
            left_price = df['low'].iloc[left_idx]
            head_price = df['low'].iloc[head_idx]
            right_price = df['low'].iloc[right_idx]
            
            # Head should be lower than both shoulders
            if head_price < left_price and head_price < right_price:
                # Shoulders should be at similar levels
                shoulder_diff = abs(left_price - right_price) / left_price
                
                if shoulder_diff <= tolerance:
                    # Calculate neckline
                    high1 = df['high'].iloc[left_idx:head_idx].max()
                    high2 = df['high'].iloc[head_idx:right_idx].max()
                    neckline = (high1 + high2) / 2
                    
                    current_price = df['close'].iloc[-1]
                    
                    if current_price > neckline:
                        result['detected'] = True
                        result['signal'] = 1  # Bullish
                        result['confidence'] = min(90, 70 + (1 - shoulder_diff) * 20)
                        
        except Exception as e:
            logger.debug(f"Inverse H&S detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_ascending_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Ascending Triangle pattern (typically bullish).
        Flat resistance with rising support.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            recent = df.tail(lookback)
            highs, lows = ChartPatterns.find_local_extrema(recent, order=5)
            
            if len(highs) < 3 or len(lows) < 3:
                return result
            
            # Check for flat resistance (horizontal top)
            resistance_prices = [recent['high'].iloc[i] for i in highs[-3:]]
            resistance_std = np.std(resistance_prices) / np.mean(resistance_prices)
            
            # Check for rising support (higher lows)
            support_prices = [recent['low'].iloc[i] for i in lows[-3:]]
            rising_support = all(
                support_prices[i] < support_prices[i+1] 
                for i in range(len(support_prices)-1)
            )
            
            if resistance_std < 0.02 and rising_support:
                result['detected'] = True
                result['signal'] = 1  # Bullish breakout expected
                result['confidence'] = 70
                
        except Exception as e:
            logger.debug(f"Ascending Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_descending_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Descending Triangle pattern (typically bearish).
        Flat support with falling resistance.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            recent = df.tail(lookback)
            highs, lows = ChartPatterns.find_local_extrema(recent, order=5)
            
            if len(highs) < 3 or len(lows) < 3:
                return result
            
            # Check for flat support (horizontal bottom)
            support_prices = [recent['low'].iloc[i] for i in lows[-3:]]
            support_std = np.std(support_prices) / np.mean(support_prices)
            
            # Check for falling resistance (lower highs)
            resistance_prices = [recent['high'].iloc[i] for i in highs[-3:]]
            falling_resistance = all(
                resistance_prices[i] > resistance_prices[i+1] 
                for i in range(len(resistance_prices)-1)
            )
            
            if support_std < 0.02 and falling_resistance:
                result['detected'] = True
                result['signal'] = -1  # Bearish breakdown expected
                result['confidence'] = 70
                
        except Exception as e:
            logger.debug(f"Descending Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_symmetrical_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Symmetrical Triangle pattern (continuation pattern).
        Converging support and resistance.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            recent = df.tail(lookback)
            highs, lows = ChartPatterns.find_local_extrema(recent, order=5)
            
            if len(highs) < 3 or len(lows) < 3:
                return result
            
            # Check for lower highs
            resistance_prices = [recent['high'].iloc[i] for i in highs[-3:]]
            lower_highs = all(
                resistance_prices[i] > resistance_prices[i+1] 
                for i in range(len(resistance_prices)-1)
            )
            
            # Check for higher lows
            support_prices = [recent['low'].iloc[i] for i in lows[-3:]]
            higher_lows = all(
                support_prices[i] < support_prices[i+1] 
                for i in range(len(support_prices)-1)
            )
            
            if lower_highs and higher_lows:
                result['detected'] = True
                # Signal based on prior trend
                prior_trend = recent['close'].iloc[0] < recent['close'].iloc[-1]
                result['signal'] = 1 if prior_trend else -1
                result['confidence'] = 65
                
        except Exception as e:
            logger.debug(f"Symmetrical Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_rising_wedge(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Rising Wedge pattern (bearish reversal).
        Both support and resistance rising, but converging.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            recent = df.tail(lookback)
            highs, lows = ChartPatterns.find_local_extrema(recent, order=5)
            
            if len(highs) < 3 or len(lows) < 3:
                return result
            
            # Check for higher highs
            resistance_prices = [recent['high'].iloc[i] for i in highs[-3:]]
            higher_highs = all(
                resistance_prices[i] < resistance_prices[i+1] 
                for i in range(len(resistance_prices)-1)
            )
            
            # Check for higher lows (but slower rate)
            support_prices = [recent['low'].iloc[i] for i in lows[-3:]]
            higher_lows = all(
                support_prices[i] < support_prices[i+1] 
                for i in range(len(support_prices)-1)
            )
            
            if higher_highs and higher_lows:
                # Check if wedge is narrowing
                high_range = resistance_prices[-1] - resistance_prices[0]
                low_range = support_prices[-1] - support_prices[0]
                
                if low_range > high_range:  # Support rising faster = wedge narrowing
                    result['detected'] = True
                    result['signal'] = -1  # Bearish
                    result['confidence'] = 65
                    
        except Exception as e:
            logger.debug(f"Rising Wedge detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_falling_wedge(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Falling Wedge pattern (bullish reversal).
        Both support and resistance falling, but converging.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            recent = df.tail(lookback)
            highs, lows = ChartPatterns.find_local_extrema(recent, order=5)
            
            if len(highs) < 3 or len(lows) < 3:
                return result
            
            # Check for lower highs
            resistance_prices = [recent['high'].iloc[i] for i in highs[-3:]]
            lower_highs = all(
                resistance_prices[i] > resistance_prices[i+1] 
                for i in range(len(resistance_prices)-1)
            )
            
            # Check for lower lows
            support_prices = [recent['low'].iloc[i] for i in lows[-3:]]
            lower_lows = all(
                support_prices[i] > support_prices[i+1] 
                for i in range(len(support_prices)-1)
            )
            
            if lower_highs and lower_lows:
                # Check if wedge is narrowing
                high_range = abs(resistance_prices[-1] - resistance_prices[0])
                low_range = abs(support_prices[-1] - support_prices[0])
                
                if high_range > low_range:  # Resistance falling faster = wedge narrowing
                    result['detected'] = True
                    result['signal'] = 1  # Bullish
                    result['confidence'] = 65
                    
        except Exception as e:
            logger.debug(f"Falling Wedge detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_engulfing_pattern(df: pd.DataFrame) -> dict:
        """
        Detect Bullish/Bearish Engulfing patterns.
        Current candle completely engulfs previous candle.
        """
        result = {'detected': False, 'signal': 0, 'confidence': 0}
        
        try:
            if len(df) < 2:
                return result
            
            prev = df.iloc[-2]
            curr = df.iloc[-1]
            
            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])
            
            # Bullish Engulfing: Previous red, current green and engulfs
            if prev['close'] < prev['open']:  # Previous is red
                if curr['close'] > curr['open']:  # Current is green
                    if (curr['open'] < prev['close'] and 
                        curr['close'] > prev['open'] and 
                        curr_body > prev_body):
                        result['detected'] = True
                        result['signal'] = 1  # Bullish
                        result['confidence'] = 75
                        return result
            
            # Bearish Engulfing: Previous green, current red and engulfs
            if prev['close'] > prev['open']:  # Previous is green
                if curr['close'] < curr['open']:  # Current is red
                    if (curr['open'] > prev['close'] and 
                        curr['close'] < prev['open'] and 
                        curr_body > prev_body):
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['confidence'] = 75
                        
        except Exception as e:
            logger.debug(f"Engulfing pattern detection error: {e}")
        
        return result
    
    @classmethod
    def detect_all_patterns(cls, df: pd.DataFrame) -> dict:
        """Detect all patterns and return results."""
        patterns = {}
        
        if df.empty or len(df) < 50:
            logger.warning("Insufficient data for pattern detection")
            return patterns
        
        try:
            patterns['double_top'] = cls.detect_double_top(df)
            patterns['double_bottom'] = cls.detect_double_bottom(df)
            patterns['head_and_shoulders'] = cls.detect_head_and_shoulders(df)
            patterns['inverse_head_and_shoulders'] = cls.detect_inverse_head_and_shoulders(df)
            patterns['ascending_triangle'] = cls.detect_ascending_triangle(df)
            patterns['descending_triangle'] = cls.detect_descending_triangle(df)
            patterns['symmetrical_triangle'] = cls.detect_symmetrical_triangle(df)
            patterns['rising_wedge'] = cls.detect_rising_wedge(df)
            patterns['falling_wedge'] = cls.detect_falling_wedge(df)
            patterns['engulfing'] = cls.detect_engulfing_pattern(df)
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
        
        return patterns
    
    @classmethod
    def get_pattern_signals(cls, df: pd.DataFrame) -> dict:
        """Get signals from detected patterns."""
        signals = {}
        patterns = cls.detect_all_patterns(df)
        
        for name, pattern in patterns.items():
            if pattern.get('detected', False):
                signals[name] = {
                    'signal': pattern['signal'],
                    'confidence': pattern['confidence']
                }
        
        return signals
