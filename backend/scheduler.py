"""Independent persistent worker: python -m backend.scheduler"""
import signal,time,logging,os,threading
from backend.cache import Cache
from backend.catalog import ASSETS
from backend.service import Service
from backend.config import INTERVALS
from backend.calendar import fetch_calendar
log=logging.getLogger('markets.worker')
HEARTBEAT_SECONDS=30

def reconcile_connectors(cache):
    # Reconcile only known adapter changes; never clear an active task lease or provider quota.
    signatures=[('calendar','bls+boe:1')]+[(a['id'],a['provider']+':'+a['code']) for a in ASSETS if a['provider'] in ('treasury','ecb','boc')]
    for id,signature in signatures:
        key='connector:'+id;old=cache.get(key)
        if old and old[0]==signature:continue
        with cache.connect() as db:
            if id=='calendar':db.execute('UPDATE jobs SET next=0,failures=0,error=NULL WHERE key=? AND (owner IS NULL OR until<?)',('calendar',time.time()))
            else:db.execute('UPDATE jobs SET next=0,failures=0,error=NULL WHERE key LIKE ? AND (owner IS NULL OR until<?)',('series:'+id+':%',time.time()))
        cache.put(key,signature)
def tick(cache,service,keep_running=lambda:True):
    owner=cache.claim('_scheduler',180)
    if not owner:return False
    done=threading.Event()
    def heartbeat():
        while not done.wait(HEARTBEAT_SECONDS):
            try:
                if not cache.renew('_scheduler',owner,180):return
                cache.put('worker',{'heartbeat':time.time()})
            except Exception:log.warning('heartbeat_failed')
    pulse=threading.Thread(target=heartbeat,daemon=True);pulse.start()
    try:
        return _cycle(cache,service,owner,keep_running)
    finally:
        done.set();pulse.join(timeout=2);cache.finish('_scheduler',owner,0)
def _cycle(cache,service,scheduler_owner,keep_running):
    cache.put('worker',{'heartbeat':time.time()})
    owner=cache.claim('calendar',120)
    if owner:
        try:
            data=fetch_calendar()
            failed={s['id'] for s in data.get('sources',[]) if s['status']!='ok'}
            old=cache.get('calendar')
            if failed and old:
                data['events'].extend({**e,'source_stale':True} for e in old[0].get('events',[]) if e.get('source_id', 'bls' if e.get('source')=='BLS' else '') in failed)
                data['events']=list({e['id']:e for e in data['events']}.values())
            cache.publish('calendar',owner,data,INTERVALS['calendar'])
            log.info('calendar_sync events=%s',len(data['events']))
        except Exception as e:
            cache.finish('calendar',owner,INTERVALS['calendar'],'Fontes oficiais de calendário indisponíveis; consulte as agendas oficiais')
            log.warning('calendar_failed kind=%s',type(e).__name__)
    # Each asset/period has a persistent lock and backoff. Active demands are served first.
    with cache.connect() as db:
        demands=[r[0] for r in db.execute("SELECT key FROM cache WHERE key LIKE 'demand:%' AND updated>?",(time.time()-86400,))]
    jobs=[]
    for key in demands:
        value=cache.get(key)[0];jobs.append((value['id'],value['period']))
    jobs.extend((a['id'],'MAX' if a['category']=='macro' else '1A') for a in ASSETS if a['provider']!='licensed' or os.getenv('LICENSED_FEED_PATH'))
    for id,period in dict.fromkeys(jobs):
        if not keep_running():break
        if not cache.renew('_scheduler',scheduler_owner,180):return False
        service.series(id,period,True)
        cache.put('worker',{'heartbeat':time.time()})
    return True
def main():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    from pathlib import Path
    from backend.processes import parent_alive
    stop_file=os.getenv('LOCAL_STOP_FILE','')
    cache=Cache();service=Service(cache);running=True
    def active():return running and not (stop_file and Path(stop_file).exists()) and parent_alive(os.getenv('LOCAL_PARENT_PID',''))
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    reconcile_connectors(cache)
    while active():
        try:tick(cache,service,active)
        except Exception:log.error('Falha no ciclo; nova tentativa no próximo ciclo')
        for _ in range(30):
            if not active():break
            time.sleep(1)
if __name__=='__main__':main()
