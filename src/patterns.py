"""
Chart Patterns Module.
Implements 10 key chart patterns for trading analysis.
Detects patterns BEFORE breakout to provide early entry opportunities.
"""

import logging
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

logger = logging.getLogger(__name__)


class ChartPatterns:
    """
    Chart Pattern Detector.
    
    Detects patterns BEFORE breakout for early entry opportunities.
    Provides entry price levels, stop loss, and take profit targets.
    
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
        Detect Double Top pattern (bearish reversal) BEFORE breakout.
        Two peaks at similar price levels with a valley between.
        Signals when pattern is forming, before neckline break.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',  # 'forming', 'ready', 'confirmed'
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    valley_price = df['low'].loc[valley_idx]
                    avg_peak = (peak1_price + peak2_price) / 2
                    
                    # Calculate pattern height for targets
                    pattern_height = avg_peak - valley_price
                    
                    # BEFORE BREAKOUT: Pattern is forming/ready
                    if current_price > valley_price:
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['breakout_level'] = valley_price
                        
                        # Entry on retest of neckline or current price
                        result['entry_price'] = valley_price * 0.998  # Just below neckline
                        result['stop_loss'] = avg_peak * 1.01  # Above peaks
                        result['take_profit'] = valley_price - pattern_height  # Pattern projection
                        
                        # Determine status based on price position
                        distance_to_neckline = (current_price - valley_price) / valley_price
                        if distance_to_neckline < 0.02:  # Within 2% of neckline
                            result['status'] = 'ready'
                            result['confidence'] = min(85, 70 + (1 - price_diff) * 20)
                        else:
                            result['status'] = 'forming'
                            result['confidence'] = min(70, 55 + (1 - price_diff) * 15)
                    
                    # AFTER BREAKOUT: Already confirmed
                    elif current_price < valley_price:
                        result['detected'] = True
                        result['signal'] = -1
                        result['status'] = 'confirmed'
                        result['confidence'] = min(90, 75 + (1 - price_diff) * 20)
                        result['entry_price'] = current_price  # Can still enter on retest
                        result['stop_loss'] = valley_price * 1.02
                        result['take_profit'] = valley_price - pattern_height
                        result['breakout_level'] = valley_price
                        
        except Exception as e:
            logger.debug(f"Double Top detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_double_bottom(df: pd.DataFrame, tolerance: float = 0.02) -> dict:
        """
        Detect Double Bottom pattern (bullish reversal) BEFORE breakout.
        Two troughs at similar price levels with a peak between.
        Signals when pattern is forming, before neckline break.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    avg_trough = (trough1_price + trough2_price) / 2
                    
                    # Calculate pattern height for targets
                    pattern_height = peak_price - avg_trough
                    
                    # BEFORE BREAKOUT: Pattern is forming/ready
                    if current_price < peak_price:
                        result['detected'] = True
                        result['signal'] = 1  # Bullish
                        result['breakout_level'] = peak_price
                        
                        # Entry just above neckline on breakout
                        result['entry_price'] = peak_price * 1.002  # Just above neckline
                        result['stop_loss'] = avg_trough * 0.99  # Below troughs
                        result['take_profit'] = peak_price + pattern_height  # Pattern projection
                        
                        # Determine status based on price position
                        distance_to_neckline = (peak_price - current_price) / peak_price
                        if distance_to_neckline < 0.02:  # Within 2% of neckline
                            result['status'] = 'ready'
                            result['confidence'] = min(85, 70 + (1 - price_diff) * 20)
                        else:
                            result['status'] = 'forming'
                            result['confidence'] = min(70, 55 + (1 - price_diff) * 15)
                    
                    # AFTER BREAKOUT: Already confirmed
                    elif current_price > peak_price:
                        result['detected'] = True
                        result['signal'] = 1
                        result['status'] = 'confirmed'
                        result['confidence'] = min(90, 75 + (1 - price_diff) * 20)
                        result['entry_price'] = current_price  # Can still enter on retest
                        result['stop_loss'] = peak_price * 0.98
                        result['take_profit'] = peak_price + pattern_height
                        result['breakout_level'] = peak_price
                        
        except Exception as e:
            logger.debug(f"Double Bottom detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_head_and_shoulders(df: pd.DataFrame, tolerance: float = 0.03) -> dict:
        """
        Detect Head and Shoulders pattern (bearish reversal) BEFORE breakout.
        Three peaks with the middle one being the highest.
        Signals when right shoulder is forming, before neckline break.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    pattern_height = head_price - neckline
                    
                    # BEFORE BREAKOUT: Pattern is forming/ready
                    if current_price > neckline:
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['breakout_level'] = neckline
                        
                        # Entry just below neckline
                        result['entry_price'] = neckline * 0.998
                        result['stop_loss'] = right_price * 1.01  # Above right shoulder
                        result['take_profit'] = neckline - pattern_height
                        
                        distance_to_neckline = (current_price - neckline) / neckline
                        if distance_to_neckline < 0.02:
                            result['status'] = 'ready'
                            result['confidence'] = min(88, 72 + (1 - shoulder_diff) * 20)
                        else:
                            result['status'] = 'forming'
                            result['confidence'] = min(72, 58 + (1 - shoulder_diff) * 15)
                    
                    # AFTER BREAKOUT: Confirmed
                    elif current_price < neckline:
                        result['detected'] = True
                        result['signal'] = -1
                        result['status'] = 'confirmed'
                        result['confidence'] = min(92, 78 + (1 - shoulder_diff) * 20)
                        result['entry_price'] = current_price
                        result['stop_loss'] = neckline * 1.02
                        result['take_profit'] = neckline - pattern_height
                        result['breakout_level'] = neckline
                        
        except Exception as e:
            logger.debug(f"Head and Shoulders detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_inverse_head_and_shoulders(df: pd.DataFrame, tolerance: float = 0.03) -> dict:
        """
        Detect Inverse Head and Shoulders pattern (bullish reversal) BEFORE breakout.
        Three troughs with the middle one being the lowest.
        Signals when right shoulder is forming, before neckline break.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    pattern_height = neckline - head_price
                    
                    # BEFORE BREAKOUT: Pattern is forming/ready
                    if current_price < neckline:
                        result['detected'] = True
                        result['signal'] = 1  # Bullish
                        result['breakout_level'] = neckline
                        
                        # Entry just above neckline
                        result['entry_price'] = neckline * 1.002
                        result['stop_loss'] = right_price * 0.99  # Below right shoulder
                        result['take_profit'] = neckline + pattern_height
                        
                        distance_to_neckline = (neckline - current_price) / neckline
                        if distance_to_neckline < 0.02:
                            result['status'] = 'ready'
                            result['confidence'] = min(88, 72 + (1 - shoulder_diff) * 20)
                        else:
                            result['status'] = 'forming'
                            result['confidence'] = min(72, 58 + (1 - shoulder_diff) * 15)
                    
                    # AFTER BREAKOUT: Confirmed
                    elif current_price > neckline:
                        result['detected'] = True
                        result['signal'] = 1
                        result['status'] = 'confirmed'
                        result['confidence'] = min(92, 78 + (1 - shoulder_diff) * 20)
                        result['entry_price'] = current_price
                        result['stop_loss'] = neckline * 0.98
                        result['take_profit'] = neckline + pattern_height
                        result['breakout_level'] = neckline
                        
        except Exception as e:
            logger.debug(f"Inverse H&S detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_ascending_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Ascending Triangle pattern (typically bullish) BEFORE breakout.
        Flat resistance with rising support.
        Signals when price is approaching apex for early entry.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                resistance_level = np.mean(resistance_prices)
                current_support = support_prices[-1]
                current_price = recent['close'].iloc[-1]
                
                # Calculate pattern height for targets
                pattern_height = resistance_level - support_prices[0]
                
                result['detected'] = True
                result['signal'] = 1  # Bullish breakout expected
                result['breakout_level'] = resistance_level
                
                # Entry just above resistance on breakout
                result['entry_price'] = resistance_level * 1.002
                result['stop_loss'] = current_support * 0.99
                result['take_profit'] = resistance_level + pattern_height
                
                # Check how close to apex (convergence)
                distance_to_resistance = (resistance_level - current_price) / resistance_level
                if distance_to_resistance < 0.015:
                    result['status'] = 'ready'
                    result['confidence'] = 78
                else:
                    result['status'] = 'forming'
                    result['confidence'] = 65
                
        except Exception as e:
            logger.debug(f"Ascending Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_descending_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Descending Triangle pattern (typically bearish) BEFORE breakout.
        Flat support with falling resistance.
        Signals when price is approaching apex for early entry.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                support_level = np.mean(support_prices)
                current_resistance = resistance_prices[-1]
                current_price = recent['close'].iloc[-1]
                
                # Calculate pattern height for targets
                pattern_height = resistance_prices[0] - support_level
                
                result['detected'] = True
                result['signal'] = -1  # Bearish breakdown expected
                result['breakout_level'] = support_level
                
                # Entry just below support on breakdown
                result['entry_price'] = support_level * 0.998
                result['stop_loss'] = current_resistance * 1.01
                result['take_profit'] = support_level - pattern_height
                
                # Check how close to apex (convergence)
                distance_to_support = (current_price - support_level) / support_level
                if distance_to_support < 0.015:
                    result['status'] = 'ready'
                    result['confidence'] = 78
                else:
                    result['status'] = 'forming'
                    result['confidence'] = 65
                
        except Exception as e:
            logger.debug(f"Descending Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_symmetrical_triangle(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Symmetrical Triangle pattern (continuation pattern) BEFORE breakout.
        Converging support and resistance.
        Signals when price is approaching apex for early entry.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                current_price = recent['close'].iloc[-1]
                current_resistance = resistance_prices[-1]
                current_support = support_prices[-1]
                
                # Calculate pattern height for targets
                pattern_height = resistance_prices[0] - support_prices[0]
                
                # Signal based on prior trend
                prior_trend = recent['close'].iloc[0] < recent['close'].iloc[-1]
                
                result['detected'] = True
                result['signal'] = 1 if prior_trend else -1
                
                if prior_trend:  # Bullish breakout expected
                    result['breakout_level'] = current_resistance
                    result['entry_price'] = current_resistance * 1.002
                    result['stop_loss'] = current_support * 0.99
                    result['take_profit'] = current_resistance + pattern_height * 0.7
                else:  # Bearish breakdown expected
                    result['breakout_level'] = current_support
                    result['entry_price'] = current_support * 0.998
                    result['stop_loss'] = current_resistance * 1.01
                    result['take_profit'] = current_support - pattern_height * 0.7
                
                # Check how tight the range is (approaching apex)
                range_width = (current_resistance - current_support) / current_price
                if range_width < 0.03:
                    result['status'] = 'ready'
                    result['confidence'] = 72
                else:
                    result['status'] = 'forming'
                    result['confidence'] = 60
                
        except Exception as e:
            logger.debug(f"Symmetrical Triangle detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_rising_wedge(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Rising Wedge pattern (bearish reversal) BEFORE breakout.
        Both support and resistance rising, but converging.
        Signals when pattern is forming for early short entry.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    current_price = recent['close'].iloc[-1]
                    current_support = support_prices[-1]
                    
                    # Calculate pattern height for targets
                    pattern_height = resistance_prices[-1] - support_prices[0]
                    
                    result['detected'] = True
                    result['signal'] = -1  # Bearish
                    result['breakout_level'] = current_support
                    
                    # Entry just below support on breakdown
                    result['entry_price'] = current_support * 0.998
                    result['stop_loss'] = resistance_prices[-1] * 1.01
                    result['take_profit'] = current_support - pattern_height * 0.6
                    
                    # Check convergence
                    range_width = (resistance_prices[-1] - current_support) / current_price
                    if range_width < 0.025:
                        result['status'] = 'ready'
                        result['confidence'] = 72
                    else:
                        result['status'] = 'forming'
                        result['confidence'] = 60
                    
        except Exception as e:
            logger.debug(f"Rising Wedge detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_falling_wedge(df: pd.DataFrame, lookback: int = 50) -> dict:
        """
        Detect Falling Wedge pattern (bullish reversal) BEFORE breakout.
        Both support and resistance falling, but converging.
        Signals when pattern is forming for early long entry.
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                    current_price = recent['close'].iloc[-1]
                    current_resistance = resistance_prices[-1]
                    
                    # Calculate pattern height for targets
                    pattern_height = resistance_prices[0] - support_prices[-1]
                    
                    result['detected'] = True
                    result['signal'] = 1  # Bullish
                    result['breakout_level'] = current_resistance
                    
                    # Entry just above resistance on breakout
                    result['entry_price'] = current_resistance * 1.002
                    result['stop_loss'] = support_prices[-1] * 0.99
                    result['take_profit'] = current_resistance + pattern_height * 0.6
                    
                    # Check convergence
                    range_width = (current_resistance - support_prices[-1]) / current_price
                    if range_width < 0.025:
                        result['status'] = 'ready'
                        result['confidence'] = 72
                    else:
                        result['status'] = 'forming'
                        result['confidence'] = 60
                    
        except Exception as e:
            logger.debug(f"Falling Wedge detection error: {e}")
        
        return result
    
    @staticmethod
    def detect_engulfing_pattern(df: pd.DataFrame) -> dict:
        """
        Detect Bullish/Bearish Engulfing patterns.
        Current candle completely engulfs previous candle.
        This is an immediate signal pattern (no pre-breakout state).
        """
        result = {
            'detected': False, 
            'signal': 0, 
            'confidence': 0,
            'status': 'none',
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'breakout_level': None
        }
        
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
                        result['status'] = 'ready'  # Immediate entry
                        result['confidence'] = 75
                        
                        # Entry at current price or slightly above close
                        result['entry_price'] = curr['close'] * 1.001
                        result['stop_loss'] = curr['low'] * 0.99
                        result['take_profit'] = curr['close'] + (curr_body * 2)
                        result['breakout_level'] = curr['close']
                        return result
            
            # Bearish Engulfing: Previous green, current red and engulfs
            if prev['close'] > prev['open']:  # Previous is green
                if curr['close'] < curr['open']:  # Current is red
                    if (curr['open'] > prev['close'] and 
                        curr['close'] < prev['open'] and 
                        curr_body > prev_body):
                        
                        result['detected'] = True
                        result['signal'] = -1  # Bearish
                        result['status'] = 'ready'  # Immediate entry
                        result['confidence'] = 75
                        
                        # Entry at current price or slightly below close
                        result['entry_price'] = curr['close'] * 0.999
                        result['stop_loss'] = curr['high'] * 1.01
                        result['take_profit'] = curr['close'] - (curr_body * 2)
                        result['breakout_level'] = curr['close']
                        
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
        """Get signals from detected patterns with entry levels."""
        signals = {}
        patterns = cls.detect_all_patterns(df)
        
        for name, pattern in patterns.items():
            if pattern.get('detected', False):
                signals[name] = {
                    'signal': pattern['signal'],
                    'confidence': pattern['confidence'],
                    'status': pattern.get('status', 'none'),
                    'entry_price': pattern.get('entry_price'),
                    'stop_loss': pattern.get('stop_loss'),
                    'take_profit': pattern.get('take_profit'),
                    'breakout_level': pattern.get('breakout_level')
                }
        
        return signals
