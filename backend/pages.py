"""Public, allowlisted data export. Never exports a private SQLite cache or env."""
import argparse,hashlib,json,os,re,time,tempfile
from pathlib import Path
from datetime import date,datetime,timedelta,timezone
from backend.catalog import ASSETS,BY_ID
from backend.validation import normalize_points

ROOT=Path(__file__).resolve().parent.parent
DEFAULT=ROOT/'public/data/market-data.json'
POLICIES={
 'bcb':('ODbL-1.0','https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom',86400),
 'fx':('ECB reuse with attribution','https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html',21600),
 'worldbank':('CC-BY-4.0 + World Bank terms','https://datacatalog.worldbank.org/public-licenses',604800),
 'ecb':('ECB reuse with attribution','https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html',86400),
 'boc':('Bank of Canada reproduction terms','https://www.bankofcanada.ca/terms/',86400),
 'treasury':('US government data; attribution','https://home.treasury.gov/treasury-daily-interest-rate-xml-feed',21600),
}
GDP_CODES={'NY.GDP.MKTP.CD','NY.GDP.MKTP.KD.ZG'}
FIELDS={'id','name','symbol','category','country','provider','source','source_url','unit','currency','frequency','reference','instrument','license','license_url','attribution','transformations','delivery','update_type','expected_interval_seconds','status','reason','message','points','latest','synced_at','window_start','window_end','max_age_days'}

def approved(a):return a['provider'] in POLICIES and (a['provider']!='worldbank' or a['code'] in GDP_CODES)
def empty(a):
    p=a['provider'];policy=POLICIES.get(p)
    reason='publication_review' if p=='eia' or p=='worldbank' and not approved(a) else 'credential_required' if p in ('fred','coingecko') else 'license_required' if p=='licensed' else 'awaiting_sync'
    message={'publication_review':'Redistribuição desta série ainda em revisão para a beta pública.','credential_required':'Coleta em servidor/Actions e revisão dos direitos exigem credencial; nunca inserir chave no navegador.','license_required':'Fonte licenciada e autorização de exibição pública necessárias.','awaiting_sync':'Primeira coleta pública ainda não concluída.'}[reason]
    if p=='eia':message='Histórico disponível apenas para validação local. Publicação suspensa até confirmar os direitos dos dados Refinitiv/LSEG distribuídos pela EIA.'
    currency=a.get('currency') or (a['code'].split('/')[1] if p=='fx' else 'USD' if a['unit'].startswith('USD') else None)
    return {'id':a['id'],'name':a['name'],'symbol':a['code'] or a['id'],'category':a['category'],'country':a.get('country',''),'provider':p,'unit':a['unit'],'currency':currency,'frequency':a.get('frequency','conforme fonte'),'reference':a.get('reference',''),'instrument':a.get('instrument',''),'delivery':'static','update_type':'periodic_release' if a['category']=='macro' else 'daily_reference','license':policy[0] if policy and approved(a) else 'Pendente de autorização/revisão','license_url':policy[1] if policy else '', 'source':{'bcb':'Banco Central do Brasil · SGS','fx':'Frankfurter · BCE','worldbank':'World Bank · WDI','ecb':'Banco Central Europeu','boc':'Bank of Canada · Valet','treasury':'US Treasury','eia':'U.S. Energy Information Administration · EIA'}.get(p,p),'source_url':a.get('source_url',''),'attribution':'Fonte indicada por série; New Era Labs não é endossado pelos provedores.','transformations':'Datas normalizadas; recortes sem interpolação; comparações calculadas na interface.','expected_interval_seconds':policy[2] if policy else None,'status':'unavailable','reason':reason,'message':message,'points':[],'latest':None,'synced_at':None}

def validate_row(r):
    if not isinstance(r,dict) or set(r)-FIELDS or r.get('id') not in BY_ID:raise ValueError('Invalid public row')
    points=normalize_points(r.get('points',[]))
    if points!=r['points'] or r.get('latest')!=(points[-1] if points else None):raise ValueError('Invalid public observations')
    if points and not approved(BY_ID[r['id']]):raise ValueError('Unapproved publication')
    legacy_empty_eia = BY_ID[r['id']]['provider']=='eia' and not points and r['unit']==''
    if r['unit']!=BY_ID[r['id']]['unit'] and BY_ID[r['id']]['provider']!='ecb' and not legacy_empty_eia:raise ValueError('Unit mismatch')
    if r.get('delivery')!='static' or r.get('update_type') not in ('daily_reference','periodic_release') or r.get('status') not in ('ok','stale','unavailable'):raise ValueError('Invalid public availability metadata')
    for key in ('source_url','license_url'):
        if r.get(key):
            from urllib.parse import urlparse
            u=urlparse(r[key])
            if u.scheme!='https' or not u.hostname or u.username or u.query or u.fragment:raise ValueError('Unsafe public URL')

def validate_document(data):
    if set(data)-{'schema_version','generated_at','series','note'} or data.get('schema_version')!=1:raise ValueError('Invalid public schema')
    rows=data.get('series');seen=set()
    if not isinstance(rows,list) or len(rows)!=len(ASSETS):raise ValueError('Incomplete public catalog')
    for r in rows:
        validate_row(r)
        if r['id'] in seen:raise ValueError('Duplicate public row')
        seen.add(r['id'])
    return data

def atomic_json(path,data):
    raw=(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if path.exists() and path.read_bytes()==raw:return False
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.collect-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)
    return True

def collect(output=DEFAULT,fetcher=None,now=None,ids=None,force=False,state_path=None):
    output=Path(output);now=now or datetime.now(timezone.utc);today=now.date();stamp=now.isoformat()
    if fetcher is None:
        from backend.providers import fetch
        fetcher=fetch
    previous=validate_document(json.loads(output.read_text(encoding='utf8'))) if output.exists() else None
    old={r['id']:r for r in previous['series']} if previous else {}
    state_path=Path(state_path) if state_path else ROOT/'var/pages-state.json'
    try:state=json.loads(state_path.read_text())
    except (OSError,ValueError):state={}
    reports=[];rows=[]
    for a in ASSETS:
        before=old.get(a['id'],empty(a))
        r=dict(before)
        r['currency']=r.get('currency') or empty(a)['currency']
        if not approved(a) or ids is not None and a['id'] not in ids:rows.append(r);continue
        if not force and now.timestamp()-state.get(a['id'],0)<POLICIES[a['provider']][2]:rows.append(r);continue
        state[a['id']]=now.timestamp()
        try:
            start=date(1960,1,1) if a['category']=='macro' else today-timedelta(days=1826)
            if a['provider']=='ecb':start=date(1999,1,1)
            data=fetcher(a,start,today);pts=normalize_points(data['points'],today)
            if not pts:raise ValueError('Empty upstream history')
            if a['provider']=='worldbank':pts=normalize_points([{**p,'date':p['date'][:4]} for p in pts],today)
            r=empty(a);r.update({k:data[k] for k in ('source','source_url','unit','frequency','reference','instrument','max_age_days','attribution') if k in data})
            # Merge valid prior observations; a rolling upstream window must not erase history.
            pts=normalize_points(list({p['date']:p for p in before['points']+pts}.values()),today)
            r.update(status='ok',reason='available',message='Referência publicada; não é preço em tempo real.',points=pts,latest=pts[-1],window_start=start.isoformat(),window_end=today.isoformat(),synced_at=stamp)
            validate_row(r)
            comparable=lambda v:{k:x for k,x in v.items() if k not in ('synced_at','window_start','window_end')}
            if comparable(r)==comparable(before):r=before
            reports.append({'id':a['id'],'result':'PASS','observations':len(pts)})
        except Exception as e:
            # Do not expose exceptions/URLs that may contain provider credentials.
            r=dict(before)
            r.update(status='stale' if r['points'] else 'unavailable',reason='cached_after_failure' if r['points'] else 'source_failure',message='Último histórico válido preservado após falha da fonte.' if r['points'] else 'A fonte não retornou um histórico válido nesta coleta.')
            reports.append({'id':a['id'],'result':'FAIL','kind':type(e).__name__,'preserved':len(r['points'])})
        rows.append(r)
    data={'schema_version':1,'generated_at':previous['generated_at'] if previous and previous['series']==rows else stamp,'series':rows,'note':'Dados reais de fontes identificadas; atualização periódica, sem garantia de tempo real. Licenças independentes por série.'}
    validate_document(data);changed=atomic_json(output,data);atomic_json(state_path,state)
    return {'changed':changed,'results':reports,'available':sum(bool(r['points']) for r in rows),'series':len(rows)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=DEFAULT);p.add_argument('--ids',default='');p.add_argument('--force',action='store_true');p.add_argument('--validate-only',action='store_true');args=p.parse_args()
    if args.validate_only:validate_document(json.loads(args.output.read_text(encoding='utf8')));print('Public JSON valid');return
    # Dedicated collector state; never export or copy the local application's DB.
    os.environ.setdefault('CACHE_PATH',str(ROOT/'var/pages.sqlite3'))
    ids=set(args.ids.split(',')) if args.ids else None
    if ids and not ids<=set(BY_ID):raise SystemExit('Unknown instrument')
    result=collect(args.output,ids=ids,force=args.force)
    atomic_json(ROOT/'var/pages-collection-report.json',result)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
