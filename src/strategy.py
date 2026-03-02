"""
Trading Strategies Module for XAUUSD
Implements multiple trading strategies
"""

import sys
from pathlib import Path

# ensure project root on sys.path for direct module runs
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, config: Dict):
        """Initialize strategy"""
        self.config = config
        self.strategy_config = config.get('strategy', {})
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate trading signals
        
        Args:
            data: DataFrame with OHLCV and indicators
        
        Returns:
            DataFrame with signals and metadata
        """
        raise NotImplementedError


class TrendFollowingStrategy(TradingStrategy):
    """Moving Average Crossover Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate trend-following signals"""
        
        logger.info("Generating Trend Following Signals...")
        
        data = data.copy()
        data['Buy'] = False
        data['Sell'] = False
        
        # Fast MA crosses above Slow MA = Buy
        data.loc[data['EMA_10'] > data['EMA_50'], 'Buy'] = True
        data.loc[data['EMA_10'] < data['EMA_50'], 'Sell'] = True
        
        # Confirm with ADX (trend strength)
        if 'ADX' in data.columns:
            data.loc[data['ADX'] < 25, 'Buy'] = False
        
        # Remove consecutive signals
        data['Buy'] = data['Buy'] & ~data['Buy'].shift(1).fillna(False)
        data['Sell'] = data['Sell'] & ~data['Sell'].shift(1).fillna(False)
        
        metadata = {
            'strategy_name': 'Trend Following (MA Crossover)',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'EMA 10/50 crossover with ADX confirmation'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


class MeanReversionStrategy(TradingStrategy):
    """Bollinger Bands Mean Reversion Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate mean reversion signals"""
        
        logger.info("Generating Mean Reversion Signals...")
        
        data = data.copy()
        data['Buy'] = False
        data['Sell'] = False
        
        # Buy when price touches lower Bollinger Band and RSI is oversold
        buy_condition = (data['Close'] <= data['BB_Lower']) & (data['RSI_14'] < 30)
        data.loc[buy_condition, 'Buy'] = True
        
        # Sell when price touches upper Bollinger Band and RSI is overbought
        sell_condition = (data['Close'] >= data['BB_Upper']) & (data['RSI_14'] > 70)
        data.loc[sell_condition, 'Sell'] = True
        
        # Remove consecutive signals
        data['Buy'] = data['Buy'] & ~data['Buy'].shift(1).fillna(False)
        data['Sell'] = data['Sell'] & ~data['Sell'].shift(1).fillna(False)
        
        metadata = {
            'strategy_name': 'Mean Reversion (BB + RSI)',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'Bollinger Bands extremes with RSI confirmation'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


class BreakoutStrategy(TradingStrategy):
    """Volatility Breakout Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate breakout signals"""
        
        logger.info("Generating Breakout Signals...")
        
        lookback = 20
        atr_multiplier = 1.5
        
        data = data.copy()
        data['Highest'] = data['High'].rolling(window=lookback).max()
        data['Lowest'] = data['Low'].rolling(window=lookback).min()
        
        data['Buy'] = data['Close'] > data['Highest'].shift(1)
        data['Sell'] = data['Close'] < data['Lowest'].shift(1)
        
        # Filter with volume confirmation
        avg_volume = data['Volume'].rolling(20).mean()
        volume_filter = data['Volume'] > avg_volume
        
        data.loc[~volume_filter, 'Buy'] = False
        data.loc[~volume_filter, 'Sell'] = False
        
        # Remove consecutive signals
        data['Buy'] = data['Buy'] & ~data['Buy'].shift(1).fillna(False)
        data['Sell'] = data['Sell'] & ~data['Sell'].shift(1).fillna(False)
        
        metadata = {
            'strategy_name': 'Breakout (20-period box)',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'Breakout above/below 20-period highs/lows with volume'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


class SupportResistanceStrategy(TradingStrategy):
    """Support and Resistance Level Strategy"""
    
    @staticmethod
    def detect_levels(data: pd.DataFrame, lookback: int = 50, num_levels: int = 5) -> Dict:
        """Detect support and resistance levels"""
        
        peaks = []
        troughs = []
        
        for i in range(lookback, len(data) - lookback):
            # Detect peaks
            if data['High'].iloc[i] == data['High'].iloc[i-lookback:i+lookback].max():
                peaks.append(data['High'].iloc[i])
            # Detect troughs
            if data['Low'].iloc[i] == data['Low'].iloc[i-lookback:i+lookback].min():
                troughs.append(data['Low'].iloc[i])
        
        # Get most common levels
        resistance_levels = sorted(peaks, reverse=True)[:num_levels]
        support_levels = sorted(troughs)[:num_levels]
        
        return {
            'resistance': resistance_levels,
            'support': support_levels
        }
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate support/resistance signals"""
        
        logger.info("Generating Support/Resistance Signals...")
        
        data = data.copy()
        levels = self.detect_levels(data, lookback=50, num_levels=5)
        
        data['Buy'] = False
        data['Sell'] = False
        
        # Buy near support levels
        for support in levels['support']:
            tolerance = support * 0.002  # 0.2% tolerance
            data.loc[(data['Close'] >= support - tolerance) & 
                    (data['Close'] <= support + tolerance), 'Buy'] = True
        
        # Sell near resistance levels
        for resistance in levels['resistance']:
            tolerance = resistance * 0.002
            data.loc[(data['Close'] >= resistance - tolerance) & 
                    (data['Close'] <= resistance + tolerance), 'Sell'] = True
        
        # Remove consecutive signals
        data['Buy'] = data['Buy'] & ~data['Buy'].shift(1).fillna(False)
        data['Sell'] = data['Sell'] & ~data['Sell'].shift(1).fillna(False)
        
        metadata = {
            'strategy_name': 'Support/Resistance Levels',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'resistance_levels': levels['resistance'],
            'support_levels': levels['support'],
            'description': 'Trading off detected support and resistance levels'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        logger.info(f"  Resistance Levels: {levels['resistance']}")
        logger.info(f"  Support Levels: {levels['support']}")
        
        return data, metadata


class MACDStrategy(TradingStrategy):
    """MACD Crossover Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate MACD signals"""
        
        logger.info("Generating MACD Signals...")
        
        data = data.copy()
        data['Buy'] = False
        data['Sell'] = False
        
        # Buy when MACD crosses above signal line
        buy_condition = (data['MACD'] > data['MACD_Signal']) & \
                       (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
        data.loc[buy_condition, 'Buy'] = True
        
        # Sell when MACD crosses below signal line
        sell_condition = (data['MACD'] < data['MACD_Signal']) & \
                        (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))
        data.loc[sell_condition, 'Sell'] = True
        
        # Filter with histogram direction
        data.loc[data['MACD_Hist'] < 0, 'Buy'] = False
        data.loc[data['MACD_Hist'] > 0, 'Sell'] = False
        
        metadata = {
            'strategy_name': 'MACD Crossover',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'MACD line crosses signal line with histogram confirmation'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


class CombinedStrategy(TradingStrategy):
    """Combined Multi-Signal Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate combined signals from multiple indicators"""
        
        logger.info("Generating Combined Multi-Signal Indicators...")
        
        # Initialize signal strength
        data = data.copy()
        data['Buy_Strength'] = 0
        data['Sell_Strength'] = 0
        
        # Trend Following Signal
        if 'EMA_10' in data.columns and 'EMA_50' in data.columns:
            data.loc[data['EMA_10'] > data['EMA_50'], 'Buy_Strength'] += 1
            data.loc[data['EMA_10'] < data['EMA_50'], 'Sell_Strength'] += 1
        
        # RSI Signal
        if 'RSI_14' in data.columns:
            data.loc[data['RSI_14'] < 30, 'Buy_Strength'] += 1
            data.loc[data['RSI_14'] > 70, 'Sell_Strength'] += 1
        
        # MACD Signal
        if 'MACD' in data.columns:
            data.loc[data['MACD'] > data['MACD_Signal'], 'Buy_Strength'] += 1
            data.loc[data['MACD'] < data['MACD_Signal'], 'Sell_Strength'] += 1
        
        # Bollinger Bands Signal
        if 'BB_Lower' in data.columns:
            data.loc[data['Close'] < data['BB_Lower'], 'Buy_Strength'] += 1
            data.loc[data['Close'] > data['BB_Upper'], 'Sell_Strength'] += 1
        
        # ADX Trend Strength
        if 'ADX' in data.columns:
            strong_trend = data['ADX'] > 25
            data.loc[strong_trend, 'Buy_Strength'] *= 1.2
            data.loc[strong_trend, 'Sell_Strength'] *= 1.2
        
        # Generate final signals (require at least 2 confirmations)
        data['Buy'] = data['Buy_Strength'] >= 2
        data['Sell'] = data['Sell_Strength'] >= 2
        
        # Remove consecutive signals
        data['Buy'] = data['Buy'] & ~data['Buy'].shift(1).fillna(False)
        data['Sell'] = data['Sell'] & ~data['Sell'].shift(1).fillna(False)
        
        metadata = {
            'strategy_name': 'Combined Multi-Signal Strategy',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'Weighted combination of trend, momentum, and volatility signals'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


class CandlestickPatternStrategy(TradingStrategy):
    """Candlestick Pattern Based Strategy"""
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate signals from candlestick patterns"""
        
        logger.info("Generating Candlestick Pattern Signals...")
        
        data = data.copy()
        data['Buy'] = False
        data['Sell'] = False
        
        # Bullish patterns
        bullish_patterns = ['Pattern_hammer', 'Pattern_bullish_engulfing', 
                           'Pattern_morning_star', 'Pattern_three_white_soldiers',
                           'Pattern_piercing_line']
        
        # Bearish patterns
        bearish_patterns = ['Pattern_hanging_man', 'Pattern_bearish_engulfing',
                           'Pattern_evening_star', 'Pattern_three_black_crows',
                           'Pattern_dark_cloud_cover']
        
        for pattern in bullish_patterns:
            if pattern in data.columns:
                data.loc[data[pattern], 'Buy'] = True
        
        for pattern in bearish_patterns:
            if pattern in data.columns:
                data.loc[data[pattern], 'Sell'] = True
        
        # Doji as indecision (no signal)
        if 'Pattern_doji' in data.columns:
            data.loc[data['Pattern_doji'], 'Buy'] = False
            data.loc[data['Pattern_doji'], 'Sell'] = False
        
        metadata = {
            'strategy_name': 'Candlestick Pattern Recognition',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum(),
            'description': 'Trading based on candlestick pattern recognition'
        }
        
        logger.info(f"  Buy Signals: {metadata['buy_signals']}")
        logger.info(f"  Sell Signals: {metadata['sell_signals']}")
        
        return data, metadata


def create_strategy(strategy_type: str, config: Dict) -> TradingStrategy:
    """Factory function to create strategy instances"""
    
    strategies = {
        'trend_following': TrendFollowingStrategy,
        'mean_reversion': MeanReversionStrategy,
        'breakout': BreakoutStrategy,
        'support_resistance': SupportResistanceStrategy,
        'macd': MACDStrategy,
        'combined': CombinedStrategy,
        'candlestick': CandlestickPatternStrategy
    }
    
    if strategy_type not in strategies:
        logger.warning(f"Unknown strategy type: {strategy_type}. Using combined strategy.")
        strategy_type = 'combined'
    
    return strategies[strategy_type](config)


if __name__ == "__main__":
    import yaml
    # ensure imports work when running directly
    from data_fetcher import DataFetcher
    from technical_indicators import TechnicalIndicators
    from candlestick_analysis import CandlestickAnalyzer
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d', start_date='2023-01-01')
    df = fetcher.prepare_data(df)
    
    df = TechnicalIndicators.add_all_indicators(df, config)
    df = CandlestickAnalyzer.analyze_patterns(df)
    
    # Test multiple strategies
    strategies = ['trend_following', 'mean_reversion', 'breakout', 'combined']
    
    for strat_name in strategies:
        strategy = create_strategy(strat_name, config)
        signals, metadata = strategy.generate_signals(df)
        print(f"\n{metadata['strategy_name']}: {metadata['buy_signals']} BUY, {metadata['sell_signals']} SELL")
