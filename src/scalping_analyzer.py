"""
Scalping Trade Analyzer Module.
Analyzes coins for scalping opportunities with multiple entry and take profit levels.
"""

import logging
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ScalpingAnalyzer:
    """
    Scalping Trade Analyzer for Binance Futures.
    
    Provides:
    - 4 Entry levels for scaling into positions
    - 4 Take Profit levels for scaling out
    - Stop Loss level
    - Trade quality validation for high-profit trades only
    """
    
    # Minimum requirements for a valid scalping trade (configurable via constructor)
    DEFAULT_MIN_RISK_REWARD_RATIO = 1.5  # Minimum 1:1.5 risk/reward
    DEFAULT_MIN_PROFIT_POTENTIAL = 0.5  # Minimum 0.5% profit potential
    DEFAULT_MIN_INDICATOR_ALIGNMENT = 6  # At least 6/10 indicators aligned
    DEFAULT_MIN_TIMEFRAME_ALIGNMENT = 0.6  # At least 60% timeframes aligned
    
    # Take profit multipliers for long positions
    TP_MULTIPLIERS_LONG = [1.005, 1.015, 1.025, 1.04]  # 0.5%, 1.5%, 2.5%, 4%
    TP_MULTIPLIERS_SHORT = [0.995, 0.985, 0.975, 0.96]  # -0.5%, -1.5%, -2.5%, -4%
    
    # Stop loss distance multiplier
    MIN_STOP_DISTANCE = 0.015  # Minimum 1.5% stop distance for scalping
    
    def __init__(
        self,
        min_risk_reward: float = None,
        min_profit_potential: float = None,
        min_indicator_alignment: int = None,
        min_timeframe_alignment: float = None
    ):
        """
        Initialize the scalping analyzer.
        
        Args:
            min_risk_reward: Minimum risk/reward ratio (default: 1.5)
            min_profit_potential: Minimum profit potential % (default: 0.5)
            min_indicator_alignment: Minimum aligned indicators (default: 6)
            min_timeframe_alignment: Minimum timeframe alignment (default: 0.6)
        """
        self.min_risk_reward = min_risk_reward or self.DEFAULT_MIN_RISK_REWARD_RATIO
        self.min_profit_potential = min_profit_potential or self.DEFAULT_MIN_PROFIT_POTENTIAL
        self.min_indicator_alignment = min_indicator_alignment or self.DEFAULT_MIN_INDICATOR_ALIGNMENT
        self.min_timeframe_alignment = min_timeframe_alignment or self.DEFAULT_MIN_TIMEFRAME_ALIGNMENT
    
    def calculate_entry_levels(
        self,
        current_price: float,
        direction: str,
        support: float,
        resistance: float,
        atr: float
    ) -> List[float]:
        """
        Calculate 4 DCA (Dollar Cost Averaging) entry levels for optimal average entry.
        
        For LONG: Entry levels decrease progressively (buy on dips)
                  - Uses weighted spacing for better avg entry
                  - Entry 4 near support for best risk/reward
        For SHORT: Entry levels increase progressively (sell on rallies)
                   - Uses weighted spacing for better avg entry
                   - Entry 4 near resistance for best risk/reward
        
        Args:
            current_price: Current market price
            direction: 'bullish' or 'bearish'
            support: Nearest support level
            resistance: Nearest resistance level
            atr: Average True Range for volatility-based spacing
            
        Returns:
            List of 4 DCA entry prices
        """
        entries = []
        
        # DCA spacing percentages - increasing distance for better average
        # Entry 1: 0.1%, Entry 2: 0.5%, Entry 3: 1.0%, Entry 4: 1.5-2%
        dca_percentages = [0.001, 0.005, 0.010, 0.015]
        
        if direction == 'bullish':
            # For longs, DCA entries are progressively lower for better avg
            # Use ATR for dynamic spacing, but respect support level
            
            # Calculate base spacing from ATR
            base_spacing = atr * 0.25  # 25% of ATR per level
            
            # Calculate the range to support
            range_to_support = (current_price - support) if support else current_price * 0.03
            
            # Entry 1: Market entry (small dip for confirmation)
            entry1 = current_price * (1 - dca_percentages[0])
            
            # Entry 2: First DCA level (0.5% below or 1x ATR spacing)
            entry2 = current_price * (1 - dca_percentages[1])
            if base_spacing > 0:
                entry2 = min(entry2, current_price - base_spacing)
            
            # Entry 3: Second DCA level (1% below or 2x ATR spacing)
            entry3 = current_price * (1 - dca_percentages[2])
            if base_spacing > 0:
                entry3 = min(entry3, current_price - base_spacing * 2)
            
            # Entry 4: Deep DCA near support (best avg entry potential)
            if support and support < current_price:
                # Place entry 4 just above support for maximum DCA benefit
                entry4 = support * 1.003  # 0.3% above support
            else:
                entry4 = current_price * (1 - dca_percentages[3])
                if base_spacing > 0:
                    entry4 = min(entry4, current_price - base_spacing * 3)
            
            entries = [
                round(entry1, 6),
                round(entry2, 6),
                round(entry3, 6),
                round(entry4, 6)
            ]
            
        else:  # bearish
            # For shorts, DCA entries are progressively higher for better avg
            
            base_spacing = atr * 0.25
            range_to_resistance = (resistance - current_price) if resistance else current_price * 0.03
            
            # Entry 1: Market entry (small rally for confirmation)
            entry1 = current_price * (1 + dca_percentages[0])
            
            # Entry 2: First DCA level
            entry2 = current_price * (1 + dca_percentages[1])
            if base_spacing > 0:
                entry2 = max(entry2, current_price + base_spacing)
            
            # Entry 3: Second DCA level
            entry3 = current_price * (1 + dca_percentages[2])
            if base_spacing > 0:
                entry3 = max(entry3, current_price + base_spacing * 2)
            
            # Entry 4: Deep DCA near resistance
            if resistance and resistance > current_price:
                entry4 = resistance * 0.997  # 0.3% below resistance
            else:
                entry4 = current_price * (1 + dca_percentages[3])
                if base_spacing > 0:
                    entry4 = max(entry4, current_price + base_spacing * 3)
            
            entries = [
                round(entry1, 6),
                round(entry2, 6),
                round(entry3, 6),
                round(entry4, 6)
            ]
        
        return entries
    
    def calculate_average_entry(self, entries: List[float], weights: List[float] = None) -> float:
        """
        Calculate the average entry price for DCA positions.
        
        Args:
            entries: List of entry prices
            weights: Optional weights for each entry (default: equal weight)
            
        Returns:
            Average entry price
        """
        if not weights:
            # Default: equal weight (25% each)
            weights = [0.25, 0.25, 0.25, 0.25]
        
        weighted_sum = sum(e * w for e, w in zip(entries, weights))
        return round(weighted_sum, 6)
    
    def calculate_take_profit_levels(
        self,
        avg_entry: float,
        direction: str,
        support: float,
        resistance: float,
        atr: float,
        pattern_target: Optional[float] = None
    ) -> List[float]:
        """
        Calculate 4 take profit levels for scaling out of a position.
        
        Args:
            avg_entry: Average entry price
            direction: 'bullish' or 'bearish'
            support: Nearest support level
            resistance: Nearest resistance level
            atr: Average True Range
            pattern_target: Optional pattern-based target price
            
        Returns:
            List of 4 take profit prices
        """
        tps = []
        
        if direction == 'bullish':
            # For longs, TPs are above entry using class multipliers
            tp1 = avg_entry * self.TP_MULTIPLIERS_LONG[0]
            tp2 = avg_entry * self.TP_MULTIPLIERS_LONG[1]
            tp3 = min(avg_entry * self.TP_MULTIPLIERS_LONG[2], resistance * 0.998) if resistance else avg_entry * self.TP_MULTIPLIERS_LONG[2]
            
            # TP4: Maximum target (pattern target or 3-5%)
            if pattern_target and pattern_target > avg_entry:
                tp4 = pattern_target
            else:
                tp4 = resistance if resistance else avg_entry * self.TP_MULTIPLIERS_LONG[3]
            
            tps = [round(tp1, 6), round(tp2, 6), round(tp3, 6), round(tp4, 6)]
            
        else:  # bearish
            # For shorts, TPs are below entry using class multipliers
            tp1 = avg_entry * self.TP_MULTIPLIERS_SHORT[0]
            tp2 = avg_entry * self.TP_MULTIPLIERS_SHORT[1]
            tp3 = max(avg_entry * self.TP_MULTIPLIERS_SHORT[2], support * 1.002) if support else avg_entry * self.TP_MULTIPLIERS_SHORT[2]
            
            # TP4: Maximum target (pattern target or 3-5%)
            if pattern_target and pattern_target < avg_entry:
                tp4 = pattern_target
            else:
                tp4 = support if support else avg_entry * self.TP_MULTIPLIERS_SHORT[3]
            
            tps = [round(tp1, 6), round(tp2, 6), round(tp3, 6), round(tp4, 6)]
        
        return tps
    
    def calculate_stop_loss(
        self,
        avg_entry: float,
        direction: str,
        support: float,
        resistance: float,
        atr: float
    ) -> float:
        """
        Calculate stop loss level.
        
        Args:
            avg_entry: Average entry price
            direction: 'bullish' or 'bearish'
            support: Nearest support level
            resistance: Nearest resistance level
            atr: Average True Range
            
        Returns:
            Stop loss price
        """
        # Use ATR-based stop, but also consider support/resistance
        atr_stop_distance = atr * 1.5  # 1.5 ATR for stop
        min_stop_multiplier = 1 - self.MIN_STOP_DISTANCE  # Use class constant
        max_stop_multiplier = 1 + self.MIN_STOP_DISTANCE
        
        if direction == 'bullish':
            # Stop below support or 1.5 ATR below entry
            if support and support < avg_entry:
                stop = support * 0.995  # Just below support
            else:
                stop = avg_entry - atr_stop_distance
            
            # Ensure stop is at least MIN_STOP_DISTANCE below entry
            stop = min(stop, avg_entry * min_stop_multiplier)
            
        else:  # bearish
            # Stop above resistance or 1.5 ATR above entry
            if resistance and resistance > avg_entry:
                stop = resistance * 1.005  # Just above resistance
            else:
                stop = avg_entry + atr_stop_distance
            
            # Ensure stop is at least MIN_STOP_DISTANCE above entry
            stop = max(stop, avg_entry * max_stop_multiplier)
        
        return round(stop, 6)
    
    def find_support_resistance(self, df: pd.DataFrame) -> Tuple[Optional[float], Optional[float]]:
        """
        Find nearest support and resistance levels.
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Tuple of (support, resistance) prices
        """
        if df.empty or len(df) < 20:
            return None, None
        
        current_price = df['close'].iloc[-1]
        
        # Find local highs and lows
        window = 10
        df_temp = df.copy()
        df_temp['local_high'] = df_temp['high'].rolling(window=window, center=True).max()
        df_temp['local_low'] = df_temp['low'].rolling(window=window, center=True).min()
        
        # Get recent highs and lows
        recent = df_temp.tail(50)
        
        # Find resistance (prices above current)
        highs = recent[recent['high'] == recent['local_high']]['high'].values
        resistances = [h for h in highs if h > current_price]
        resistance = min(resistances) if resistances else None
        
        # Find support (prices below current)
        lows = recent[recent['low'] == recent['local_low']]['low'].values
        supports = [l for l in lows if l < current_price]
        support = max(supports) if supports else None
        
        return support, resistance
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        if df.empty or len(df) < period:
            return 0
        
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr if not pd.isna(atr) else 0
    
    def validate_trade_quality(
        self,
        entries: List[float],
        take_profits: List[float],
        stop_loss: float,
        direction: str,
        indicator_signals: dict,
        timeframe_alignment: float,
        pattern_confidence: float
    ) -> dict:
        """
        Validate if the trade meets high-profit criteria.
        
        Args:
            entries: List of 4 entry prices
            take_profits: List of 4 take profit prices
            stop_loss: Stop loss price
            direction: 'bullish' or 'bearish'
            indicator_signals: Dict of indicator signals
            timeframe_alignment: Percentage of timeframes aligned
            pattern_confidence: Pattern detection confidence
            
        Returns:
            Dict with validation results
        """
        avg_entry = sum(entries) / len(entries)
        avg_tp = sum(take_profits) / len(take_profits)
        
        # Calculate risk and reward
        if direction == 'bullish':
            risk = abs(avg_entry - stop_loss) / avg_entry * 100
            reward = abs(avg_tp - avg_entry) / avg_entry * 100
        else:
            risk = abs(stop_loss - avg_entry) / avg_entry * 100
            reward = abs(avg_entry - avg_tp) / avg_entry * 100
        
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Count aligned indicators
        aligned_count = sum(1 for s in indicator_signals.values() if (
            (direction == 'bullish' and s == 1) or
            (direction == 'bearish' and s == -1)
        ))
        
        # Validation checks using instance variables
        is_valid = True
        reasons = []
        
        if risk_reward_ratio < self.min_risk_reward:
            is_valid = False
            reasons.append(f"Risk/Reward {risk_reward_ratio:.2f} < {self.min_risk_reward}")
        
        if reward < self.min_profit_potential:
            is_valid = False
            reasons.append(f"Profit potential {reward:.2f}% < {self.min_profit_potential}%")
        
        if aligned_count < self.min_indicator_alignment:
            is_valid = False
            reasons.append(f"Indicator alignment {aligned_count}/10 < {self.min_indicator_alignment}")
        
        if timeframe_alignment < self.min_timeframe_alignment:
            is_valid = False
            reasons.append(f"Timeframe alignment {timeframe_alignment:.0%} < {self.min_timeframe_alignment:.0%}")
        
        # Calculate overall trade score (0-100)
        score = (
            (min(risk_reward_ratio / 3, 1) * 25) +  # RR contribution (max 25)
            (min(reward / 3, 1) * 25) +  # Profit potential (max 25)
            (aligned_count / 10 * 25) +  # Indicator alignment (max 25)
            (timeframe_alignment * 15) +  # Timeframe alignment (max 15)
            (pattern_confidence / 100 * 10)  # Pattern confidence (max 10)
        )
        
        return {
            'is_valid': is_valid,
            'score': round(score, 1),
            'risk_percent': round(risk, 2),
            'reward_percent': round(reward, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'indicators_aligned': aligned_count,
            'avg_entry': avg_entry,
            'reasons': reasons
        }
    
    def generate_scalping_trade(
        self,
        symbol: str,
        current_price: float,
        direction: str,
        df: pd.DataFrame,
        indicator_signals: dict,
        timeframe_alignment: float,
        pattern_confidence: float = 70,
        pattern_target: Optional[float] = None
    ) -> Optional[dict]:
        """
        Generate a complete scalping trade setup.
        
        Args:
            symbol: Trading pair symbol
            current_price: Current market price
            direction: 'bullish' or 'bearish'
            df: OHLCV DataFrame for calculations
            indicator_signals: Dict of indicator signals
            timeframe_alignment: Percentage of timeframes aligned
            pattern_confidence: Pattern detection confidence
            pattern_target: Optional pattern-based target
            
        Returns:
            Complete scalping trade setup or None if invalid
        """
        if direction not in ['bullish', 'bearish']:
            return None
        
        # Calculate ATR for volatility-based levels
        atr = self.calculate_atr(df)
        if atr == 0:
            atr = current_price * 0.01  # Fallback to 1% of price
        
        # Find support and resistance
        support, resistance = self.find_support_resistance(df)
        
        # Calculate entry levels
        entries = self.calculate_entry_levels(
            current_price, direction, support, resistance, atr
        )
        
        # Calculate average entry for TP/SL calculations
        avg_entry = sum(entries) / len(entries)
        
        # Calculate take profit levels
        take_profits = self.calculate_take_profit_levels(
            avg_entry, direction, support, resistance, atr, pattern_target
        )
        
        # Calculate stop loss
        stop_loss = self.calculate_stop_loss(
            avg_entry, direction, support, resistance, atr
        )
        
        # Validate trade quality
        validation = self.validate_trade_quality(
            entries, take_profits, stop_loss, direction,
            indicator_signals, timeframe_alignment, pattern_confidence
        )
        
        # Only return trade if it meets quality criteria
        if not validation['is_valid']:
            logger.info(f"Trade rejected for {symbol}: {validation['reasons']}")
            return None
        
        return {
            'symbol': symbol,
            'direction': 'LONG' if direction == 'bullish' else 'SHORT',
            'current_price': current_price,
            'entries': entries,
            'avg_entry': avg_entry,
            'take_profits': take_profits,
            'stop_loss': stop_loss,
            'support': support,
            'resistance': resistance,
            'trade_score': validation['score'],
            'risk_percent': validation['risk_percent'],
            'reward_percent': validation['reward_percent'],
            'risk_reward_ratio': validation['risk_reward_ratio'],
            'indicators_aligned': validation['indicators_aligned'],
            'is_high_probability': validation['score'] >= 70
        }
