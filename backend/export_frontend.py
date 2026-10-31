"""Export identities and official source directory, never prices or secrets."""
import json
from backend.catalog import ASSETS,OVERVIEW
from backend.calendar import DIRECTORY
from backend.config import ROOT
def generate():
    values={'ASSETS':ASSETS,'OVERVIEW':OVERVIEW,'DIRECTORY':DIRECTORY}
    text='// Gerado por python -m backend.export_frontend. Metadados públicos; nenhuma cotação.\n'
    for name,value in values.items():text+=f'export const {name} = '+json.dumps(value,ensure_ascii=False,indent=2)+';\n'
    return text
def main():
    (ROOT/'public'/'catalog.js').write_text(generate(),encoding='utf8')
    print('Catálogo local exportado sem dados de mercado.')
if __name__=='__main__':main()
