from __future__ import annotations

import asyncio
import random
from typing import Final

import httpx


class PriceOracleClient:
    """Price oracle client for fetching token prices from external APIs."""
    
    _PRICES_USD: Final[dict[str, float]] = {
        "ETH": 3000.0,
        "USDC": 1.0,
        "WBTC": 65000.0,
        "USDT": 1.0,
        "DAI": 1.0,
        "LINK": 15.0,
        "UNI": 8.0,
        "AAVE": 120.0,
    }
    
    # Simulate some price volatility
    _VOLATILITY_RANGE = 0.02  # 2% price variation

    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def get_price_usd(self, symbol: str) -> float:
        """Get USD price for a token symbol."""
        symbol_upper = symbol.upper()
        
        # First try our static prices
        if symbol_upper in self._PRICES_USD:
            base_price = self._PRICES_USD[symbol_upper]
            # Add some realistic volatility
            volatility = random.uniform(-self._VOLATILITY_RANGE, self._VOLATILITY_RANGE)
            return base_price * (1 + volatility)
        
        # For unknown symbols, try external API (simulated)
        try:
            return await self._fetch_external_price(symbol_upper)
        except Exception:
            # Fallback to a default price if external API fails
            raise ValueError(f"No price available for {symbol}")

    async def _fetch_external_price(self, symbol: str) -> float:
        """Fetch price from external API (simulated for demo)."""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Simulate API response with some realistic price
        mock_prices = {
            "BTC": 45000.0,
            "SOL": 100.0,
            "MATIC": 0.8,
            "AVAX": 25.0,
        }
        
        if symbol in mock_prices:
            return mock_prices[symbol]
        
        raise ValueError(f"Symbol {symbol} not supported by external API")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
