import argparse, json, tempfile, shutil
from pathlib import Path
from .generator import generate

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    g=sub.add_parser("generate"); g.add_argument("--scale",choices=["starter","full"],default="starter"); g.add_argument("--seed",type=int,default=20261022); g.add_argument("--out")
    v=sub.add_parser("validate"); v.add_argument("--input",required=True)
    r=sub.add_parser("reproducibility"); r.add_argument("--seed",type=int,default=20261022)
    sub.add_parser("demo")
    a=p.parse_args()
    if a.cmd=="generate":
        out=a.out or f"artifacts/{a.scale}"; _,rep=generate(a.scale,a.seed,out); print(json.dumps(rep,indent=2))
    elif a.cmd=="validate":
        print((Path(a.input)/"validation_report.json").read_text())
    elif a.cmd=="reproducibility":
        d1=tempfile.mkdtemp(); d2=tempfile.mkdtemp()
        try:
            generate("starter",a.seed,d1); generate("starter",a.seed,d2)
            m1=json.loads((Path(d1)/"manifest.json").read_text()); m2=json.loads((Path(d2)/"manifest.json").read_text())
            ok=m1["files"]==m2["files"]; print("REPRODUCIBLE:",ok)
            if not ok: raise SystemExit(1)
        finally: shutil.rmtree(d1,ignore_errors=True); shutil.rmtree(d2,ignore_errors=True)
    else:
        print("Request -> approval -> RFQ -> 3+ quotes -> comparison -> award -> PO -> delivery events")

if __name__=="__main__": main()
