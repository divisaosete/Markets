"""Local-only energy validation. Never authorizes publication or writes public/.

python -m backend.energy_validation --force
The data and source comparison report remain in ignored var/.
"""
import argparse,json
from datetime import date,datetime,timezone
from pathlib import Path
from backend.catalog import BY_ID
from backend.pages import ROOT,atomic_json,empty
from backend.providers.eia import SERIES
from backend.validation import normalize_points

DEFAULT=ROOT/'var/energy-validation.json'

def validate_local(data):
    if data.get('publication')!='local_validation_only':raise ValueError('Local validation marker required')
    rows=data.get('series',[])
    if len(rows)!=len(SERIES) or {r['id'] for r in rows}!=set(SERIES):raise ValueError('Incomplete energy validation data')
    for r in rows:
        points=normalize_points(r['points'])
        if points!=r['points'] or r['latest']!=(points[-1] if points else None):raise ValueError('Invalid local history')
        if r['unit']!=SERIES[r['id']][3] or r['currency']!='USD':raise ValueError('Invalid local unit/currency')
    return data

def collect_energy(output=DEFAULT,fetcher=None,now=None,force=False):
    output=Path(output).resolve()
    # This entry point cannot be used to place unapproved observations in public artifacts.
    private=(ROOT/'var').resolve()
    if not output.is_relative_to(private):raise ValueError('Energy validation output must stay under var/')
    now=now or datetime.now(timezone.utc)
    old=validate_local(json.loads(output.read_text(encoding='utf8'))) if output.exists() else None
    before={r['id']:r for r in old['series']} if old else {}
    if fetcher is None:
        from backend.providers import request
        from backend.providers.eia import fetch as fetch_eia
        fetcher=lambda a,start,end:fetch_eia(a,start,end,request)
    rows=[];results=[]
    for id in SERIES:
        row=before.get(id,empty(BY_ID[id]))
        last=row.get('synced_at')
        if not force and last and (now-datetime.fromisoformat(last)).total_seconds()<86400:
            rows.append(row);results.append({'id':id,'result':'SKIP'});continue
        try:
            fresh=fetcher(BY_ID[id],date(1980,1,1),now.date())
            points=normalize_points(fresh['points'],now.date())
            if not points or fresh.get('unit',row['unit'])!=SERIES[id][3]:raise ValueError('Invalid upstream history')
            prior={p['date']:p for p in row['points']}
            # Compare independent samples before merging; report stays local.
            samples=[points[i] for i in sorted({0,len(points)//2,len(points)-1})]
            compared=[{'date':p['date'],'source_value':p['value'],'cached_value':prior.get(p['date'],{}).get('value'),'matches':prior.get(p['date'])==p} for p in samples]
            points=normalize_points(list({p['date']:p for p in row['points']+points}.values()),now.date())
            row={**empty(BY_ID[id]),**{k:fresh[k] for k in ('source','source_url','reference','frequency','instrument','attribution') if k in fresh},
                 'points':points,'latest':points[-1],'synced_at':now.isoformat(),'status':'ok',
                 'reason':'local_validation_only','license':'Redistribuição pública não confirmada',
                 'message':'Somente validação local; não autorizado para publicação.'}
            results.append({'id':id,'result':'PASS','observations':len(points),'samples':compared})
        except Exception as error:
            row={**row,'status':'stale' if row['points'] else 'unavailable','reason':'cached_after_failure' if row['points'] else 'source_failure',
                 'message':'Falha da fonte; histórico local anterior preservado.'}
            results.append({'id':id,'result':'FAIL','kind':type(error).__name__,'preserved':len(row['points'])})
        rows.append(row)
    data={'schema_version':1,'generated_at':now.isoformat(),'publication':'local_validation_only','series':rows}
    validate_local(data);atomic_json(output,data)
    report={'publication':'local_validation_only','results':results}
    atomic_json(output.with_name(output.stem+'-report.json'),report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');args=p.parse_args()
    result=collect_energy(force=args.force)
    print(json.dumps({'results':[{k:v for k,v in r.items() if k!='samples'} for r in result['results']]}))

if __name__=='__main__':main()
