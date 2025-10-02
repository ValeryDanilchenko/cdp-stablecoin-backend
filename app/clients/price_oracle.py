from __future__ import annotations

from typing import Final


class PriceOracleClient:
    _PRICES_USD: Final[dict[str, float]] = {
        "ETH": 3000.0,
        "USDC": 1.0,
        "WBTC": 65000.0,
    }

    async def get_price_usd(self, symbol: str) -> float:
        price = self._PRICES_USD.get(symbol.upper())
        if price is None:
            raise ValueError(f"No price for {symbol}")
        return price
