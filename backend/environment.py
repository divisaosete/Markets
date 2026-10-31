"""Minimal .env loader: literal KEY=value only, never executes or expands text."""
import os,re
def load_env(path):
    if not path.is_file():return
    for number,line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
        text=line.strip()
        if not text or text.startswith('#'):continue
        key,separator,value=text.partition('=')
        if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*',key.strip()):
            raise ValueError(f'.env: linha {number} inválida')
        value=value.strip()
        if value.startswith(('"',"'")) and value.endswith(value[0]):value=value[1:-1]
        os.environ.setdefault(key.strip(),value)
