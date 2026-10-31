"""Deployment checks; prints variable names only, never secret values."""
import os
from urllib.parse import urlsplit
def errors(env):
    issues=[]
    if len(env.get('ADMIN_TOKEN',''))<32:issues.append('ADMIN_TOKEN: configure segredo aleatório com pelo menos 32 caracteres')
    origins=[s.strip() for s in env.get('ALLOWED_ORIGINS','').split(',') if s.strip()]
    if not origins:issues.append('ALLOWED_ORIGINS: configure origem HTTPS real da aplicação')
    for origin in origins:
        p=urlsplit(origin)
        if p.scheme!='https' or not p.hostname or p.path or p.query or p.fragment or p.username or '*' in origin:issues.append('ALLOWED_ORIGINS: apenas origens HTTPS exatas, sem caminho ou wildcard')
    frames=env.get('FRAME_ANCESTORS',"'self'").split()
    if not frames:issues.append('FRAME_ANCESTORS: política vazia não é permitida')
    for item in frames:
        if item in ("'self'","'none'"):continue
        p=urlsplit(item)
        if p.scheme!='https' or not p.hostname or p.path or p.query or p.fragment or '*' in item:issues.append('FRAME_ANCESTORS: configure política válida com origem HTTPS exata')
    if "'none'" in frames and len(frames)>1:issues.append('FRAME_ANCESTORS: none não pode ser combinado com outras origens')
    if not os.path.isabs(env.get('CACHE_PATH','')):issues.append('CACHE_PATH: use caminho absoluto em volume persistente')
    return issues
def main():
    from pathlib import Path
    from backend.environment import load_env
    from backend.config import ROOT
    load_env(ROOT/'.env')
    issues=errors(os.environ)
    for item in issues:print(item)
    if issues:raise SystemExit(1)
    print('Configuração estrutural válida. DNS, TLS, persistência e WordPress ainda exigem teste no ambiente real.')
if __name__=='__main__':main()
