"""A static file preview only: no API, worker or private directory exposure."""
import argparse,functools,webbrowser
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from backend.build_pages import build,ROOT
def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);p.add_argument('--prefix',default='');p.add_argument('--no-browser',action='store_true');args=p.parse_args()
    if args.prefix and (not args.prefix.isascii() or not args.prefix.replace('-','').isalnum()):raise SystemExit('Invalid preview prefix')
    base=ROOT/'var/pages-preview';target=base/args.prefix if args.prefix else ROOT/'_site'
    build(target)
    directory=base if args.prefix else target
    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(directory))
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    except OSError:raise SystemExit('Porta ocupada: encerre a visualização anterior ou escolha --port.')
    url=f'http://127.0.0.1:{args.port}/'+(args.prefix+'/' if args.prefix else '')
    print('New Era Markets — Beta estática: '+url+' | Ctrl+C para encerrar.',flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
