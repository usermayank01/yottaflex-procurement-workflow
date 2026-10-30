from datetime import date,datetime,timedelta
from pathlib import Path
import csv,json,random,sqlite3,hashlib,shutil
from .config import SCALES
from .rules import RuleConfig,approval_required,competitive_purchase
from .schema import SCHEMA

FIRST=["Aarav","Vivaan","Aditya","Arjun","Ishaan","Kabir","Riya","Ananya","Diya","Meera"]
LAST=["Sharma","Singh","Gupta","Verma","Joshi","Khan","Patel","Das","Rao","Kapoor"]
ITEMS=[("Laptop","IT"),("Monitor","IT"),("Network Switch","IT"),("Office Chair","Facilities"),
("Printer","Facilities"),("Safety Equipment","Operations"),("Packaging Material","Operations"),
("Software License","Software"),("Server RAM","IT"),("Barcode Scanner","Operations")]
DEPTS=["IT","Finance","Operations","Facilities","HR","Sales","Procurement","Engineering"]
SUPN=["Northstar","BluePeak","Vertex","Apex","Orion","Nimbus","Cedar","Summit","Prime","Atlas"]

def dt(d): return datetime(d.year,d.month,d.day,10,0,0).isoformat()
def write_csv(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()) if rows else []); w.writeheader(); w.writerows(rows)
def write_json(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(rows,indent=2),encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def make_db(p,tables):
    db=sqlite3.connect(p)
    numeric={"approval_threshold","allocated_amount","reserved_amount","estimated_total","unit_cost","estimated_cost","quantity",
             "quoted_total","shipping_cost","landed_cost","delivery_days","awarded_total","active","approval_required"}
    for name,rows in tables.items():
        cols=SCHEMA[name]
        defs=[f'"{c}" {"REAL" if c in numeric else "TEXT"}' for c in cols]
        db.execute(f'CREATE TABLE "{name}" ({",".join(defs)})')
        if rows:
            db.executemany(f'INSERT INTO "{name}" ({",".join(cols)}) VALUES ({",".join(["?"]*len(cols))})',
                           [[r.get(c) for c in cols] for r in rows])
    db.commit(); db.close()

def generate(scale_name="starter",seed=20261022,out_dir="artifacts/starter"):
    s=SCALES[scale_name]; rng=random.Random(seed); out=Path(out_dir)
    if out.exists(): shutil.rmtree(out)
    (out/"csv").mkdir(parents=True); (out/"json").mkdir(parents=True)
    base=date(2026,1,1); rule=RuleConfig()
    departments=[{"department_id":f"DEP-{i:03d}","name":n,"approval_threshold":float(3000+(i%4)*1000),"currency":"INR"} for i,n in enumerate(DEPTS,1)]
    budgets=[{"budget_id":f"BUG-{i:03d}","department_id":d["department_id"],"fiscal_year":"2026",
              "allocated_amount":float(500000+i*25000),"reserved_amount":0.0} for i,d in enumerate(departments,1)]
    requesters=[]
    for i in range(1,s.requesters+1):
        d=departments[(i-1)%len(departments)]
        requesters.append({"requester_id":f"REQ-{i:04d}","name":f"{FIRST[(i-1)%10]} {LAST[((i-1)//10)%10]}",
                           "email":f"user{i:04d}@example.local","department_id":d["department_id"],"active":1})
    suppliers=[]
    for i in range(1,s.suppliers+1):
        suppliers.append({"supplier_id":f"SUP-{i:04d}","supplier_code":f"S{i:04d}",
                          "name":f"{SUPN[(i-1)%10]} Supplier {i:03d}","active":0 if i%29==0 else 1,
                          "risk_flag":"HIGH" if i%17==0 else ("MEDIUM" if i%7==0 else "LOW"),
                          "currency":"USD" if i%13==0 else "INR"})
    requests=[]; lines=[]; approvals=[]
    for i in range(1,s.requests+1):
        u=requesters[(i-1)%len(requesters)]; d=next(x for x in departments if x["department_id"]==u["department_id"])
        b=next(x for x in budgets if x["department_id"]==d["department_id"])
        total=0.0
        for j in range(1,1+(i%3)+1):
            item,cat=ITEMS[(i+j)%len(ITEMS)]; qty=1+((i+j)%10); unit=round(300+rng.random()*4700,2); cost=round(qty*unit,2); total+=cost
            lines.append({"request_line_id":f"RL-{i:05d}-{j:02d}","request_id":f"PR-2026-{i:06d}","item":item,
                          "category":cat,"quantity":qty,"unit_cost":unit,"estimated_cost":cost,"currency":"INR"})
        total=round(total,2); rid=f"PR-2026-{i:06d}"; need=approval_required(total,d["approval_threshold"])
        requests.append({"request_id":rid,"requester_id":u["requester_id"],"department_id":d["department_id"],"budget_id":b["budget_id"],
                         "status":"APPROVED" if need else "READY_FOR_SOURCING","requested_at":dt(base+timedelta(days=i%180)),
                         "estimated_total":total,"currency":"INR","approval_required":int(need)})
        if need: approvals.append({"approval_id":f"APR-{i:06d}","request_id":rid,"approver_role":"DIRECTOR" if total>20000 else "MANAGER",
                                   "status":"APPROVED","approved_at":dt(base+timedelta(days=i%180+1)),"reason":"Threshold-based approval granted"})
    eligible=[r["request_id"] for r in requests if competitive_purchase(r["estimated_total"],rule.competitive_threshold)]
    rng.shuffle(eligible); eligible=eligible[:s.rfqs]
    rfqs=[]; quotes=[]
    per=max(3,s.quotes//max(1,s.rfqs))
    for i,rid in enumerate(eligible,1):
        day=base+timedelta(days=(i*2)%200); rfqid=f"RFQ-2026-{i:06d}"
        rfqs.append({"rfq_id":rfqid,"request_id":rid,"status":"QUOTES_RECEIVED","issued_at":dt(day),"expires_at":dt(day+timedelta(days=7))})
        req=next(r for r in requests if r["request_id"]==rid)
        for j in range(per):
            sup=suppliers[(i*3+j)%len(suppliers)]; qn=len(quotes)+1; quoted=round(req["estimated_total"]*(.92+rng.random()*.22),2)
            ship=round(150+rng.random()*700,2)
            quotes.append({"quote_id":f"QUO-{sup['supplier_code']}-2026-{qn:06d}","rfq_id":rfqid,"supplier_id":sup["supplier_id"],
                           "quoted_total":quoted,"shipping_cost":ship,"landed_cost":round(quoted+ship,2),"delivery_days":3+qn%15,
                           "currency":sup["currency"],"valid_until":dt(day+timedelta(days=7)),"status":"VALID","selection_rationale":""})
    # Exact quote target, while retaining at least 3/RFQ.
    if len(quotes)>s.quotes: quotes=quotes[:s.quotes]
    while len(quotes)<s.quotes and rfqs:
        qn=len(quotes)+1; rfq=rfqs[(qn-1)%len(rfqs)]; sup=suppliers[(qn+37)%len(suppliers)]
        req=next(r for r in requests if r["request_id"]==rfq["request_id"]); quoted=round(req["estimated_total"]*(.95+rng.random()*.18),2); ship=round(200+rng.random()*500,2)
        quotes.append({"quote_id":f"QUO-{sup['supplier_code']}-2026-{qn:06d}","rfq_id":rfq["rfq_id"],"supplier_id":sup["supplier_id"],
                       "quoted_total":quoted,"shipping_cost":ship,"landed_cost":round(quoted+ship,2),"delivery_days":4+qn%12,
                       "currency":sup["currency"],"valid_until":rfq["expires_at"],"status":"VALID","selection_rationale":""})
    by={}
    for q in quotes: by.setdefault(q["rfq_id"],[]).append(q)
    pos=[]; deliveries=[]; events=[]
    for i in range(1,s.purchase_orders+1):
        if not rfqs: break
        rfq=rfqs[(i-1)%len(rfqs)]; cand=[q for q in by.get(rfq["rfq_id"],[]) if q["currency"]=="INR" and next(x for x in suppliers if x["supplier_id"]==q["supplier_id"])["active"]]
        if not cand: continue
        q=sorted(cand,key=lambda x:(x["landed_cost"],x["delivery_days"],x["quote_id"]))[0]; q["status"]="AWARDED"; q["selection_rationale"]="Lowest landed cost among valid INR quotes"
        po=f"PO-2026-{i:06d}"; pos.append({"po_id":po,"request_id":rfq["request_id"],"quote_id":q["quote_id"],"supplier_id":q["supplier_id"],
                                          "status":"ISSUED","awarded_total":q["landed_cost"],"currency":"INR","issued_at":rfq["issued_at"]})
        deliveries.append({"delivery_id":f"DEL-{po}-01","po_id":po,"event_type":"DELIVERED","event_date":dt(date.fromisoformat(rfq["issued_at"][:10])+timedelta(days=q["delivery_days"])),
                            "quantity":1,"status":"PARTIAL" if i%7==0 else "DELIVERED"})
        events.append({"event_id":f"EVT-{po}-01","entity_type":"PurchaseOrder","entity_id":po,"event_type":"ISSUED","from_status":"DRAFT","to_status":"ISSUED",
                       "event_time":rfq["issued_at"],"actor":"procurement_bot","reason":"Approved quote awarded"})
    gt=[]
    def add(n,typ,eid,issue,label,reason): gt.append({"case_id":f"GT-{n:04d}","entity_type":typ,"entity_id":eid,"issue_type":issue,"ground_truth_label":label,"rationale":reason})
    add(1,"PurchaseOrder",pos[0]["po_id"] if pos else "PO-2026-000001","PO_WITHOUT_APPROVAL","REJECT","PO requires approval when threshold is exceeded.")
    add(2,"SupplierQuote",quotes[0]["quote_id"],"QUOTE_EXPIRED_BEFORE_AWARD","REJECT","Expired quotes cannot be awarded.")
    add(3,"SupplierQuote",quotes[min(1,len(quotes)-1)]["quote_id"],"NONCHEAPEST_WITHOUT_RATIONALE","REVIEW","A non-cheapest selection requires documented rationale.")
    add(4,"Supplier",suppliers[-1]["supplier_id"],"INACTIVE_SUPPLIER","REJECT","Inactive suppliers are ineligible for award.")
    add(5,"Budget",budgets[0]["budget_id"],"BUDGET_OVERRUN","REVIEW","Budget exceptions require review.")
    add(6,"PurchaseRequest",requests[0]["request_id"],"DUPLICATE_REQUEST","REVIEW","Duplicate requests should be flagged.")
    add(7,"SupplierQuote",quotes[-1]["quote_id"],"QUOTE_CURRENCY_MISMATCH","REVIEW","Currency must match before comparison/award.")
    t={"requester":requesters,"department":departments,"budget":budgets,"purchase_request":requests,"request_line":lines,
       "supplier":suppliers,"rfq":rfqs,"supplier_quote":quotes,"approval":approvals,"purchase_order":pos,"delivery":deliveries,
       "workflow_event":events,"ground_truth":gt}
    for n,rows in t.items(): write_csv(out/"csv"/f"{n}.csv",rows); write_json(out/"json"/f"{n}.json",rows)
    make_db(out/"procurement.db",t)
    # Also export a portable SQL seed script for reviewers who want plain SQL.
    db_tmp = out/"procurement.db"
    sql_dump = out/"procurement_seed.sql"
    con = sqlite3.connect(db_tmp)
    sql_dump.write_text("\\n".join(con.iterdump()) + "\\n", encoding="utf-8")
    con.close()
    from .validator import validate_tables
    report=validate_tables(t)
    manifest={"seed":seed,"scale":scale_name,"counts":{k:len(v) for k,v in t.items()},"files":{}}
    for p in sorted((out/"csv").glob("*.csv")): manifest["files"][str(p.relative_to(out))]=sha(p)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (out/"validation_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (out/"validation_summary.md").write_text("# Validation Summary\n\n"+f"**{'PASS' if report['passed'] else 'FAIL'}** — {report['passed_checks']}/{report['total_checks']} checks passed.\n",encoding="utf-8")
    return t,report
