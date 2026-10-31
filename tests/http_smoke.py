"""Actual local HTTP/Waitress smoke checks; does not seed market data."""
import json,threading,tempfile,time
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from waitress import create_server
from backend import app as web
from backend.cache import Cache
from backend.service import Service
def main():
    results=[]
    with tempfile.TemporaryDirectory() as folder:
        oldcache,oldservice=web.cache,web.service
        web.cache=Cache(Path(folder)/'http.db');web.service=Service(web.cache)
        server=create_server(web.app,host='127.0.0.1',port=0,threads=2)
        thread=threading.Thread(target=server.run,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.effective_port)
        def check(name,path,status=200,headers=None,contains=None):
            try:response=urlopen(Request(base+path,headers=headers or {}),timeout=10)
            except HTTPError as e:response=e
            with response:
                body=response.read();actual=response.code;assert actual==status,(name,actual,status)
                if contains:assert contains.encode() in body
                assert response.headers.get('X-Content-Type-Options')=='nosniff'
                assert 'frame-ancestors' in response.headers.get('Content-Security-Policy','')
                results.append({'test':name,'status':'PASS','http_status':actual})
        try:
            check('public per-instrument availability','/api/availability',contains='ibov')
            check('frontend initialization','/',contains='New Era Markets');check('frontend module asset','/app.js',contains='Poller');check('catalog','/api/catalog',contains='Ibovespa');check('health','/api/health',contains='offline');check('series read and queue','/api/series?id=usdbrl',contains='pending');check('protected diagnostic','/api/admin/diagnostics',401);check('invalid period','/api/series?id=selic&period=bad',400);check('restrictive CORS','/api/catalog',403,{'Origin':'https://untrusted.invalid'});check('no environment exposure','/.env',404);check('calendar fallback','/api/calendar',contains='BLS');check('iframe policy','/',contains='New Era');check('static traversal','/../backend/config.py',404)
        finally:
            server.task_dispatcher.shutdown();server.close();thread.join(timeout=5);web.cache,web.service=oldcache,oldservice
    report={'executed_at':time.time(),'type':'HTTP real local, dados de mercado não simulados','results':results}
    Path('docs/http-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
