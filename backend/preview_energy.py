"""Explicit local-only energy preview. Not a Pages build or deploy target."""
import argparse,functools,json
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from backend.build_pages import build,ROOT
from backend.energy_validation import DEFAULT,validate_local

def prepare_preview(data_path=DEFAULT,output=None):
    data_path=Path(data_path).resolve()
    if not data_path.is_relative_to((ROOT/'var').resolve()):raise ValueError('Local input must stay in var/')
    local=validate_local(json.loads(data_path.read_text(encoding='utf8')))
    target=Path(output or ROOT/'var/energy-preview/Markets').resolve()
    if not target.is_relative_to((ROOT/'var').resolve()):raise ValueError('Local preview output must stay in var/')
    build(target,dynamic_fx=False)
    path=target/'data/market-data.json';data=json.loads(path.read_text(encoding='utf8'))
    restricted={r['id']:r for r in local['series']}
    data['series']=[restricted.get(r['id'],r) for r in data['series']]
    data['generated_at']=local['generated_at']
    # Same UI, but no public builder accepts this dataset: validate_document rejects it.
    path.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False),encoding='utf8')
    index=target/'index.html'
    banner='<div role="note" style="position:sticky;top:0;z-index:5;padding:12px;background:#593e12;color:white;text-align:center">VALIDAÇÃO LOCAL · Dados de energia com redistribuição não confirmada · NÃO PUBLICAR</div>'
    index.write_text(index.read_text(encoding='utf8').replace('<body>','<body>'+banner),encoding='utf8')
    app=target/'app.js'
    app.write_text(app.read_text(encoding='utf8').replace('Dados publicados','Validação local').replace('JSON publicado · atualização periódica','Arquivo local · não publicar'),encoding='utf8')
    labels=target/'data.js'
    labels.write_text(labels.read_text(encoding='utf8').replace('Dados publicados','Validação local'),encoding='utf8')
    return target

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8081);args=p.parse_args()
    target=prepare_preview()
    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(target.parent))
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    print(f'LOCAL ONLY / NÃO PUBLICAR: http://127.0.0.1:{args.port}/Markets/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
