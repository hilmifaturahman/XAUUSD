"""
Candlestick Analysis Module for XAUUSD
Identifies candlestick patterns and provides analysis
"""

import sys
from pathlib import Path

# ensure project root is on sys.path for imports when module is run directly
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CandlestickAnalyzer:
    """Analyze candlestick patterns and characteristics"""
    
    @staticmethod
    def get_body_size(data: pd.DataFrame, index: int) -> float:
        """Get candlestick body size (absolute)"""
        return abs(data['Close'].iloc[index] - data['Open'].iloc[index])
    
    @staticmethod
    def get_upper_wick(data: pd.DataFrame, index: int) -> float:
        """Get upper wick length"""
        close_open = max(data['Open'].iloc[index], data['Close'].iloc[index])
        return data['High'].iloc[index] - close_open
    
    @staticmethod
    def get_lower_wick(data: pd.DataFrame, index: int) -> float:
        """Get lower wick length"""
        close_open = min(data['Open'].iloc[index], data['Close'].iloc[index])
        return close_open - data['Low'].iloc[index]
    
    @staticmethod
    def get_total_range(data: pd.DataFrame, index: int) -> float:
        """Get total candle range (High - Low)"""
        return data['High'].iloc[index] - data['Low'].iloc[index]
    
    @staticmethod
    def is_bullish(data: pd.DataFrame, index: int) -> bool:
        """Check if candle is bullish (Close > Open)"""
        return data['Close'].iloc[index] > data['Open'].iloc[index]
    
    @staticmethod
    def is_bearish(data: pd.DataFrame, index: int) -> bool:
        """Check if candle is bearish (Close < Open)"""
        return data['Close'].iloc[index] < data['Open'].iloc[index]
    
    @staticmethod
    def is_doji(data: pd.DataFrame, index: int, threshold: float = 0.1) -> bool:
        """Identify Doji pattern"""
        body = CandlestickAnalyzer.get_body_size(data, index)
        total_range = CandlestickAnalyzer.get_total_range(data, index)
        
        if total_range == 0:
            return False
        
        return (body / total_range) < threshold
    
    @staticmethod
    def is_hammer(data: pd.DataFrame, index: int) -> bool:
        """Identify Hammer pattern (bullish reversal)"""
        if index < 1:
            return False
        
        # Lower wick should be at least 2x body size
        lower_wick = CandlestickAnalyzer.get_lower_wick(data, index)
        body = CandlestickAnalyzer.get_body_size(data, index)
        upper_wick = CandlestickAnalyzer.get_upper_wick(data, index)
        
        if body == 0:
            return False
        
        # Bullish hammer: close > open, long lower wick
        return (CandlestickAnalyzer.is_bullish(data, index) and 
                lower_wick > body * 2 and 
                upper_wick < body)
    
    @staticmethod
    def is_hanging_man(data: pd.DataFrame, index: int) -> bool:
        """Identify Hanging Man pattern (bearish reversal)"""
        if index < 1:
            return False
        
        lower_wick = CandlestickAnalyzer.get_lower_wick(data, index)
        body = CandlestickAnalyzer.get_body_size(data, index)
        upper_wick = CandlestickAnalyzer.get_upper_wick(data, index)
        
        if body == 0:
            return False
        
        # Bearish hanging man: close < open, long lower wick
        return (CandlestickAnalyzer.is_bearish(data, index) and 
                lower_wick > body * 2 and 
                upper_wick < body)
    
    @staticmethod
    def is_bullish_engulfing(data: pd.DataFrame, index: int) -> bool:
        """Identify Bullish Engulfing pattern"""
        if index < 1:
            return False
        
        # Current candle must be bullish
        if not CandlestickAnalyzer.is_bullish(data, index):
            return False
        
        # Previous candle must be bearish
        if not CandlestickAnalyzer.is_bearish(data, index - 1):
            return False
        
        # Current open must be below previous close
        # Current close must be above previous open
        return (data['Open'].iloc[index] < data['Close'].iloc[index - 1] and
                data['Close'].iloc[index] > data['Open'].iloc[index - 1])
    
    @staticmethod
    def is_bearish_engulfing(data: pd.DataFrame, index: int) -> bool:
        """Identify Bearish Engulfing pattern"""
        if index < 1:
            return False
        
        # Current candle must be bearish
        if not CandlestickAnalyzer.is_bearish(data, index):
            return False
        
        # Previous candle must be bullish
        if not CandlestickAnalyzer.is_bullish(data, index - 1):
            return False
        
        # Current open must be above previous close
        # Current close must be below previous open
        return (data['Open'].iloc[index] > data['Close'].iloc[index - 1] and
                data['Close'].iloc[index] < data['Open'].iloc[index - 1])
    
    @staticmethod
    def is_morning_star(data: pd.DataFrame, index: int) -> bool:
        """Identify Morning Star pattern (bullish reversal)"""
        if index < 2:
            return False
        
        # First: bearish long candle
        # Second: small body (gap or small move)
        # Third: bullish, closes above first candle
        
        first_bearish = CandlestickAnalyzer.is_bearish(data, index - 2)
        second_small = CandlestickAnalyzer.get_body_size(data, index - 1) < \
                      CandlestickAnalyzer.get_body_size(data, index - 2) * 0.5
        third_bullish = CandlestickAnalyzer.is_bullish(data, index)
        third_above = data['Close'].iloc[index] > data['Open'].iloc[index - 2]
        
        return first_bearish and second_small and third_bullish and third_above
    
    @staticmethod
    def is_evening_star(data: pd.DataFrame, index: int) -> bool:
        """Identify Evening Star pattern (bearish reversal)"""
        if index < 2:
            return False
        
        first_bullish = CandlestickAnalyzer.is_bullish(data, index - 2)
        second_small = CandlestickAnalyzer.get_body_size(data, index - 1) < \
                      CandlestickAnalyzer.get_body_size(data, index - 2) * 0.5
        third_bearish = CandlestickAnalyzer.is_bearish(data, index)
        third_below = data['Close'].iloc[index] < data['Open'].iloc[index - 2]
        
        return first_bullish and second_small and third_bearish and third_below
    
    @staticmethod
    def is_three_white_soldiers(data: pd.DataFrame, index: int) -> bool:
        """Identify Three White Soldiers pattern (bullish)"""
        if index < 2:
            return False
        
        # Three consecutive bullish candles with higher closes
        candle1_bullish = CandlestickAnalyzer.is_bullish(data, index - 2)
        candle2_bullish = CandlestickAnalyzer.is_bullish(data, index - 1)
        candle3_bullish = CandlestickAnalyzer.is_bullish(data, index)
        
        higher_closes = (data['Close'].iloc[index - 1] > data['Close'].iloc[index - 2] and
                        data['Close'].iloc[index] > data['Close'].iloc[index - 1])
        
        return candle1_bullish and candle2_bullish and candle3_bullish and higher_closes
    
    @staticmethod
    def is_three_black_crows(data: pd.DataFrame, index: int) -> bool:
        """Identify Three Black Crows pattern (bearish)"""
        if index < 2:
            return False
        
        candle1_bearish = CandlestickAnalyzer.is_bearish(data, index - 2)
        candle2_bearish = CandlestickAnalyzer.is_bearish(data, index - 1)
        candle3_bearish = CandlestickAnalyzer.is_bearish(data, index)
        
        lower_closes = (data['Close'].iloc[index - 1] < data['Close'].iloc[index - 2] and
                       data['Close'].iloc[index] < data['Close'].iloc[index - 1])
        
        return candle1_bearish and candle2_bearish and candle3_bearish and lower_closes
    
    @staticmethod
    def is_spinning_top(data: pd.DataFrame, index: int) -> bool:
        """Identify Spinning Top pattern (indecision)"""
        body = CandlestickAnalyzer.get_body_size(data, index)
        upper_wick = CandlestickAnalyzer.get_upper_wick(data, index)
        lower_wick = CandlestickAnalyzer.get_lower_wick(data, index)
        
        if body == 0:
            return False
        
        total_range = CandlestickAnalyzer.get_total_range(data, index)
        if total_range == 0:
            return False
        # Small body with roughly equal wicks
        return (body < total_range * 0.3 and
                abs(upper_wick - lower_wick) < body)
    
    @staticmethod
    def is_marubozu(data: pd.DataFrame, index: int) -> bool:
        """Identify Marubozu pattern (strong momentum)"""
        upper_wick = CandlestickAnalyzer.get_upper_wick(data, index)
        lower_wick = CandlestickAnalyzer.get_lower_wick(data, index)
        
        # Candle with little or no wicks
        return upper_wick < 1e-6 and lower_wick < 1e-6
    
    @staticmethod
    def is_harami(data: pd.DataFrame, index: int) -> bool:
        """Identify Harami pattern (reversal)"""
        if index < 1:
            return False
        
        prev_body = CandlestickAnalyzer.get_body_size(data, index - 1)
        curr_body = CandlestickAnalyzer.get_body_size(data, index)
        
        # Current candle body inside previous candle's body
        prev_high = max(data['Open'].iloc[index - 1], data['Close'].iloc[index - 1])
        prev_low = min(data['Open'].iloc[index - 1], data['Close'].iloc[index - 1])
        
        curr_high = max(data['Open'].iloc[index], data['Close'].iloc[index])
        curr_low = min(data['Open'].iloc[index], data['Close'].iloc[index])
        
        return (curr_body < prev_body and
                curr_high < prev_high and
                curr_low > prev_low)
    
    @staticmethod
    def is_piercing_line(data: pd.DataFrame, index: int) -> bool:
        """Identify Piercing Line pattern (bullish reversal)"""
        if index < 1:
            return False
        
        # Previous bearish, current bullish
        if not CandlestickAnalyzer.is_bearish(data, index - 1):
            return False
        if not CandlestickAnalyzer.is_bullish(data, index):
            return False
        
        # Current opens below previous close, closes above 50% of previous body
        prev_body_mid = (data['Open'].iloc[index - 1] + data['Close'].iloc[index - 1]) / 2
        
        return (data['Open'].iloc[index] < data['Close'].iloc[index - 1] and
                data['Close'].iloc[index] > prev_body_mid)
    
    @staticmethod
    def is_dark_cloud_cover(data: pd.DataFrame, index: int) -> bool:
        """Identify Dark Cloud Cover pattern (bearish reversal)"""
        if index < 1:
            return False
        
        # Previous bullish, current bearish
        if not CandlestickAnalyzer.is_bullish(data, index - 1):
            return False
        if not CandlestickAnalyzer.is_bearish(data, index):
            return False
        
        # Current opens above previous close, closes below 50% of previous body
        prev_body_mid = (data['Open'].iloc[index - 1] + data['Close'].iloc[index - 1]) / 2
        
        return (data['Open'].iloc[index] > data['Close'].iloc[index - 1] and
                data['Close'].iloc[index] < prev_body_mid)
    
    @staticmethod
    def analyze_patterns(data: pd.DataFrame, patterns: List[str] = None) -> pd.DataFrame:
        """
        Analyze all candlestick patterns
        
        Args:
            data: DataFrame with OHLCV data
            patterns: List of patterns to analyze
        
        Returns:
            DataFrame with pattern columns
        """
        
        if patterns is None:
            patterns = [
                "hammer", "hanging_man", "bullish_engulfing", "bearish_engulfing",
                "morning_star", "evening_star", "three_white_soldiers", "three_black_crows",
                "doji", "spinning_top", "marubozu", "harami", "piercing_line",
                "dark_cloud_cover"
            ]
        
        logger.info(f"Analyzing {len(patterns)} candlestick patterns...")
        
        for pattern in patterns:
            data[f"Pattern_{pattern}"] = False
        
        pattern_methods = {
            "hammer": CandlestickAnalyzer.is_hammer,
            "hanging_man": CandlestickAnalyzer.is_hanging_man,
            "bullish_engulfing": CandlestickAnalyzer.is_bullish_engulfing,
            "bearish_engulfing": CandlestickAnalyzer.is_bearish_engulfing,
            "morning_star": CandlestickAnalyzer.is_morning_star,
            "evening_star": CandlestickAnalyzer.is_evening_star,
            "three_white_soldiers": CandlestickAnalyzer.is_three_white_soldiers,
            "three_black_crows": CandlestickAnalyzer.is_three_black_crows,
            "doji": CandlestickAnalyzer.is_doji,
            "spinning_top": CandlestickAnalyzer.is_spinning_top,
            "marubozu": CandlestickAnalyzer.is_marubozu,
            "harami": CandlestickAnalyzer.is_harami,
            "piercing_line": CandlestickAnalyzer.is_piercing_line,
            "dark_cloud_cover": CandlestickAnalyzer.is_dark_cloud_cover,
        }
        
        for i in range(len(data)):
            for pattern in patterns:
                if pattern in pattern_methods:
                    try:
                        data.loc[data.index[i], f"Pattern_{pattern}"] = \
                            pattern_methods[pattern](data, i)
                    except Exception as e:
                        logger.warning(f"Error analyzing {pattern} at index {i}: {e}")
        
        logger.info("✓ Pattern analysis completed")
        return data
    
    @staticmethod
    def get_pattern_strength(data: pd.DataFrame, index: int) -> float:
        """Calculate pattern strength (0-1)"""
        bullish = CandlestickAnalyzer.is_bullish(data, index)
        total_range = CandlestickAnalyzer.get_total_range(data, index)
        if total_range == 0:
            body_ratio = 0
        else:
            body_ratio = CandlestickAnalyzer.get_body_size(data, index) / total_range
        vol_mean = data['Volume'].mean()
        volume_strength = 0 if vol_mean == 0 else min(data['Volume'].iloc[index] / vol_mean, 1.0)
        
        return (body_ratio * 0.5 + volume_strength * 0.5)
    
    @staticmethod
    def analyze_wicks(data: pd.DataFrame) -> pd.DataFrame:
        """Analyze wick patterns"""
        data['Upper_Wick'] = data.apply(
            lambda row: CandlestickAnalyzer.get_upper_wick(data, data.index.get_loc(row.name)),
            axis=1
        )
        data['Lower_Wick'] = data.apply(
            lambda row: CandlestickAnalyzer.get_lower_wick(data, data.index.get_loc(row.name)),
            axis=1
        )
        data['Body_Size'] = abs(data['Close'] - data['Open'])
        data['Total_Range'] = data['High'] - data['Low']
        data['Wick_Ratio'] = (data['Upper_Wick'] + data['Lower_Wick']) / data['Total_Range'].replace(0, np.nan)
        data['Wick_Ratio'] = data['Wick_Ratio'].fillna(0)
        
        return data


if __name__ == "__main__":
    import yaml
    from data_fetcher import DataFetcher
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d')
    df = fetcher.prepare_data(df)
    
    analyzer = CandlestickAnalyzer()
    df = analyzer.analyze_patterns(df)
    df = analyzer.analyze_wicks(df)
    
    print(df[['Close', 'Pattern_hammer', 'Pattern_doji', 'Upper_Wick', 'Lower_Wick']].tail(20))
