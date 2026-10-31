# Teste final — New Era Markets / PR #2

Data: 31/10/2026. Branch: `feature/expand-market-data`. Não foi realizado merge nem deploy. A `main` foi preservada.

## Resultado

O dashboard foi testado em navegador real e nas suítes automatizadas. O pacote público continua com **30 históricos funcionais de 167 instrumentos**. As quatro séries de energia foram tecnicamente validadas, mas continuam **sem autorização específica de redistribuição comprovada** e não integram os artefatos públicos.

| Categoria publicável | Históricos com dados |
|---|---:|
| Câmbio de referência BCE / Frankfurter | 10 |
| PIB e crescimento do PIB, sete economias / WDI | 14 |
| Selic meta / BCB | 1 |
| Taxa overnight alvo / Bank of Canada | 1 |
| Treasury nominal 2, 5, 10 e 30 anos | 4 |
| **Total público** | **30** |

Os históricos públicos anteriores foram preservados; as 137 séries sem histórico público têm motivos explícitos. BCE permanece sem histórico por falha da fonte. Índices, metais e cripto não foram liberados nem substituídos por proxies.

## Energia validada somente no computador

| Série | Natureza / mercado | Unidade | Observações | Início | Última |
|---|---|---|---:|---|---|
| Brent | Spot Europa FOB | USD/barril | 9.117 | 1987-05-20 | 2026-10-27 |
| WTI | Spot Cushing, Oklahoma FOB | USD/barril | 9.532 | 1986-01-02 | 2026-10-27 |
| Henry Hub | Spot gás natural, Louisiana | USD/MMBtu | 7.485 | 1997-01-07 | 2026-10-27 |
| Óleo de aquecimento | Spot New York Harbor No. 2 FOB | USD/galão EUA | 8.815 | 1986-06-02 | 2026-10-27 |

Total local: **34.949 observações**, moeda USD. Os quatro XLS oficiais foram baixados novamente. Foram comparadas 12 amostras independentes — primeira, central e última de cada arquivo — com correspondência em todas as datas e valores. Cabeçalhos, unidades, quantidade, ordenação, duplicações e valores finitos foram validados. Preços e amostras numéricas ficam somente no relatório local, não neste documento público.

Os arquivos usados são os links explícitos de download `RBRTEd.xls`, `RWTCd.xls`, `RNGWHHDd.xls` e `EER_EPD2F_PF4_Y35NY_DPGd.xls` no domínio oficial `www.eia.gov`. HTTP 200, por si só, não é considerado validação.

## Inspeção real no navegador

- Navegação pelos dez módulos, incluindo calendário e fontes; botão de atualização de leitura; ausência de erros/avisos nos consoles consultados.
- Filtro Energia: cinco instrumentos, incluindo a gasolina RBOB ainda indisponível. Busca digitada por WTI: uma opção e uma linha de resultado.
- Gráficos das quatro séries locais com datas, valores finais e unidades conferidos; histórico máximo Brent com 9.117 datas. Janelas de 1 mês e 1 ano verificadas.
- Linha, área, barras, zoom e restauração funcionando. Óleo de aquecimento em 1 mês: 19 observações; zoom reduziu para 15 e restaurou para 19. Candles permanecem desabilitados sem OHLC real.
- Comparador Brent/WTI: duas séries, base 100 e retorno acumulado; em um ano, 243 datas comuns, sem interpolação.
- Responsividade em 375×812, 768×1024 e 1440×1000: sem transbordamento horizontal da página. Navegação e tabelas mantêm rolagem interna quando necessário.
- Pacote público: energia sem valores, gráfico com explicação de redistribuição em revisão. Prévia privada: faixa persistente NÃO PUBLICAR e identificação de arquivo local.

## Automação e falhas

A simulação executou atualização com falha de fonte, preservação do histórico, respeito ao intervalo e recuperação. O coletor público foi chamado com `--force` e os quatro IDs EIA: nenhuma consulta foi feita, nenhum histórico restrito foi publicado e o total público permaneceu 30.

Na simulação privada, uma indisponibilidade total preservou as 34.949 observações. No navegador, o gráfico continuou visível com estado Dado atrasado. Uma falha parcial também foi testada, preservando o histórico da fonte que falhou e as séries bem-sucedidas. Detalhes de exceções e URLs privadas não são expostos.

O cache do Actions agora mantém `pages-state.json` e o banco dedicado `pages.sqlite3`, preservando intervalos e adiamentos por host entre execuções. Ele não inclui os arquivos privados de energia e não integra o artefato Pages.

## Correções e barreiras de publicação

1. EIA retirada da lista de publicação aprovada. O coletor público não a consulta, inclusive com `--force`.
2. Os quatro históricos foram removidos de `public/data/market-data.json`; ficaram metadados, unidades e mensagem clara.
3. O validador público e o build rejeitam a reintrodução de observações de energia. O backend opcional também recusa essas séries.
4. Coletor e prévia privados gravam somente em `var/` e recusam destinos em `public/` ou `_site/`. O servidor privado escuta somente em 127.0.0.1.
5. Testes de prévia usam fixtures em diretórios temporários; não substituem os dados reais locais. Relatórios de comparação e de falha têm arquivos separados.
6. A documentação anterior que classificava as séries como domínio público foi corrigida. A origem EIA → Refinitiv/LSEG fica explícita.

Os commits anteriores do PR continuam no histórico do Git: remover dados do estado atual não apaga versões anteriores. Não foi realizado force-push nem reescrita do histórico. O compromisso verificado aqui é ausência de observações restritas nos arquivos públicos e artefatos novos.

## Testes automatizados

- 121 testes Python aprovados, incluindo proteção de publicação, atualização, cache, falhas, recuperação e isolamento das prévias.
- 51 testes JavaScript aprovados, incluindo ausência de energia no pacote público e comportamento de gráficos com fixtures locais explícitas.
- Sintaxe Python/JavaScript, validação integral do JSON e build estático aprovados.
- 41 verificações HTTP reais sob `/Markets/` aprovadas, sem exposição de backend ou arquivos privados.
- O workflow do PR executa testes, auditoria de dependências, build e verificação HTTP. O deploy é ignorado em PRs; a coleta de produção não foi disparada na `main` durante este trabalho.

## Direitos e alternativas investigadas

As [notas de petróleo](https://www.eia.gov/dnav/pet/TblDefs/pet_pri_spt_tbldef2.asp) e [gás spot](https://www.eia.gov/dnav/ng/TblDefs/ng_pri_fut_tbldef2.asp) identificam Refinitiv/LSEG como fonte. A [política EIA](https://www.eia.gov/about/copyrights_reuse.php) ressalva materiais de terceiros. Nenhuma autorização específica para redistribuir os quatro benchmarks foi encontrada ou presumida.

Foram identificados produtos diferentes, cuja origem em levantamentos governamentais está documentada e para os quais a política geral de reutilização da EIA oferece uma base mais clara:

| Alternativa | Documentação específica da origem | Frequência / diferença |
|---|---|---|
| Petróleo — preço de primeira compra, inclusive correntes WTI | [EIA-182, definições e fonte](https://www.eia.gov/dnav/pet/TblDefs/pet_pri_dfp2_tbldef2.asp) | Mensal; preço de primeira compra. Não é WTI spot Cushing nem Brent. |
| Gás natural citygate / residencial | [EIA-857 e EIA-910, fontes](https://www.eia.gov/dnav/ng/TblDefs/ng_pri_sum_tbldef2.asp) | Mensal; preço de entrega/distribuição em USD por mil pés cúbicos. Não é Henry Hub spot. |
| Óleo de aquecimento residencial | [EIA-877 e metodologia](https://www.eia.gov/petroleum/heatingoilpropane/faq_respondents.php) | Semanal de outubro a março e mensal de abril a setembro; varejo residencial. Não é New York Harbor spot FOB. |

Essas alternativas não foram inseridas como substituições. Uma implementação futura deve cadastrá-las com nomes próprios, selecionar séries exatas e validar os respectivos arquivos e atribuições. Não se declara resolvida a licença dos quatro benchmarks por existir uma alternativa governamental.

CoinPaprika também foi investigada: [a documentação atual de licenciamento](https://coinpaprika.com/api/licensing) reserva redistribuição ao plano Enterprise com contrato. Portanto, não é uma alternativa gratuita já autorizada para publicar históricos cripto neste projeto.

## Capturas e reprodução local

As capturas, os valores amostrados e o relatório completo com imagens estão em `var/`, ignorado pelo Git. Não foram anexados ao PR para evitar a distribuição de gráficos de energia ainda sem autorização comprovada.

Capturas: `01-public-overview-desktop.jpg`, `02-public-energy-blocked.jpg`, `03-local-brent-desktop.jpg`, `04-local-energy-comparison-desktop.jpg`, `05-public-mobile-375.jpg`, `06-local-wti-mobile-375.jpg` e `07-local-source-failure-preserved.jpg`, em `var/final-test-screenshots/`.

Prévia pública: `python -m backend.preview_pages --prefix Markets`. Prévia restrita: instalar `requirements.txt`, executar `python -m backend.energy_validation --force` e depois `python -m backend.preview_energy`, abrindo `http://127.0.0.1:8081/Markets/`.

**Conclusão:** funcionamento técnico validado com as limitações descritas; produção permanece com 30 históricos. As quatro séries estão disponíveis somente para validação local e continuam impedidas de publicação até documentação específica dos direitos.
