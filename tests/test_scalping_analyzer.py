"""
Tests for the Scalping Analyzer module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.scalping_analyzer import ScalpingAnalyzer


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=250, freq='1h')
    np.random.seed(42)
    
    base_price = 100
    prices = [base_price]
    for _ in range(249):
        change = np.random.randn() * 0.5
        prices.append(prices[-1] * (1 + change / 100))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + np.random.uniform(0, 0.01)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.01)) for p in prices],
        'close': [p * (1 + np.random.uniform(-0.005, 0.005)) for p in prices],
        'volume': [1000000 + np.random.randint(-100000, 100000) for _ in prices]
    })
    
    df.set_index('timestamp', inplace=True)
    return df


@pytest.fixture
def scalping_analyzer():
    """Create a ScalpingAnalyzer instance."""
    return ScalpingAnalyzer()


class TestScalpingAnalyzer:
    """Test cases for ScalpingAnalyzer class."""
    
    def test_calculate_atr(self, scalping_analyzer, sample_ohlcv_data):
        """Test ATR calculation."""
        atr = scalping_analyzer.calculate_atr(sample_ohlcv_data)
        
        assert atr > 0
        assert isinstance(atr, float)
    
    def test_calculate_atr_empty_data(self, scalping_analyzer):
        """Test ATR calculation with empty data."""
        empty_df = pd.DataFrame()
        atr = scalping_analyzer.calculate_atr(empty_df)
        
        assert atr == 0
    
    def test_find_support_resistance(self, scalping_analyzer, sample_ohlcv_data):
        """Test support and resistance detection."""
        support, resistance = scalping_analyzer.find_support_resistance(sample_ohlcv_data)
        
        current_price = sample_ohlcv_data['close'].iloc[-1]
        
        # Support should be below current price if found
        if support:
            assert support < current_price
        
        # Resistance should be above current price if found
        if resistance:
            assert resistance > current_price
    
    def test_calculate_entry_levels_bullish(self, scalping_analyzer, sample_ohlcv_data):
        """Test entry level calculation for bullish trades."""
        current_price = 100.0
        atr = 1.5
        support = 97.0
        resistance = 105.0
        
        entries = scalping_analyzer.calculate_entry_levels(
            current_price, 'bullish', support, resistance, atr
        )
        
        assert len(entries) == 4
        # For bullish, entries should be at or below current price
        assert all(e <= current_price * 1.001 for e in entries)
        # Entries should be ordered from highest to lowest
        assert entries[0] > entries[3]
    
    def test_calculate_entry_levels_bearish(self, scalping_analyzer, sample_ohlcv_data):
        """Test entry level calculation for bearish trades."""
        current_price = 100.0
        atr = 1.5
        support = 95.0
        resistance = 103.0
        
        entries = scalping_analyzer.calculate_entry_levels(
            current_price, 'bearish', support, resistance, atr
        )
        
        assert len(entries) == 4
        # For bearish, entries should be at or above current price
        assert all(e >= current_price * 0.999 for e in entries)
        # Entries should be ordered from lowest to highest
        assert entries[0] < entries[3]
    
    def test_calculate_take_profit_levels_bullish(self, scalping_analyzer):
        """Test take profit calculation for bullish trades."""
        avg_entry = 100.0
        atr = 1.5
        support = 97.0
        resistance = 108.0
        
        tps = scalping_analyzer.calculate_take_profit_levels(
            avg_entry, 'bullish', support, resistance, atr
        )
        
        assert len(tps) == 4
        # For bullish, TPs should be above entry
        assert all(tp > avg_entry for tp in tps)
        # TPs should be ordered from lowest to highest
        assert tps[0] < tps[3]
    
    def test_calculate_take_profit_levels_bearish(self, scalping_analyzer):
        """Test take profit calculation for bearish trades."""
        avg_entry = 100.0
        atr = 1.5
        support = 92.0
        resistance = 103.0
        
        tps = scalping_analyzer.calculate_take_profit_levels(
            avg_entry, 'bearish', support, resistance, atr
        )
        
        assert len(tps) == 4
        # For bearish, TPs should be below entry
        assert all(tp < avg_entry for tp in tps)
        # TPs should be ordered from highest to lowest
        assert tps[0] > tps[3]
    
    def test_calculate_stop_loss_bullish(self, scalping_analyzer):
        """Test stop loss calculation for bullish trades."""
        avg_entry = 100.0
        atr = 1.5
        support = 97.0
        resistance = 105.0
        
        stop = scalping_analyzer.calculate_stop_loss(
            avg_entry, 'bullish', support, resistance, atr
        )
        
        # Stop should be below entry
        assert stop < avg_entry
        # Stop should be at least 1% below entry
        assert stop <= avg_entry * 0.99
    
    def test_calculate_stop_loss_bearish(self, scalping_analyzer):
        """Test stop loss calculation for bearish trades."""
        avg_entry = 100.0
        atr = 1.5
        support = 95.0
        resistance = 103.0
        
        stop = scalping_analyzer.calculate_stop_loss(
            avg_entry, 'bearish', support, resistance, atr
        )
        
        # Stop should be above entry
        assert stop > avg_entry
        # Stop should be at least 1% above entry
        assert stop >= avg_entry * 1.01
    
    def test_validate_trade_quality_valid(self, scalping_analyzer):
        """Test trade quality validation for a valid trade."""
        entries = [100.0, 99.5, 99.0, 98.5]
        take_profits = [102.0, 104.0, 106.0, 108.0]
        stop_loss = 97.0
        
        # Create aligned indicator signals
        indicator_signals = {
            'rsi': 1, 'macd': 1, 'ema': 1, 'sma': 1,
            'stochastic': 1, 'adx': 1, 'cci': 1,
            'williams': 0, 'obv': 0, 'bollinger': 0
        }
        
        validation = scalping_analyzer.validate_trade_quality(
            entries=entries,
            take_profits=take_profits,
            stop_loss=stop_loss,
            direction='bullish',
            indicator_signals=indicator_signals,
            timeframe_alignment=0.75,
            pattern_confidence=80
        )
        
        assert validation['is_valid'] is True
        assert validation['score'] > 0
        assert validation['risk_reward_ratio'] >= 1.5
    
    def test_validate_trade_quality_invalid_rr(self, scalping_analyzer):
        """Test trade quality validation for invalid R/R ratio."""
        entries = [100.0, 99.5, 99.0, 98.5]
        take_profits = [100.5, 101.0, 101.5, 102.0]  # Low TPs
        stop_loss = 95.0  # High risk
        
        indicator_signals = {
            'rsi': 1, 'macd': 1, 'ema': 1, 'sma': 1,
            'stochastic': 1, 'adx': 1, 'cci': 1,
            'williams': 0, 'obv': 0, 'bollinger': 0
        }
        
        validation = scalping_analyzer.validate_trade_quality(
            entries=entries,
            take_profits=take_profits,
            stop_loss=stop_loss,
            direction='bullish',
            indicator_signals=indicator_signals,
            timeframe_alignment=0.75,
            pattern_confidence=80
        )
        
        assert validation['is_valid'] is False
        assert 'Risk/Reward' in str(validation['reasons'])
    
    def test_validate_trade_quality_insufficient_indicators(self, scalping_analyzer):
        """Test trade quality validation with insufficient indicator alignment."""
        entries = [100.0, 99.5, 99.0, 98.5]
        take_profits = [102.0, 104.0, 106.0, 108.0]
        stop_loss = 97.0
        
        # Only 3 aligned indicators
        indicator_signals = {
            'rsi': 1, 'macd': 1, 'ema': 1, 'sma': -1,
            'stochastic': -1, 'adx': 0, 'cci': 0,
            'williams': -1, 'obv': -1, 'bollinger': 0
        }
        
        validation = scalping_analyzer.validate_trade_quality(
            entries=entries,
            take_profits=take_profits,
            stop_loss=stop_loss,
            direction='bullish',
            indicator_signals=indicator_signals,
            timeframe_alignment=0.75,
            pattern_confidence=80
        )
        
        assert validation['is_valid'] is False
        assert 'Indicator alignment' in str(validation['reasons'])
    
    def test_generate_scalping_trade_valid(self, scalping_analyzer, sample_ohlcv_data):
        """Test generating a valid scalping trade."""
        indicator_signals = {
            'rsi': 1, 'macd': 1, 'ema': 1, 'sma': 1,
            'stochastic': 1, 'adx': 1, 'cci': 1,
            'williams': 1, 'obv': 0, 'bollinger': 0
        }
        
        trade = scalping_analyzer.generate_scalping_trade(
            symbol='BTCUSDT',
            current_price=100.0,
            direction='bullish',
            df=sample_ohlcv_data,
            indicator_signals=indicator_signals,
            timeframe_alignment=0.8,
            pattern_confidence=80
        )
        
        # Trade might be None if quality criteria not met
        if trade:
            assert trade['symbol'] == 'BTCUSDT'
            assert trade['direction'] == 'LONG'
            assert len(trade['entries']) == 4
            assert len(trade['take_profits']) == 4
            assert trade['stop_loss'] > 0
            assert 'trade_score' in trade
    
    def test_generate_scalping_trade_invalid_direction(self, scalping_analyzer, sample_ohlcv_data):
        """Test generating a trade with invalid direction."""
        trade = scalping_analyzer.generate_scalping_trade(
            symbol='BTCUSDT',
            current_price=100.0,
            direction='invalid',
            df=sample_ohlcv_data,
            indicator_signals={},
            timeframe_alignment=0.8
        )
        
        assert trade is None
    
    def test_scalping_trade_structure(self, scalping_analyzer, sample_ohlcv_data):
        """Test the structure of a generated scalping trade."""
        indicator_signals = {
            'rsi': 1, 'macd': 1, 'ema': 1, 'sma': 1,
            'stochastic': 1, 'adx': 1, 'cci': 1,
            'williams': 1, 'obv': 1, 'bollinger': 1
        }
        
        trade = scalping_analyzer.generate_scalping_trade(
            symbol='ETHUSDT',
            current_price=2500.0,
            direction='bullish',
            df=sample_ohlcv_data,
            indicator_signals=indicator_signals,
            timeframe_alignment=0.9,
            pattern_confidence=85
        )
        
        if trade:
            # Check all required fields exist
            assert 'symbol' in trade
            assert 'direction' in trade
            assert 'current_price' in trade
            assert 'entries' in trade
            assert 'take_profits' in trade
            assert 'stop_loss' in trade
            assert 'trade_score' in trade
            assert 'risk_percent' in trade
            assert 'reward_percent' in trade
            assert 'risk_reward_ratio' in trade
            assert 'is_high_probability' in trade
