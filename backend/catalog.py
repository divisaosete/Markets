"""Instrument identities, never substituted with proxies."""
ASSETS = []
def add(id, name, category, country='', unit='', provider='licensed', code='', **extra):
    ASSETS.append(dict(id=id,name=name,category=category,country=country,unit=unit,provider=provider,code=code,**extra))

indices = [
('ibov','Ibovespa','Brasil','BRL','B3'),('sp500','S&P 500','Estados Unidos','USD','S&P DJI'),('nasdaq','Nasdaq Composite','Estados Unidos','USD','Nasdaq'),('dow','Dow Jones','Estados Unidos','USD','S&P DJI'),('russell','Russell 2000','Estados Unidos','USD','FTSE Russell'),('tsx','S&P/TSX Composite','Canadá','CAD','TSX'),('ipc','S&P/BMV IPC','México','MXN','BMV'),('merval','S&P Merval','Argentina','ARS','BYMA'),
('stoxx600','STOXX Europe 600','Europa','EUR','STOXX'),('stoxx50','EURO STOXX 50','Zona do Euro','EUR','STOXX'),('dax','DAX','Alemanha','EUR','Deutsche Börse'),('ftse','FTSE 100','Reino Unido','GBP','LSE'),('cac','CAC 40','França','EUR','Euronext'),('mib','FTSE MIB','Itália','EUR','Borsa Italiana'),('ibex','IBEX 35','Espanha','EUR','BME'),('smi','SMI','Suíça','CHF','SIX'),
('nikkei','Nikkei 225','Japão','JPY','Nikkei'),('topix','TOPIX','Japão','JPY','JPX'),('shanghai','Shanghai Composite','China','CNY','SSE'),('shenzhen','Shenzhen Component','China','CNY','SZSE'),('hangseng','Hang Seng','Hong Kong','HKD','HSI'),('csi300','CSI 300','China','CNY','CSI'),('kospi','KOSPI','Coreia do Sul','KRW','KRX'),('nifty','Nifty 50','Índia','INR','NSE'),('sensex','BSE Sensex','Índia','INR','BSE'),('asx','S&P/ASX 200','Austrália','AUD','ASX'),('taiex','TAIEX','Taiwan','TWD','TWSE')]
for i,(id,n,c,currency,exchange) in enumerate(indices):
    add(id,n,'indices',c,'pontos',currency=currency,exchange=exchange,region='Américas' if i<8 else 'Europa' if i<16 else 'Ásia e Pacífico',reference='Índice à vista')
for group,names in [('Energia',['Petróleo Brent','Petróleo WTI','Gás natural','Gasolina RBOB','Óleo de aquecimento']),('Metais',['Ouro','Prata','Platina','Paládio','Cobre','Alumínio','Níquel','Zinco','Chumbo','Estanho']),('Agricultura',['Soja','Milho','Trigo','Café arábica','Café robusta','Açúcar','Algodão','Cacau','Arroz']),('Pecuária',['Boi gordo','Gado de reposição','Suínos'])]:
    for n in names:
        id={'Petróleo Brent':'brent','Petróleo WTI':'wti','Ouro':'gold'}.get(n,'commodity-'+str(len(ASSETS)))
        add(id,n,'commodities',region=group,reference='Referência depende do feed contratado; unidade, mercado e contrato obrigatórios')
for pair in ['USD/BRL','EUR/BRL','EUR/USD','GBP/USD','USD/JPY','USD/CNY','USD/CHF','AUD/USD','USD/CAD','USD/MXN']:
    add(pair.replace('/','').lower(),pair,'fx',unit=pair.split('/')[1],provider='fx',code=pair,frequency='diária',reference='Referência diária BCE; não é cotação intradiária')
add('dxy','DXY','fx',unit='pontos',reference='Índice ICE US Dollar Index')
for code,n in [('bitcoin','Bitcoin'),('ethereum','Ethereum'),('solana','Solana'),('ripple','XRP'),('binancecoin','BNB'),('cardano','Cardano'),('dogecoin','Dogecoin'),('chainlink','Chainlink')]:
    add(code,n,'crypto',unit='USD',provider='coingecko',code=code,frequency='24h',reference='Preço agregado; variação 24h fornecida separadamente')
add('selic','Selic meta','rates','Brasil','% a.a.','bcb','432',instrument='Meta Selic',frequency='diária',source_url='https://www.bcb.gov.br/controleinflacao/taxaselic')
rates=[('fed','Estados Unidos','Federal Reserve','Limite superior da faixa alvo federal funds','DFEDTARU','https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'),('ecb','Zona do Euro','BCE','Taxa da facilidade permanente de depósito','','https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html'),('boe','Reino Unido','Bank of England','Bank Rate','','https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes'),('boj','Japão','Bank of Japan','Taxa de política monetária','','https://www.boj.or.jp/en/mopo/'),('pboc','China','PBoC','Reverse repo de 7 dias','','https://www.pbc.gov.cn/en/'),('boc','Canadá','Bank of Canada','Target for the overnight rate','','https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/'),('rba','Austrália','RBA','Cash rate target','','https://www.rba.gov.au/monetary-policy/'),('snb','Suíça','SNB','SNB policy rate','','https://www.snb.ch/en/'),('rbi','Índia','RBI','Policy repo rate','','https://www.rbi.org.in/'),('banxico','México','Banxico','Objetivo para tasa de interés interbancaria a un día','','https://www.banxico.org.mx/'),('bok','Coreia do Sul','Bank of Korea','Base Rate','','https://www.bok.or.kr/eng/'),('rbnz','Nova Zelândia','RBNZ','Official Cash Rate','','https://www.rbnz.govt.nz/monetary-policy')]
for id,c,bank,instrument,code,url in rates:
    add(id,bank,'rates',c,'%', 'fred' if code else 'licensed',code,instrument=instrument,frequency='diária',source_url=url)
for country,iso in [('Brasil','BRA'),('Estados Unidos','USA'),('Zona do Euro','EMU'),('China','CHN'),('Japão','JPN'),('Reino Unido','GBR'),('Índia','IND')]:
    for code,n,unit in [('NY.GDP.MKTP.CD','PIB','USD correntes'),('FP.CPI.TOTL.ZG','Inflação','% anual'),('SL.UEM.TOTL.ZS','Desemprego','% força de trabalho'),('NV.IND.TOTL.KD.ZG','Atividade industrial (valor adicionado)','% anual'),('GC.DOD.TOTL.GD.ZS','Dívida do governo central','% PIB'),('NE.RSB.GNFS.CD','Saldo externo de bens e serviços','USD correntes'),('NY.GDP.MKTP.KD.ZG','Crescimento do PIB','% anual')]:
        add(f'{iso}-{code}',n,'macro',country,unit,'worldbank',code,iso=iso,frequency='anual',reference='World Development Indicators; atividade industrial não é produção industrial mensal')
for country in ['Estados Unidos','Brasil','Alemanha','Reino Unido','Japão','China','Canadá','Austrália']:
    for tenor in [2,5,10,30]:
        add(f'yield-{country}-{tenor}',f'{country} · {tenor} anos','yields',country,'%', 'fred' if country=='Estados Unidos' else 'licensed',f'DGS{tenor}' if country=='Estados Unidos' else '',tenor=tenor,reference='Treasury constant maturity' if country=='Estados Unidos' else 'Rendimento soberano nominal; fonte pendente')
BY_ID={a['id']:a for a in ASSETS}
BY_ID['ecb'].update(provider='ecb',code='FM.D.U2.EUR.4F.KR.DFR.LEV',frequency='datas de alteração de vigência')
BY_ID['boc'].update(provider='boc',code='V39079')
for a in ASSETS:
    if a['category']=='yields' and a['country']=='Estados Unidos':
        a.update(provider='treasury',code=f"BC_{a['tenor']}YEAR",reference='Treasury nominal par yield curve (CMT)')
OVERVIEW=['ibov','sp500','nasdaq','nikkei','brent','wti','gold','usdbrl','bitcoin','selic','fed']
