"""
Unit tests for the indicators module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.indicators import TechnicalIndicators


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=250, freq='1h')
    
    # Generate realistic price data
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


class TestTechnicalIndicators:
    """Test cases for TechnicalIndicators class."""
    
    def test_calculate_rsi(self, sample_ohlcv_data):
        """Test RSI calculation."""
        rsi = TechnicalIndicators.calculate_rsi(sample_ohlcv_data)
        
        assert rsi is not None
        assert len(rsi) == len(sample_ohlcv_data)
        # RSI should be between 0 and 100 (excluding NaN values)
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_macd(self, sample_ohlcv_data):
        """Test MACD calculation."""
        macd = TechnicalIndicators.calculate_macd(sample_ohlcv_data)
        
        assert 'macd' in macd
        assert 'signal' in macd
        assert 'histogram' in macd
        assert len(macd['macd']) == len(sample_ohlcv_data)
    
    def test_calculate_bollinger_bands(self, sample_ohlcv_data):
        """Test Bollinger Bands calculation."""
        bb = TechnicalIndicators.calculate_bollinger_bands(sample_ohlcv_data)
        
        assert 'upper' in bb
        assert 'middle' in bb
        assert 'lower' in bb
        assert 'width' in bb
        
        # Upper should be above lower
        valid_idx = bb['upper'].notna() & bb['lower'].notna()
        assert (bb['upper'][valid_idx] >= bb['lower'][valid_idx]).all()
    
    def test_calculate_ema(self, sample_ohlcv_data):
        """Test EMA calculation."""
        emas = TechnicalIndicators.calculate_ema(sample_ohlcv_data)
        
        assert 'ema_9' in emas
        assert 'ema_21' in emas
        assert 'ema_50' in emas
        assert 'ema_200' in emas
    
    def test_calculate_sma(self, sample_ohlcv_data):
        """Test SMA calculation."""
        smas = TechnicalIndicators.calculate_sma(sample_ohlcv_data)
        
        assert 'sma_20' in smas
        assert 'sma_50' in smas
        assert 'sma_100' in smas
        assert 'sma_200' in smas
    
    def test_calculate_stochastic(self, sample_ohlcv_data):
        """Test Stochastic Oscillator calculation."""
        stoch = TechnicalIndicators.calculate_stochastic(sample_ohlcv_data)
        
        assert 'k' in stoch
        assert 'd' in stoch
        
        # Check stochastic is calculated and has values
        valid_k = stoch['k'].dropna()
        assert len(valid_k) > 0
        # The mean should be in a reasonable range (roughly 0-100)
        assert 0 <= valid_k.mean() <= 100
    
    def test_calculate_adx(self, sample_ohlcv_data):
        """Test ADX calculation."""
        adx = TechnicalIndicators.calculate_adx(sample_ohlcv_data)
        
        assert 'adx' in adx
        assert 'di_plus' in adx
        assert 'di_minus' in adx
    
    def test_calculate_cci(self, sample_ohlcv_data):
        """Test CCI calculation."""
        cci = TechnicalIndicators.calculate_cci(sample_ohlcv_data)
        
        assert cci is not None
        assert len(cci) == len(sample_ohlcv_data)
    
    def test_calculate_williams_r(self, sample_ohlcv_data):
        """Test Williams %R calculation."""
        williams = TechnicalIndicators.calculate_williams_r(sample_ohlcv_data)
        
        assert williams is not None
        # Williams %R should have valid values (typically between -100 and 0)
        valid = williams.dropna()
        assert len(valid) > 0
        # The mean should be in a reasonable range
        assert -100 <= valid.mean() <= 0
    
    def test_calculate_obv(self, sample_ohlcv_data):
        """Test OBV calculation."""
        obv = TechnicalIndicators.calculate_obv(sample_ohlcv_data)
        
        assert obv is not None
        assert len(obv) == len(sample_ohlcv_data)
    
    def test_calculate_all(self, sample_ohlcv_data):
        """Test calculation of all indicators."""
        indicators = TechnicalIndicators.calculate_all(sample_ohlcv_data)
        
        assert 'rsi' in indicators
        assert 'macd' in indicators
        assert 'bollinger' in indicators
        assert 'ema' in indicators
        assert 'sma' in indicators
        assert 'stochastic' in indicators
        assert 'adx' in indicators
        assert 'cci' in indicators
        assert 'williams_r' in indicators
        assert 'obv' in indicators
    
    def test_get_indicator_signals(self, sample_ohlcv_data):
        """Test signal generation from indicators."""
        signals = TechnicalIndicators.get_indicator_signals(sample_ohlcv_data)
        
        # Should have signals for all 10 indicators
        expected_indicators = [
            'rsi', 'macd', 'bollinger', 'ema', 'sma',
            'stochastic', 'adx', 'cci', 'williams_r', 'obv'
        ]
        
        for indicator in expected_indicators:
            assert indicator in signals
            # Signal should be -1, 0, or 1
            assert signals[indicator] in [-1, 0, 1]
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        indicators = TechnicalIndicators.calculate_all(df)
        
        assert indicators == {}
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        df = pd.DataFrame({
            'close': [100, 101, 102],
            'open': [99, 100, 101],
            'high': [102, 103, 104],
            'low': [98, 99, 100],
            'volume': [1000, 1100, 1200]
        })
        
        indicators = TechnicalIndicators.calculate_all(df)
        assert indicators == {}
