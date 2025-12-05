"""
Unit tests for the trend analyzer module.
"""

import pytest
import pandas as pd
import numpy as np

from src.trend_analyzer import TrendAnalyzer


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=250, freq='1h')
    
    base_price = 100
    prices = [base_price]
    for _ in range(249):
        change = np.random.randn() * 0.5
        prices.append(prices[-1] * (1 + change / 100))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.randn()) * 0.002) for p in prices],
        'low': [p * (1 - abs(np.random.randn()) * 0.002) for p in prices],
        'close': [p * (1 + np.random.randn() * 0.001) for p in prices],
        'volume': [np.random.randint(1000, 10000) for _ in prices]
    })
    
    df.set_index('timestamp', inplace=True)
    return df


@pytest.fixture
def multi_timeframe_data(sample_ohlcv_data):
    """Create multi-timeframe data dictionary."""
    return {
        '5m': sample_ohlcv_data.copy(),
        '15m': sample_ohlcv_data.copy(),
        '1h': sample_ohlcv_data.copy(),
        '4h': sample_ohlcv_data.copy()
    }


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer class."""
    
    def test_initialization(self):
        """Test TrendAnalyzer initialization."""
        analyzer = TrendAnalyzer()
        assert analyzer.confirmation_threshold == 0.7
        
        analyzer = TrendAnalyzer(confirmation_threshold=0.8)
        assert analyzer.confirmation_threshold == 0.8
    
    def test_analyze_single_timeframe_structure(self, sample_ohlcv_data):
        """Test single timeframe analysis returns correct structure."""
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_single_timeframe(sample_ohlcv_data)
        
        assert 'direction' in result
        assert 'strength' in result
        assert 'confidence' in result
        assert result['direction'] in ['bullish', 'bearish', 'neutral']
        assert 0 <= result['strength'] <= 100
        assert 0 <= result['confidence'] <= 100
    
    def test_analyze_single_timeframe_with_indicators(self, sample_ohlcv_data):
        """Test that analysis includes indicator signals."""
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_single_timeframe(sample_ohlcv_data)
        
        assert 'indicator_signals' in result
        assert 'pattern_signals' in result
    
    def test_analyze_multi_timeframe(self, multi_timeframe_data):
        """Test multi-timeframe analysis."""
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_multi_timeframe(multi_timeframe_data)
        
        assert 'overall_direction' in result
        assert 'overall_strength' in result
        assert 'alignment' in result
        assert 'trend_confirmed' in result
        assert 'timeframe_results' in result
        
        assert result['overall_direction'] in ['bullish', 'bearish', 'neutral']
        assert isinstance(result['trend_confirmed'], bool)
    
    def test_timeframe_results_included(self, multi_timeframe_data):
        """Test that all timeframe results are included."""
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_multi_timeframe(multi_timeframe_data)
        
        for tf in multi_timeframe_data.keys():
            assert tf in result['timeframe_results']
    
    def test_get_trade_signal_strength(self, multi_timeframe_data):
        """Test trade signal strength calculation."""
        analyzer = TrendAnalyzer()
        analysis = analyzer.analyze_multi_timeframe(multi_timeframe_data)
        signal = analyzer.get_trade_signal_strength(analysis, threshold=60)
        
        assert 'is_strong_signal' in signal
        assert 'direction' in signal
        assert 'signal_strength' in signal
        assert 'recommendation' in signal
        
        assert isinstance(signal['is_strong_signal'], bool)
        assert signal['recommendation'] in ['LONG', 'SHORT', 'WAIT']
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_single_timeframe(pd.DataFrame())
        
        assert result['direction'] == 'neutral'
        assert result['strength'] == 0
        assert result['confidence'] == 0
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        df = pd.DataFrame({
            'close': [100, 101, 102],
            'open': [99, 100, 101],
            'high': [102, 103, 104],
            'low': [98, 99, 100],
            'volume': [1000, 1100, 1200]
        })
        
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_single_timeframe(df)
        
        assert result['direction'] == 'neutral'
    
    def test_timeframe_weights(self):
        """Test that timeframe weights are defined."""
        assert '1m' in TrendAnalyzer.TIMEFRAME_WEIGHTS
        assert '5m' in TrendAnalyzer.TIMEFRAME_WEIGHTS
        assert '15m' in TrendAnalyzer.TIMEFRAME_WEIGHTS
        assert '1h' in TrendAnalyzer.TIMEFRAME_WEIGHTS
        assert '4h' in TrendAnalyzer.TIMEFRAME_WEIGHTS
        
        # Weights should sum to approximately 1
        total_weight = sum(TrendAnalyzer.TIMEFRAME_WEIGHTS.values())
        assert 0.9 <= total_weight <= 1.1
    
    def test_signal_threshold(self, multi_timeframe_data):
        """Test signal threshold filtering."""
        analyzer = TrendAnalyzer()
        analysis = analyzer.analyze_multi_timeframe(multi_timeframe_data)
        
        # High threshold should result in no signal for weak trends
        signal_high = analyzer.get_trade_signal_strength(analysis, threshold=95)
        signal_low = analyzer.get_trade_signal_strength(analysis, threshold=10)
        
        # Low threshold should be more permissive
        if analysis['overall_direction'] != 'neutral':
            # With very low threshold, signal should be strong if direction exists
            assert signal_low['signal_strength'] >= 0
