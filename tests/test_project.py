from src.generator import generate

def test_validation(tmp_path):
    t,r=generate("starter",20261022,str(tmp_path/"out"))
    assert r["passed"]
    assert len(t["requester"])==20 and len(t["supplier"])==10 and len(t["purchase_request"])==40

def test_edge_cases(tmp_path):
    t,_=generate("starter",20261022,str(tmp_path/"out"))
    issues={x["issue_type"] for x in t["ground_truth"]}
    assert {"PO_WITHOUT_APPROVAL","QUOTE_EXPIRED_BEFORE_AWARD","NONCHEAPEST_WITHOUT_RATIONALE","INACTIVE_SUPPLIER","BUDGET_OVERRUN","DUPLICATE_REQUEST","QUOTE_CURRENCY_MISMATCH"} <= issues
