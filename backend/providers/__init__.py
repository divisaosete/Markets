"""Only configured providers, fixed upstream hosts and bounded requests."""
import json,os,time,threading,math
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlencode,urlparse
from datetime import date,datetime,timedelta,timezone

class Unavailable(Exception):pass
_lock=threading.Lock()
_last={}
_crypto_markets=(0,{})
class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlparse(newurl).scheme!='https' or urlparse(newurl).hostname!=urlparse(req.full_url).hostname:
            raise Unavailable('Redirecionamento entre hosts recusado para proteger credenciais')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def request(url,headers=None,output='json'):
    host=urlparse(url).hostname
    allowed={'www.eia.gov','api.bcb.gov.br','api.frankfurter.dev','api.coingecko.com','pro-api.coingecko.com','api.worldbank.org','api.stlouisfed.org','home.treasury.gov','data-api.ecb.europa.eu','www.bankofcanada.ca','www.bankofengland.co.uk'}
    if urlparse(url).scheme!='https' or host not in allowed:raise Unavailable('Host de dados não autorizado')
    with _lock:
        from backend.cache import Cache
        delay=max(2.1,float(os.getenv('PROVIDER_DELAY','2.1')))
        wait=Cache().request_slot(host,delay,int(os.getenv('COINGECKO_MONTHLY_BUDGET','8000')) if 'coingecko' in host else 0)
        if wait is None:raise Unavailable('Orçamento mensal CoinGecko esgotado; ajuste o plano ou aguarde renovação')
        if wait<0:raise Unavailable('Fonte em pausa após limite de uso; cache preservado')
        if wait:time.sleep(wait)
    # No URL is taken from an HTTP request. Do not log URLs containing keys.
    try:
        with build_opener(SameHostRedirect()).open(Request(url,headers={'User-Agent':'NewEraMarkets/1.0','Accept':'application/vnd.ms-excel' if output=='bytes' else 'application/json',**(headers or {})}),timeout=20) as r:
            if urlparse(r.geturl()).hostname not in allowed:raise Unavailable('Redirecionamento de fonte não autorizado')
            raw=r.read(12_000_001)
            if len(raw)>12_000_000:raise Unavailable('Resposta excede limite')
            return raw if output=='bytes' else raw.decode('utf-8-sig') if output=='text' else json.loads(raw)
    except HTTPError as e:
        if e.code not in (429,503):
            e.close()
            raise
        value=e.headers.get('Retry-After','120');seconds=120
        try:seconds=max(1,int(value))
        except ValueError:
            try:
                from email.utils import parsedate_to_datetime
                seconds=max(1,int(parsedate_to_datetime(value).timestamp()-time.time()))
            except (ValueError,TypeError,OverflowError):pass
        seconds=min(seconds,86400);e.close();Cache().defer_provider(host,seconds)
        error=Unavailable('Fonte limitou requisições; retentativa adiada conforme Retry-After');error.retry_after=seconds
        raise error from None
def point(d,v):
    v=float(v)
    if not math.isfinite(v):raise ValueError('Non-finite observation')
    return {'date':d,'value':v}
def fetch(a,start,end):
    p=a['provider']; code=a['code']; points=[]; extra={}
    if p=='eia':
        from backend.providers.eia import fetch as fetch_eia
        return fetch_eia(a,start,end,request)
    if p in ('treasury','ecb','boc'):
        from backend.providers import official
        get_text=lambda url:request(url,headers={'Accept':'text/csv' if p=='ecb' else 'application/atom+xml'},output='text')
        if p=='treasury':
            from backend.cache import Cache
            data=official.treasury(a,start,end,get_text,cache=Cache())
        else:data=getattr(official,p)(a,start,end,get_text if p=='ecb' else request)
        from backend.validation import normalize_points
        data['points']=normalize_points(data['points'],end)
        return data
    if p=='bcb':
        cursor=start
        while cursor<=end:
            stop=min(end,cursor+timedelta(days=3650))
            q=urlencode({'formato':'json','dataInicial':cursor.strftime('%d/%m/%Y'),'dataFinal':stop.strftime('%d/%m/%Y')})
            rows=request(f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?{q}')
            points.extend(point(datetime.strptime(r['data'],'%d/%m/%Y').date().isoformat(),r['valor']) for r in rows)
            cursor=stop+timedelta(days=1)
        source='Banco Central do Brasil · SGS'; url='https://dadosabertos.bcb.gov.br/'; extra={'frequency':'diária','instrument':a.get('instrument')}
    elif p=='fx':
        base,quote=code.split('/')
        q=urlencode({'base':base,'quotes':quote,'providers':'ecb','from':start.isoformat(),'to':end.isoformat()})
        rows=request('https://api.frankfurter.dev/v2/rates?'+q)
        points=[point(r['date'],r['rate']) for r in rows]
        source='Frankfurter · BCE';url='https://frankfurter.dev/';extra={'frequency':'diária','reference':'Referência diária BCE; sem negociação intradiária'}
    elif p=='coingecko':
        key=os.getenv('COINGECKO_API_KEY','')
        if not key:raise Unavailable('Configure COINGECKO_API_KEY e confirme o plano/licença')
        days=max(1,(end-start).days)
        if days>int(os.getenv('COINGECKO_HISTORY_DAYS','365')):raise Unavailable('Histórico excede o plano CoinGecko configurado')
        pro=os.getenv('COINGECKO_PLAN','demo')=='pro';base='https://pro-api.coingecko.com/api/v3' if pro else 'https://api.coingecko.com/api/v3'
        auth={'x-cg-pro-api-key' if pro else 'x-cg-demo-api-key':key}
        rows=request(f'{base}/coins/{code}/market_chart?'+urlencode({'vs_currency':'usd','days':days}),auth)
        points=[point(datetime.fromtimestamp(t/1000,timezone.utc).isoformat(),v) for t,v in rows['prices'] if start<=datetime.fromtimestamp(t/1000,timezone.utc).date()<=end]
        global _crypto_markets
        quote_error=None
        if not _crypto_markets[1] or time.monotonic()-_crypto_markets[0]>900:
            try:
                ids='bitcoin,ethereum,solana,ripple,binancecoin,cardano,dogecoin,chainlink'
                market=request(base+'/coins/markets?'+urlencode({'vs_currency':'usd','ids':ids}),auth)
                _crypto_markets=(time.monotonic(),{r['id']:r for r in market})
            except Exception:quote_error='Snapshot 24h indisponível; histórico preservado'
        quote=_crypto_markets[1].get(code,{})
        source='CoinGecko';url='https://www.coingecko.com/';extra={'frequency':'agregada','volume':quote.get('total_volume'),'market_cap':quote.get('market_cap'),'change_24h':quote.get('price_change_percentage_24h'),'quote_time':quote.get('last_updated'),'quote_price':quote.get('current_price'),'quote_error':quote_error}
    elif p=='worldbank':
        q=urlencode({'format':'json','date':f'{start.year}:{end.year}','per_page':1000})
        rows=request(f"https://api.worldbank.org/v2/country/{a['iso']}/indicator/{code}?{q}")
        points=[point(r['date'],r['value']) for r in (rows[1] or []) if r['value'] is not None]
        source='World Bank · WDI';url=f'https://data.worldbank.org/indicator/{code}';extra={'frequency':'anual','publication_date':None,'publication_note':'Data de publicação por observação não fornecida por este conector'}
    elif p=='fred':
        key=os.getenv('FRED_API_KEY','')
        if not key:raise Unavailable('Configure FRED_API_KEY; confira os direitos da série')
        q=urlencode({'series_id':code,'api_key':key,'file_type':'json','observation_start':start.isoformat(),'observation_end':end.isoformat()})
        rows=request('https://api.stlouisfed.org/fred/series/observations?'+q)
        points=[point(r['date'],r['value']) for r in rows['observations'] if r['value']!='.']
        source='FRED';url='https://fred.stlouisfed.org/series/'+code
    else:
        # A contracted distributor can export the documented JSON feed locally.
        # Paths are server configuration; clients cannot submit files or URLs.
        from pathlib import Path
        feed=os.getenv('LICENSED_FEED_PATH','')
        if not feed or os.getenv('LICENSED_REDISTRIBUTION_APPROVED')!='yes':
            raise Unavailable('Cotação indisponível: exige feed licenciado e autorização de redistribuição')
        if Path(feed).stat().st_size>20_000_000:raise Unavailable('Feed excede limite')
        record=json.loads(Path(feed).read_text(encoding='utf-8'))['assets'].get(a['id'])
        if not record:raise Unavailable('Instrumento ausente no feed licenciado')
        for field in ('source','source_url','unit','reference','frequency','instrument_id','currency','market'):
            if not record.get(field):raise Unavailable('Metadados obrigatórios ausentes no feed')
        if urlparse(record['source_url']).scheme!='https' or not urlparse(record['source_url']).hostname or urlparse(record['source_url']).username:raise Unavailable('Fonte inválida')
        if a.get('currency') and record['currency']!=a['currency']:raise Unavailable('Moeda do instrumento divergente')
        if record.get('reference')=='future' and not all(record.get(k) for k in ('contract','expiry')):raise Unavailable('Contrato e vencimento obrigatórios')
        if a['category']=='indices' and record['reference']!='cash_index':raise Unavailable('Índices exigem referência cash_index; proxies rejeitados')
        if a['category']=='commodities' and record['reference'] not in ('spot','future','monthly'):raise Unavailable('Natureza da commodity inválida')
        if a['category']=='rates' and record.get('instrument')!=a.get('instrument'):raise Unavailable('Instrumento monetário divergente')
        if a['category'] in ('rates','yields') and record['unit'] not in ('%','% a.a.'):raise Unavailable('Taxas devem estar em percentual, não fração ou pontos-base')
        if a['category']=='yields' and (record.get('tenor')!=a['tenor'] or record.get('country')!=a['country'] or record['reference']!='sovereign_nominal'):raise Unavailable('Prazo, país ou referência soberana divergente')
        points=[r for r in record['points'] if start.isoformat()<=r['date'][:10]<=end.isoformat()]
        fields=('frequency','reference','unit','currency','market','instrument_id','contract','expiry','instrument','publication_date','decision_date','next_meeting','decisions','tenor','country','max_age_days')
        source=record['source'];url=record['source_url'];extra={k:record[k] for k in fields if k in record}
        if a['category']=='rates':
            from backend.validation import policy_metadata
            extra.update(policy_metadata(record))
    from backend.validation import normalize_points
    points=normalize_points(points,end)
    return {'points':points,'source':source,'source_url':url,'unit':a['unit'],**extra}
