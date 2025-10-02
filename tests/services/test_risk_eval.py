from app.services.risk import RiskEvaluator


def test_compute_health_safe() -> None:
    r = RiskEvaluator()
    m = r.compute_health(collateral_usd=1000, debt_usd=500)
    assert m.health_factor > 1
    assert m.eligible is False


def test_compute_health_eligible() -> None:
    r = RiskEvaluator()
    m = r.compute_health(collateral_usd=500, debt_usd=600)
    assert m.health_factor < 1
    assert m.eligible is True


def test_compute_health_no_debt() -> None:
    r = RiskEvaluator()
    m = r.compute_health(collateral_usd=1000, debt_usd=0)
    assert m.eligible is False
