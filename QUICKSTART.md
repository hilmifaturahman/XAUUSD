# XAUUSD System - Quick Setup & Installation Guide

## 🚀 Step-by-Step Installation

### Prerequisites
- Python 3.8 or higher
- Git (untuk version control)
- ~2GB disk space untuk dependencies dan data cache

### Option 1: Automated Installation (Recommended for Beginners)

**Windows Users:**
1. Open Command Prompt or PowerShell
2. Navigate ke folder XAUUSD
3. Double-click `run_analysis.bat`
4. System akan otomatis:
   - Install Python dependencies
   - Set up virtual environment
   - Run analysis

**Linux/Mac Users:**
```bash
chmod +x run_analysis.sh
./run_analysis.sh
```

### Option 2: Manual Installation (For Advanced Users)

**1. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Run Analysis**
```bash
python main.py
```

---

## 📦 Key Dependencies Explained

### Data & Processing
- `yfinance` - Download market data dari Yahoo Finance
- `pandas` - DataFrame manipulation
- `numpy` - Numerical computations

### Technical Analysis
- `pandas-ta` - 200+ TA indicators
- `ta` - Technical analysis library
- `mplfinance` - Professional candlestick charting

### Visualization
- `plotly` - Interactive HTML charts
- `matplotlib` - Static & dynamic plots
- `seaborn` - Statistical visualization

### Machine Learning (Optional)
- `scikit-learn` - ML algorithms
- `tensorflow` - Deep learning
- `keras` - Neural networks

### Utilities
- `PyYAML` - Configuration file parsing
- `sqlalchemy` - Database operations
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping

---

## ⚙️ Configuration Guide

### Editing config/config.yaml

**1. Data Collection**
```yaml
data:
  symbol: "GC=F"              # Gold Futures = GC=F, Spot = XAUUSD
  start_date: "2023-01-01"    # Backtest start date
  end_date: null              # null = today
  timeframes: ["1d", "1h"]    # Frames to analyze
```

**2. Technical Indicators**
```yaml
indicators:
  moving_averages:
    enabled: true
    fast_period: 10            # 10-day MA
    slow_period: 50            # 50-day MA
  rsi:
    period: 14                 # Standard 14-period RSI
    overbought: 70             # RSI threshold
    oversold: 30
```

**3. Backtesting**
```yaml
backtest:
  initial_capital: 10000       # Starting capital
  commission: 0.001            # 0.1% per trade
  position_size: 0.95          # Use 95% of capital
  max_drawdown: 0.20           # 20% max allowed DD
```

**4. Strategies**
```yaml
strategy:
  types: ["combined", "trend_following"]
```

**5. Visualization**
```yaml
visualization:
  theme: "dark"                # dark atau light
  save_plots: true             # Save to HTML
  interactive_charts: true     # Plotly charts
```

---

## 🏃 Running Your First Analysis

### Quick Test (5 minutes)
```python
python main.py
```
Ini akan:
- Download 2 tahun data terakhir
- Calculate semua indicators
- Run 5 strategi
- Generate reports & charts

### Custom Analysis
Edit config.yaml untuk customize, kemudian:
```python
python main.py
```

### Testing Specific Strategy
```python
from src.data_fetcher import DataFetcher
from src.strategy import create_strategy
import yaml

config = yaml.safe_load(open('config/config.yaml'))
fetcher = DataFetcher(config)
data = fetcher.fetch_yfinance_data()

strategy = create_strategy('trend_following', config)
signals, meta = strategy.generate_signals(data)
print(meta)
```

---

## 📊 Output Files

Setelah analysis selesai, check folder `results/`:

```
results/
├── candlestick_chart.html        ← Open di browser
├── indicators_chart.html          ← Technical indicators
├── signals_chart.html             ← Trading signals
├── backtest_results.html          ← Equity curve
├── returns_distribution.html      ← Return histogram
├── correlation_heatmap.html       ← Indicator correlation
├── report_summary.html            ← Full report
└── analysis_results.json          ← Raw data (Python readable)
```

**Cara Lihat Results:**
- Open HTML files di web browser
- Interactive charts dengan zoom, hover
- Exportable sebagai image/data

---

## 🔌 Git & GitHub Setup

### Push ke GitHub

**Windows:**
1. Double-click `setup_github.bat`
2. Ikuti prompts
3. Repository akan push otomatis

**Linux/Mac:**
```bash
chmod +x setup_github.sh
./setup_github.sh
```

**Manual Setup:**
```bash
git init
git add .
git commit -m "Initial XAUUSD project"
git remote add origin https://github.com/hilmifaturahman/XAUUSD.git
git branch -M main
git push -u origin main
```

**Requirements:**
- Git installed
- GitHub account active
- SSH keys atau Personal Access Token configured

---

## 🛠️ Troubleshooting

### Problem 1: "Module not found"
```
Error: ModuleNotFoundError: No module named 'yfinance'
```
**Solution:**
```bash
pip install yfinance
# Or reinstall all:
pip install -r requirements.txt
```

### Problem 2: "No data downloaded"
**Causes:**
- Invalid symbol (check: it's "GC=F" for gold, not "XAUUSD")
- Internet connection issue
- Data validation failed

**Solution:**
```python
# Test data fetching
from src.data_fetcher import DataFetcher
import yaml
config = yaml.safe_load(open('config/config.yaml'))
fetcher = DataFetcher(config)
df = fetcher.fetch_yfinance_data(interval='1d')
print(df.head())  # Should show data
```

### Problem 3: "Git not found"
```
error: git is not recognized as an internal or external command
```
**Solution:**
- Install Git: https://git-scm.com/download/win
- Add to PATH environment variable
- Restart terminal/command prompt

### Problem 4: "Out of memory"
**Solution:**
- Reduce data range (shorter period)
- Process fewer timeframes
- Increase system RAM / Use cloud

### Problem 5: ".sh file permission denied"
```bash
chmod +x *.sh
./run_analysis.sh
```

---

## 📚 Next Steps

### 1. Understand the System
- [ ] Read README.md (overview)
- [ ] Read STRATEGY_GUIDE.md (strategies)
- [ ] Review config.yaml (customization)

### 2. Run First Analysis
- [ ] Run `python main.py`
- [ ] Check results in `results/` folder
- [ ] Open HTML charts in browser

### 3. Customize System
- [ ] Edit config.yaml parameters
- [ ] Test different strategies
- [ ] Optimize for your timeframe

### 4. Live Trading (Optional)
- [ ] Paper trade first
- [ ] Use real broker integration
- [ ] Monitor performance
- [ ] Adjust strategy monthly

---

## 📖 Learning Resources

### Technical Analysis
- **Khan Academy** - Finance & Capital Markets
- **Investopedia** - TA indicators explained
- **Trading View** - Community & ideas

### Python for Trading
- **Real Python** - Python tutorials
- **Pandas Docs** - Data manipulation
- **Plotly Docs** - Interactive charts

### Gold Markets
- **Kitco** - Gold price analysis
- **Trading Economics** - Economic data
- **LBMA** - Gold market info

---

## 🆘 Getting Help

### In-Code Help
Press Ctrl+click di class/function untuk docstring

### External Resources
- GitHub Issues: Report bugs
- Stack Overflow: Python questions
- Reddit r/algotrading: Trading questions

### Community
- Trading Discord servers
- Algo-trading GitHub forums
- Local trading meetups

---

## 💾 System Requirements

### Minimum
- RAM: 4GB
- Disk: 2GB
- CPU: Dual-core 2GHz
- Internet: Stable connection

### Recommended
- RAM: 8GB+
- Disk: SSD 10GB+
- CPU: Quad-core 2.5GHz+
- Internet: Fast connection (>5Mbps)

### Cloud (AWS/Google/Azure)
- EC2/GCE t3.medium or equivalent
- 2vCPU, 4GB RAM
- Cost: ~$10-20/month

---

## ✅ Verification Checklist

After installation, verify:
- [ ] Python 3.8+ installed (`python --version`)
- [ ] All packages installed (`pip list | grep yfinance`)
- [ ] Virtual environment active (should see `(venv)` in terminal)
- [ ] Data downloading works (`results/` folder created)
- [ ] HTML charts generated (open in browser)
- [ ] No error messages in logs

---

## 🎓 Demo Analysis Details

Default analysis (no config changes) will:

**Data**: Download 2 years XAUUSD daily candles

**Indicators**: Calculate 
- 8 Moving Averages (SMA/EMA)
- RSI, MACD, Stochastic, ADX
- Bollinger Bands, Keltner Channels
- ATR, OBV, Volume indicators
- ROC, CCI, Williams %R

**Patterns**: Detect 14 candlestick patterns

**Strategies**: Test 5 different strategies
1. Trend Following (MA crossover)
2. Mean Reversion (BB + RSI)
3. Breakout (20-period)
4. Support/Resistance
5. Combined Multi-Signal (Recommended)

**Backtesting**: With $10,000 initial capital
- Report each trade
- Calculate Sharpe ratio, drawdown
- Compare strategy performance

**Output**: 6 interactive HTML charts + JSON results

**Time**: ~2-5 minutes untuk complete analysis

---

## 🔔 Important Notes

⚠️ **Disclaimer:**
- System for EDUCATIONAL purposes only
- Not financial advice
- Always do your own research
- Risk management REQUIRED
- Past performance ≠ Future results
- Trade at your own risk

⚡ **Best Practices:**
- Start with paper trading
- Test thoroughly before live
- Risk max 1-2% per trade
- Keep detailed trade logs
- Review & adjust monthly
- Never go all-in on single trade

---

## 📞 Support Channel

- **Documentation**: README.md, STRATEGY_GUIDE.md
- **Code Issues**: Check GitHub Issues
- **Python Questions**: Stack Overflow + Python docs
- **Trading Questions**: r/algotrading, r/investing

---

**Ready to start? Run: `python main.py`** 🚀

Good luck with your XAUUSD trading analysis!

---

**Version**: 1.0.0
**Last Updated**: March 2, 2026
