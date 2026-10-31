"""Static-root + public-root resource checks, and optional API outage test server."""
import sys,json,threading,re,time,argparse
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urljoin,urlparse
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from backend.config import ROOT
class References(HTMLParser):
    def __init__(self):super().__init__();self.resources=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link' and a.get('href'):self.resources.append(a['href'])
        if tag=='script' and a.get('src'):self.resources.append(a['src'])
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def static_checks():
    results=[]
    for name,folder,path in [('project-root',ROOT,'/public/index.html'),('public-root',ROOT/'public','/index.html')]:
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'+path
        try:
            with urlopen(base,timeout=10) as response:html=response.read().decode('utf8');assert response.status==200
            parser=References();parser.feed(html);todo=[urljoin(base,r) for r in parser.resources];seen=set()
            while todo:
                url=todo.pop()
                if url in seen:continue
                seen.add(url)
                with urlopen(url,timeout=10) as r:
                    raw=r.read();assert r.status==200;ctype=r.headers.get('Content-Type','')
                    if urlparse(url).path.endswith('.css'):assert 'text/css' in ctype
                    if urlparse(url).path.endswith('.js'):
                        assert 'javascript' in ctype or 'ecmascript' in ctype
                        text=raw.decode('utf8')
                        for spec in re.findall(r"(?:from\s+|import\()['\"]([^'\"]+)['\"]",text):todo.append(urljoin(url,spec))
                results.append({'mode':name,'resource':urlparse(url).path,'status':200})
        finally:server.shutdown();server.server_close();thread.join(timeout=3)
    (ROOT/'docs'/'static-loading-results.json').write_text(json.dumps({'executed_at':time.time(),'type':'HTTP estático real, sem backend e sem fixtures de cotações','results':results},ensure_ascii=False,indent=2),encoding='utf8')
    print(f'{len(results)} recursos essenciais verificados nos dois tipos de raiz estática.')
def failure_server(port):
    from backend.app import app
    from waitress import serve
    def outage(env,start):
        if env.get('PATH_INFO','').startswith('/api/'):
            data=json.dumps({'error':'Serviço de dados indisponível. Inicie o backend para consultar informações atualizadas.'},ensure_ascii=False).encode()
            start('503 Service Unavailable',[('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(data)))]);return [data]
        return app(env,start)
    print('Servidor exclusivo de teste: todos os endpoints de dados retornam 503.',flush=True)
    serve(outage,host='127.0.0.1',port=port,threads=4)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--serve-failure',action='store_true');parser.add_argument('--port',type=int,default=5553);args=parser.parse_args()
    if args.serve_failure:failure_server(args.port)
    else:static_checks()
