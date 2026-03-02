"""
Data Fetcher Module for XAUUSD Analysis
Fetches historical and real-time data from multiple sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import os
import pickle
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch XAUUSD data from various sources"""
    
    def __init__(self, config: Dict):
        """Initialize data fetcher with configuration"""
        self.config = config
        self.symbol = config.get('data', {}).get('symbol', 'GC=F')
        
        # Use absolute path for cache directory
        cache_dir = config.get('data', {}).get('cache_dir', 'data/cache')
        if not Path(cache_dir).is_absolute():
            # Make it relative to project root
            from pathlib import Path as PathlibPath
            cache_dir = PathlibPath(__file__).parent.parent / cache_dir
        
        self.cache_dir = Path(cache_dir)
        self.cache_enabled = config.get('data', {}).get('cache_data', True)
        
        # Create cache directory if it doesn't exist
        if self.cache_enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Failed to create cache directory: {e}")
                self.cache_enabled = False
    
    def fetch_yfinance_data(self, 
                           symbol: str = None,
                           start_date: str = None,
                           end_date: str = None,
                           interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        Fetch data from Yahoo Finance
        
        Args:
            symbol: Trading symbol (default: GC=F for Gold Futures)
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            interval: Interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        symbol = symbol or self.symbol
        
        # Get dates from config if not provided
        config_data = self.config.get('data', {})
        start_date = start_date or config_data.get('start_date', '2020-01-01')
        end_date = end_date or config_data.get('end_date')
        
        cache_file = self._get_cache_file(symbol, start_date, end_date, interval)
        
        # Check cache first
        if self.cache_enabled and cache_file.exists():
            try:
                logger.info(f"Loading cached data from {cache_file.name}")
                df = pd.read_csv(cache_file, index_col='Date', parse_dates=True)
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        try:
            logger.info(f"Fetching {symbol} data from Yahoo Finance ({interval})")
            
            # Retry mechanism for network issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    df = yf.download(symbol, 
                                    start=start_date, 
                                    end=end_date,
                                    interval=interval,
                                    progress=False)
                    
                    if df is not None and not df.empty:
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        continue
                    else:
                        raise
            
            if df is None or df.empty:
                logger.error(f"No data fetched for {symbol}")
                return None
            
            # Ensure proper column names
            if len(df.columns) >= 5:
                df.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'][:len(df.columns)]
            
            # Remove duplicate index
            df = df[~df.index.duplicated(keep='first')]
            
            # Cache the data
            if self.cache_enabled:
                try:
                    df.to_csv(cache_file)
                    logger.info(f"Data cached to {cache_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to cache data: {e}")
            
            logger.info(f"✓ Successfully fetched {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def fetch_multiple_timeframes(self, 
                                 symbol: str = None,
                                 start_date: str = None,
                                 end_date: str = None,
                                 timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            timeframes: List of timeframes to fetch
        
        Returns:
            Dictionary with DataFrames for each timeframe
        """
        timeframes = timeframes or self.config.get('data', {}).get('timeframes', ['1d', '4h', '1h'])
        data = {}
        
        for tf in timeframes:
            logger.info(f"Fetching data for timeframe: {tf}")
            df = self.fetch_yfinance_data(symbol, start_date, end_date, tf)
            if df is not None:
                data[tf] = df
        
        return data
    
    def fetch_realtime_data(self, symbol: str = None) -> Optional[pd.Series]:
        """
        Fetch current/realtime data
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Series with current OHLCV data
        """
        symbol = symbol or self.symbol
        
        try:
            logger.info(f"Fetching realtime data for {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.info
            
            current_data = pd.Series({
                'Open': data.get('open'),
                'High': data.get('dayHigh'),
                'Low': data.get('dayLow'),
                'Close': data.get('currentPrice'),
                'Volume': data.get('volume'),
                'Timestamp': datetime.now()
            })
            
            return current_data
            
        except Exception as e:
            logger.error(f"Error fetching realtime data: {e}")
            return None
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns from price data
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with returns columns
        """
        df['Daily_Return'] = df['Close'].pct_change()
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        df['High_Low_Range'] = (df['High'] - df['Low']) / df['Close']
        df['Close_Open_Range'] = (df['Close'] - df['Open']) / df['Close']
        
        return df
    
    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features
        
        Args:
            df: DataFrame with DateTime index
        
        Returns:
            DataFrame with time features
        """
        df['Year'] = df.index.year
        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['DayOfWeek'] = df.index.dayofweek
        df['Hour'] = df.index.hour if hasattr(df.index, 'hour') else 0
        df['Quarter'] = df.index.quarter
        df['Week'] = df.index.isocalendar().week
        
        # Market session (assuming UTC)
        df['Is_NYSE_Session'] = ((df['Hour'] >= 13) & (df['Hour'] < 21)).astype(int)
        df['Is_European_Session'] = ((df['Hour'] >= 7) & (df['Hour'] < 16)).astype(int)
        df['Is_Asian_Session'] = ((df['Hour'] >= 0) & (df['Hour'] < 9)).astype(int)
        
        return df
    
    def resample_data(self, df: pd.DataFrame, target_interval: str) -> pd.DataFrame:
        """
        Resample data to target timeframe
        
        Args:
            df: DataFrame with intraday data
            target_interval: Target interval (e.g., '4h', '1d')
        
        Returns:
            Resampled DataFrame
        """
        resampled = df.resample(target_interval).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
        
        # Remove NaN rows
        resampled = resampled.dropna()
        
        return resampled
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data
        
        Args:
            df: Raw DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Remove rows with missing OHLCV data
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Ensure High >= Low
        df.loc[df['High'] < df['Low'], ['High', 'Low']] = df.loc[df['High'] < df['Low'], ['Low', 'High']].values
        
        # Ensure High >= Open, Close and Low <= Open, Close
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
        
        # Remove outliers (more than 10% price change in one period)
        df['Price_Change'] = abs(df['Close'].pct_change())
        df = df[df['Price_Change'] < 0.10].copy()
        df.drop('Price_Change', axis=1, inplace=True)
        
        logger.info(f"Data cleaned. Final shape: {df.shape}")
        
        return df
    
    def prepare_data(self, df: pd.DataFrame, add_features: bool = True) -> pd.DataFrame:
        """
        Prepare data for analysis
        
        Args:
            df: Raw DataFrame
            add_features: Whether to add time features
        
        Returns:
            Prepared DataFrame
        """
        # Clean data
        df = self.clean_data(df)
        
        # Calculate returns
        df = self.calculate_returns(df)
        
        # Add time features
        if add_features:
            df = self.add_time_features(df)
        
        # Sort by date
        df = df.sort_index()
        
        return df
    
    def save_data_to_csv(self, df: pd.DataFrame, filepath: str):
        """Save data to CSV"""
        df.to_csv(filepath)
        logger.info(f"Data saved to {filepath}")
    
    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """Load data from CSV"""
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        logger.info(f"Data loaded from {filepath}")
        return df
    
    def _get_cache_file(self, symbol: str, start_date: str, end_date: str, interval: str) -> Path:
        """Generate cache filename"""
        filename = f"{symbol}_{start_date}_{end_date}_{interval}.csv"
        return self.cache_dir / filename
    
    def get_latest_data(self, df: pd.DataFrame, num_periods: int = 1) -> pd.DataFrame:
        """Get latest N periods of data"""
        return df.tail(num_periods)
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate data integrity"""
        if df.empty:
            logger.error("DataFrame is empty")
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns. Got: {df.columns.tolist()}")
            return False
        
        if df.isna().sum().sum() > 0:
            logger.warning(f"Found NaN values: {df.isna().sum()}")
        
        logger.info("Data validation passed")
        return True


if __name__ == "__main__":
    # Test data fetcher
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    
    # Fetch data
    df = fetcher.fetch_yfinance_data(interval='1d')
    
    # Prepare data
    df = fetcher.prepare_data(df)
    
    # Validate
    fetcher.validate_data(df)
    
    print(df.head())
    print(df.info())
