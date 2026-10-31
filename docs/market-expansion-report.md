# Relatório de expansão — estado final seguro

Data: 31/10/2026. PR #2, branch `feature/expand-market-data`. Este estado substitui a classificação anterior das quatro séries EIA como publicáveis.

- Catálogo: 167 instrumentos. Históricos públicos antes: 30; depois: 30.
- Validação local: quatro históricos de energia, 34.949 observações; não entram no JSON público nem no Pages.
- Os 30 históricos públicos anteriores foram preservados. As quatro séries de energia contêm somente metadados e motivo publication_review.
- Não foi comprovada autorização específica para redistribuir preços Refinitiv/LSEG via EIA. A política genérica não foi usada como autorização.
- Relatório dos testes finais e investigação de alternativas: [final-market-test.md](final-market-test.md).

| Indicador / país | Fonte | Disponibilidade pública | Tipo | Frequência | Credencial | Implementação / motivo |
|---|---|---|---|---|---|---|
| Ibovespa / Brasil | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P 500 / Estados Unidos | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nasdaq Composite / Estados Unidos | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Dow Jones / Estados Unidos | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Russell 2000 / Estados Unidos | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/TSX Composite / Canadá | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/BMV IPC / México | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P Merval / Argentina | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| STOXX Europe 600 / Europa | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| EURO STOXX 50 / Zona do Euro | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| DAX / Alemanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| FTSE 100 / Reino Unido | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| CAC 40 / França | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| FTSE MIB / Itália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| IBEX 35 / Espanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| SMI / Suíça | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nikkei 225 / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| TOPIX / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Shanghai Composite / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Shenzhen Component / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Hang Seng / Hong Kong | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| CSI 300 / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| KOSPI / Coreia do Sul | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nifty 50 / Índia | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| BSE Sensex / Índia | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/ASX 200 / Austrália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| TAIEX / Taiwan | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Petróleo Brent | U.S. Energy Information Administration · EIA | Indisponível | spot diário, só validação local | diária (dias publicados) | Não | Coletor local pronto; direitos não confirmados |
| Petróleo WTI | U.S. Energy Information Administration · EIA | Indisponível | spot diário, só validação local | diária (dias publicados) | Não | Coletor local pronto; direitos não confirmados |
| Gás natural | U.S. Energy Information Administration · EIA | Indisponível | spot diário, só validação local | diária (dias publicados) | Não | Coletor local pronto; direitos não confirmados |
| Gasolina RBOB | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Óleo de aquecimento | U.S. Energy Information Administration · EIA | Indisponível | spot diário, só validação local | diária (dias publicados) | Não | Coletor local pronto; direitos não confirmados |
| Ouro | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Prata | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Platina | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Paládio | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Cobre | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alumínio | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Níquel | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Zinco | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Chumbo | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Estanho | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Soja | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Milho | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Trigo | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Café arábica | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Café robusta | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Açúcar | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Algodão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Cacau | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Arroz | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Boi gordo | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Gado de reposição | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Suínos | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| USD/BRL | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| EUR/BRL | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| EUR/USD | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| GBP/USD | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| USD/JPY | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| USD/CNY | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| USD/CHF | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| AUD/USD | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| USD/CAD | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| USD/MXN | Frankfurter · BCE | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| DXY | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Bitcoin | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Ethereum | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Solana | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| XRP | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| BNB | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Cardano | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Dogecoin | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Chainlink | coingecko | Indisponível | não publicado | 24h | Sim, plano | credential_required |
| Selic meta / Brasil | Banco Central do Brasil · SGS | Disponível | referência periódica | diária | Não | Implementado; 2026-10-31 |
| Federal Reserve / Estados Unidos | fred | Indisponível | não publicado | diária | Sim, plano | credential_required |
| BCE / Zona do Euro | Banco Central Europeu | Indisponível | não publicado | datas de alteração de vigência | Não | source_failure |
| Bank of England / Reino Unido | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Japan / Japão | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| PBoC / China | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Canada / Canadá | Bank of Canada · Valet | Disponível | referência periódica | diária | Não | Implementado; 2026-10-29 |
| RBA / Austrália | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| SNB / Suíça | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| RBI / Índia | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Banxico / México | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Korea / Coreia do Sul | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| RBNZ / Nova Zelândia | licensed | Indisponível | não publicado | diária | Depende do contrato | license_required |
| PIB / Brasil | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Brasil | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Brasil | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Brasil | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Brasil | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Brasil | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Brasil | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / Estados Unidos | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Estados Unidos | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Estados Unidos | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Estados Unidos | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Estados Unidos | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Estados Unidos | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Estados Unidos | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / Zona do Euro | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Zona do Euro | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Zona do Euro | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Zona do Euro | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Zona do Euro | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Zona do Euro | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Zona do Euro | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / China | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / China | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / China | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / China | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / China | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / China | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / China | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / Japão | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Japão | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Japão | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Japão | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Japão | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Japão | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Japão | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / Reino Unido | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Reino Unido | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Reino Unido | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Reino Unido | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Reino Unido | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Reino Unido | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Reino Unido | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| PIB / Índia | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Inflação / Índia | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Desemprego / Índia | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Atividade industrial (valor adicionado) / Índia | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Dívida do governo central / Índia | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Saldo externo de bens e serviços / Índia | World Bank · WDI | Indisponível | não publicado | anual | Não | publication_review |
| Crescimento do PIB / Índia | World Bank · WDI | Disponível | referência periódica | anual | Não | Implementado; 2025 |
| Estados Unidos · 2 anos / Estados Unidos | US Treasury · Daily Par Yield Curve | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| Estados Unidos · 5 anos / Estados Unidos | US Treasury · Daily Par Yield Curve | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| Estados Unidos · 10 anos / Estados Unidos | US Treasury · Daily Par Yield Curve | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| Estados Unidos · 30 anos / Estados Unidos | US Treasury · Daily Par Yield Curve | Disponível | referência periódica | diária | Não | Implementado; 2026-10-30 |
| Brasil · 2 anos / Brasil | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 5 anos / Brasil | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 10 anos / Brasil | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 30 anos / Brasil | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 2 anos / Alemanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 5 anos / Alemanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 10 anos / Alemanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 30 anos / Alemanha | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 2 anos / Reino Unido | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 5 anos / Reino Unido | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 10 anos / Reino Unido | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 30 anos / Reino Unido | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 2 anos / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 5 anos / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 10 anos / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 30 anos / Japão | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 2 anos / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 5 anos / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 10 anos / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 30 anos / China | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 2 anos / Canadá | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 5 anos / Canadá | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 10 anos / Canadá | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 30 anos / Canadá | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 2 anos / Austrália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 5 anos / Austrália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 10 anos / Austrália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 30 anos / Austrália | licensed | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
