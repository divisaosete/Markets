"""Build release from an explicit allowlist; never package runtime data or secrets."""
from pathlib import Path
import zipfile,hashlib
ROOT=Path(__file__).resolve().parent
def build():
    output=ROOT/'New-Era-Markets-GitHub-Corrigido.zip'
    # Root entry is the actual dashboard, sharing the existing public modules/data.
    entry=(ROOT/'public/index.html').read_text(encoding='utf8')
    for asset in ('favicon.svg','styles.css','bootstrap.js'):
        entry=entry.replace('./'+asset,'./public/'+asset)
    (ROOT/'index.html').write_text(entry,encoding='utf8')
    (ROOT/'.nojekyll').write_text('',encoding='utf8')
    dirs=['backend','public','tests','.github/workflows']
    names=['README.md','FONTES-DE-DADOS.md','GUIA-GITHUB-PAGES.md','RELATORIO-OTIMIZACAO.md','.env.example','.gitignore','requirements.txt','requirements-dev.txt','package.json','run.py','tools_finalize.py','INICIAR-NEW-ERA.cmd','VISUALIZAR-BETA.cmd','deploy/wordpress.html','deploy/wordpress-link.html','docs/RELATORIO-DE-TESTES.md','docs/dependency-audit-pages.json','docs/pages-collection-results.json','docs/pages-browser-results.json','docs/pages-publication-manifest.json']
    files=[ROOT/n for n in names]
    files += [ROOT/n for n in ('index.html','.nojekyll','INSTRUCOES-PUBLICACAO.md','RELATORIO-CORRECAO-PAGES.md')]
    files += [p for d in dirs for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    if len(files)!=len(set(files)):raise ValueError('Duplicate package entry')
    for p in files:
        if not p.is_file() or p.is_symlink():raise ValueError('Missing file or symlink')
        if p.name.startswith('.env') and p.name!='.env.example':raise ValueError('Private environment file')
        if p.suffix.lower() in ('.zip','.bak','.log','.db','.sqlite','.sqlite3','.pem','.key','.pfx','.p12'):raise ValueError('Private or generated file')
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            if p.is_symlink():raise ValueError('Refusing symlink in release')
            z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert 'index.html' in z.namelist() and 'public/index.html' in z.namelist() and '.github/workflows/pages.yml' in z.namelist()
        assert not any('/var/' in n or '/.vendor/' in n or n.endswith('/.env') for n in z.namelist())
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.sha256').write_text(digest+'  '+output.name+'\n')
    print(f'{output.name}: {len(files)} files, {output.stat().st_size} bytes, SHA256 {digest}')
if __name__=='__main__':build()
