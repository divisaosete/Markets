"""Local live HTTP evidence from the actual cache, no quote fixtures or writes."""
import json,time
from pathlib import Path
from urllib.request import urlopen
def main():
    base='http://127.0.0.1:8011/';results=[]
    for route in ['api/health','api/series?id=usdbrl&period=1M','api/series?id=selic&period=1M','api/series?id=ibov&period=1A','api/availability']:
        start=time.monotonic()
        with urlopen(base+route,timeout=30) as response:data=json.load(response)
        if route.endswith('health'):detail=data
        elif 'instruments' in data:detail={'instruments':len(data['instruments'])}
        else:detail=[{k:s.get(k) for k in ('id','status','reason','latest','cache_source_period')}|{'observations':len(s['points'])} for s in data['series']]
        results.append({'route':route,'elapsed_seconds':round(time.monotonic()-start,3),'result':detail})
    report={'executed_at':time.time(),'method':'HTTP local, cache operacional real, sem fixtures; GET pode registrar demanda de sincronização.','results':results}
    Path('docs/http-cache-real.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
