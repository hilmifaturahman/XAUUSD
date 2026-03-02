"""
Fundamental Analysis Module for XAUUSD
Analyzes news, economic data, and sentiment
"""

import sys
from pathlib import Path

# ensure project root is on sys.path when running module directly
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import feedparser
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Analyze fundamental factors affecting XAUUSD"""
    
    def __init__(self, config: Dict):
        """Initialize fundamental analyzer"""
        self.config = config
        self.fundamental_config = config.get('fundamental', {})
        self.rss_feeds = {
            'investing.com': 'https://feeds.bloomberg.com/markets/news.rss',
            'tradingeconomics': 'https://tradingeconomics.com/rss/news.rss',
            'forex.com': 'https://www.forexfactory.com/feedcalendar.php'
        }
    
    def get_economic_calendar_events(self, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming economic events
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            List of economic events
        """
        events = []
        
        try:
            # Target events that affect XAUUSD
            keywords = [
                'CPI', 'inflation', 'Fed', 'interest rates', 'NFP',
                'unemployment', 'GDP', 'retail sales', 'housing',
                'durable goods', 'ADP', 'ISM', 'PMI'
            ]
            
            logger.info(f"Looking for economic events in next {days_ahead} days")
            
            # Simulated economic events (in production, use calendar API)
            events = [
                {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'event': 'US Initial Jobless Claims',
                    'country': 'USA',
                    'importance': 'High',
                    'expected': '-10K',
                    'impact': 'Bullish for USD, Bearish for Gold'
                },
                {
                    'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'event': 'Fed Interest Rate Decision',
                    'country': 'USA',
                    'importance': 'Critical',
                    'expected': '+25 bps',
                    'impact': 'Very Bearish for Gold'
                },
                {
                    'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                    'event': 'CPI (YoY)',
                    'country': 'USA',
                    'importance': 'High',
                    'expected': '3.2%',
                    'impact': 'Bullish for Gold if beats'
                },
            ]
            
            logger.info(f"Found {len(events)} economic events")
            
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
        
        return events
    
    def analyze_news_sentiment(self, keywords: List[str] = None) -> Dict[str, float]:
        """
        Analyze sentiment from news articles
        
        Args:
            keywords: Keywords to search for
        
        Returns:
            Sentiment scores (positive, negative, neutral)
        """
        
        keywords = keywords or self.fundamental_config.get('keywords', [
            'gold', 'XAUUSD', 'inflation', 'fed', 'interest rates'
        ])
        
        sentiment = {
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 0.0,
            'articles_analyzed': 0,
            'overall_sentiment': 0.0
        }
        
        try:
            logger.info(f"Analyzing sentiment for keywords: {keywords}")
            
            # Simulated sentiment analysis
            # In production, use NewsAPI or other sources
            positive_words = ['bullish', 'surge', 'rally', 'jump', 'strength', 'support']
            negative_words = ['bearish', 'plunge', 'crash', 'weakness', 'resistance', 'decline']
            
            # Example sentiment (in production, fetch real news)
            sentiment['positive'] = 0.35
            sentiment['negative'] = 0.45
            sentiment['neutral'] = 0.20
            sentiment['articles_analyzed'] = 25
            sentiment['overall_sentiment'] = sentiment['positive'] - sentiment['negative']
            
            logger.info(f"Sentiment Analysis: Positive={sentiment['positive']:.2%}, "
                       f"Negative={sentiment['negative']:.2%}, "
                       f"Neutral={sentiment['neutral']:.2%}")
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
        
        return sentiment
    
    def get_usd_strength_index(self) -> Optional[float]:
        """
        Get USD Strength Index
        Gold is inversely correlated with USD strength
        
        Returns:
            USD Strength Index value
        """
        try:
            logger.info("Calculating USD Strength Index...")
            
            # Fetch DXY (Dollar Index) equivalent
            # In production, fetch from real-time API
            usd_index = 103.5  # Example value
            
            logger.info(f"USD Strength Index: {usd_index:.2f}")
            return usd_index
            
        except Exception as e:
            logger.error(f"Error calculating USD strength: {e}")
            return None
    
    def get_real_interest_rates(self) -> Dict[str, float]:
        """
        Get real interest rates (affect gold prices inversely)
        
        Returns:
            Dictionary with interest rate information
        """
        rates = {
            'fed_rate': 5.25,  # Current Fed Rate
            'inflation_rate': 3.2,  # Current inflation
            'real_rate': 5.25 - 3.2,
            'market_expectations': {
                '3m': 5.25,
                '1y': 4.75,
                '2y': 4.00
            }
        }
        
        logger.info(f"Current Fed Rate: {rates['fed_rate']}%")
        logger.info(f"Inflation Rate: {rates['inflation_rate']}%")
        logger.info(f"Real Rate: {rates['real_rate']:.2f}%")
        
        return rates
    
    def analyze_geopolitical_risk(self) -> float:
        """
        Analyze geopolitical risk premium
        Gold benefits from geopolitical uncertainty
        
        Returns:
            Risk score (0-1, higher = more risk premium)
        """
        try:
            # Simulated geopolitical risk
            risk_factors = {
                'us_china_tensions': 0.35,
                'middle_east': 0.45,
                'russia_ukraine': 0.55,
                'political_uncertainty': 0.25
            }
            
            avg_risk = sum(risk_factors.values()) / len(risk_factors)
            
            logger.info(f"Geopolitical Risk Score: {avg_risk:.2f}")
            logger.info(f"Risk Factors: {risk_factors}")
            
            return avg_risk
            
        except Exception as e:
            logger.error(f"Error analyzing geopolitical risk: {e}")
            return 0.5
    
    def analyze_inflation_trends(self) -> Dict[str, float]:
        """
        Analyze inflation trends (bullish for gold)
        
        Returns:
            Dictionary with inflation metrics
        """
        inflation_data = {
            'cpi_yoy': 3.2,
            'pce_yoy': 2.8,
            'core_cpi': 4.1,
            'inflation_expectation': 2.5,
            'real_yields_10y': -0.8,
            'bullish_gold': True
        }
        
        logger.info(f"CPI YoY: {inflation_data['cpi_yoy']:.2f}%")
        logger.info(f"Core CPI: {inflation_data['core_cpi']:.2f}%")
        logger.info(f"Real Yields (10Y): {inflation_data['real_yields_10y']:.2f}%")
        
        return inflation_data
    
    def get_gold_etf_flows(self) -> Dict[str, float]:
        """
        Analyze gold ETF flows (GLD, IAU, etc.)
        Positive flows indicate institutional buying
        
        Returns:
            ETF flow data
        """
        flows = {
            'gld_flow_1w': 1250000,  # dollars
            'iau_flow_1w': 850000,
            'gdx_flow_1w': 320000,
            'total_flow': 2420000,
            'trend': 'positive',
            'interpretation': 'Institutional accumulation - Bullish'
        }
        
        logger.info(f"Gold ETF Flows (1 week): ${flows['total_flow']:,.0f}")
        logger.info(f"Trend: {flows['trend'].upper()}")
        logger.info(f"Interpretation: {flows['interpretation']}")
        
        return flows
    
    def analyze_correlation_matrix(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze correlations with key assets
        
        Args:
            data: DataFrame with price data
        
        Returns:
            Correlation matrix
        """
        logger.info("Analyzing correlation matrix...")
        
        # Key correlations with XAUUSD
        correlations = {
            'usd_index': -0.85,  # Strong negative correlation
            'sp500': -0.15,      # Weak negative correlation
            'treasury_yields': -0.75,  # Strong negative correlation
            'vix': 0.45,          # Positive correlation (risk-off)
            'euro': 0.60,         # Positive correlation
            'oil': 0.35,          # Weak positive correlation
            'copper': 0.40,       # Weak positive correlation (risk-on)
        }
        
        logger.info("Gold Correlations:")
        for asset, corr in correlations.items():
            direction = "↓ Negative" if corr < 0 else "↑ Positive"
            logger.info(f"  {asset}: {corr:.2f} {direction}")
        
        return correlations
    
    def calculate_fundamental_score(self, 
                                   sentiment: Dict,
                                   rates: Dict,
                                   geopolitical: float,
                                   inflation: Dict) -> float:
        """
        Calculate overall fundamental score for gold
        
        Args:
            sentiment: News sentiment data
            rates: Interest rate data
            geopolitical: Geopolitical risk score
            inflation: Inflation data
        
        Returns:
            Fundamental score (-1 to 1)
        """
        
        # Sentiment component (weight 20%)
        sentiment_score = sentiment.get('overall_sentiment', 0) * 0.2
        
        # Interest rates component (weight 30%, lower rates = bullish for gold)
        real_rate = rates.get('real_rate', 0)
        try:
            rate_score = (1 - (real_rate + 3) / 6) * 0.3  # Normalize to -1 to 1
        except Exception:
            rate_score = 0
        
        # Geopolitical component (weight 25%, higher risk = bullish for gold)
        try:
            geo_score = (geopolitical - 0.5) * 2 * 0.25
        except Exception:
            geo_score = 0
        
        # Inflation component (weight 25%, higher inflation = bullish)
        try:
            inflation_score = (inflation.get('cpi_yoy', 0) / 5) * 0.25  # Normalize
        except Exception:
            inflation_score = 0
        
        fundamental_score = sentiment_score + rate_score + geo_score + inflation_score
        
        # Clamp to -1 to 1
        fundamental_score = max(-1, min(1, fundamental_score))
        
        logger.info(f"\nFundamental Score Breakdown:")
        logger.info(f"  Sentiment: {sentiment_score:.3f}")
        logger.info(f"  Interest Rates: {rate_score:.3f}")
        logger.info(f"  Geopolitical Risk: {geo_score:.3f}")
        logger.info(f"  Inflation: {inflation_score:.3f}")
        logger.info(f"  TOTAL SCORE: {fundamental_score:.3f}")
        
        return fundamental_score
    
    def generate_fundamental_report(self) -> Dict:
        """
        Generate comprehensive fundamental analysis report
        
        Returns:
            Complete fundamental analysis
        """
        
        logger.info("\n" + "="*50)
        logger.info("FUNDAMENTAL ANALYSIS REPORT - XAUUSD")
        logger.info("="*50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'economic_calendar': self.get_economic_calendar_events(),
            'news_sentiment': self.analyze_news_sentiment(),
            'usd_strength': self.get_usd_strength_index(),
            'interest_rates': self.get_real_interest_rates(),
            'geopolitical_risk': self.analyze_geopolitical_risk(),
            'inflation_trends': self.analyze_inflation_trends(),
            'etf_flows': self.get_gold_etf_flows(),
        }
        
        # Calculate overall score
        fundamental_score = self.calculate_fundamental_score(
            report['news_sentiment'],
            report['interest_rates'],
            report['geopolitical_risk'],
            report['inflation_trends']
        )
        
        report['fundamental_score'] = fundamental_score
        report['outlook'] = self._get_outlook(fundamental_score)
        
        logger.info(f"Outlook: {report['outlook']}")
        logger.info("="*50 + "\n")
        
        return report
    
    @staticmethod
    def _get_outlook(score: float) -> str:
        """Get outlook based on fundamental score"""
        if score > 0.6:
            return "STRONG BULLISH - Gold likely to appreciate"
        elif score > 0.3:
            return "MODERATELY BULLISH - Gold may appreciate"
        elif score > -0.3:
            return "NEUTRAL - No clear directional bias"
        elif score > -0.6:
            return "MODERATELY BEARISH - Gold may depreciate"
        else:
            return "STRONG BEARISH - Gold likely to depreciate"


if __name__ == "__main__":
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    analyzer = FundamentalAnalyzer(config)
    report = analyzer.generate_fundamental_report()
    
    print("\n" + "="*50)
    print("REPORT SUMMARY:")
    print("="*50)
    for key, value in report.items():
        if key not in ['economic_calendar', 'outlook']:
            print(f"{key}: {value}")
