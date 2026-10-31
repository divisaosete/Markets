"""Consistent SQLite backup/restore; restore refuses to overwrite any existing DB."""
import argparse,sqlite3
from contextlib import closing
from pathlib import Path
from backend.config import DB
def backup(source,destination):
    source=Path(source);destination=Path(destination)
    if not source.is_file():raise ValueError('Banco de origem inexistente')
    if destination.exists():raise ValueError('Destino já existe; use um novo nome')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(f'{source.resolve().as_uri()}?mode=ro',uri=True)) as src,closing(sqlite3.connect(destination)) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Backup inválido')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['backup','restore']);parser.add_argument('file');parser.add_argument('--database',default=str(DB));args=parser.parse_args()
    if args.action=='backup':backup(args.database,args.file)
    else:backup(args.file,args.database)
    print('Operação concluída com verificação de integridade.')
if __name__=='__main__':main()
