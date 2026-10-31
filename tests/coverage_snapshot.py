"""Read the real worker cache; report missing data without inventing prices."""
import json,csv,time
from pathlib import Path
from backend.catalog import ASSETS
from backend.cache import Cache
from backend.service import Service
def main():
    cache=Cache();service=Service(cache);report=[]
    for a in ASSETS:
        period='MAX' if a['category']=='macro' else '1A';s=service.series(a['id'],period)
        report.append({'id':a['id'],'name':a['name'],'category':a['category'],'country':a['country'],'provider':a['provider'],'code':a['code'],'status':s['status'],'observations':len(s['points']),'source':s.get('source'),'synced_at':s.get('synced_at'),'latest_reference':s.get('latest',{}).get('date') if s.get('latest') else None,'message':s.get('message')})
    Path('docs/worker-coverage.json').write_text(json.dumps({'executed_at':time.time(),'method':'Leitura do cache do worker real, sem fixtures. Não representa teste direto de todas as APIs.','instruments':report},ensure_ascii=False,indent=2),encoding='utf8')
    with open('docs/CATALOGO-AUDITADO.csv','w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['id','name','category','country','provider','code','currency','exchange','unit','reference','instrument','tenor'],extrasaction='ignore');writer.writeheader();writer.writerows(ASSETS)
    from collections import Counter
    print(json.dumps(dict(Counter(r['status'] for r in report)),ensure_ascii=False))
if __name__=='__main__':main()
