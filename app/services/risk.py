from dataclasses import dataclass


@dataclass(slots=True)
class RiskMetrics:
    health_factor: float
    eligible: bool


class RiskEvaluator:
    def compute_health(self, collateral_usd: float, debt_usd: float, liquidation_threshold: float = 0.85) -> RiskMetrics:
        if debt_usd <= 0:
            return RiskMetrics(health_factor=10.0, eligible=False)
        hf = (collateral_usd * liquidation_threshold) / debt_usd
        return RiskMetrics(health_factor=hf, eligible=hf < 1.0)
