"""Public source readiness, without credential values or private filesystem paths."""
import os,time
from backend.catalog import ASSETS
def classify(a,s):
    p=a['provider'];message=s.get('message','');state=s['status']
    if state in ('ok','stale') and s.get('points'):
        reason=('reference_stale' if s.get('reference_stale') else 'cached_after_failure') if state=='stale' else 'available';detail=message or 'Observações reais preservadas no cache; consulte referência e sincronização.'
    elif p in ('fred','coingecko') and not os.getenv('FRED_API_KEY' if p=='fred' else 'COINGECKO_API_KEY'):
        reason='credential_required';detail='Chave do provedor não configurada no backend.'
    elif p=='licensed' and (not os.getenv('LICENSED_FEED_PATH') or os.getenv('LICENSED_REDISTRIBUTION_APPROVED')!='yes'):
        reason='license_required';detail='Feed autorizado e licença de redistribuição necessários; identificador do fornecedor ainda não validado.'
    elif 'Orçamento' in message or 'limite de uso' in message:
        reason='quota_limited';detail='Consulta adiada por quota ou pausa do provedor.'
    elif state=='pending':reason='awaiting_sync';detail='Aguardando coleta pelo agendador.'
    elif state=='empty':reason='no_observations';detail='Fonte retornou janela sem observações; não houve preenchimento.'
    elif state=='unavailable':reason='source_failure';detail=message or 'A fonte não retornou dados válidos.'
    elif state=='stale':reason='reference_stale' if s.get('reference_stale') else 'cached_after_failure';detail=message or 'Cache atrasado; data de referência continua visível.'
    else:reason='available';detail='Dados disponíveis na frequência declarada, sem garantia de tempo real.'
    return {'id':a['id'],'name':a['name'],'category':a['category'],'country':a['country'],'provider':p,'identifier':a['code'] or None,'unit':s.get('unit',a['unit']),'currency':a.get('currency'),'instrument':a.get('instrument',a.get('reference')),'frequency':s.get('frequency',a.get('frequency')),'status':state,'reason':reason,'detail':detail,'source':s.get('source'),'source_url':s.get('source_url',a.get('source_url')),'latest_reference':s.get('latest',{}).get('date') if s.get('latest') else None,'synced_at':s.get('synced_at')}
def report(service):
    rows=[]
    from backend.service import Service
    with service.cache.read_session() as cache:
        reader=Service(cache)
        for a in ASSETS:rows.append(classify(a,reader.series(a['id'],'MAX' if a['category']=='macro' else '1A')))
    return {'generated_at':time.time(),'instruments':rows,'note':'Diagnóstico de leitura do cache e configuração; não dispara coleta nem revela chaves.'}
