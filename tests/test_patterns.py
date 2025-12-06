"""
Unit tests for the patterns module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.patterns import ChartPatterns


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1h')
    
    base_price = 100
    prices = [base_price]
    for _ in range(199):
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
def double_top_data():
    """Create data with a double top pattern."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    
    # Create a W-shape inverted (double top)
    prices = []
    for i in range(100):
        if i < 20:
            prices.append(100 + i * 0.5)
        elif i < 35:
            prices.append(110 - (i - 20) * 0.5)
        elif i < 50:
            prices.append(102.5 + (i - 35) * 0.5)
        elif i < 65:
            prices.append(110 - (i - 50) * 0.5)
        else:
            prices.append(102.5 - (i - 65) * 0.2)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.002 for p in prices],
        'low': [p * 0.998 for p in prices],
        'close': [p * 1.001 for p in prices],
        'volume': [1000 for _ in prices]
    })
    
    df.set_index('timestamp', inplace=True)
    return df


@pytest.fixture
def engulfing_bullish_data():
    """Create data with a bullish engulfing pattern."""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')
    
    prices = list(range(100, 90, -1)) + list(range(90, 100, 1)) + [100] * 30
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices[:-1] + [90],
        'close': [p - 1 for p in prices[:-2]] + [89, 95],  # Last: big green after red
        'high': [max(prices[i], prices[i] + 1) for i in range(len(prices))],
        'low': [min(prices[i], prices[i] - 1) for i in range(len(prices))],
        'volume': [1000 for _ in prices]
    })
    
    df.set_index('timestamp', inplace=True)
    return df


class TestChartPatterns:
    """Test cases for ChartPatterns class."""
    
    def test_find_local_extrema(self, sample_ohlcv_data):
        """Test finding local extrema."""
        highs, lows = ChartPatterns.find_local_extrema(sample_ohlcv_data, order=5)
        
        assert len(highs) > 0
        assert len(lows) > 0
        # Highs and lows should be valid indices
        assert all(0 <= h < len(sample_ohlcv_data) for h in highs)
        assert all(0 <= l < len(sample_ohlcv_data) for l in lows)
    
    def test_detect_double_top_structure(self, sample_ohlcv_data):
        """Test double top detection returns correct structure with entry levels."""
        result = ChartPatterns.detect_double_top(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
        assert 'status' in result
        assert 'entry_price' in result
        assert 'stop_loss' in result
        assert 'take_profit' in result
        assert 'breakout_level' in result
        assert isinstance(result['detected'], bool)
        assert result['signal'] in [-1, 0, 1]
        assert result['status'] in ['none', 'forming', 'ready', 'confirmed']
    
    def test_detect_double_bottom_structure(self, sample_ohlcv_data):
        """Test double bottom detection returns correct structure with entry levels."""
        result = ChartPatterns.detect_double_bottom(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
        assert 'status' in result
        assert 'entry_price' in result
        assert 'stop_loss' in result
        assert 'take_profit' in result
    
    def test_detect_head_and_shoulders_structure(self, sample_ohlcv_data):
        """Test head and shoulders detection returns correct structure."""
        result = ChartPatterns.detect_head_and_shoulders(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_inverse_head_and_shoulders_structure(self, sample_ohlcv_data):
        """Test inverse H&S detection returns correct structure."""
        result = ChartPatterns.detect_inverse_head_and_shoulders(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_ascending_triangle_structure(self, sample_ohlcv_data):
        """Test ascending triangle detection returns correct structure."""
        result = ChartPatterns.detect_ascending_triangle(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_descending_triangle_structure(self, sample_ohlcv_data):
        """Test descending triangle detection returns correct structure."""
        result = ChartPatterns.detect_descending_triangle(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_symmetrical_triangle_structure(self, sample_ohlcv_data):
        """Test symmetrical triangle detection returns correct structure."""
        result = ChartPatterns.detect_symmetrical_triangle(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_rising_wedge_structure(self, sample_ohlcv_data):
        """Test rising wedge detection returns correct structure."""
        result = ChartPatterns.detect_rising_wedge(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_falling_wedge_structure(self, sample_ohlcv_data):
        """Test falling wedge detection returns correct structure."""
        result = ChartPatterns.detect_falling_wedge(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_engulfing_pattern_structure(self, sample_ohlcv_data):
        """Test engulfing pattern detection returns correct structure."""
        result = ChartPatterns.detect_engulfing_pattern(sample_ohlcv_data)
        
        assert 'detected' in result
        assert 'signal' in result
        assert 'confidence' in result
    
    def test_detect_all_patterns(self, sample_ohlcv_data):
        """Test detection of all patterns."""
        patterns = ChartPatterns.detect_all_patterns(sample_ohlcv_data)
        
        expected_patterns = [
            'double_top', 'double_bottom',
            'head_and_shoulders', 'inverse_head_and_shoulders',
            'ascending_triangle', 'descending_triangle', 'symmetrical_triangle',
            'rising_wedge', 'falling_wedge',
            'engulfing'
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns
    
    def test_get_pattern_signals(self, sample_ohlcv_data):
        """Test getting signals from detected patterns with entry levels."""
        signals = ChartPatterns.get_pattern_signals(sample_ohlcv_data)
        
        # Signals should only contain detected patterns
        for name, data in signals.items():
            assert 'signal' in data
            assert 'confidence' in data
            assert 'status' in data
            assert 'entry_price' in data
            assert 'stop_loss' in data
            assert 'take_profit' in data
            assert 'breakout_level' in data
            assert data['signal'] in [-1, 0, 1]
            assert 0 <= data['confidence'] <= 100
            assert data['status'] in ['none', 'forming', 'ready', 'confirmed']
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        patterns = ChartPatterns.detect_all_patterns(df)
        
        assert patterns == {}
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        df = pd.DataFrame({
            'open': [100, 101],
            'high': [102, 103],
            'low': [98, 99],
            'close': [101, 102],
            'volume': [1000, 1100]
        })
        
        patterns = ChartPatterns.detect_all_patterns(df)
        assert patterns == {}
    
    def test_pattern_signals_are_directional(self, sample_ohlcv_data):
        """Test that bearish patterns give -1 and bullish give +1."""
        patterns = ChartPatterns.detect_all_patterns(sample_ohlcv_data)
        
        # Check pattern signal direction makes sense
        bearish_patterns = ['double_top', 'head_and_shoulders', 
                          'descending_triangle', 'rising_wedge']
        bullish_patterns = ['double_bottom', 'inverse_head_and_shoulders',
                          'ascending_triangle', 'falling_wedge']
        
        for pattern in bearish_patterns:
            if patterns[pattern]['detected']:
                assert patterns[pattern]['signal'] == -1
        
        for pattern in bullish_patterns:
            if patterns[pattern]['detected']:
                assert patterns[pattern]['signal'] == 1
