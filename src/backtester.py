"""
Backtesting Engine for XAUUSD Strategies
Simulates trading strategies and calculates performance metrics
"""

import sys
from pathlib import Path

# ensure project root on sys.path when running directly
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """Execute backtesting for trading strategies"""
    
    def __init__(self, config: Dict):
        """Initialize backtest engine"""
        self.config = config
        self.backtest_config = config.get('backtest', {})
        self.initial_capital = self.backtest_config.get('initial_capital', 10000)
        self.commission = self.backtest_config.get('commission', 0.001)
        self.slippage = self.backtest_config.get('slippage', 0.0005)
        self.position_size = self.backtest_config.get('position_size', 0.95)
        
        self.trades = []
        self.equity_curve = []
        self.drawdowns = []
    
    def run_backtest(self, 
                    data: pd.DataFrame, 
                    signals: pd.DataFrame,
                    strategy_name: str = "Test Strategy") -> Dict:
        """
        Execute backtest on historical data
        
        Args:
            data: OHLCV DataFrame
            signals: Buy/Sell signals
            strategy_name: Name of strategy
        
        Returns:
            Backtest results and metrics
        """
        
        logger.info(f"\nStarting backtest: {strategy_name}")
        logger.info(f"Period: {data.index[0]} to {data.index[-1]}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Commission: {self.commission*100:.2f}%")
        logger.info(f"Slippage: {self.slippage*100:.2f}%")
        
        self.trades = []
        self.equity_curve = []
        
        cash = self.initial_capital
        position = 0
        entry_price = 0
        entry_index = 0
        
        # quick length check
        if len(data) != len(signals):
            logger.warning("Data and signals length mismatch; aligning by minimum length")
            min_len = min(len(data), len(signals))
            data = data.iloc[:min_len]
            signals = signals.iloc[:min_len]
        
        for i in range(len(data)):
            current_price = data['Close'].iloc[i]
            equity = cash + (position * current_price)
            self.equity_curve.append(equity)
            
            # Check for buy signal
            if signals['Buy'].iloc[i] and position == 0:
                position_size_amount = cash * self.position_size
                num_contracts = position_size_amount / (current_price * (1 + self.slippage))
                entry_cost = num_contracts * current_price * (1 + self.commission)
                
                cash -= entry_cost
                position = num_contracts
                entry_price = current_price
                entry_index = i
                
                logger.debug(f"BUY at index {i}: Price={current_price:.2f}, "
                           f"Position={position:.4f}")
            
            # Check for sell signal
            elif signals['Sell'].iloc[i] and position > 0:
                exit_value = position * current_price * (1 - self.slippage)
                exit_commission = exit_value * self.commission
                
                cash += (exit_value - exit_commission)
                profit = (current_price - entry_price) * position
                profit_pct = (profit / (entry_price * position)) * 100 if entry_price * position != 0 else 0
                
                trade = {
                    'entry_date': data.index[entry_index],
                    'entry_price': entry_price,
                    'exit_date': data.index[i],
                    'exit_price': current_price,
                    'size': position,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'bars_held': i - entry_index
                }
                self.trades.append(trade)
                
                logger.debug(f"SELL at index {i}: Price={current_price:.2f}, "
                           f"Profit={profit:+.2f}, Return={profit_pct:+.2f}%")
                
                position = 0
        
        # Close any open position at end
        if position > 0:
            final_price = data['Close'].iloc[-1]
            exit_value = position * final_price
            cash += exit_value
            
            profit = (final_price - entry_price) * position
            trade = {
                'entry_date': data.index[entry_index],
                'entry_price': entry_price,
                'exit_date': data.index[-1],
                'exit_price': final_price,
                'size': position,
                'profit': profit,
                'profit_pct': (profit / (entry_price * position)) * 100 if entry_price * position != 0 else 0,
                'bars_held': len(data) - entry_index
            }
            self.trades.append(trade)
        
        # Calculate metrics
        results = {
            'strategy_name': strategy_name,
            'period': f"{data.index[0].date()} to {data.index[-1].date()}",
            'initial_capital': self.initial_capital,
            'final_capital': cash + (position * data['Close'].iloc[-1]),
            'total_return': cash - self.initial_capital,
            'total_return_pct': ((cash - self.initial_capital) / self.initial_capital) * 100,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        # Add performance metrics
        metrics = self._calculate_metrics(results)
        results.update(metrics)
        
        return results
    
    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calculate performance metrics"""
        
        trades = results.get('trades', []) or []
        equity_curve = np.array(results.get('equity_curve', []))
        initial_capital = results.get('initial_capital', self.initial_capital)
        
        metrics = {}
        
        if len(trades) == 0:
            logger.warning("No trades executed")
            return metrics
        
        # Trade statistics
        trades_df = pd.DataFrame(trades)
        
        metrics['total_trades'] = len(trades)
        metrics['winning_trades'] = len(trades_df[trades_df['profit'] > 0])
        metrics['losing_trades'] = len(trades_df[trades_df['profit'] < 0])
        metrics['break_even_trades'] = len(trades_df[trades_df['profit'] == 0])
        
        if metrics['total_trades'] > 0:
            metrics['win_rate'] = (metrics['winning_trades'] / metrics['total_trades']) * 100
        else:
            metrics['win_rate'] = 0
        
        # Profit metrics
        if len(trades_df[trades_df['profit'] > 0]) > 0:
            metrics['avg_win'] = trades_df[trades_df['profit'] > 0]['profit'].mean()
            metrics['max_win'] = trades_df['profit'].max()
        else:
            metrics['avg_win'] = 0
            metrics['max_win'] = 0
        
        if len(trades_df[trades_df['profit'] < 0]) > 0:
            metrics['avg_loss'] = trades_df[trades_df['profit'] < 0]['profit'].mean()
            metrics['max_loss'] = trades_df['profit'].min()
        else:
            metrics['avg_loss'] = 0
            metrics['max_loss'] = 0
        
        # Profit factor
        gross_profit = trades_df[trades_df['profit'] > 0]['profit'].sum()
        gross_loss = abs(trades_df[trades_df['profit'] < 0]['profit'].sum())
        
        if gross_loss > 0:
            metrics['profit_factor'] = gross_profit / gross_loss
        else:
            metrics['profit_factor'] = float('inf') if gross_profit > 0 else 0
        
        # Risk metrics
        metrics['max_drawdown'] = self._calculate_max_drawdown(equity_curve, initial_capital)
        metrics['drawdown_pct'] = (metrics['max_drawdown'] / initial_capital) * 100
        
        # Returns metrics
        try:
            daily_returns = np.diff(equity_curve) / equity_curve[:-1]
        except Exception:
            daily_returns = np.array([])
        
        metrics['annual_return'] = self._calculate_annual_return(equity_curve, initial_capital)
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(daily_returns)
        metrics['sortino_ratio'] = self._calculate_sortino_ratio(daily_returns)
        metrics['calmar_ratio'] = self._calculate_calmar_ratio(metrics.get('annual_return',0), 
                                                              metrics.get('max_drawdown',0), 
                                                              initial_capital)
        
        # Average trade metrics
        metrics['avg_trade_return'] = trades_df['profit_pct'].mean()
        metrics['avg_bars_held'] = trades_df['bars_held'].mean()
        
        # Consecutive wins/losses
        metrics['max_consecutive_wins'] = self._get_max_consecutive(trades_df, True)
        metrics['max_consecutive_losses'] = self._get_max_consecutive(trades_df, False)
        
        return metrics
    
    def _calculate_max_drawdown(self, equity_curve: np.ndarray, initial_capital: float) -> float:
        """Calculate maximum drawdown"""
        peak = initial_capital
        max_dd = 0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = peak - equity
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _calculate_annual_return(self, equity_curve: np.ndarray, initial_capital: float) -> float:
        """Calculate annualized return"""
        final_value = equity_curve[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # Assume 252 trading days per year
        years = len(equity_curve) / 252
        
        if years > 0:
            annual_return = (final_value / initial_capital) ** (1 / years) - 1
        else:
            annual_return = total_return
        
        return annual_return * 100
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.04) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)
        
        if np.std(excess_returns) == 0:
            return 0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe
    
    def _calculate_sortino_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.04) -> float:
        """Calculate Sortino ratio (uses downside deviation)"""
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)
        downside = returns[returns < 0]
        
        if len(downside) == 0 or np.std(downside) == 0:
            return 0
        
        sortino = np.mean(excess_returns) / np.std(downside) * np.sqrt(252)
        return sortino
    
    def _calculate_calmar_ratio(self, annual_return: float, max_dd: float, initial_capital: float) -> float:
        """Calculate Calmar ratio"""
        dd_pct = (max_dd / initial_capital) * 100
        
        if dd_pct == 0:
            return 0
        
        return annual_return / dd_pct
    
    def _get_max_consecutive(self, trades_df: pd.DataFrame, is_winning: bool) -> int:
        """Get maximum consecutive wins or losses"""
        if is_winning:
            trades = trades_df['profit'] > 0
        else:
            trades = trades_df['profit'] < 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if trade:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def print_results(self, results: Dict):
        """Print backtest results in readable format"""
        
        logger.info("\n" + "="*70)
        logger.info(f"BACKTEST RESULTS: {results['strategy_name']}")
        logger.info("="*70)
        
        logger.info(f"\nPeriod: {results['period']}")
        logger.info(f"Initial Capital: ${results['initial_capital']:,.2f}")
        logger.info(f"Final Capital: ${results['final_capital']:,.2f}")
        logger.info(f"Total Return: ${results['total_return']:,.2f} "
                   f"({results['total_return_pct']:+.2f}%)")
        
        logger.info(f"\n{'TRADE STATISTICS':^70}")
        logger.info("-"*70)
        logger.info(f"Total Trades: {results.get('total_trades', 0)}")
        logger.info(f"Winning Trades: {results.get('winning_trades', 0)}")
        logger.info(f"Losing Trades: {results.get('losing_trades', 0)}")
        logger.info(f"Win Rate: {results.get('win_rate', 0):.2f}%")
        
        logger.info(f"\n{'PROFIT METRICS':^70}")
        logger.info("-"*70)
        logger.info(f"Average Win: ${results.get('avg_win', 0):,.2f}")
        logger.info(f"Average Loss: ${results.get('avg_loss', 0):,.2f}")
        logger.info(f"Max Win: ${results.get('max_win', 0):,.2f}")
        logger.info(f"Max Loss: ${results.get('max_loss', 0):,.2f}")
        logger.info(f"Profit Factor: {results.get('profit_factor', 0):.2f}")
        
        logger.info(f"\n{'RISK METRICS':^70}")
        logger.info("-"*70)
        logger.info(f"Max Drawdown: ${results.get('max_drawdown', 0):,.2f} "
                   f"({results.get('drawdown_pct', 0):.2f}%)")
        logger.info(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        logger.info(f"Sortino Ratio: {results.get('sortino_ratio', 0):.2f}")
        logger.info(f"Calmar Ratio: {results.get('calmar_ratio', 0):.2f}")
        
        logger.info("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import yaml
    from data_fetcher import DataFetcher
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    fetcher = DataFetcher(config)
    df = fetcher.fetch_yfinance_data(interval='1d', start_date='2023-01-01')
    df = fetcher.prepare_data(df)
    
    # Create dummy signals for testing
    df['Buy'] = (df['Close'].shift(1) < df['Close'].shift(2)) & (df['Close'] > df['Close'].shift(1))
    df['Sell'] = (df['Close'].shift(1) > df['Close'].shift(2)) & (df['Close'] < df['Close'].shift(1))
    
    backtester = BacktestEngine(config)
    results = backtester.run_backtest(df, df, "Test Strategy")
    backtester.print_results(results)
