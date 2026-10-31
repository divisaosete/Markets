# Diagnóstico do dashboard publicado

Data: 31/10/2026. Site: https://divisaosete.github.io/Markets/ . Base auditada: `main` em `759e182`. Correções isoladas na branch `fix/published-category-data`; nenhum merge ou deploy automático foi realizado.

## Conclusão

Não se confirmou que somente Forex possua dados no site atual. O JSON publicado contém 30 históricos e é semanticamente idêntico ao arquivo `public/data/market-data.json` da `main`. Selic, Banco do Canadá, PIB e Treasury foram abertos com gráficos no site publicado. Foram confirmados e corrigidos um erro de seleção de instrumento na navegação de juros e uma janela inicial pouco adequada ao PIB anual.

## Carregamento, caminhos e comparação

O HTML publicado usa `./bootstrap.js`. A partir desse caminho, foram baixados `config.js`, `static-data.js`, `app.js`, `catalog.js` e `data/market-data.json`: todos responderam HTTP 200 com conteúdo apropriado. O JSON correto no Pages fica em `/Markets/data/market-data.json`; `public/` é a pasta de origem do repositório e não um prefixo a acrescentar à URL do artefato construído.

JSON remoto: 947.056 bytes, 167 séries, 30 com observações, `generated_at` igual a `2026-10-31T12:51:43.986343+00:00`. SHA-256 do corpo remoto: `a0c5ac318657c8152898f2c01c0383402900cf43dc9ce8211fd2edd36d095ee1`. A comparação do conteúdo JSON inteiro com a `main` foi igual. O arquivo público do repositório não foi alterado por este PR.

Não foram encontrados erros nos consoles consultados. Não se reproduziu uma falha geral de filtros ou de rede. O modo de recuperação por câmbio direto pode fornecer Forex quando o pacote estático falha, mas isso é uma possibilidade já coberta por testes, não a causa demonstrada no site nesta auditoria.

## Situação de cada categoria

| Categoria | Históricos públicos / catálogo | Situação e motivo |
|---|---:|---|
| Forex | 10/11 | Dez pares de referência disponíveis. DXY continua sem feed/licença configurados; não é substituído por uma cesta calculada. |
| Política monetária | 2/13 | Selic e taxa overnight alvo do Canadá disponíveis. Fed depende de credencial/revisão de direitos; BCE registra falha de fonte; nove outras autoridades dependem de feed/licença. |
| Rendimentos soberanos | 4/32 | Treasury EUA 2, 5, 10 e 30 anos disponíveis; outros 28 rendimentos sem feed/licença. Acesso por Juros Globais → Rendimentos soberanos. |
| Macroeconomia | 14/49 | PIB nominal e crescimento do PIB de sete economias disponíveis. As outras 35 séries estão em revisão dos direitos de publicação. Não é ausência geral de dados macro. |
| Bolsas | 0/27 | Ausência real de feed e autorização de redistribuição configurados. Não foi encontrado defeito de caminho ou filtro que esconda históricos existentes. |
| Commodities | 0/27 | Na `main`, nenhum histórico público aprovado. Os quatro históricos de energia pertencem ao trabalho separado do PR #2 e seguem sem autorização específica comprovada. |
| Criptoativos | 0/8 | Integração pública bloqueada por credencial/plano e revisão dos direitos; nenhuma chave exposta ou dados inventados. |
| Calendário | Sem eventos automáticos no pacote estático | O diretório de agendas oficiais funciona; não existe promessa de calendário global automático nessa versão. |
| Comparador | Derivado das séries disponíveis | Compara observações existentes; selecionar um ativo sem histórico não cria dados. |

Total de indisponíveis no pacote da `main`: 137 — 92 por feed/licença, nove por credencial/direitos, 35 por revisão de publicação e uma por falha de fonte (BCE).

## Verificação dos instrumentos solicitados

| Instrumento | Histórico completo no JSON | Verificação real na interface publicada |
|---|---:|---|
| Selic meta | 1.827 observações | Gráfico anual com 366 datas, unidade % a.a. |
| Banco do Canadá — overnight alvo | 1.292 | Gráfico anual com 257 datas, unidade %. |
| PIB Brasil nominal | 66 | Última observação 2025; máximo com 66 datas. Fonte WDI, unidade USD correntes, frequência anual. |
| Treasury 2/5/10/30 anos | 1.249 por prazo | Treasury de 10 anos aberto no site, gráfico anual com 250 datas; todos os prazos exercitados no cliente estático automatizado e na prévia corrigida. |

Esses resultados verificam o pacote publicado; não representam nova coleta nas APIs financeiras nem garantia de que o mercado esteja atualizado em tempo real.

## Problemas técnicos corrigidos

### Seleção incorreta após visitar rendimentos soberanos

Reprodução no site: Juros Globais → Rendimentos soberanos → Visão Geral → cartão Selic. A URL chegava a `#rates/selic`, mas o gráfico e o seletor exibiam Treasury de dois anos. A variável do subpainel continuava em `yields`; a seleção descartava a Selic por não pertencer à lista de rendimentos. O mesmo problema atingia o link do Banco do Canadá.

Correção: o destino da rota agora determina explicitamente o subpainel. Selic e Canadá abrem política monetária; IDs de Treasury abrem rendimentos soberanos. O acesso genérico a Juros Globais retorna ao painel monetário. Teste de regressão cobre a sequência com Treasury, Selic e Canadá.

### PIB anual com apenas um ponto na janela inicial

O site exibia somente 2025 na janela de um ano, apesar de o histórico completo conter 66 observações. Isso pode parecer um gráfico sem histórico, mas é a combinação de frequência anual e período curto.

Correção: ao entrar em Macroeconomia a partir de uma janela de até um ano, a interface inicia em cinco anos. A prévia mostrou cinco observações e uma linha histórica. A seleção manual de um ano continua disponível; a janela máxima é preservada.

## PR #2 e energia

O [PR #2](https://github.com/divisaosete/Markets/pull/2) foi consultado pela API: aberto, sem merge, no commit `1903dd9`. Seu último workflow conhecido está aprovado. Ele não foi publicado no Pages, que usa a `main`.

Brent, WTI, Henry Hub e óleo de aquecimento foram isolados em validação local no PR #2. Seus direitos de redistribuição EIA/Refinitiv-LSEG continuam pendentes. Este PR de correção não incorpora esses dados, não faz merge do PR #2 e não muda a lista de fontes publicáveis. As quatro séries continuam sem observações no pacote publicado.

## Validação das correções

- Prévia estática real servida sob `/Markets/`, sem backend financeiro.
- Sequências Treasury → Visão Geral → Selic e Treasury → Visão Geral → Canadá confirmadas com instrumento e marcador corretos.
- PIB Brasil aberto com cinco observações na janela inicial corrigida.
- Testes de regressão de navegação, codificação dos IDs, janela anual e leitura dos sete instrumentos Selic/Canadá/PIB/Treasuries sem recorrer ao fallback Forex.
- Suítes Python e JavaScript, sintaxe, build e verificações HTTP executadas. Os resultados finais e o link do Actions são informados na entrega e no PR.

Evidências de rede estão em `var/published-audit/`. Capturas locais em `var/category-audit-screenshots/`: `01-published-selic-wrong-panel.jpg`, `02-fixed-selic.jpg` e `03-fixed-gdp-five-years.jpg`. Essas pastas são ignoradas pelo Git.

## Como acessar os dados que já existem

- Selic e Canadá: **Juros Globais → Política monetária**.
- Treasury: **Juros Globais → Rendimentos soberanos → Estados Unidos**.
- PIB e crescimento: **Macroeconomia**, escolhendo país e indicador. Para histórico longo, usar cinco anos ou Máx.

O novo PR depende de revisão e merge manual para chegar ao site publicado. As ausências de fontes financeiras não são resolvidas por essa correção de interface.
