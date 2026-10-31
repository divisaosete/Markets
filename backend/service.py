import time,os,logging,json
from datetime import date,timedelta,datetime,timezone
from backend.catalog import BY_ID
from backend.config import PERIODS,INTERVALS,MAX_AGE_DAYS
from backend.validation import normalize_points
from backend.providers import fetch,Unavailable

def utc():return datetime.now(timezone.utc).isoformat()
def reference_points(a,points):
    # Old WDI caches encoded an annual reference as January 1. Restore its year,
    # not a publication date or a daily observation; validate duplicate conflicts.
    if a['provider']=='worldbank' and a['category']=='macro':
        return normalize_points([{**p,'date':p['date'][:4]} for p in points])
    return points
def start_date(period,end=None,category=''):
    end=end or date.today()
    if period=='MAX':return date(1960 if category=='macro' else 1999 if category=='fx' else 1900,1,1)
    # Annual observations use their reference year, including the current year.
    return end-timedelta(days=PERIODS[period])

class Service:
    def __init__(self,cache,fetcher=fetch):self.cache=cache;self.fetcher=fetcher
    def series(self,id,period='1A',refresh=False):
        a=BY_ID[id]
        result=self._series(id,period,refresh)
        from backend.availability import classify
        diagnosis=classify(a,result)
        result['reason']=diagnosis['reason']
        if not result.get('points') and diagnosis['reason'] in ('credential_required','license_required'):
            result.update(status='unavailable',message=diagnosis['detail'])
        result.setdefault('source',diagnosis['source'] or a['provider'])
        result.setdefault('source_url',diagnosis['source_url'])
        return result
    def covering_record(self,id,period):
        """Reuse only a window that covers the request, never extrapolate history."""
        a=BY_ID[id];begin=start_date(period,category=a['category']);candidates=[]
        keys={f'series:{id}:{other}':other for other in PERIODS if other!=period}
        with self.cache.connect() as db:
            records=db.execute('SELECT key,payload,updated FROM cache WHERE key IN ('+','.join('?' for _ in keys)+')',list(keys)).fetchall()
        for key,payload,updated in records:
            other=keys[key];data=json.loads(payload)
            if not data.get('points'):continue
            data['points']=reference_points(a,data['points'])
            collected=date.fromtimestamp(updated)
            coverage=date.fromisoformat(data['window_start']) if data.get('window_start') else start_date(other,collected,a['category'])
            if coverage>begin:continue
            filtered=[p for p in data['points'] if (begin.year<=int(p['date'])<=date.today().year if len(p['date'])==4 else begin.isoformat()<=p['date'][:10]<=date.today().isoformat())]
            derived={k:v for k,v in data.items() if k not in ('latest','change','change_pct','change_bps','change_reference')}
            derived.update(points=filtered,status='ok' if filtered else 'empty',cache_source_period=other)
            candidates.append((derived,updated))
        return max(candidates,key=lambda r:r[1]) if candidates else None
    def _series(self,id,period='1A',refresh=False):
        a=BY_ID[id];key=f'series:{id}:{period}';old=self.cache.get(key)
        if old is None or not old[0].get('points'):
            covering=self.covering_record(id,period)
            if covering and (old is None or covering[0].get('points')):old=covering
        if not refresh:
            with self.cache.connect() as db:failure=db.execute('SELECT error FROM jobs WHERE key=?',(key,)).fetchone()
            if failure and failure[0]:
                if old:
                    result=self.decorate(a,old);result.update(status='stale',message=failure[0]);return result
                return {'id':id,'status':'unavailable','message':failure[0],'points':[],'unit':a['unit']}
            if old:return self.decorate(a,old)
            return {'id':id,'status':'pending' if a['provider']!='licensed' else 'unavailable','message':'Aguardando sincronização' if a['provider']!='licensed' else 'Requer feed licenciado configurado','points':[],'unit':a['unit']}
        owner=self.cache.claim(key)
        if not owner:return self.decorate(a,old) if old else {'id':id,'status':'pending','points':[]}
        try:
            end=date.today();begin=start_date(period,end,a['category'])
            if a['provider']=='bcb':begin=max(begin,date(1996,7,1))
            if a['provider']=='treasury':begin=max(begin,date(1990,1,1))
            if a['provider']=='coingecko' and period=='MAX':begin=end-timedelta(days=int(os.getenv('COINGECKO_HISTORY_DAYS','365')))
            data=self.fetcher(a,begin,end)
            data['points']=normalize_points(data['points'],end)
            data.update(id=id,synced_at=utc(),status='ok' if data['points'] else 'empty',window_start=begin.isoformat(),window_end=end.isoformat())
            if not self.cache.publish(key,owner,data,INTERVALS[a['category']]):
                return self.series(id,period)
            logging.getLogger('markets.worker').info('sync key=%s points=%s',key,len(data['points']))
            return self.decorate(a,self.cache.get(key))
        except Exception as e:
            message=str(e) if isinstance(e,Unavailable) else 'Fonte indisponível ou resposta inválida'
            self.cache.finish(key,owner,INTERVALS[a['category']],message,retry_after=getattr(e,'retry_after',0))
            logging.getLogger('markets.worker').warning('sync_failed key=%s kind=%s',key,type(e).__name__)
            if old:
                result=self.decorate(a,old);result.update(status='stale',message=message);return result
            return {'id':id,'status':'unavailable','message':message,'points':[],'unit':a['unit']}
    def decorate(self,a,record):
        data,updated=record;data=dict(data);data['status']='stale' if time.time()-updated>INTERVALS[a['category']]*2 else data['status']
        pts=reference_points(a,data['points']);data['points']=pts;data['latest']=pts[-1] if pts else None
        if pts:
            raw=pts[-1]['date']
            if len(raw)==4:ref=date(int(raw),12,31)
            elif len(raw)==7:
                import calendar
                y,m=map(int,raw.split('-'));ref=date(y,m,calendar.monthrange(y,m)[1])
            else:ref=date.fromisoformat(raw[:10])
            age=max(0,(date.today()-ref).days)
            limit=int(data.get('max_age_days',45 if data.get('reference')=='monthly' else MAX_AGE_DAYS[a['category']]))
            data['reference_age_days']=age;data['reference_stale']=age>limit
            if age>limit:data['status']='stale';data['message']='Referência antiga; não representa cotação atual'
        if len(pts)>1:
            delta=pts[-1]['value']-pts[-2]['value'];data['change']=delta;data['change_pct']=delta/pts[-2]['value']*100 if pts[-2]['value'] else None
            data['change_reference']=pts[-2]['date']
            if a['category'] in ('rates','yields'):data['change_bps']=delta*100
        return data
    def queue(self,id,period):self.queue_many([(id,period)])
    def queue_many(self,requests):
        now=time.time()
        with self.cache.connect() as db:
            db.executemany('INSERT OR REPLACE INTO cache VALUES (?,?,?)',[(f'demand:{id}:{period}',json.dumps({'id':id,'period':period}),now) for id,period in requests])

def compare(series,mode='base100',alignment='exact'):
    nonempty=[s for s in series if s.get('points')]
    if not nonempty:return []
    if alignment=='daily':
        aligned=[]
        for s in nonempty:
            daily={}
            for p in sorted(s['points'],key=lambda p:p['date']):
                # Select the final real observation for each UTC date; never interpolate.
                d=p['date'][:10] if len(p['date'])>=10 else p['date']
                daily[d]={'date':d,'value':p['value'],'observed_at':p['date']}
            aligned.append({**s,'points':list(daily.values())})
        nonempty=aligned
    common=set(p['date'] for p in nonempty[0]['points'])
    for s in nonempty[1:]:common &= {p['date'] for p in s['points']}
    dates=sorted(common)
    if not dates:return []
    out=[]
    for s in nonempty:
        values={p['date']:p['value'] for p in s['points']};base=values[dates[0]]
        if mode in ('base100','percent') and base==0:continue
        points=[]
        for d in dates:
            v=values[d]
            value=v/base*100 if mode=='base100' else (v/base-1)*100 if mode=='percent' else v-base if mode=='pp' else (v-base)*100
            points.append({'date':d,'value':value})
        out.append({'id':s['id'],'points':points})
    return out
