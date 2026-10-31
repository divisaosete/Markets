# Fontes de dados — beta GitHub Pages

Revisão em 31/10/2026. Acesso gratuito não equivale a licença irrestrita. O coletor usa uma lista explícita e não exporta SQLite privado. Cada registro público identifica licença, fonte, unidade, referência e coleta.

| Fonte | Publicação nesta beta | Frequência / condições |
|---|---|---|
| BCB SGS 432 | Meta Selic, % a.a. | Série diária; coleta diária, sem chave. [Dataset ODbL](https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom). Atribuição BCB/Copom; adaptações da série sob ODbL |
| Frankfurter / provider ECB | Dez pares de câmbio do catálogo | Referência diária; coleta a cada 6h. Sem chave, CORS `*` verificado com Origin. [API](https://frankfurter.dev/) e [reprodução BCE com atribuição e indicação de alterações](https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html). Conversões de base vêm do provedor |
| World Bank / WDI | PIB e crescimento do PIB de sete economias | Anual; consulta semanal. [CC BY 4.0 e termos adicionais](https://datacatalog.worldbank.org/public-licenses). Outras 35 séries WDI permanecem em revisão por possíveis direitos de terceiros |
| Bank of Canada / Valet V39079 | Target for overnight rate, não Bank Rate | Série e coleta diárias; sem chave. [Reprodução com atribuição, sem logo/endosso](https://www.bankofcanada.ca/terms/); informação disponível gratuitamente na fonte |
| US Treasury | Curva nominal par 2/5/10/30 anos, quando publicada | Diário; coleta a cada 6h; XML anual compartilhado entre vencimentos. [Feed oficial](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed), atribuição US Treasury. Obras do governo federal têm regime próprio de domínio público nos EUA; não estendemos isso a material de terceiros/logos. [US Copyright Office](https://www.copyright.gov/history/copyright-exhibit/lifecycle/) |
| BCE / taxa de depósito | Conector preparado; sem dados nesta coleta | Vigência da taxa; tentativa diária. Falha externa registrada. Não foi inferido nível ou data de decisão |

Históricos diários abrangem aproximadamente cinco anos; WDI preserva referências anuais disponíveis desde 1960. “Máx.” significa o histórico efetivamente disponível na modalidade usada, não promessa de cobertura ilimitada. GitHub Actions pode atrasar; não é tempo real. Metadados e condições também estão em public/DATA-LICENSES.md, incluído no site.

## Modalidade dinâmica

O navegador pode consultar Frankfurter/BCE por HTTPS, sem autenticação. Há cache de 30 minutos e pausa de cinco minutos após falha. A renderização inicial usa JSON; o resultado direto aparece em uma atualização seguinte. Respostas são validadas por par, data e valor. Falhas não apagam o histórico publicado. Coleta e observação têm horários distintos; nenhum resultado é anunciado como intradiário.

PUBLIC_API_BASE permite, opcionalmente, um proxy/backend público HTTPS controlado pelo proprietário. Esse serviço não foi criado/contratado nesta entrega. Exige licença, CORS para a origem GitHub Pages e controles de uso. Chaves ficam no servidor ou Actions Secrets, nunca em URL, JSON ou JavaScript. Sem proxy, a beta continua funcional.

## Índices, commodities e cripto

| Indicadores | Viabilidade e pendência |
|---|---|
| Ibovespa | Fonte autorizada e direitos de exibição: [B3 — distribuição](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/distribuidores/perguntas-frequentes/) |
| S&P 500 / Dow Jones | Dados para websites são licenciados: [S&P DJI](https://www.spglobal.com/spdji/en/about-us/data-index-licensing/) |
| Nasdaq Composite | Contrato e política de distribuição: [Nasdaq](https://www.nasdaqtrader.com/content/technicalsupport/dataproducts/indexdatapolicy.pdf) |
| Nikkei 225 | Serviço e autorização de redistribuição: [Nikkei](https://indexes.nikkei.co.jp/nkave/license/index.en.html) |
| Brent, WTI, ouro | Definir spot/futuro, mercado, moeda/unidade e direitos. [CME](https://www.cmegroup.com/market-data/license-data.html) exemplifica o licenciamento de futuros. Alternativas oficiais spot exigem revisão separada e identificação explícita; não foram usadas como substituições silenciosas |
| CoinGecko / FRED | Chaves e direitos por plano/série; indisponíveis na publicação padrão. Uma chave não aprova redistribuição |

Nenhum plano comercial foi presumido ou contratado. Não há scraping, ETFs como índices, candles sintéticos, previsões ou resultados inventados. As instituições não endossam New Era Labs. Cálculos e recortes são identificados; fontes originais prevalecem.
