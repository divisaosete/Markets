# Relatório de expansão dos dados financeiros

Data: 31/10/2026. Branch: `feature/expand-market-data`.

- Históricos antes: 30/167; depois: 34/167.
- Novos históricos: 4; observações novas: 34,949.
- Históricos das demais séries preservados integralmente: True.
- Indisponíveis: {'license_required': 88, 'credential_required': 9, 'source_failure': 1, 'publication_review': 35}.
- Testes finais: 111 Python, 50 Node, sintaxe Python/JS, JSON público, build e 41 verificações HTTP sob /Markets/. Consultas reais EIA aprovadas; consulta BCE falhou por URLError.
- Credenciais no Actions: EIA_API_KEY, FRED_API_KEY e COINGECKO_API_KEY ausentes. Novas integrações EIA não precisam de chave.
- Documentação das fontes, limites, direitos e decisões: [market-source-review.md](market-source-review.md).
- Ação necessária para publicação: revisar e fazer merge manual do PR; nenhum cadastro para EIA. Outras fontes dependem das condições documentadas.

## Históricos incorporados

| Indicador | Fonte | Observações | Primeira | Última | Unidade |
|---|---|---:|---|---|---|
| Petróleo Brent | EIA | 9117 | 1987-05-20 | 2026-10-27 | USD/barril |
| Petróleo WTI | EIA | 9532 | 1986-01-02 | 2026-10-27 | USD/barril |
| Gás natural | EIA | 7485 | 1997-01-07 | 2026-10-27 | USD/MMBtu |
| Óleo de aquecimento | EIA | 8815 | 1986-06-02 | 2026-10-27 | USD/galão EUA |

## Catálogo completo após a expansão

Tipos e frequências pendentes não são inferidos para feeds sem contrato. Credencial e autorização são requisitos separados.

| Indicador / país | Fonte | Disponibilidade | Tipo de dado | Frequência | Credencial | Implementação / motivo |
|---|---|---|---|---|---|
| Ibovespa / Brasil | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P 500 / Estados Unidos | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nasdaq Composite / Estados Unidos | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Dow Jones / Estados Unidos | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Russell 2000 / Estados Unidos | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/TSX Composite / Canadá | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/BMV IPC / México | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P Merval / Argentina | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| STOXX Europe 600 / Europa | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| EURO STOXX 50 / Zona do Euro | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| DAX / Alemanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| FTSE 100 / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| CAC 40 / França | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| FTSE MIB / Itália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| IBEX 35 / Espanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| SMI / Suíça | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nikkei 225 / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| TOPIX / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Shanghai Composite / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Shenzhen Component / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Hang Seng / Hong Kong | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| CSI 300 / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| KOSPI / Coreia do Sul | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Nifty 50 / Índia | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| BSE Sensex / Índia | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| S&P/ASX 200 / Austrália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| TAIEX / Taiwan | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Petróleo Brent | U.S. Energy Information Administration · EIA | Disponível | spot diário com atraso | diária (dias publicados) | Não | Implementado; 2026-10-27 |
| Petróleo WTI | U.S. Energy Information Administration · EIA | Disponível | spot diário com atraso | diária (dias publicados) | Não | Implementado; 2026-10-27 |
| Gás natural | U.S. Energy Information Administration · EIA | Disponível | spot diário com atraso | diária (dias publicados) | Não | Implementado; 2026-10-27 |
| Gasolina RBOB | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Óleo de aquecimento | U.S. Energy Information Administration · EIA | Disponível | spot diário com atraso | diária (dias publicados) | Não | Implementado; 2026-10-27 |
| Ouro | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Prata | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Platina | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Paládio | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Cobre | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alumínio | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Níquel | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Zinco | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Chumbo | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Estanho | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Soja | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Milho | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Trigo | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Café arábica | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Café robusta | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Açúcar | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Algodão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Cacau | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Arroz | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Boi gordo | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Gado de reposição | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Suínos | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
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
| DXY | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
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
| Bank of England / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Japan / Japão | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| PBoC / China | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Canada / Canadá | Bank of Canada · Valet | Disponível | referência periódica | diária | Não | Implementado; 2026-10-29 |
| RBA / Austrália | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| SNB / Suíça | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| RBI / Índia | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Banxico / México | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| Bank of Korea / Coreia do Sul | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
| RBNZ / Nova Zelândia | Feed autorizado pendente | Indisponível | não publicado | diária | Depende do contrato | license_required |
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
| Brasil · 2 anos / Brasil | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 5 anos / Brasil | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 10 anos / Brasil | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Brasil · 30 anos / Brasil | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 2 anos / Alemanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 5 anos / Alemanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 10 anos / Alemanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Alemanha · 30 anos / Alemanha | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 2 anos / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 5 anos / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 10 anos / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Reino Unido · 30 anos / Reino Unido | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 2 anos / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 5 anos / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 10 anos / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Japão · 30 anos / Japão | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 2 anos / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 5 anos / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 10 anos / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| China · 30 anos / China | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 2 anos / Canadá | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 5 anos / Canadá | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 10 anos / Canadá | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Canadá · 30 anos / Canadá | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 2 anos / Austrália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 5 anos / Austrália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 10 anos / Austrália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
| Austrália · 30 anos / Austrália | Feed autorizado pendente | Indisponível | não publicado | conforme fonte | Depende do contrato | license_required |
