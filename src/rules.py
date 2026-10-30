from dataclasses import dataclass

@dataclass(frozen=True)
class RuleConfig:
    default_approval_threshold: float = 5000.0
    competitive_threshold: float = 2500.0
    quote_expiry_days: int = 7

def approval_required(amount, threshold):
    return amount > threshold

def competitive_purchase(amount, threshold):
    return amount >= threshold

def choose_quote(quotes):
    valid = [q for q in quotes if q["status"] == "VALID"]
    return sorted(valid, key=lambda q:(q["landed_cost"],q["delivery_days"],q["quote_id"]))[0] if valid else None
