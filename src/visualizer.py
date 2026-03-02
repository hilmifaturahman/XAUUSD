"""
Visualization Module for XAUUSD Analysis
Creates interactive charts and analysis visualizations
"""

import sys
from pathlib import Path

# ensure project root is on sys.path for direct execution
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizer:
    """Create visualizations for XAUUSD analysis"""
    
    def __init__(self, config: Dict):
        """Initialize visualizer"""
        self.config = config
        self.viz_config = config.get('visualization', {})
        
        # Get plot directory and ensure it's absolute
        plot_dir = self.viz_config.get('plot_dir', 'results/plots')
        plot_dir = Path(plot_dir)
        if not plot_dir.is_absolute():
            # Make it relative to project root (parent of parent of this file)
            plot_dir = Path(__file__).parent.parent / plot_dir
        
        self.plot_dir = plot_dir
        self.theme = self.viz_config.get('theme', 'dark')
        
        # Create plot directory
        try:
            self.plot_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Plot directory ready: {self.plot_dir}")
        except Exception as e:
            logger.error(f"Failed to create plot directory: {e}")
            raise
        
        # Set style
        try:
            if self.theme == 'dark':
                plt.style.use('dark_background')
                self.bg_color = '#1e1e1e'
                self.grid_color = '#444444'
            else:
                plt.style.use('seaborn-v0_8-lightgrid')
                self.bg_color = 'white'
                self.grid_color = '#cccccc'
        except Exception as e:
            logger.warning(f"Failed to set matplotlib style: {e}")
    
    def plot_candlestick_with_indicators(self,
                                        data: pd.DataFrame,
                                        title: str = "XAUUSD Candlestick Chart",
                                        save: bool = True) -> Optional[go.Figure]:
        """Create interactive candlestick chart with technical indicators"""
        
        logger.info(f"Creating candlestick chart: {title}")
        
        # Create figure with secondary y-axis
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.08,
                           row_heights=[0.7, 0.3])
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='XAUUSD'
        ), row=1, col=1)
        
        # Add Moving Averages
        if 'EMA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['EMA_20'],
                name='EMA 20', line=dict(color='orange', width=1)
            ), row=1, col=1)
        
        if 'EMA_50' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['EMA_50'],
                name='EMA 50', line=dict(color='blue', width=1)
            ), row=1, col=1)
        
        if 'EMA_200' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['EMA_200'],
                name='EMA 200', line=dict(color='red', width=1)
            ), row=1, col=1)
        
        # Add Bollinger Bands
        if 'BB_Upper' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['BB_Upper'],
                name='BB Upper', line=dict(color='rgba(0,100,80,0.2)'),
                hoverinfo='skip'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=data.index, y=data['BB_Lower'],
                name='BB Lower', line=dict(color='rgba(0,100,80,0.2)'),
                fill='tonexty', hoverinfo='skip'
            ), row=1, col=1)
        
        # Add Volume
        colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green'
                 for i in range(len(data))]
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'],
            name='Volume', marker_color=colors,
            opacity=0.3
        ), row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_dark' if self.theme == 'dark' else 'plotly',
            height=800,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text='Price', row=1, col=1)
        fig.update_yaxes(title_text='Volume', row=2, col=1)
        
        if save:
            filepath = self.plot_dir / "candlestick_chart.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def plot_technical_indicators(self,
                                 data: pd.DataFrame,
                                 indicators: list = None,
                                 save: bool = True) -> Optional[go.Figure]:
        """Create interactive indicators chart"""
        
        logger.info("Creating technical indicators chart")
        
        indicators = indicators or ['RSI_14', 'MACD', 'ADX']
        
        fig = make_subplots(
            rows=len(indicators), cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=indicators
        )
        
        row = 1
        
        # RSI
        if 'RSI_14' in data.columns and 'RSI_14' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['RSI_14'],
                name='RSI(14)', line=dict(color='cyan')
            ), row=row, col=1)
            fig.add_hline(y=70, line_dash='dash', line_color='red', row=row, col=1)
            fig.add_hline(y=30, line_dash='dash', line_color='green', row=row, col=1)
            row += 1
        
        # MACD
        if 'MACD' in data.columns and 'MACD' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MACD'],
                name='MACD', line=dict(color='blue')
            ), row=row, col=1)
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MACD_Signal'],
                name='Signal', line=dict(color='red')
            ), row=row, col=1)
            fig.add_trace(go.Bar(
                x=data.index, y=data['MACD_Hist'],
                name='Histogram', marker_color='gray', opacity=0.3
            ), row=row, col=1)
            row += 1
        
        # ADX
        if 'ADX' in data.columns and 'ADX' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['ADX'],
                name='ADX', line=dict(color='purple')
            ), row=row, col=1)
            fig.add_hline(y=25, line_dash='dash', line_color='orange', row=row, col=1)
        
        fig.update_layout(
            title='Technical Indicators',
            height=300 * len(indicators),
            template='plotly_dark' if self.theme == 'dark' else 'plotly',
            hovermode='x unified'
        )
        
        if save:
            filepath = self.plot_dir / "indicators_chart.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def plot_signals_on_price(self,
                             data: pd.DataFrame,
                             signals_df: pd.DataFrame,
                             save: bool = True) -> Optional[go.Figure]:
        """Plot trading signals on price chart"""
        
        logger.info("Creating signals chart")
        
        fig = go.Figure()
        
        # Price line
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Close'],
            mode='lines', name='Price',
            line=dict(color='blue', width=2)
        ))
        
        # Buy signals
        buy_signals = signals_df[signals_df['Buy_Signal']]
        if len(buy_signals) > 0:
            fig.add_trace(go.Scatter(
                x=buy_signals.index, y=buy_signals['Close'],
                mode='markers', name='BUY Signal',
                marker=dict(color='green', size=12, symbol='triangle-up')
            ))
        
        # Sell signals
        sell_signals = signals_df[signals_df['Sell_Signal']]
        if len(sell_signals) > 0:
            fig.add_trace(go.Scatter(
                x=sell_signals.index, y=sell_signals['Close'],
                mode='markers', name='SELL Signal',
                marker=dict(color='red', size=12, symbol='triangle-down')
            ))
        
        fig.update_layout(
            title='Trading Signals on Price',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            height=600,
            template='plotly_dark' if self.theme == 'dark' else 'plotly',
            hovermode='x unified'
        )
        
        if save:
            filepath = self.plot_dir / "signals_chart.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def plot_backtest_results(self,
                            results: Dict,
                            save: bool = True) -> Optional[go.Figure]:
        """Plot backtest equity curve and drawdown"""
        
        logger.info("Creating backtest results chart")
        
        equity_curve = np.array(results.get('equity_curve', []))
        
        if len(equity_curve) == 0:
            logger.warning("No equity curve data available")
            return None
        
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Equity curve
        fig.add_trace(go.Scatter(
            y=equity_curve, name='Equity',
            fill='tozeroy', line=dict(color='green', width=2)
        ), row=1, col=1)
        
        # Drawdown
        peak = equity_curve[0]
        drawdown = []
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = ((equity - peak) / peak) * 100
            drawdown.append(dd)
        
        fig.add_trace(go.Bar(
            y=drawdown, name='Drawdown %',
            marker_color='red', opacity=0.3
        ), row=2, col=1)
        
        fig.update_layout(
            title=f"Backtest Results: {results.get('strategy_name', 'Strategy')}",
            height=700,
            template='plotly_dark' if self.theme == 'dark' else 'plotly',
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text='Equity ($)', row=1, col=1)
        fig.update_yaxes(title_text='Drawdown (%)', row=2, col=1)
        
        if save:
            filepath = self.plot_dir / "backtest_results.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def plot_correlation_heatmap(self,
                                data: pd.DataFrame,
                                columns: list = None,
                                save: bool = True):
        """Plot correlation heatmap"""
        
        logger.info("Creating correlation heatmap")
        
        # Select relevant columns
        if columns is None:
            columns = [col for col in data.columns if col in
                      ['Close', 'RSI_14', 'MACD', 'ADX', 'ATR', 'Volume']]
        else:
            columns = [col for col in columns if col in data.columns]
        
        if len(columns) < 2:
            logger.warning("Not enough columns for correlation")
            return None
        
        corr = data[columns].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title='Indicator Correlation Matrix',
            height=600,
            width=600,
            template='plotly_dark' if self.theme == 'dark' else 'plotly'
        )
        
        if save:
            filepath = self.plot_dir / "correlation_heatmap.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def plot_returns_distribution(self,
                                 data: pd.DataFrame,
                                 save: bool = True):
        """Plot returns distribution histogram"""
        
        logger.info("Creating returns distribution chart")
        
        returns = data['Daily_Return'].dropna() * 100  # Convert to percentage
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Returns Distribution',
            marker_color='blue'
        ))
        
        fig.add_vline(x=returns.mean(), line_dash='dash', line_color='green',
                     annotation_text=f"Mean: {returns.mean():.2f}%")
        fig.add_vline(x=returns.median(), line_dash='dash', line_color='orange',
                     annotation_text=f"Median: {returns.median():.2f}%")
        
        fig.update_layout(
            title='Daily Returns Distribution',
            xaxis_title='Daily Return (%)',
            yaxis_title='Frequency',
            height=500,
            template='plotly_dark' if self.theme == 'dark' else 'plotly'
        )
        
        if save:
            filepath = self.plot_dir / "returns_distribution.html"
            try:
                fig.write_html(str(filepath))
                logger.info(f"✓ Chart saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save chart: {e}")
        
        return fig
    
    def generate_summary_report(self,
                               data: pd.DataFrame,
                               signals_df: pd.DataFrame,
                               backtest_results: Dict,
                               save: bool = True) -> str:
        """Generate HTML summary report"""
        
        logger.info("Generating summary report...")
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>XAUUSD Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                h1 { color: #ffb700; }
                h2 { color: #4db8ff; margin-top: 30px; }
                .metric { display: inline-block; background: #2d2d2d; padding: 15px; margin: 10px;
                         border-radius: 5px; border-left: 4px solid #ffb700; }
                .metric-value { font-size: 24px; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
                th { background-color: #2d2d2d; }
                .positive { color: #00ff00; }
                .negative { color: #ff6b6b; }
            </style>
        </head>
        <body>
            <div class="container">
        """
        
        # Title and summary
        html += f"<h1>XAUUSD Market Analysis Report</h1>"
        html += f"<p>Period: {data.index[0].date()} to {data.index[-1].date()}</p>"
        
        # Key metrics
        html += "<h2>Key Metrics</h2>"
        html += f"<div class='metric'><div>Current Price</div><div class='metric-value'>${data['Close'].iloc[-1]:.2f}</div></div>"
        html += f"<div class='metric'><div>Period Return</div><div class='metric-value positive'>{((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100):+.2f}%</div></div>"
        html += f"<div class='metric'><div>High</div><div class='metric-value'>${data['High'].max():.2f}</div></div>"
        html += f"<div class='metric'><div>Low</div><div class='metric-value'>${data['Low'].min():.2f}</div></div>"
        
        # Signal summary
        html += "<h2>Trading Signals</h2>"
        buy_count = signals_df['Buy_Signal'].sum() if 'Buy_Signal' in signals_df.columns else 0
        sell_count = signals_df['Sell_Signal'].sum() if 'Sell_Signal' in signals_df.columns else 0
        html += f"<div class='metric'><div>Buy Signals</div><div class='metric-value positive'>{buy_count}</div></div>"
        html += f"<div class='metric'><div>Sell Signals</div><div class='metric-value negative'>{sell_count}</div></div>"
        
        # Backtest results
        if backtest_results:
            html += "<h2>Backtest Results</h2>"
            html += f"<table>"
            html += f"<tr><td>Strategy</td><td>{backtest_results.get('strategy_name', 'N/A')}</td></tr>"
            html += f"<tr><td>Total Return</td><td class='positive'>{backtest_results.get('total_return_pct', 0):+.2f}%</td></tr>"
            html += f"<tr><td>Total Trades</td><td>{backtest_results.get('total_trades', 0)}</td></tr>"
            html += f"<tr><td>Win Rate</td><td>{backtest_results.get('win_rate', 0):.2f}%</td></tr>"
            html += f"<tr><td>Max Drawdown</td><td class='negative'>{backtest_results.get('drawdown_pct', 0):.2f}%</td></tr>"
            html += f"<tr><td>Sharpe Ratio</td><td>{backtest_results.get('sharpe_ratio', 0):.2f}</td></tr>"
            html += f"</table>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        if save:
            filepath = self.plot_dir / "report_summary.html"
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"✓ Report saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
        
        return html


if __name__ == "__main__":
    import yaml
    from data_fetcher import DataFetcher
    from technical_indicators import TechnicalIndicators
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d', start_date='2023-01-01')
    df = fetcher.prepare_data(df)
    
    df = TechnicalIndicators.add_all_indicators(df, config)
    
    viz = Visualizer(config)
    viz.plot_candlestick_with_indicators(df)
    viz.plot_technical_indicators(df)
    viz.plot_returns_distribution(df)
    
    logger.info("Visualizations created successfully!")
