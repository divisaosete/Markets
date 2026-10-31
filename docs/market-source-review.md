# Expansão de fontes — 31/10/2026

Base: `origin/main` em `759e182`, árvore local limpa; branch `feature/expand-market-data`. Nenhum ETF ou futuro substitui um índice ou preço spot.

## Fontes aprovadas e testadas

EIA publica os arquivos XLS por links explícitos “Download Data”, sem chave, distintos da API v2 que exige cadastro. Os quatro arquivos foram baixados e seus cabeçalhos, mercados, unidades e observações foram verificados. A [política EIA](https://www.eia.gov/about/copyrights_reuse.php) permite reprodução e distribuição dos seus dados com atribuição; material de terceiros não recebe autorização automática.

| Série | Download oficial | Natureza | Unidade | Início incorporado |
|---|---|---|---|---|
| Brent | [RBRTEd.xls](https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls) | Europe Brent spot FOB | USD/barril | 1987-05-20 |
| WTI | [RWTCd.xls](https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls) | Cushing, Oklahoma, spot FOB | USD/barril | 1986-01-02 |
| Gás natural | [RNGWHHDd.xls](https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDd.xls) | Henry Hub spot | USD/MMBtu | 1997-01-07 |
| Óleo de aquecimento | [EER_EPD2F_PF4_Y35NY_DPGd.xls](https://www.eia.gov/dnav/pet/hist_xls/EER_EPD2F_PF4_Y35NY_DPGd.xls) | New York Harbor No. 2 spot FOB | USD/galão EUA | 1986-06-02 |

Frequência: diária nos dias publicados, com atraso; última observação na coleta: 27/10/2026. Não são cotações de execução nem dados em tempo real. O coletor solicita arquivos Excel com o cabeçalho Accept correspondente: solicitar JSON resultou em HTTP 406 em três arquivos. Não houve contorno de bloqueios ou autenticação.

Os downloads não publicam nesta documentação uma quota contratual. A aplicação limita a uma consulta por série a cada 24 horas, com espaçamento compartilhado de no mínimo 2,1 segundos por host; o workflow verifica fontes a cada seis horas, respeitando os intervalos persistidos. HTTP 429/503 respeita Retry-After com adiamento persistido e preservação de cache; erros de formato, série, unidade ou histórico também preservam os dados anteriores. Não há retentativas em laço. `--force` é uma exceção operacional manual documentada.

API v2 EIA: [documentação e cadastro](https://www.eia.gov/opendata/), credencial obrigatória. Não foi necessária para estes downloads, e não foi introduzida dependência dessa chave.

## Índices prioritários

| Índice | Evidência oficial / resultado da pesquisa | Decisão |
|---|---|---|
| S&P 500 e Dow Jones | [Licenciamento S&P DJI](https://www.spglobal.com/spdji/en/about-us/data-index-licensing/) | Nenhuma licença de redistribuição foi encontrada no projeto; manter indisponíveis. |
| Nasdaq Composite | [Aviso Nasdaq para dados EOD e históricos](https://www.nasdaqtrader.com/TraderNews.aspx?id=DN2024-5) | Redistribuidores precisam de licença direta; manter indisponível. |
| Ibovespa | [FAQ B3](https://www.b3.com.br/en_us/market-data-and-indices/data-services/market-data/distributors/faq/) | A B3 admite distribuição gratuita de certos dados D-1 obtidos pelas plataformas de Market Data. Isso não comprova acesso gratuito automatizado a um histórico oficial de Ibovespa nem libera todo canal de obtenção. Não usar endpoints internos do site; integração permanece pendente de canal oficial e condições aplicáveis. |
| Nikkei 225 | [Licença de exibição Nikkei](https://indexes.nikkei.co.jp/nkave/license/index.en.html) | Exibição em sites depende de contrato; manter indisponível. |
| FTSE 100 | [Redistribuição LSEG](https://www.lseg.com/en/data-analytics/market-data/data-redistribution) | Não comprovada licença gratuita para JSON público; manter indisponível. |
| DAX | [Condições STOXX](https://stoxx.com/legal/stoxx-conditions-of-use/) | Valores históricos incluídos nos dados sujeitos a licença; manter indisponível. |
| CAC 40 | [Políticas e contratos Euronext](https://www.euronext.com/en/data/real-time-data/pricing-specs-agreements/market-data-pricing-policies) | Não comprovada licença gratuita para redistribuição pública do histórico; manter indisponível. |

Uma página de cotação visível não foi tratada como API autorizada. Não foram feitos scraping ou testes de endpoints privados dessas bolsas.

## Metais, cripto e provedores alternativos

| Fonte | Histórico, credencial e direitos | Resultado |
|---|---|---|
| Ouro e prata LBMA / IBA | [LBMA](https://www.lbma.org.uk/) informa licença para obter, usar ou redistribuir benchmarks históricos e em tempo real; [WGC](https://www.gold.org/goldhub/data/gold-prices) removeu históricos a pedido da IBA. | Não incorporar benchmarks protegidos. |
| Cobre LME | [Distribuição LME](https://www.lme.com/Market-data/Market-data-licensing/Data-distribution) exige licença para exibição em site público. | Não incorporar sem licença. |
| Banco Mundial — Pink Sheet | [Downloads oficiais mensais](https://www.worldbank.org/en/research/commodity-markets) e [licença padrão](https://datacatalog.worldbank.org/public-licenses) não eliminam direitos de componentes de terceiros. | Não aprovado nesta entrega para metais/commodities; requer revisão por série e componente. Não substituir spot diário por média mensal silenciosamente. |
| FRED | API existente exige chave; [termos](https://fred.stlouisfed.org/legal/terms/) preservam direitos de terceiros. | Chave não encontrada no Actions. Não usar FRED como forma de remover restrições S&P, Nasdaq ou metais. |
| CoinGecko — Bitcoin/Ethereum | [Termos](https://www.coingecko.com/en/api_terms) vinculam direitos ao plano; [licenciamento](https://support.coingecko.com/articles/1043089972-what-are-the-differences-between-commercial-and-custom-licenses) distingue exibição e redistribuição. Histórico e limites dependem do plano. | Coletor local existente mantém orçamento, Retry-After e cache. Sem chave no Actions e sem licença para download JSON público comprovada: não liberar publicação nem afirmar teste real bem-sucedido. |
| Coin Metrics Community | [Documentação](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data), sem chave, limite 10 requisições/6s; [arquivo oficial e licença CC BY-NC 4.0](https://github.com/coinmetrics/data/blob/master/README.md). Oferta de reference rates tem histórico limitado conforme produto. | Restrição não comercial não resolvida para este projeto; não integrar automaticamente. |
| Alpha Vantage | [Termos](https://www.alphavantage.co/terms_of_service/): uso pessoal não comercial salvo acordo escrito. | Plano gratuito não comprova autorização para distribuição pública. |

Não foram solicitadas credenciais em chat. A API do GitHub foi usada apenas para verificar presença das chaves nomeadas EIA_API_KEY, FRED_API_KEY e COINGECKO_API_KEY: todas ausentes, sem acesso aos seus valores. Os provedores restritos não foram testados com chaves fictícias ou limites contornados.

## Operação e validação

- Downloads EIA integrados ao mesmo pipeline de JSON estático do Pages, sem backend permanente e sem chamadas EIA no navegador. `xlrd==2.0.2` lê os arquivos XLS; dependência instalada no workflow de coleta.
- Históricos válidos anteriores são mesclados por data; revisões upstream prevalecem na mesma data, sem apagar observações antigas fora da janela recebida. Falha mantém dados e informa estado `stale`.
- Cabeçalhos verificam mercado e unidade; datas inválidas/futuras, valores não finitos e duplicações conflitantes são rejeitados. Preços negativos legítimos não são descartados.
- Início, fim, quantidade, fonte, licença, frequência, unidade, moeda, última observação e data de coleta ficam no JSON. A interface existente mostra datas e disponibilidade; Brent, WTI e Henry Hub ganham prioridade no resumo inicial. Identidade visual, filtros e gráficos preservados.
- Testes: suíte Python, suíte Node, sintaxe, validação do JSON, build do Pages e recursos HTTP reais sob `/Markets/`; teste adicional do frontend usa os quatro históricos publicados nas janelas e comparação de gráficos. Nenhuma alegação de inspeção visual em navegador.

Após revisão e merge manual do PR, o workflow existente publica o site e a coleta diária EIA passa a operar. Estas quatro integrações não requerem ação de cadastro ou configuração de Secrets. Índices, metais e cripto exigem resolver os impedimentos acima antes de ampliar a lista de publicação aprovada.
