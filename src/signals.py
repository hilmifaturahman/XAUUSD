"""
Signal Generation Module for XAUUSD
Combines technical analysis with fundamental analysis for robust signals
"""

import sys
from pathlib import Path

# ensure imports from project root when running directly
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generate trading signals with confidence scoring"""
    
    def __init__(self, config: Dict):
        """Initialize signal generator"""
        self.config = config
        self.signals_config = config.get('signals', {})
        self.min_confidence = self.signals_config.get('min_confidence', 0.65)
        self.required_confirmations = self.signals_config.get('required_confirmations', 3)
    
    def generate_buy_signal(self,
                           data: pd.DataFrame,
                           fundamental_score: float,
                           technical_signals: Dict,
                           index: int) -> Tuple[bool, float]:
        """
        Generate buy signal with confidence score
        
        Args:
            data: OHLCV DataFrame
            fundamental_score: Fundamental analysis score (-1 to 1)
            technical_signals: Dictionary with technical signal flags
            index: Current index
        
        Returns:
            (signal_triggered, confidence_score)
        """
        
        confidence = 0.0
        signal_count = 0
        
        # Moving Average Crossover (25% weight)
        if technical_signals.get('ma_bullish_cross', False):
            confidence += 0.25
            signal_count += 1
        
        # RSI Oversold (25% weight)
        if technical_signals.get('rsi_oversold', False):
            confidence += 0.25
            signal_count += 1
        
        # MACD Bullish (25% weight)
        if technical_signals.get('macd_bullish_cross', False):
            confidence += 0.25
            signal_count += 1
        
        # Candlestick Pattern (15% weight)
        if technical_signals.get('bullish_pattern', False):
            confidence += 0.15
            signal_count += 1
        
        # Support Level (10% weight)
        if technical_signals.get('at_support', False):
            confidence += 0.10
            signal_count += 1
        
        # Fundamental Analysis (applied to confidence)
        if fundamental_score > 0.2:
            confidence *= (1 + (fundamental_score * 0.2))
        
        # Normalize confidence
        max_possible = 1.0
        confidence = min(confidence / max_possible, 1.0)
        
        # Signal triggered if meets minimum confidence
        signal_triggered = (confidence >= self.min_confidence and 
                           signal_count >= self.required_confirmations)
        
        return signal_triggered, confidence
    
    def generate_sell_signal(self,
                            data: pd.DataFrame,
                            fundamental_score: float,
                            technical_signals: Dict,
                            index: int) -> Tuple[bool, float]:
        """Generate sell signal with confidence score"""
        
        confidence = 0.0
        signal_count = 0
        
        # Moving Average Bearish Cross (25% weight)
        if technical_signals.get('ma_bearish_cross', False):
            confidence += 0.25
            signal_count += 1
        
        # RSI Overbought (25% weight)
        if technical_signals.get('rsi_overbought', False):
            confidence += 0.25
            signal_count += 1
        
        # MACD Bearish (25% weight)
        if technical_signals.get('macd_bearish_cross', False):
            confidence += 0.25
            signal_count += 1
        
        # Candlestick Pattern (15% weight)
        if technical_signals.get('bearish_pattern', False):
            confidence += 0.15
            signal_count += 1
        
        # Resistance Level (10% weight)
        if technical_signals.get('at_resistance', False):
            confidence += 0.10
            signal_count += 1
        
        # Fundamental Analysis
        if fundamental_score < -0.2:
            confidence *= (1 + (abs(fundamental_score) * 0.2))
        
        # Normalize confidence
        max_possible = 1.0
        confidence = min(confidence / max_possible, 1.0)
        
        signal_triggered = (confidence >= self.min_confidence and 
                           signal_count >= self.required_confirmations)
        
        return signal_triggered, confidence
    
    def extract_technical_signals(self, data: pd.DataFrame, index: int) -> Dict[str, bool]:
        """Extract technical signal flags at given index"""
        
        signals = {}
        
        if index < 2 or pd.isna(data).any().any():
            return signals
        
        try:
            close = data['Close'].iloc[index]
            
            # Moving Average Signals
            if 'EMA_10' in data.columns and 'EMA_50' in data.columns:
                ema_10 = data['EMA_10'].iloc[index]
                ema_50 = data['EMA_50'].iloc[index]
                
                signals['ma_bullish_cross'] = (
                    (ema_10 > ema_50) and 
                    (data['EMA_10'].iloc[index-1] <= data['EMA_50'].iloc[index-1])
                )
                
                signals['ma_bearish_cross'] = (
                    (ema_10 < ema_50) and 
                    (data['EMA_10'].iloc[index-1] >= data['EMA_50'].iloc[index-1])
                )
            
            # RSI Signals
            if 'RSI_14' in data.columns:
                rsi = data['RSI_14'].iloc[index]
                signals['rsi_oversold'] = rsi < 30
                signals['rsi_overbought'] = rsi > 70
            
            # MACD Signals
            if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
                signals['macd_bullish_cross'] = (
                    (data['MACD'].iloc[index] > data['MACD_Signal'].iloc[index]) and
                    (data['MACD'].iloc[index-1] <= data['MACD_Signal'].iloc[index-1])
                )
                
                signals['macd_bearish_cross'] = (
                    (data['MACD'].iloc[index] < data['MACD_Signal'].iloc[index]) and
                    (data['MACD'].iloc[index-1] >= data['MACD_Signal'].iloc[index-1])
                )
            
            # Candlestick Patterns
            bullish_patterns = [
                'Pattern_hammer', 'Pattern_bullish_engulfing',
                'Pattern_morning_star', 'Pattern_three_white_soldiers'
            ]
            bearish_patterns = [
                'Pattern_hanging_man', 'Pattern_bearish_engulfing',
                'Pattern_evening_star', 'Pattern_three_black_crows'
            ]
            
            # safer pattern check: only access if column exists and index valid
            bullish_flag = False
            for pat in bullish_patterns:
                if pat in data.columns:
                    try:
                        if data[pat].iloc[index]:
                            bullish_flag = True
                            break
                    except Exception:
                        pass
            signals['bullish_pattern'] = bullish_flag
            
            bearish_flag = False
            for pat in bearish_patterns:
                if pat in data.columns:
                    try:
                        if data[pat].iloc[index]:
                            bearish_flag = True
                            break
                    except Exception:
                        pass
            signals['bearish_pattern'] = bearish_flag
            
            # Support/Resistance Signals
            if 'BB_Lower' in data.columns and 'BB_Upper' in data.columns:
                lower_band = data['BB_Lower'].iloc[index]
                upper_band = data['BB_Upper'].iloc[index]
                threshold = (upper_band - lower_band) * 0.05
                
                signals['at_support'] = close <= (lower_band + threshold)
                signals['at_resistance'] = close >= (upper_band - threshold)
            
            # Volatility Signal
            if 'ATR' in data.columns:
                atr = data['ATR'].iloc[index]
                avg_price = (data['High'].iloc[index] + data['Low'].iloc[index]) / 2
                volatility_pct = (atr / avg_price) * 100
                signals['high_volatility'] = volatility_pct > 2
        
        except Exception as e:
            logger.warning(f"Error extracting technical signals at index {index}: {e}")
        
        return signals
    
    def generate_signal_dataframe(self,
                                 data: pd.DataFrame,
                                 strategy_signals: pd.DataFrame,
                                 fundamental_scores: Optional[List[float]] = None) -> pd.DataFrame:
        """
        Generate comprehensive signal dataframe
        
        Args:
            data: OHLCV DataFrame
            strategy_signals: Buy/Sell signals from strategy
            fundamental_scores: Optional fundamental scores for each bar
        
        Returns:
            DataFrame with signal information
        """
        
        logger.info("Generating comprehensive signals...")
        
        signals_df = pd.DataFrame(index=data.index)
        signals_df['Close'] = data['Close']
        signals_df['Strategy_Buy'] = strategy_signals['Buy']
        signals_df['Strategy_Sell'] = strategy_signals['Sell']
        
        # Initialize signal columns
        signals_df['Buy_Signal'] = False
        signals_df['Sell_Signal'] = False
        signals_df['Buy_Confidence'] = 0.0
        signals_df['Sell_Confidence'] = 0.0
        
        # Use default fundamental scores if not provided
        if fundamental_scores is None:
            fundamental_scores = [0.0] * len(data)
        
        # Generate signals for each bar
        for i in range(2, len(data)):
            technical_sigs = self.extract_technical_signals(data, i)
            fund_score = fundamental_scores[i] if i < len(fundamental_scores) else 0.0
            
            # Generate buy signal
            buy_signal, buy_conf = self.generate_buy_signal(
                data, fund_score, technical_sigs, i
            )
            signals_df.loc[signals_df.index[i], 'Buy_Signal'] = buy_signal
            signals_df.loc[signals_df.index[i], 'Buy_Confidence'] = buy_conf
            
            # Generate sell signal
            sell_signal, sell_conf = self.generate_sell_signal(
                data, fund_score, technical_sigs, i
            )
            signals_df.loc[signals_df.index[i], 'Sell_Signal'] = sell_signal
            signals_df.loc[signals_df.index[i], 'Sell_Confidence'] = sell_conf
        
        logger.info(f"✓ Generated {signals_df['Buy_Signal'].sum()} buy signals")
        logger.info(f"✓ Generated {signals_df['Sell_Signal'].sum()} sell signals")
        
        return signals_df
    
    def filter_signals_by_timeframe(self,
                                   signals_df: pd.DataFrame,
                                   lookback_periods: int = 5) -> pd.DataFrame:
        """
        Filter signals to respect minimum distance between trades
        
        Args:
            signals_df: Signal DataFrame
            lookback_periods: Minimum bars between signals
        
        Returns:
            Filtered signal DataFrame
        """
        
        logger.info(f"Filtering signals (min {lookback_periods} bars between trades)...")
        
        buy_idx = signals_df[signals_df['Buy_Signal']].index
        sell_idx = signals_df[signals_df['Sell_Signal']].index
        
        # Remove signals that are too close together
        filtered_buys = []
        last_buy_idx = -lookback_periods
        
        for idx in buy_idx:
            position = signals_df.index.get_loc(idx)
            if position - last_buy_idx >= lookback_periods:
                filtered_buys.append(idx)
                last_buy_idx = position
        
        filtered_sells = []
        last_sell_idx = -lookback_periods
        
        for idx in sell_idx:
            position = signals_df.index.get_loc(idx)
            if position - last_sell_idx >= lookback_periods:
                filtered_sells.append(idx)
                last_sell_idx = position
        
        # Apply filters
        signals_df['Buy_Signal'] = signals_df.index.isin(filtered_buys)
        signals_df['Sell_Signal'] = signals_df.index.isin(filtered_sells)
        
        logger.info(f"✓ After filtering: {signals_df['Buy_Signal'].sum()} buy, "
                   f"{signals_df['Sell_Signal'].sum()} sell signals")
        
        return signals_df
    
    def print_signals_summary(self, signals_df: pd.DataFrame):
        """Print signal summary"""
        
        buy_count = signals_df['Buy_Signal'].sum()
        sell_count = signals_df['Sell_Signal'].sum()
        
        logger.info("\n" + "="*50)
        logger.info("SIGNAL SUMMARY")
        logger.info("="*50)
        logger.info(f"Total Buy Signals: {buy_count}")
        logger.info(f"Total Sell Signals: {sell_count}")
        
        if buy_count > 0:
            avg_buy_confidence = signals_df[signals_df['Buy_Signal']]['Buy_Confidence'].mean()
            logger.info(f"Average Buy Confidence: {avg_buy_confidence:.2%}")
        
        if sell_count > 0:
            avg_sell_confidence = signals_df[signals_df['Sell_Signal']]['Sell_Confidence'].mean()
            logger.info(f"Average Sell Confidence: {avg_sell_confidence:.2%}")
        
        logger.info("="*50 + "\n")


if __name__ == "__main__":
    import yaml
    from data_fetcher import DataFetcher
    from technical_indicators import TechnicalIndicators
    from candlestick_analysis import CandlestickAnalyzer
    from fundamental_analysis import FundamentalAnalyzer
    from strategy import create_strategy
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Prepare data
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d', start_date='2023-01-01')
    df = fetcher.prepare_data(df)
    
    # Add indicators
    df = TechnicalIndicators.add_all_indicators(df, config)
    df = CandlestickAnalyzer.analyze_patterns(df)
    
    # Get fundamental score
    fundamental = FundamentalAnalyzer(config)
    report = fundamental.generate_fundamental_report()
    fundamental_scores = [report['fundamental_score']] * len(df)
    
    # Generate strategy signals
    strategy = create_strategy('combined', config)
    df, metadata = strategy.generate_signals(df)
    
    # Generate final signals
    signal_gen = SignalGenerator(config)
    signals_df = signal_gen.generate_signal_dataframe(df, df, fundamental_scores)
    signals_df = signal_gen.filter_signals_by_timeframe(signals_df, 5)
    signal_gen.print_signals_summary(signals_df)
    
    print(signals_df[['Close', 'Buy_Signal', 'Buy_Confidence', 'Sell_Signal', 'Sell_Confidence']].tail(30))
