# XAUUSD Market Analysis System

Advanced XAUUSD (Gold/US Dollar) trading analysis platform dengan backtesting, strategi otomatis, dan analisis fundamental lengkap.

## 🎯 Fitur Utama

### 1. **Data Collection & Management**
- Fetch real-time data dari Yahoo Finance
- Support multiple timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo)
- Built-in caching system untuk performance
- Data cleaning dan validation

### 2. **Technical Analysis**
Indikator teknikal lengkap:
- **Moving Averages**: SMA, EMA, WMA
- **Momentum**: RSI, MACD, Stochastic, CCI, Williams %R
- **Volatility**: Bollinger Bands, Keltner Channels, ATR
- **Trend**: ADX, Parabolic SAR, Plus/Minus DI
- **Volume**: OBV, Accumulation/Distribution, Volume Price Trend, Money Flow Index

### 3. **Candlestick Pattern Recognition**
14 pola candlestick yang diidentifikasi:
- Hammer, Hanging Man
- Bullish/Bearish Engulfing
- Morning Star, Evening Star
- Three White Soldiers, Three Black Crows
- Doji, Spinning Top
- Marubozu, Harami
- Piercing Line, Dark Cloud Cover

Deep wick dan body analysis untuk pattern strength assessment.

### 4. **Fundamental Analysis**
- Economic calendar monitoring
- News sentiment analysis
- USD Strength Index correlation
- Interest rates impact analysis
- Geopolitical risk assessment
- Inflation trends tracking
- Gold ETF flows analysis
- Multi-asset correlation matrix

### 5. **Multiple Trading Strategies**
Enam strategi trading yang berbeda:
1. **Trend Following** - EMA crossover dengan ADX confirmation
2. **Mean Reversion** - Bollinger Bands + RSI
3. **Breakout** - 20-period box breakout dengan volume
4. **Support/Resistance** - Level detection dan trading
5. **MACD Crossover** - MACD signal line crossing
6. **Combined Multi-Signal** - Weighted indicator combination

### 6. **Advanced Signal Generation**
- Confidence scoring system (0-100%)
- Multi-timeframe confirmation
- Technical + Fundamental integration
- Automatic noise filtering
- Risk-weighted signal generation

### 7. **Professional Backtesting**
Comprehensive performance metrics:
- Total return dan Sharpe ratio
- Win rate dan profit factor
- Max drawdown (absolute & percentage)
- Consecutive wins/losses
- Sortino ratio dan Calmar ratio
- Trade-by-trade analysis

### 8. **Interactive Visualization**
- Candlestick charts dengan indicators overlay
- Technical indicators subplots
- Trading signals visualization
- Backtest equity curve
- Drawdown analysis
- Returns distribution histogram
- Correlation heatmap
- HTML reports dengan interactive Plotly charts

## 📊 Project Structure

```
XAUUSD/
├── config/
│   └── config.yaml                 # Configuration file
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py             # Data collection module
│   ├── technical_indicators.py     # Technical analysis
│   ├── candlestick_analysis.py     # Pattern recognition
│   ├── fundamental_analysis.py     # News & economic data
│   ├── strategy.py                 # Trading strategies
│   ├── signals.py                  # Signal generation
│   ├── backtester.py               # Backtesting engine
│   └── visualizer.py               # Visualization module
├── data/                           # Data files (cached)
├── results/                        # Analysis results
│   └── plots/                      # Generated charts
├── logs/                           # Log files
├── notebooks/                      # Jupyter notebooks
└── main.py                         # Main execution file
```

## 🚀 Quick Start

### GUI Application
The project includes a simple graphical interface using `tkinter`. After installing dependencies, launch the GUI with:

```bash
python -m src.gui
```

The window provides fields for symbol and date range; results are logged and a chart is saved to `results/plots`.

## 🚀 Quick Start

### Installation

1. **Clone repository**
```bash
git clone https://github.com/hilmifaturahman/XAUUSD.git
cd XAUUSD
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Analysis

1. **Basic analysis dengan default config**
```bash
python main.py
```

2. **Custom configuration**
Edit `config/config.yaml` sesuai kebutuhan, kemudian jalankan:
```bash
python main.py
```

## 📈 Configuration

### Config Parameters (config/config.yaml)

**Data Collection**
```yaml
data:
  symbol: "GC=F"              # Gold futures symbol
  start_date: "2020-01-01"
  timeframes: ["1d", "4h", "1h"]
  cache_data: true
```

**Technical Indicators**
```yaml
indicators:
  moving_averages:
    enabled: true
    fast_period: 10
    medium_period: 20
    slow_period: 50
```

**Backtesting**
```yaml
backtest:
  initial_capital: 10000
  commission: 0.001          # 0.1% per trade
  slippage: 0.0005           # 0.05%
  position_size: 0.95        # 95% of capital
```

**Strategies**
```yaml
strategy:
  types: ["trend_following", "mean_reversion", "breakout", "combined"]
```

## 📊 Usage Examples

### Contoh 1: Run Full Analysis
```python
from main import XAUUSDAnalysisSystem

system = XAUUSDAnalysisSystem()
system.run_full_analysis(
    interval='1d',
    strategy_types=['trend_following', 'combined'],
    start_date='2023-01-01'
)
```

### Contoh 2: Test Single Strategy
```python
from src.data_fetcher import DataFetcher
from src.technical_indicators import TechnicalIndicators
from src.strategy import create_strategy
from src.backtester import BacktestEngine
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Fetch and prepare data
fetcher = DataFetcher(config)
df = fetcher.fetch_yfinance_data(interval='1d', start_date='2023-01-01')
df = fetcher.prepare_data(df)

# Add indicators
df = TechnicalIndicators.add_all_indicators(df, config)

# Generate signals
strategy = create_strategy('trend_following', config)
df, meta = strategy.generate_signals(df)

# Backtest
backtester = BacktestEngine(config)
results = backtester.run_backtest(df, df, "Trend Following")
backtester.print_results(results)
```

### Contoh 3: Create Custom Strategy
```python
from src.strategy import TradingStrategy

class MyCustomStrategy(TradingStrategy):
    def generate_signals(self, data):
        data['Buy'] = data['RSI_14'] < 30
        data['Sell'] = data['RSI_14'] > 70
        
        metadata = {
            'strategy_name': 'My RSI Strategy',
            'buy_signals': data['Buy'].sum(),
            'sell_signals': data['Sell'].sum()
        }
        
        return data, metadata
```

## 📉 Analysis Output

Generated files dalam folder `results/`:

1. **candlestick_chart.html** - Interactive candlestick chart dengan indicators
2. **indicators_chart.html** - Technical indicators (RSI, MACD, ADX)
3. **signals_chart.html** - Trading signals overlay pada harga
4. **backtest_results.html** - Equity curve & drawdown analysis
5. **returns_distribution.html** - Daily returns histogram
6. **correlation_heatmap.html** - Indicator correlation matrix
7. **report_summary.html** - Executive summary
8. **analysis_results.json** - Detailed numeric results

## 🎓 Key Metrics Explained

### Performance Metrics
- **Total Return**: Total profit dalam persentase
- **Win Rate**: % trades yang menguntungkan
- **Profit Factor**: Gross profit / Gross loss
- **Max Drawdown**: Penurunan terbesar dari peak
- **Sharpe Ratio**: Risk-adjusted return (>1 bagus)
- **Sortino Ratio**: Downside risk-adjusted return
- **Calmar Ratio**: Return / Max Drawdown ratio

### Signal Strength
- **Confidence Score**: 0-100%, berdasarkan multiple indicators
- **Required Confirmations**: Minimal 3 indicators untuk signal
- **Fundamental Integration**: Scoring fundamental analysis in signals

## 🔧 Advanced Features

### Multi-Timeframe Analysis
Analisis pada multiple timeframes simultaneously untuk confirmation:
```python
timeframes_data = fetcher.fetch_multiple_timeframes(
    symbol='GC=F',
    timeframes=['1h', '4h', '1d']
)
```

### Risk Management
- Automatic position sizing (Kelly Criterion atau fixed)
- Stop-loss dan take-profit calculation
- Trailing stop support
- Daily loss limits
- Maximum drawdown enforcement

### News & Sentiment
- Economic calendar monitoring
- News sentiment analysis (positive/negative/neutral)
- Geopolitical risk scoring
- Real-time fundamental data integration

## 📚 Dependencies

Key libraries:
- **yfinance** - Data fetching
- **pandas/numpy** - Data processing
- **plotly/matplotlib** - Visualization
- **scikit-learn** - Machine learning
- **ta-lib** - Technical analysis
- **TensorFlow** - Deep learning (optional)

Full list: `requirements.txt`

## 🤝 Contributing

Kontribusi welcome! Areas untuk improvement:
- Machine learning / Deep learning strategies
- Real-time trading bot integration
- Additional fundamental data sources
- More pattern recognition algorithms
- Mobile app interface

## 📝 License

MIT License - Feel free to use in personal/commercial projects

## ⚠️ Disclaimer

Sistem ini untuk **educational purposes** saja. Bukan financial advice.
Always do your own research sebelum trading real money.

## 🔗 Resources

- [TradingView Documentation](https://www.tradingview.com/)
- [Yahoo Finance API](https://finance.yahoo.com/)
- [Technical Analysis Guide](https://www.investopedia.com/)
- [Gold Market Fundamentals](https://www.kitco.com/)

## 📧 Contact

Author: Hilmi Faturahman
GitHub: https://github.com/hilmifaturahman
Email: contact@example.com

---

**Last Updated**: March 2, 2026
**Version**: 1.0.0
