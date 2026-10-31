"""Validation shared by all providers; no interpolation or OHLC synthesis."""
import math,re
from datetime import date,datetime,timezone
def canonical_date(value):
    if not isinstance(value,str):raise ValueError('Data inválida')
    if re.fullmatch(r'\d{4}',value):
        if not 1900<=int(value)<=date.today().year:raise ValueError('Ano inválido')
        return value
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):return date.fromisoformat(value).isoformat()
    if re.fullmatch(r'\d{4}-\d{2}',value):
        date.fromisoformat(value+'-01')
        return value
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    if not parsed.tzinfo:raise ValueError('Timestamp sem fuso')
    return parsed.astimezone(timezone.utc).isoformat()
def number(value):
    if isinstance(value,bool):raise ValueError('Valor inválido')
    value=float(value)
    if not math.isfinite(value):raise ValueError('Valor não finito')
    return value
def normalize_points(points,end=None):
    end=end or date.today();unique={}
    if not isinstance(points,list) or len(points)>100000:raise ValueError('Série inválida ou excessiva')
    for raw in points:
        d=canonical_date(raw['date']);p={'date':d,'value':number(raw['value'])}
        if d[:10]>end.isoformat():raise ValueError('Observação futura')
        fields=['open','high','low','close']
        if any(k in raw for k in fields):
            if not all(k in raw for k in fields):raise ValueError('OHLC incompleto')
            p.update({k:number(raw[k]) for k in fields})
            if p['low']>min(p['open'],p['close']) or p['high']<max(p['open'],p['close']) or p['low']>p['high'] or p['value']!=p['close']:raise ValueError('OHLC inconsistente')
        if d in unique and unique[d]!=p:raise ValueError('Observações conflitantes na mesma data')
        unique[d]=p
    return sorted(unique.values(),key=lambda p:p['date'])
def policy_metadata(record):
    from urllib.parse import urlparse
    out={}
    def official_url(value):
        u=urlparse(value)
        if u.scheme!='https' or not u.hostname or u.username:raise ValueError('Link de fonte inválido')
        return value
    if record.get('decision_date'):
        d=canonical_date(record['decision_date'])
        if len(d)!=10 or d>date.today().isoformat():raise ValueError('Data de decisão inválida')
        out['decision_date']=d
    if record.get('next_meeting'):
        meeting=record['next_meeting'];d=canonical_date(meeting['date'])
        if len(d)<10:raise ValueError('Próxima reunião exige dia confirmado')
        if meeting.get('status')!='confirmed':raise ValueError('Reunião não confirmada não pode ser próxima reunião oficial')
        out['next_meeting']={'date':d,'status':'confirmed','source_url':official_url(meeting['source_url'])}
    if record.get('decisions'):
        if len(record['decisions'])>5000:raise ValueError('Histórico de decisões excessivo')
        rows={}
        for r in record['decisions']:
            d=canonical_date(r['date']);value=number(r['value'])
            if len(d)!=10 or d>date.today().isoformat():raise ValueError('Decisão futura inválida')
            rows[d]={'date':d,'value':value,'source_url':official_url(r.get('source_url',record['source_url']))}
            if r.get('previous_value') is not None:rows[d]['change_bps']=(value-number(r['previous_value']))*100
        out['decisions']=sorted(rows.values(),key=lambda r:r['date'],reverse=True)
    return out
