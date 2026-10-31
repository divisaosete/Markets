"""Explicit network smoke tests, separate from deterministic unit tests."""
import json,time
from datetime import date,timedelta
from backend.providers import fetch
from backend.catalog import BY_ID
from backend.calendar import fetch_calendar
def main():
    output=[]
    for id in ['selic','usdbrl','USA-NY.GDP.MKTP.CD','bitcoin','fed','ecb','boc',*[f'yield-Estados Unidos-{n}' for n in [2,5,10,30]]]:
        begin=date.today()-timedelta(days=30 if id in ('selic','usdbrl','bitcoin') else 3653 if id.startswith('USA-') else 365)
        try:
            result=fetch(BY_ID[id],begin,date.today());points=result['points'];output.append({'id':id,'status':'PASS' if points else 'EMPTY','observations':len(points),'latest':points[-1] if points else None,'source':result['source']})
        except Exception as e:
            from backend.providers import Unavailable
            output.append({'id':id,'status':'DEPENDENCY' if isinstance(e,Unavailable) else 'FAIL','error':str(e) if isinstance(e,Unavailable) else type(e).__name__})
    try:
        result=fetch_calendar()
        for source in result['sources']:output.append({'id':'calendar-'+source['id'],'status':'PASS' if source['status']=='ok' else 'FAIL','events':source['events'],'error':source.get('error')})
    except Exception as e:output.append({'id':'calendar-official','status':'FAIL','error':type(e).__name__})
    from pathlib import Path
    Path('docs/live-results.json').write_text(json.dumps({'executed_at':time.time(),'results':output},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
