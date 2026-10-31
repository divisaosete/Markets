"""Build the only directory allowed to become the GitHub Pages artifact."""
import argparse,html,json,os
from pathlib import Path
from urllib.parse import urlparse
from backend.pages import validate_document,ROOT
ASSETS=['index.html','styles.css','bootstrap.js','app.js','chart.js','data.js','static-data.js','direct-fx.js','offline.js','analytics.js','presentation.js','polling.js','catalog.js','favicon.svg','DATA-LICENSES.md']

def public_api(value):
    if not value:return ''
    u=urlparse(value)
    if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.hostname in ('localhost','127.0.0.1','::1'):raise ValueError('PUBLIC_API_BASE must be a public HTTPS URL without credentials/query/fragment')
    try:
        import ipaddress
        if not ipaddress.ip_address(u.hostname).is_global:raise ValueError('Non-public API address')
    except ValueError as e:
        if str(e)=='Non-public API address':raise
    return value.rstrip('/')+'/'

def build(output,api_base='',dynamic_fx=True):
    output=Path(output).resolve()
    if output in (ROOT.resolve(),(ROOT/'public').resolve()) or output.is_symlink():raise ValueError('Unsafe build output')
    allowed=set(ASSETS+['config.js','data/market-data.json','.nojekyll'])
    if output.exists():
        if any(p.is_symlink() or p.is_file() and p.stat().st_nlink>1 for p in output.rglob('*')):raise ValueError('Links in build output are refused')
        unexpected=[str(p.relative_to(output)) for p in output.rglob('*') if p.is_file() and p.relative_to(output).as_posix() not in allowed]
        if unexpected:raise ValueError('Output contains unexpected files; choose an empty directory')
    api_base=public_api(api_base)
    data=validate_document(json.loads((ROOT/'public/data/market-data.json').read_text(encoding='utf8')))
    output.mkdir(parents=True,exist_ok=True)
    for name in ASSETS:
        source=ROOT/'public'/name
        if source.is_symlink():raise ValueError('Symlink in static source')
        content=source.read_bytes()
        if name=='index.html':
            connect="'self'"+(' https://api.frankfurter.dev' if dynamic_fx else '')+((' '+urlparse(api_base).scheme+'://'+urlparse(api_base).netloc) if api_base else '')
            policy=f"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src {connect}; object-src 'none'; base-uri 'none'; form-action 'none'"
            content=content.replace(b'<head>',('<head>\n<meta http-equiv="Content-Security-Policy" content="'+html.escape(policy,quote=True)+'">').encode())
        (output/name).write_bytes(content)
    (output/'config.js').write_text('export const config = Object.freeze('+json.dumps({'apiBase':api_base,'timeoutMs':15000,'staticData':True,'dynamicFx':dynamic_fx})+');\n',encoding='utf8')
    (output/'data').mkdir(exist_ok=True)
    (output/'data/market-data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n',encoding='utf8')
    (output/'.nojekyll').write_text('')
    return {'files':len(allowed),'available':sum(bool(r['points']) for r in data['series']),'output':str(output)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'_site');p.add_argument('--api-base',default=os.getenv('PUBLIC_API_BASE',''));p.add_argument('--no-direct-fx',action='store_true');args=p.parse_args()
    print(json.dumps(build(args.output,args.api_base,not args.no_direct_fx and os.getenv('ENABLE_DIRECT_FX','true')=='true'),ensure_ascii=False))
if __name__=='__main__':main()
