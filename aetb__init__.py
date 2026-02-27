"""
Autonomous Evolutionary Trading Bot (AETB)
A self-evolving AI trading system combining reinforcement learning,
genetic algorithms, and sentiment analysis.
"""

__version__ = "1.0.0"
__author__ = "Evolution Ecosystem"
__license__ = "Proprietary"

from aetb.config import Config
from aetb.data_manager import DataManager
from aetb.strategy_evolver import StrategyEvolver
from aetb.trading_engine import TradingEngine
from aetb.risk_manager import RiskManager

__all__ = [
    "Config",
    "DataManager",
    "StrategyEvolver",
    "TradingEngine",
    "RiskManager"
]