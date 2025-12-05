"""
Trend Analysis Module.
Analyzes trend direction across multiple timeframes.
"""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from .indicators import TechnicalIndicators
from .patterns import ChartPatterns

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Multi-timeframe trend analyzer.
    Combines indicators and patterns to determine trend direction.
    """
    
    TIMEFRAME_WEIGHTS = {
        '1m': 0.05,
        '5m': 0.15,
        '15m': 0.20,
        '30m': 0.10,
        '1h': 0.25,
        '4h': 0.20,
        '1d': 0.05
    }
    
    def __init__(self, confirmation_threshold: float = 0.7):
        """
        Initialize the trend analyzer.
        
        Args:
            confirmation_threshold: Minimum agreement ratio for trend confirmation
        """
        self.confirmation_threshold = confirmation_threshold
    
    def analyze_single_timeframe(self, df: pd.DataFrame) -> dict:
        """
        Analyze trend for a single timeframe.
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Dictionary with trend analysis results
        """
        if df.empty or len(df) < 200:
            return {'direction': 'neutral', 'strength': 0, 'confidence': 0}
        
        # Get indicator signals
        indicator_signals = TechnicalIndicators.get_indicator_signals(df)
        
        # Get pattern signals
        pattern_signals = ChartPatterns.get_pattern_signals(df)
        
        # Combine signals
        all_signals = []
        
        # Add indicator signals
        for name, signal in indicator_signals.items():
            all_signals.append({
                'source': f'indicator_{name}',
                'signal': signal,
                'weight': 1.0
            })
        
        # Add pattern signals with higher weight
        for name, data in pattern_signals.items():
            all_signals.append({
                'source': f'pattern_{name}',
                'signal': data['signal'],
                'weight': 1.5,  # Patterns get higher weight
                'confidence': data['confidence']
            })
        
        if not all_signals:
            return {'direction': 'neutral', 'strength': 0, 'confidence': 0}
        
        # Calculate weighted average
        bullish_score = 0
        bearish_score = 0
        total_weight = 0
        
        for sig in all_signals:
            weight = sig['weight']
            total_weight += weight
            
            if sig['signal'] == 1:
                bullish_score += weight
            elif sig['signal'] == -1:
                bearish_score += weight
        
        # Determine direction and strength
        if total_weight == 0:
            return {'direction': 'neutral', 'strength': 0, 'confidence': 0}
        
        bullish_ratio = bullish_score / total_weight
        bearish_ratio = bearish_score / total_weight
        
        if bullish_ratio > bearish_ratio:
            direction = 'bullish'
            strength = bullish_ratio
        elif bearish_ratio > bullish_ratio:
            direction = 'bearish'
            strength = bearish_ratio
        else:
            direction = 'neutral'
            strength = 0
        
        # Calculate confidence
        signal_count = len(all_signals)
        agreement_count = sum(1 for s in all_signals if (
            (direction == 'bullish' and s['signal'] == 1) or
            (direction == 'bearish' and s['signal'] == -1)
        ))
        confidence = (agreement_count / signal_count) * 100 if signal_count > 0 else 0
        
        return {
            'direction': direction,
            'strength': round(strength * 100, 2),
            'confidence': round(confidence, 2),
            'indicator_signals': indicator_signals,
            'pattern_signals': pattern_signals,
            'bullish_ratio': round(bullish_ratio * 100, 2),
            'bearish_ratio': round(bearish_ratio * 100, 2)
        }
    
    def analyze_multi_timeframe(
        self, 
        timeframe_data: dict[str, pd.DataFrame]
    ) -> dict:
        """
        Analyze trend across multiple timeframes.
        
        Args:
            timeframe_data: Dictionary with timeframe as key and OHLCV DataFrame as value
            
        Returns:
            Multi-timeframe analysis results
        """
        results = {}
        weighted_bullish = 0
        weighted_bearish = 0
        total_weight = 0
        
        for timeframe, df in timeframe_data.items():
            analysis = self.analyze_single_timeframe(df)
            results[timeframe] = analysis
            
            weight = self.TIMEFRAME_WEIGHTS.get(timeframe, 0.1)
            total_weight += weight
            
            if analysis['direction'] == 'bullish':
                weighted_bullish += weight * (analysis['strength'] / 100)
            elif analysis['direction'] == 'bearish':
                weighted_bearish += weight * (analysis['strength'] / 100)
        
        # Calculate overall trend
        if total_weight == 0:
            overall_direction = 'neutral'
            overall_strength = 0
        elif weighted_bullish > weighted_bearish:
            overall_direction = 'bullish'
            overall_strength = (weighted_bullish / total_weight) * 100
        elif weighted_bearish > weighted_bullish:
            overall_direction = 'bearish'
            overall_strength = (weighted_bearish / total_weight) * 100
        else:
            overall_direction = 'neutral'
            overall_strength = 0
        
        # Check alignment across timeframes
        aligned_count = sum(
            1 for tf_result in results.values() 
            if tf_result['direction'] == overall_direction
        )
        alignment = aligned_count / len(results) if results else 0
        
        # Trend is confirmed if alignment exceeds threshold
        trend_confirmed = alignment >= self.confirmation_threshold
        
        return {
            'overall_direction': overall_direction,
            'overall_strength': round(overall_strength, 2),
            'alignment': round(alignment * 100, 2),
            'trend_confirmed': trend_confirmed,
            'timeframe_results': results
        }
    
    def get_trade_signal_strength(
        self, 
        analysis: dict, 
        threshold: int = 60
    ) -> dict:
        """
        Determine if analysis warrants a trade signal.
        
        Args:
            analysis: Multi-timeframe analysis results
            threshold: Minimum strength for signal
            
        Returns:
            Trade signal information
        """
        direction = analysis['overall_direction']
        strength = analysis['overall_strength']
        alignment = analysis['alignment']
        confirmed = analysis['trend_confirmed']
        
        # Calculate signal strength
        signal_strength = (strength * 0.6) + (alignment * 0.4)
        
        is_strong_signal = (
            confirmed and 
            signal_strength >= threshold and 
            direction != 'neutral'
        )
        
        return {
            'is_strong_signal': is_strong_signal,
            'direction': direction,
            'signal_strength': round(signal_strength, 2),
            'recommendation': 'LONG' if direction == 'bullish' else 'SHORT' if direction == 'bearish' else 'WAIT'
        }
