"""Generate a copy/paste embed using the actual deployment URL; no active default URL."""
import argparse,html
from pathlib import Path
from urllib.parse import urlsplit
def embed(url):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:raise ValueError('Informe a URL HTTPS real, sem credenciais')
    safe=html.escape(url,quote=True)
    return f'''<div style="width:100%;min-width:0;">
  <iframe src="{safe}" title="New Era Markets" loading="lazy" referrerpolicy="strict-origin-when-cross-origin"
    style="display:block;width:100%;height:85vh;min-height:650px;border:0;border-radius:8px;" allow="fullscreen"></iframe>
</div>
<p><a href="{safe}" target="_blank" rel="noopener noreferrer">Abrir New Era Markets em nova aba ↗</a></p>
'''
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',required=True);parser.add_argument('--output',default='deploy/wordpress-configurado.html');args=parser.parse_args()
    Path(args.output).write_text(embed(args.url),encoding='utf8');print('HTML gerado. Verifique a URL e a política frame-ancestors antes de incorporar.')
if __name__=='__main__':main()
