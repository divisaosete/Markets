import json,mimetypes,time,os,secrets,threading
from urllib.parse import parse_qs
from collections import defaultdict,deque
from pathlib import Path
from backend.config import ROOT,PERIODS,ORIGINS,FRAME_ANCESTORS,ADMIN_TOKEN
from backend.catalog import ASSETS,BY_ID,OVERVIEW
from backend.cache import Cache
from backend.service import Service,compare
from backend.calendar import DIRECTORY
cache=Cache();service=Service(cache)
_requests=defaultdict(deque);_mutex=threading.Lock()
def limited(ip):
    with _mutex:
        now=time.monotonic()
        # Bound memory even with many client addresses.
        if len(_requests)>=10000:
            for k in list(_requests):
                if not _requests[k] or now-_requests[k][-1]>60:del _requests[k]
        if ip not in _requests and len(_requests)>=10000:return True
        q=_requests[ip]
        while q and now-q[0]>60:q.popleft()
        if len(q)>=max(1,int(os.getenv('RATE_LIMIT_PER_MINUTE','120'))):return True
        q.append(now);return False
def app(env,start_response):
    origin=env.get('HTTP_ORIGIN','');path=env.get('PATH_INFO','/');status='200 OK'
    headers=[('X-Content-Type-Options','nosniff'),('Referrer-Policy','strict-origin-when-cross-origin'),('Content-Security-Policy',f"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors {FRAME_ANCESTORS}; base-uri 'none'; object-src 'none'"),('Cache-Control','no-store')]
    def reply(data,code='200 OK',ctype='application/json; charset=utf-8'):
        body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False,allow_nan=False).encode()
        start_response(code,headers+[('Content-Type',ctype),('Content-Length',str(len(body)))]);return [body]
    if path.startswith('/api/') and origin and origin not in ORIGINS:return reply({'error':'Origem não permitida'},'403 Forbidden')
    if origin and origin in ORIGINS:headers.extend([('Access-Control-Allow-Origin',origin),('Vary','Origin')])
    if env.get('REQUEST_METHOD')!='GET':return reply({'error':'Método não permitido'},'405 Method Not Allowed')
    if path.startswith('/api/') and limited(env.get('REMOTE_ADDR','unknown')):return reply({'error':'Limite de requisições'},'429 Too Many Requests')
    try:
        raw_query=env.get('QUERY_STRING','')
        if len(raw_query)>8192:return reply({'error':'Consulta excessiva'},'414 URI Too Long')
        q=parse_qs(raw_query,max_num_fields=12,keep_blank_values=True)
        if path.startswith('/api/'):
            allowed={'id','period'} if path=='/api/series' else {'ids','period','mode','alignment'} if path=='/api/compare' else {'ids','period'} if path=='/api/snapshot' else set()
            if any(k not in allowed or len(v)!=1 or not v[0] for k,v in q.items()):return reply({'error':'Parâmetros desconhecidos, vazios ou duplicados'},'400 Bad Request')
            if path=='/api/series' and 'id' not in q or path=='/api/compare' and 'ids' not in q:return reply({'error':'Ativo obrigatório'},'400 Bad Request')
        period=q.get('period',['1A'])[0]
        if period not in PERIODS:return reply({'error':'Período inválido'},'400 Bad Request')
        if path=='/api/catalog':return reply({'assets':ASSETS,'overview':OVERVIEW,'periods':list(PERIODS)})
        if path=='/api/availability':
            from backend.availability import report
            return reply(report(service))
        if path=='/api/health':
            worker=cache.get('worker');return reply({'api':'ok','worker':'active' if worker and time.time()-worker[1]<180 else 'offline','worker_last_seen':worker[1] if worker else None})
        if path=='/api/admin/diagnostics':
            token=env.get('HTTP_AUTHORIZATION','')
            if not ADMIN_TOKEN or not secrets.compare_digest(token.encode('utf-8'),('Bearer '+ADMIN_TOKEN).encode('utf-8')):return reply({'error':'Não autorizado'},'401 Unauthorized')
            return reply(cache.diagnostics())
        if path=='/api/calendar':
            record=cache.get('calendar')
            job=cache.job('calendar')
            return reply({**(record[0] if record else {'events':[],'directory':DIRECTORY,'limitation':'BLS e BoE ainda não sincronizados; demais fontes por consulta oficial'}),'synced_at':record[1] if record else None,'stale':not record or time.time()-record[1]>172800 or bool(job and job['error']) or bool(record and record[0].get('partial')),'error':job['error'] if job else None})
        if path in ('/api/series','/api/snapshot','/api/compare'):
            ids=q.get('ids',q.get('id',[','.join(OVERVIEW)]))[0].split(',')
            if not 1<=len(ids)<=(5 if path=='/api/compare' else 1 if path=='/api/series' else 60) or len(set(ids))!=len(ids) or any(id not in BY_ID for id in ids):return reply({'error':'Ativos inválidos, duplicados ou limite excedido'},'400 Bad Request')
            mode=q.get('mode',['base100'])[0]
            alignment=q.get('alignment',['daily'])[0]
            if alignment not in ('daily','exact'):return reply({'error':'Alinhamento inválido'},'400 Bad Request')
            if mode not in ('base100','percent','pp','bps'):return reply({'error':'Modo inválido'},'400 Bad Request')
            if mode in ('pp','bps') and any(BY_ID[id]['category'] not in ('rates','yields') for id in ids):return reply({'error':'Pontos percentuais e base exigem taxas'},'400 Bad Request')
            requests=[(id,'MAX' if path=='/api/snapshot' and BY_ID[id]['category']=='macro' else period) for id in ids]
            service.queue_many(requests)
            with cache.read_session() as snapshot:
                reader=Service(snapshot)
                rows=[reader.series(id,actual) for id,actual in requests]
            return reply({'series':rows,'comparison':compare(rows,mode,alignment) if path=='/api/compare' else None,'alignment':'Datas UTC comuns; última observação real de cada dia por fonte, sem sincronismo intradiário ou interpolação' if alignment=='daily' else 'Interseção exata de datas/horários; sem interpolação','period':period})
        if path.startswith('/api/'):return reply({'error':'Não encontrado'},'404 Not Found')
        target=(ROOT/'public'/('index.html' if path=='/' else path.lstrip('/'))).resolve()
        if not target.is_relative_to((ROOT/'public').resolve()) or not target.is_file():return reply({'error':'Não encontrado'},'404 Not Found')
        body=target.read_bytes()
        if target.name=='index.html':
            body=body.replace(b'<meta name="markets-api-base" content="">',b'<meta name="markets-api-base" content="/api/">')
        return reply(body,ctype=mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
    except (ValueError,KeyError):return reply({'error':'Parâmetros inválidos'},'400 Bad Request')
    except Exception:return reply({'error':'Falha interna; consulte o administrador'},'500 Internal Server Error')
def main():
    from waitress import serve
    proxy=os.getenv('TRUSTED_PROXY','').strip();options={}
    if proxy:
        import ipaddress
        ipaddress.ip_address(proxy) # Only one explicitly trusted IP; wildcard is refused.
        options={'trusted_proxy':proxy,'trusted_proxy_count':1,'trusted_proxy_headers':{'x-forwarded-for','x-forwarded-proto'}}
    serve(app,host=os.getenv('HOST','127.0.0.1'),port=int(os.getenv('PORT','8000')),threads=6,**options)
if __name__=='__main__':main()
