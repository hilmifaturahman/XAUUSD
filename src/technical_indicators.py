"""
Technical Indicators Module for XAUUSD Analysis
Implements comprehensive technical analysis indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for trading analysis"""
    
    @staticmethod
    def _safe_divide(numerator, denominator):
        """Return numerator / denominator handling zeros and infinities."""
        result = numerator / denominator
        result = result.replace([np.inf, -np.inf], np.nan)
        return result

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20, column: str = 'Close') -> pd.Series:
        """Simple Moving Average"""
        return data[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 20, column: str = 'Close') -> pd.Series:
        """Exponential Moving Average"""
        return data[column].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_wma(data: pd.DataFrame, period: int = 20, column: str = 'Close') -> pd.Series:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        wma = data[column].rolling(period).apply(
            lambda x: np.sum(x * weights) / np.sum(weights), raw=False
        )
        return wma
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14, column: str = 'Close') -> pd.Series:
        """Relative Strength Index (RSI)"""
        delta = data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # avoid division by zero: if loss is zero RS should be large (RSI ->100)
        rs = TechnicalIndicators._safe_divide(gain, loss)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(method='ffill').fillna(0)
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, 
                      fast: int = 12, 
                      slow: int = 26, 
                      signal: int = 9,
                      column: str = 'Close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = data[column].ewm(span=fast, adjust=False).mean()
        ema_slow = data[column].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, 
                                 period: int = 20, 
                                 std_dev: float = 2,
                                 column: str = 'Close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = data[column].rolling(window=period).mean()
        std = data[column].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_stochastic(data: pd.DataFrame, 
                            k_period: int = 14, 
                            d_period: int = 3,
                            smooth_k: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Stochastic Oscillator"""
        low_min = data['Low'].rolling(window=k_period).min()
        high_max = data['High'].rolling(window=k_period).max()
        
        # avoid zero division when high_max == low_min
        denominator = (high_max - low_min).replace(0, np.nan)
        k_raw = 100 * (data['Close'] - low_min) / denominator
        k_percent = k_raw.rolling(window=smooth_k).mean()
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent.fillna(method='ffill'), d_percent.fillna(method='ffill')
    
    @staticmethod
    def calculate_adx(data: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Average Directional Index (ADX)"""
        high_diff = data['High'].diff()
        low_diff = -data['Low'].diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        tr = TechnicalIndicators.calculate_atr(data, period)
        
        # ensure Series align to index
        plus_di = 100 * pd.Series(plus_dm, index=data.index).rolling(period).mean()
        minus_di = 100 * pd.Series(minus_dm, index=data.index).rolling(period).mean()
        plus_di = TechnicalIndicators._safe_divide(plus_di, tr)
        minus_di = TechnicalIndicators._safe_divide(minus_di, tr)
        
        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        dx = TechnicalIndicators._safe_divide(100 * di_diff, di_sum)
        adx = dx.rolling(period).mean()
        
        return plus_di.fillna(0), minus_di.fillna(0), adx.fillna(0)
    
    @staticmethod
    def calculate_obv(data: pd.DataFrame) -> pd.Series:
        """On Balance Volume"""
        obv = pd.Series(0, index=data.index)
        obv.iloc[0] = data['Volume'].iloc[0]
        
        for i in range(1, len(data)):
            if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + data['Volume'].iloc[i]
            elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - data['Volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def calculate_ad_line(data: pd.DataFrame) -> pd.Series:
        """Accumulation/Distribution Line"""
        clv = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
        clv = clv.replace([np.inf, -np.inf], 0).fillna(0)
        
        ad = clv * data['Volume']
        ad_line = ad.cumsum()
        
        return ad_line
    
    @staticmethod
    def calculate_vpt(data: pd.DataFrame) -> pd.Series:
        """Volume Price Trend"""
        returns = data['Close'].pct_change()
        vpt = (returns * data['Volume']).cumsum()
        
        return vpt
    
    @staticmethod
    def calculate_keltner_channels(data: pd.DataFrame, 
                                  period: int = 20,
                                  atr_multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Keltner Channels"""
        ema = data['Close'].ewm(span=period, adjust=False).mean()
        atr = TechnicalIndicators.calculate_atr(data, period)
        
        upper_band = ema + (atr * atr_multiplier)
        lower_band = ema - (atr * atr_multiplier)
        
        return upper_band, ema, lower_band
    
    @staticmethod
    def calculate_parabolic_sar(data: pd.DataFrame, 
                               af_start: float = 0.02,
                               af_max: float = 0.2) -> pd.Series:
        """Parabolic SAR"""
        length = len(data)
        sar = data['Close'].copy()
        af = af_start
        hp = data['High'].iloc[0]
        lp = data['Low'].iloc[0]
        bull = True
        
        for i in range(2, length):
            if bull:
                sar.iloc[i] = sar.iloc[i-1] + af * (hp - sar.iloc[i-1])
                sar.iloc[i] = min(sar.iloc[i], data['Low'].iloc[i-1], data['Low'].iloc[i-2])
                
                if data['High'].iloc[i] > hp:
                    hp = data['High'].iloc[i]
                    af = min(af + af_start, af_max)
                
                if data['Low'].iloc[i] < sar.iloc[i]:
                    bull = False
                    sar.iloc[i] = hp
                    lp = data['Low'].iloc[i]
                    af = af_start
            else:
                sar.iloc[i] = sar.iloc[i-1] - af * (sar.iloc[i-1] - lp)
                sar.iloc[i] = max(sar.iloc[i], data['High'].iloc[i-1], data['High'].iloc[i-2])
                
                if data['Low'].iloc[i] < lp:
                    lp = data['Low'].iloc[i]
                    af = min(af + af_start, af_max)
                
                if data['High'].iloc[i] > sar.iloc[i]:
                    bull = True
                    sar.iloc[i] = lp
                    hp = data['High'].iloc[i]
                    af = af_start
        
        return sar
    
    @staticmethod
    def calculate_atr_bands(data: pd.DataFrame, 
                           atr_multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """ATR-based Bands (Price + ATR * Multiplier)"""
        atr = TechnicalIndicators.calculate_atr(data)
        
        upper_band = data['Close'] + (atr * atr_multiplier)
        lower_band = data['Close'] - (atr * atr_multiplier)
        
        return upper_band, data['Close'], lower_band
    
    @staticmethod
    def calculate_roc(data: pd.DataFrame, period: int = 12, column: str = 'Close') -> pd.Series:
        """Rate of Change"""
        roc = ((data[column] - data[column].shift(period)) / data[column].shift(period)) * 100
        roc = roc.replace([np.inf, -np.inf], np.nan)
        return roc.fillna(0)
    
    @staticmethod
    def calculate_cci(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Commodity Channel Index"""
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (tp - sma_tp) / (0.015 * mad)
        
        return cci
    
    @staticmethod
    def calculate_williams_r(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Williams %R"""
        high_high = data['High'].rolling(window=period).max()
        low_low = data['Low'].rolling(window=period).min()
        
        wr = -100 * (high_high - data['Close']) / (high_high - low_low)
        
        return wr
    
    @staticmethod
    def calculate_mfi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Money Flow Index"""
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        pmf = tp * data['Volume']
        
        positive_mf = pd.Series(0, index=data.index)
        negative_mf = pd.Series(0, index=data.index)
        
        for i in range(1, len(data)):
            if tp.iloc[i] > tp.iloc[i-1]:
                positive_mf.iloc[i] = pmf.iloc[i]
            else:
                negative_mf.iloc[i] = pmf.iloc[i]
        
        pmf_sum_pos = positive_mf.rolling(window=period).sum()
        pmf_sum_neg = negative_mf.rolling(window=period).sum()
        
        denom = pmf_sum_pos + pmf_sum_neg
        mfi = TechnicalIndicators._safe_divide(100 * pmf_sum_pos, denom)
        return mfi.fillna(0)
    
    @staticmethod
    def add_all_indicators(data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Add all configured indicators to dataframe"""
        
        indicator_config = config.get('indicators', {})
        
        logger.info("Calculating all technical indicators...")
        
        # Moving Averages
        ma_config = indicator_config.get('moving_averages', {})
        if ma_config.get('enabled', True):
            data['SMA_10'] = TechnicalIndicators.calculate_sma(data, 10)
            data['SMA_20'] = TechnicalIndicators.calculate_sma(data, 20)
            data['SMA_50'] = TechnicalIndicators.calculate_sma(data, 50)
            data['SMA_200'] = TechnicalIndicators.calculate_sma(data, 200)
            
            data['EMA_10'] = TechnicalIndicators.calculate_ema(data, 10)
            data['EMA_20'] = TechnicalIndicators.calculate_ema(data, 20)
            data['EMA_50'] = TechnicalIndicators.calculate_ema(data, 50)
            data['EMA_200'] = TechnicalIndicators.calculate_ema(data, 200)
            
            logger.info("✓ Moving averages calculated")
        
        # Momentum
        momentum_config = indicator_config.get('momentum', {})
        
        if momentum_config.get('rsi', {}).get('enabled', True):
            data['RSI_14'] = TechnicalIndicators.calculate_rsi(data, 14)
            data['RSI_21'] = TechnicalIndicators.calculate_rsi(data, 21)
            logger.info("✓ RSI calculated")
        
        if momentum_config.get('macd', {}).get('enabled', True):
            data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = \
                TechnicalIndicators.calculate_macd(data, 12, 26, 9)
            logger.info("✓ MACD calculated")
        
        if momentum_config.get('stochastic', {}).get('enabled', True):
            data['Stoch_K'], data['Stoch_D'] = TechnicalIndicators.calculate_stochastic(data, 14, 3, 3)
            logger.info("✓ Stochastic calculated")
        
        if momentum_config.get('atr', {}).get('enabled', True):
            data['ATR'] = TechnicalIndicators.calculate_atr(data, 14)
            logger.info("✓ ATR calculated")
        
        # Volume
        volume_config = indicator_config.get('volume', {})
        if volume_config.get('enabled', True):
            if volume_config.get('obv', True):
                data['OBV'] = TechnicalIndicators.calculate_obv(data)
            if volume_config.get('ad_line', True):
                data['AD_Line'] = TechnicalIndicators.calculate_ad_line(data)
            if volume_config.get('vpt', True):
                data['VPT'] = TechnicalIndicators.calculate_vpt(data)
            if volume_config.get('mfi', True):
                data['MFI'] = TechnicalIndicators.calculate_mfi(data, 14)
            logger.info("✓ Volume indicators calculated")
        
        # Volatility
        vol_config = indicator_config.get('volatility', {})
        if vol_config.get('bollinger_bands', {}).get('enabled', True):
            data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = \
                TechnicalIndicators.calculate_bollinger_bands(data, 20, 2)
            logger.info("✓ Bollinger Bands calculated")
        
        if vol_config.get('keltner_channels', {}).get('enabled', True):
            data['KC_Upper'], data['KC_Middle'], data['KC_Lower'] = \
                TechnicalIndicators.calculate_keltner_channels(data, 20, 2.0)
            logger.info("✓ Keltner Channels calculated")
        
        # Trend
        trend_config = indicator_config.get('trend', {})
        if trend_config.get('adx', {}).get('enabled', True):
            data['Plus_DI'], data['Minus_DI'], data['ADX'] = \
                TechnicalIndicators.calculate_adx(data, 14)
            logger.info("✓ ADX calculated")
        
        if trend_config.get('parabolic_sar', {}).get('enabled', True):
            data['SAR'] = TechnicalIndicators.calculate_parabolic_sar(data, 0.02, 0.2)
            logger.info("✓ Parabolic SAR calculated")
        
        # create copy to avoid SettingWithCopy warnings
        data = data.copy()

        # Additional indicators
        data['ROC'] = TechnicalIndicators.calculate_roc(data, 12)
        data['CCI'] = TechnicalIndicators.calculate_cci(data, 20)
        data['Williams_R'] = TechnicalIndicators.calculate_williams_r(data, 14)
        
        logger.info("✓ All indicators calculated successfully")
        
        return data


if __name__ == "__main__":
    import yaml
    from data_fetcher import DataFetcher
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d')
    df = fetcher.prepare_data(df)
    
    df = TechnicalIndicators.add_all_indicators(df, config)
    
    print(df.tail())
    print(df.columns.tolist())
