"""Serve only the Pages artifact below /repo/, never a Python data backend."""
import functools,json,re,tempfile,threading,time,sys,shutil
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.request import urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from backend.build_pages import build,ASSETS,ROOT
def main():
    results=[]
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);build(root/'Markets')
        fallback=root/'fallback'/'Markets';fallback.mkdir(parents=True)
        shutil.copyfile(ROOT/'index.html',fallback/'index.html')
        shutil.copyfile(ROOT/'.nojekyll',fallback/'.nojekyll')
        shutil.copytree(ROOT/'public',fallback/'public')
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
        try:
            for name in ASSETS+['config.js','data/market-data.json','.nojekyll']:
                with urlopen(base+'/Markets/'+name,timeout=15) as response:
                    raw=response.read();assert response.status==200
                    if name=='index.html':assert b'./bootstrap.js' in raw and b'Content-Security-Policy' in raw
                    if name=='config.js':assert b'"apiBase": ""' in raw and b'127.0.0.1' not in raw
                    if name=='data/market-data.json':
                        data=json.loads(raw);assert any(r['points'] for r in data['series'])
                    results.append({'resource':'/Markets/'+name,'status':200})
            for name in ['index.html','.nojekyll']+['public/'+p.relative_to(ROOT/'public').as_posix() for p in (ROOT/'public').rglob('*') if p.is_file()]:
                with urlopen(base+'/fallback/Markets/'+name,timeout=15) as response:
                    raw=response.read();assert response.status==200
                    if name=='index.html':
                        assert b'New Era Markets | New Era Labs' in raw and b'./public/bootstrap.js' in raw and b'./public/styles.css' in raw
                    results.append({'resource':'/fallback/Markets/'+name,'status':200})
            for name in ['api/health','backend/config.py','.env','var/markets.sqlite3']:
                try:urlopen(base+'/Markets/'+name,timeout=15);raise AssertionError('Unexpected exposure '+name)
                except HTTPError as e:assert e.code==404;results.append({'resource':'/Markets/'+name,'status':404})
        finally:server.shutdown();server.server_close();thread.join(5)
    report={'executed_at':time.time(),'type':'HTTP estático real em subdiretório, sem backend permanente nem fixtures de preços','results':results}
    (ROOT/'docs/pages-static-http.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(str(len(results))+' verificações estáticas reais aprovadas; backend e arquivos privados ausentes.')
if __name__=='__main__':main()
