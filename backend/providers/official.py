"""Official keyless adapters; preserve instrument identity and observed dates."""
import csv,io
from datetime import date
from urllib.parse import urlencode
from xml.etree import ElementTree

TREASURY_URL='https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml'
ECB_URL='https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV'
BOC_URL='https://www.bankofcanada.ca/valet/observations/V39079/json'

def parse_treasury(text,tenor,start,end):
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():raise ValueError('XML com entidades recusado')
    root=ElementTree.fromstring(text);points=[];field=f'BC_{int(tenor)}YEAR'
    if int(tenor) not in (2,5,10,30):raise ValueError('Prazo não suportado')
    for entry in root.iter():
        if entry.tag.rsplit('}',1)[-1]!='entry':continue
        values={node.tag.rsplit('}',1)[-1]:node.text for node in entry.iter()}
        d=(values.get('NEW_DATE') or '')[:10];v=values.get(field)
        if d and v not in (None,'') and start.isoformat()<=d<=end.isoformat():points.append({'date':date.fromisoformat(d).isoformat(),'value':float(v)})
    return points

def treasury(a,start,end,get_text,cache=None):
    start=max(start,date(1990,1,1));points=[]
    for year in range(start.year,end.year+1):
        key=f'upstream:treasury:{year}';old=cache.get(key) if cache else None
        import time
        ttl=3600 if year==end.year else 604800
        if old and time.time()-old[1]<ttl:text=old[0]
        else:
            text=get_text(TREASURY_URL+'?'+urlencode({'data':'daily_treasury_yield_curve','field_tdr_date_value':year}))
            # Validate the payload before sharing it with other maturities.
            parse_treasury(text,a['tenor'],start,end)
            if cache:cache.put(key,text)
        points.extend(parse_treasury(text,a['tenor'],start,end))
    return {'points':points,'source':'US Treasury · Daily Par Yield Curve','source_url':'https://home.treasury.gov/treasury-daily-interest-rate-xml-feed','unit':'%','frequency':'diária','reference':'Treasury nominal par yield curve (CMT)','tenor':a['tenor'],'country':a['country']}

def ecb(a,start,end,get_text):
    q=urlencode({'startPeriod':max(start,date(1999,1,1)).isoformat(),'endPeriod':end.isoformat(),'format':'csvdata'})
    rows=list(csv.DictReader(io.StringIO(get_text(ECB_URL+'?'+q))))
    points=[]
    for row in rows:
        if row.get('KEY') and row['KEY']!='FM.D.U2.EUR.4F.KR.DFR.LEV':raise ValueError('Série BCE divergente')
        d=row.get('TIME_PERIOD');value=row.get('OBS_VALUE')
        if d and value not in (None,''):points.append({'date':d,'value':float(value)})
    return {'points':points,'source':'Banco Central Europeu · Data API','source_url':'https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV','unit':'% a.a.','frequency':'datas de alteração de vigência','reference':'policy_change','max_age_days':36525,'instrument':a['instrument'],'publication_note':'A data da observação é a vigência publicada, não uma data de decisão inferida.'}

def boc(a,start,end,get_json):
    data=get_json(BOC_URL+'?'+urlencode({'start_date':max(start,date(1990,1,1)).isoformat(),'end_date':end.isoformat()}))
    label=data.get('seriesDetail',{}).get('V39079',{}).get('label','').lower()
    if 'target' not in label or 'overnight' not in label:raise ValueError('Identidade monetária BoC não confirmada')
    points=[{'date':r['d'],'value':float(r['V39079']['v'])} for r in data.get('observations',[]) if r.get('V39079',{}).get('v') not in ('',None)]
    return {'points':points,'source':'Bank of Canada · Valet','source_url':'https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/','unit':'%','frequency':'diária','instrument':a['instrument'],'reference':'Target for the overnight rate'}
