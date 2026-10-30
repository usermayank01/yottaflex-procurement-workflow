from collections import Counter, defaultdict

def validate_tables(t):
    checks=[]
    def ck(name, ok, detail):
        checks.append({"name":name,"passed":bool(ok),"detail":detail})
    pk={"requester":"requester_id","department":"department_id","budget":"budget_id",
        "purchase_request":"request_id","request_line":"request_line_id","supplier":"supplier_id",
        "rfq":"rfq_id","supplier_quote":"quote_id","approval":"approval_id",
        "purchase_order":"po_id","delivery":"delivery_id","workflow_event":"event_id","ground_truth":"case_id"}
    for name,key in pk.items():
        vals=[r[key] for r in t[name]]
        ck(name+".primary_key_unique",len(vals)==len(set(vals)),f"{len(vals)} rows; {len(set(vals))} unique IDs")
    def fk(child,field,parent,key):
        ids={r[key] for r in t[parent]}
        bad=[r[field] for r in t[child] if r[field] not in ids]
        ck(f"{child}.{field}_foreign_key",not bad,"all references resolve" if not bad else f"{len(bad)} invalid")
    fk("requester","department_id","department","department_id")
    fk("budget","department_id","department","department_id")
    fk("purchase_request","requester_id","requester","requester_id")
    fk("purchase_request","department_id","department","department_id")
    fk("purchase_request","budget_id","budget","budget_id")
    fk("request_line","request_id","purchase_request","request_id")
    fk("rfq","request_id","purchase_request","request_id")
    fk("supplier_quote","rfq_id","rfq","rfq_id")
    fk("supplier_quote","supplier_id","supplier","supplier_id")
    fk("approval","request_id","purchase_request","request_id")
    fk("purchase_order","request_id","purchase_request","request_id")
    fk("purchase_order","quote_id","supplier_quote","quote_id")
    fk("purchase_order","supplier_id","supplier","supplier_id")
    fk("delivery","po_id","purchase_order","po_id")
    line_totals=defaultdict(float)
    for r in t["request_line"]: line_totals[r["request_id"]]+=float(r["estimated_cost"])
    bad=[r["request_id"] for r in t["purchase_request"] if round(line_totals[r["request_id"]],2)!=round(float(r["estimated_total"]),2)]
    ck("request_total_reconciliation",not bad,"request totals equal request-line sums")
    qmap={q["quote_id"]:q for q in t["supplier_quote"]}
    bad=[p["po_id"] for p in t["purchase_order"] if round(float(p["awarded_total"]),2)!=round(float(qmap[p["quote_id"]]["landed_cost"]),2)]
    ck("po_quote_reconciliation",not bad,"PO values equal awarded quote landed costs")
    counts=Counter(q["rfq_id"] for q in t["supplier_quote"])
    bad=[r["rfq_id"] for r in t["rfq"] if counts[r["rfq_id"]]<3]
    ck("rfq_minimum_quotes",not bad,"every RFQ has at least three quotes")
    required={"PO_WITHOUT_APPROVAL","QUOTE_EXPIRED_BEFORE_AWARD","NONCHEAPEST_WITHOUT_RATIONALE",
              "INACTIVE_SUPPLIER","BUDGET_OVERRUN","DUPLICATE_REQUEST","QUOTE_CURRENCY_MISMATCH"}
    issues={g["issue_type"] for g in t["ground_truth"]}
    ck("required_edge_cases_present",required<=issues,f"missing: {sorted(required-issues)}")
    passed=sum(c["passed"] for c in checks)
    return {"passed":passed==len(checks),"passed_checks":passed,"total_checks":len(checks),"checks":checks}
