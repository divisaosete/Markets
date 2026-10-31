"""BLS official iCalendar; unsupported authorities remain explicit directory links."""
import re
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from html.parser import HTMLParser
BOE_URL='https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates'
DIRECTORY=[
 {'country':'Brasil','name':'Copom','url':'https://www.bcb.gov.br/controleinflacao/calendariocopom'},
 {'country':'Brasil','name':'IPCA, PIB, desemprego · IBGE','url':'https://www.ibge.gov.br/calendario-de-divulgacoes.html'},
 {'country':'Estados Unidos','name':'FOMC','url':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'},
 {'country':'Estados Unidos','name':'CPI e Payroll · BLS','url':'https://www.bls.gov/schedule/'},
 {'country':'Estados Unidos','name':'PIB e PCE · BEA','url':'https://www.bea.gov/news/schedule'},
 {'country':'Zona do Euro','name':'BCE','url':'https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html'},
 {'country':'Zona do Euro','name':'Inflação e PIB · Eurostat','url':'https://ec.europa.eu/eurostat/news/release-calendar'},
 {'country':'Reino Unido','name':'Bank of England · datas confirmadas MPC','url':'https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates'},
 {'country':'Reino Unido','name':'Inflação e PIB · ONS','url':'https://www.ons.gov.uk/releasecalendar'},
 {'country':'Japão','name':'Bank of Japan','url':'https://www.boj.or.jp/en/mopo/'},
 {'country':'Japão','name':'Inflação · Statistics Bureau','url':'https://www.stat.go.jp/english/'},
 {'country':'Japão','name':'PIB · Cabinet Office / ESRI','url':'https://www.esri.cao.go.jp/en/sna/menu.html'},
 {'country':'China','name':'PBoC','url':'https://www.pbc.gov.cn/en/'},
 {'country':'China','name':'Inflação e PIB · NBS','url':'https://www.stats.gov.cn/english/'}]
def parse_ics(text):
    text=re.sub(r'\r?\n[ \t]','',text)
    events={}
    for block in text.split('BEGIN:VEVENT')[1:]:
        fields={}
        for line in block.split('END:VEVENT')[0].splitlines():
            if ':' in line:
                k,v=line.split(':',1);fields[k]=v
        key=next((k for k in fields if k.split(';')[0]=='DTSTART'),None)
        if not key:continue
        raw=fields[key]
        if len(raw)==8:
            when=datetime.strptime(raw,'%Y%m%d').date().isoformat();zone='data sem horário'
        elif raw.endswith('Z'):
            when=datetime.strptime(raw,'%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).isoformat();zone='UTC'
        elif 'TZID=' in key:
            from zoneinfo import ZoneInfo
            try: tz=ZoneInfo(key.split('TZID=')[1])
            except Exception:continue
            when=datetime.strptime(raw,'%Y%m%dT%H%M%S').replace(tzinfo=tz).isoformat();zone=key.split('TZID=')[1]
        else:continue # Never guess a floating timezone.
        uid=fields.get('UID',when+fields.get('SUMMARY',''));recurrence=next((v for k,v in fields.items() if k.split(';')[0]=='RECURRENCE-ID'),'')
        identifier=uid+(':'+recurrence if recurrence else '')
        sequence=int(fields.get('SEQUENCE','0'));modified=fields.get('LAST-MODIFIED',fields.get('DTSTAMP',''))
        event={'id':identifier,'date':when,'timezone':zone,'country':'Estados Unidos','name':fields.get('SUMMARY','Publicação BLS').replace('\\,',',').replace('\\n',' '),'status':{'CANCELLED':'cancelado','TENTATIVE':'estimado'}.get(fields.get('STATUS'),'confirmado'),'result':None,'source_url':'https://www.bls.gov/schedule/','source':'BLS','sequence':sequence,'last_modified':modified}
        old=events.get(identifier)
        if not old or (sequence,modified)>=(old['sequence'],old['last_modified']):events[identifier]=event
    return sorted(events.values(),key=lambda e:e['date'])
def fetch_bls():
    with urlopen(Request('https://www.bls.gov/schedule/news_release/bls.ics',headers={'User-Agent':'NewEraMarkets/1.0'}),timeout=20) as r:
        raw=r.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError('Calendar too large')
    return [{**e,'source_id':'bls'} for e in parse_ics(raw.decode('utf-8-sig'))]

class CalendarText(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style') and self.skip:self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

def parse_boe(html):
    parser=CalendarText();parser.feed(html);text=' '.join(' '.join(parser.parts).split())
    sections=list(re.finditer(r'\b(20\d{2}) confirmed dates\b',text,re.I));events={}
    months=['January','February','March','April','May','June','July','August','September','October','November','December'];weekdays=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    pattern=r'\b('+ '|'.join(weekdays)+r')\s+(\d{1,2})\s+('+ '|'.join(months)+r')\b'
    for i,section in enumerate(sections):
        year=int(section.group(1));block=text[section.end():sections[i+1].start() if i+1<len(sections) else len(text)]
        block=re.split(r'Monetary Policy Committee Reports|Current Bank Rate|MPC voting history',block,flags=re.I)[0]
        # Only dates under an explicit confirmed-year heading; no inferred times.
        for match in re.finditer(pattern,block,re.I):
            when=datetime(year,next(j+1 for j,m in enumerate(months) if m.lower()==match.group(3).lower()),int(match.group(2))).date()
            if weekdays[when.weekday()].lower()!=match.group(1).lower():raise ValueError('Dia da semana BoE inconsistente')
            key='boe-mpc-'+when.isoformat();events[key]={'id':key,'date':when.isoformat(),'timezone':'data sem horário','country':'Reino Unido','name':'Bank of England · MPC','status':'confirmado','result':None,'source_url':BOE_URL,'source':'Bank of England','source_id':'boe'}
    if not sections or not events:raise ValueError('Estrutura do calendário BoE não reconhecida')
    return sorted(events.values(),key=lambda e:e['date'])

def fetch_boe():
    from backend.providers import request
    return parse_boe(request(BOE_URL,headers={'Accept':'text/html'},output='text'))

def fetch_calendar():
    events=[];sources=[]
    for id,name,fetcher in [('bls','BLS',fetch_bls),('boe','Bank of England',fetch_boe)]:
        try:
            result=fetcher();events.extend(result);sources.append({'id':id,'name':name,'status':'ok','events':len(result)})
        except Exception as e:sources.append({'id':id,'name':name,'status':'unavailable','events':0,'error':type(e).__name__})
    if not any(s['status']=='ok' for s in sources):raise RuntimeError('Fontes oficiais de calendário indisponíveis')
    failed=[s['name'] for s in sources if s['status']!='ok']
    return {'events':events,'directory':DIRECTORY,'sources':sources,'partial':bool(failed),'limitation':'Sincronização automática: BoE (datas confirmadas sem horário inferido) e BLS, conforme disponibilidade. Demais órgãos e resultados: consulte links oficiais.'+(' Fonte indisponível: '+', '.join(failed)+'.' if failed else '')}
