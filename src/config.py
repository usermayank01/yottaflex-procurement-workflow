from dataclasses import dataclass

@dataclass(frozen=True)
class Scale:
    requesters: int
    suppliers: int
    requests: int
    rfqs: int
    quotes: int
    purchase_orders: int

SCALES = {
    "starter": Scale(20, 10, 40, 15, 45, 25),
    "full": Scale(300, 120, 1200, 500, 1500, 900),
}
