"""
Configuration management for AETB.
Uses Firebase for dynamic configuration updates.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

import firebase_admin
from firebase_admin import firestore, credentials
from pydantic import BaseModel, Field, validator


class TradingConfig(BaseModel):
    """Validated trading configuration"""
    exchange: str = Field(default="binance", description="Exchange name from CCXT")
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital in quote currency")
    
    @validator('exchange')
    def validate_exchange(cls, v):
        valid_exchanges = ['binance', 'coinbase', 'kraken', 'bybit']
        if v not in valid_exchanges:
            raise ValueError(f"Exchange must be one of {valid_exchanges}")
        return v


class EvolutionConfig(BaseModel):
    """Validated evolution configuration"""
    population_size: int = Field(default=50, gt=0, description="Number of strategies in population")
    generations: int = Field(default=100, gt=0, description="Number of generations to evolve")
    mutation_rate: float = Field(default=0.1, ge=0, le=1, description="Mutation probability")
    crossover_rate: float = Field(default=0.7, ge=0, le=1, description="Crossover probability")
    elite_count: int = Field(default=5, ge=0, description="Number of elites to preserve")


class Config:
    """Main configuration manager with Firebase integration"""
    
    def __init__(self, config_path: str = "config.json", firebase_creds_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self._config_cache: Dict[str, Any] = {}
        self._firebase_initialized = False
        
        # Load local config
        self._load_local_config()
        
        # Initialize Firebase if credentials provided
        if firebase_creds_path and os.path.exists(firebase_creds_path):
            self._init_firebase(firebase_creds_path)
    
    def _load_local_config(self) -> None:
        """Load configuration from local JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self._config_cache = json.load(f)
                self.logger.info(f"Loaded config from {self.config_path}")
            else:
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration"""
        self._config_cache = {
            "trading": {
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "initial_capital": 10000.0
            },
            "evolution": {
                "population_size": 50,
                "generations": 100,
                "mutation_rate": 0.1,
                "crossover_rate": 0.7,
                "elite_count": 5
            },
            "risk": {
                "max_position_size": 0.1,  # 10% of capital
                "stop_loss_pct": 0.02,  # 2% stop loss
                "take_profit_pct": 0.05,  # 5% take profit
                "max_daily_loss": 0.03  # 3% max daily loss
            }
        }
        
        # Save default config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config_cache, f, indent=2)
            self.logger.info(f"Created default config at {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save default config: {e}")
    
    def _init_firebase(self, creds_path: str) -> None:
        """Initialize Firebase connection"""
        try:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred)
            self._firebase_initialized = True
            self.logger.info("Firebase initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            self._firebase_initialized = False
    
    def get(self, key: str, default: Any =