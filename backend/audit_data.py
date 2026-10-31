"""Reproducible per-instrument report from real cache/configuration; never embeds keys."""
import json,csv
from pathlib import Path
def main():
    root=Path(__file__).resolve().parent.parent
    from backend.environment import load_env
    load_env(root/'.env')
    from backend.cache import Cache
    from backend.service import Service
    from backend.availability import report
    data=report(Service(Cache()))
    (root/'docs'/'DISPONIBILIDADE-POR-ATIVO.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    fields=['id','name','category','country','provider','identifier','status','reason','detail','unit','currency','frequency','latest_reference','synced_at','source','source_url']
    with (root/'docs'/'DISPONIBILIDADE-POR-ATIVO.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(data['instruments'])
    from collections import Counter
    print(json.dumps(dict(Counter(r['reason'] for r in data['instruments'])),ensure_ascii=False))
if __name__=='__main__':main()
