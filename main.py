#!/usr/bin/env python3
"""
XAUUSD Market Analysis System
Main execution file - Integrates all analysis modules
"""

import sys
import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
import json
import traceback

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import all modules
try:
    from src.data_fetcher import DataFetcher
    from src.technical_indicators import TechnicalIndicators
    from src.candlestick_analysis import CandlestickAnalyzer
    from src.fundamental_analysis import FundamentalAnalyzer
    from src.strategy import create_strategy
    from src.signals import SignalGenerator
    from src.backtester import BacktestEngine
    from src.visualizer import Visualizer
except ImportError as e:
    print(f"ERROR: Failed to import modules: {e}")
    print(f"Make sure you're in the {PROJECT_ROOT} directory")
    sys.exit(1)

# Create logs directory
logs_dir = PROJECT_ROOT / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'xauusd_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XAUUSDAnalysisSystem:
    """Main XAUUSD analysis system"""
    
    def __init__(self, config_path: str = None):
        """Initialize the system"""
        
        logger.info("Initializing XAUUSD Analysis System...")
        
        # Use default config path if not provided
        if config_path is None:
            config_path = PROJECT_ROOT / 'config' / 'config.yaml'
        else:
            config_path = Path(config_path)
        
        # Ensure config path is absolute
        if not config_path.is_absolute():
            config_path = PROJECT_ROOT / config_path
        
        # Load configuration
        try:
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            if self.config is None:
                logger.error("Config file is empty")
                raise ValueError("Config file is empty")
            
            logger.info(f"✓ Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
        
        # Initialize components
        try:
            self.data_fetcher = DataFetcher(self.config)
            self.fundamental_analyzer = FundamentalAnalyzer(self.config)
            self.backtester = BacktestEngine(self.config)
            self.visualizer = Visualizer(self.config)
            self.signal_generator = SignalGenerator(self.config)
            
            # Create results directory
            results_dir = PROJECT_ROOT / 'results'
            results_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("✓ All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def run_full_analysis(self, 
                         interval: str = '1d',
                         strategy_types: list = None,
                         start_date: str = None,
                         end_date: str = None):
        """
        Run complete XAUUSD analysis
        
        Args:
            interval: Timeframe (1d, 4h, 1h, etc.)
            strategy_types: List of strategies to test
            start_date: Analysis start date
            end_date: Analysis end date
        """
        
        try:
            logger.info("\n" + "="*70)
            logger.info("STARTING XAUUSD FULL ANALYSIS")
            logger.info("="*70)
            
            strategy_types = strategy_types or ['combined', 'trend_following', 'mean_reversion']
            
            # Step 1: Data Collection
            logger.info("\n[1/6] STEP 1: FETCHING DATA")
            logger.info("-" * 70)
            
            data = self.data_fetcher.fetch_yfinance_data(
                start_date=start_date or self.config['data']['start_date'],
                end_date=end_date or self.config['data']['end_date'],
                interval=interval
            )
            
            if data is None or data.empty:
                logger.error("Failed to fetch data. Exiting.")
                return
            
            # Prepare data
            data = self.data_fetcher.prepare_data(data)
            logger.info(f"✓ Data ready: {len(data)} candles from {data.index[0]} to {data.index[-1]}")
            
            # Step 2: Technical Analysis
            logger.info("\n[2/6] STEP 2: TECHNICAL ANALYSIS")
            logger.info("-" * 70)
            
            data = TechnicalIndicators.add_all_indicators(data, self.config)
            logger.info("✓ All technical indicators calculated")
            
            # Step 3: Candlestick Analysis
            logger.info("\n[3/6] STEP 3: CANDLESTICK PATTERN ANALYSIS")
            logger.info("-" * 70)
            
            data = CandlestickAnalyzer.analyze_patterns(data)
            data = CandlestickAnalyzer.analyze_wicks(data)
            logger.info("✓ Candlestick patterns analyzed")
            
            # Step 4: Fundamental Analysis
            logger.info("\n[4/6] STEP 4: FUNDAMENTAL ANALYSIS")
            logger.info("-" * 70)
            
            fundamental_report = self.fundamental_analyzer.generate_fundamental_report()
            fundamental_scores = [fundamental_report['fundamental_score']] * len(data)
            logger.info("✓ Fundamental analysis completed")
            
            # Step 5: Strategy & Signal Generation
            logger.info("\n[5/6] STEP 5: STRATEGY & SIGNAL GENERATION")
            logger.info("-" * 70)
            
            backtest_results = {}
            all_signals = {}
            
            for strategy_type in strategy_types:
                try:
                    logger.info(f"\nTesting {strategy_type} strategy...")
                    
                    # Generate strategy signals
                    strategy = create_strategy(strategy_type, self.config)
                    strategy_data, strategy_meta = strategy.generate_signals(data.copy())
                    
                    # Generate final signals
                    signals_df = self.signal_generator.generate_signal_dataframe(
                        data, strategy_data, fundamental_scores
                    )
                    signals_df = self.signal_generator.filter_signals_by_timeframe(signals_df, 5)
                    
                    # Backtest the strategy
                    results = self.backtester.run_backtest(data, signals_df, strategy_type)
                    self.backtester.print_results(results)
                    
                    # Store results
                    backtest_results[strategy_type] = results
                    all_signals[strategy_type] = signals_df
                except Exception as e:
                    logger.error(f"Error testing {strategy_type} strategy: {e}")
                    continue
            
            if not backtest_results:
                logger.error("No successful strategy backtests")
                return
            
            logger.info("✓ Strategy testing completed")
            
            # Step 6: Visualization and Reporting
            logger.info("\n[6/6] STEP 6: VISUALIZATION & REPORTING")
            logger.info("-" * 70)
            
            # Create visualizations
            self.visualizer.plot_candlestick_with_indicators(data, save=True)
            self.visualizer.plot_technical_indicators(data, save=True)
            self.visualizer.plot_returns_distribution(data, save=True)
            self.visualizer.plot_correlation_heatmap(data, save=True)
            
            # Plot best strategy signals
            best_strategy = max(backtest_results.items(), 
                               key=lambda x: x[1].get('total_return_pct', 0))[0]
            self.visualizer.plot_signals_on_price(data, all_signals[best_strategy], save=True)
            self.visualizer.plot_backtest_results(backtest_results[best_strategy], save=True)
            
            # Generate summary report
            self.visualizer.generate_summary_report(
                data, all_signals[best_strategy], backtest_results[best_strategy]
            )
            
            logger.info("✓ Visualizations created")
            
            # Save results to JSON
            self._save_results_to_json(backtest_results, fundamental_report, data)
            
            # Print final summary
            self._print_final_summary(backtest_results, fundamental_report)
            
            logger.info("\n" + "="*70)
            logger.info("ANALYSIS COMPLETED SUCCESSFULLY!")
            logger.info("="*70)
            logger.info(f"Results saved to: {PROJECT_ROOT / 'results'}/")
            logger.info(f"Plots saved to: {self.visualizer.plot_dir}/")
            logger.info(f"Logs saved to: {logs_dir}/xauusd_analysis.log")
            
        except Exception as e:
            logger.error(f"Fatal error in analysis: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _save_results_to_json(self, backtest_results, fundamental_report, data):
        """Save results to JSON for future reference"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'data_range': {
                'start': str(data.index[0]),
                'end': str(data.index[-1]),
                'candles': len(data)
            },
            'fundamental_analysis': {
                'score': fundamental_report['fundamental_score'],
                'outlook': fundamental_report['outlook'],
                'sentiment': fundamental_report['news_sentiment'],
                'usd_strength': fundamental_report['usd_strength'],
                'geopolitical_risk': fundamental_report['geopolitical_risk']
            },
            'backtest_results': {}
        }
        
        for strategy, result in backtest_results.items():
            results['backtest_results'][strategy] = {
                'total_return_pct': result.get('total_return_pct', 0),
                'total_trades': result.get('total_trades', 0),
                'win_rate': result.get('win_rate', 0),
                'max_drawdown_pct': result.get('drawdown_pct', 0),
                'sharpe_ratio': result.get('sharpe_ratio', 0),
                'profit_factor': result.get('profit_factor', 0)
            }
        
        results_file = PROJECT_ROOT / 'results' / 'analysis_results.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"✓ Results saved to {results_file}")
        except Exception as e:
            logger.error(f"Failed to save results JSON: {e}")
    
    def _print_final_summary(self, backtest_results, fundamental_report):
        """Print final analysis summary"""
        
        logger.info("\n" + "="*70)
        logger.info("FINAL SUMMARY")
        logger.info("="*70)
        
        logger.info(f"\nFundamental Outlook: {fundamental_report['outlook']}")
        logger.info(f"Fundamental Score: {fundamental_report['fundamental_score']:.2f} (-1 to 1)")
        
        logger.info("\nStrategy Performance Ranking:")
        ranked = sorted(backtest_results.items(), 
                       key=lambda x: x[1].get('total_return_pct', 0),
                       reverse=True)
        
        for i, (strategy, result) in enumerate(ranked, 1):
            ret = result.get('total_return_pct', 0)
            wr = result.get('win_rate', 0)
            sharpe = result.get('sharpe_ratio', 0)
            
            logger.info(f"{i}. {strategy}")
            logger.info(f"   Return: {ret:+.2f}% | Win Rate: {wr:.1f}% | Sharpe: {sharpe:.2f}")
        
        logger.info("\n" + "="*70)


def main():
    """Main entry point"""
    
    try:
        system = XAUUSDAnalysisSystem()
        
        # Run analysis with multiple timeframes and strategies
        system.run_full_analysis(
            interval='1d',
            strategy_types=['trend_following', 'mean_reversion', 'breakout', 
                          'combined', 'candlestick'],
            start_date='2023-01-01'
        )
        
        logger.info("\n✓✓✓ ALL ANALYSIS COMPLETED SUCCESSFULLY! ✓✓✓\n")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please make sure config/config.yaml exists")
        sys.exit(1)
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
