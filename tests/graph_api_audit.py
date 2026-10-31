"""Actual local HTTP history + restart proof, no market fixtures."""
import sys,json,time,hashlib
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parent.parent
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def main():
    results=[];base='http://127.0.0.1:8011/'
    for id in ['usdbrl','eurbrl','eurusd','gbpusd','usdjpy','selic','USA-NY.GDP.MKTP.CD','yield-Estados Unidos-10']:
        period='MAX' if id.startswith('USA-') else '1A'
        with urlopen(base+'api/series?'+urlencode({'id':id,'period':period}),timeout=30) as response:row=json.load(response)['series'][0]
        points=row['points'];assert points,id
        assert points==sorted(points,key=lambda p:p['date']),id
        assert points[-1]==row['latest'],id
        canonical=[{**p,'date':p['date'][:4]} for p in points] if id.startswith('USA-') else points
        results.append({'id':id,'period':period,'observations':len(points),'latest':row['latest'],'unit':row['unit'],'source':row['source'],'points_sha256':digest(canonical)})
    asset_checks=[]
    for name in ['app.js','chart.js','styles.css']:
        with urlopen(base+name,timeout=30) as response:raw=response.read()
        matches=raw==(ROOT/'public'/name).read_bytes();assert matches,name
        asset_checks.append({'file':name,'matches_current_workspace':matches})
    report={'executed_at':time.time(),'method':'HTTP local com cache operacional, sem fixtures. GET registra demanda; não equivale a consulta externa individual.','series':results,'served_files':asset_checks}
    target=ROOT/'docs/graficos-api-real.json'
    if '--after-restart' in sys.argv:
        before=json.loads(target.read_text(encoding='utf8'))
        report['persistence']=[{'id':r['id'],'same_observations_after_restart':r['points_sha256']==next(old['points_sha256'] for old in before['series'] if old['id']==r['id'])} for r in results]
        assert all(r['same_observations_after_restart'] for r in report['persistence'])
        target=ROOT/'docs/graficos-persistencia-real.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(target.name+': '+str(len(results))+' séries reais verificadas; arquivos atuais confirmados.')
if __name__=='__main__':main()
