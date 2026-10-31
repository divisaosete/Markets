> Registro da entrega anterior, com 83 arquivos. A versão corrigida atual tem 87 arquivos; consulte RELATORIO-CORRECAO-PAGES.md e INSTRUCOES-PUBLICACAO.md.

# Relatório de otimização — New Era Markets

Data: 31/10/2026. Projeto existente preservado; nenhuma publicação remota realizada.

## Quantidade e estrutura

| Medida | Antes | Depois |
|---|---:|---:|
| Arquivos no pacote de repositório | 152 | 83 |
| Arquivos públicos de origem | 17 | 17 |
| Workflows | 2 | 2 |

Redução líquida de 69 arquivos (45,4%): 70 entradas antigas excluídas do pacote e este relatório acrescentado. A contagem ignora entradas de diretórios do ZIP. A auditoria recursiva inicial encontrou 4.370 arquivos na pasta de trabalho, incluindo dependências instaladas, caches e cópias de versões anteriores. Esse número não é a contagem da versão Beta: ela tinha 152 arquivos. A limpeza é do pacote; pastas locais de trabalho não foram apagadas.

O novo ZIP coloca README.md, public/, backend/, tests/, deploy/ e .github/workflows/ diretamente na raiz. Não existe pasta intermediária New-Era-Markets/. O HTML de origem correto é public/index.html. O workflow constrói e publica apenas _site/, com 18 recursos estáticos; não publica a raiz do repositório como site.

O maior arquivo é public/data/market-data.json: 1.902.766 bytes, bem abaixo de 25 MiB. Nenhum histórico foi reduzido para atingir a contagem.

## Preservado e dependências

- Todos os 17 arquivos públicos: HTML, CSS, JavaScript, gráficos, catálogo, dados JSON, ícone, configuração e atribuições DATA-LICENSES.md.
- Todos os 23 arquivos de backend sem cache: coletores, provedores, validação, build, prévia e backend opcional.
- Todos os 21 arquivos de testes úteis, incluindo integração e validação de workflows.
- Os dois workflows originais de coleta e publicação em .github/workflows, requirements.txt, requirements-dev.txt e package.json.
- Guias atuais, FONTES-DE-DADOS.md, cinco arquivos de documentação/evidência, exemplos seguros e os dois modelos WordPress.

A procura por dependências em backend/tests confirmou que deploy/wordpress.html é lido por um teste; foi mantido. deploy/wordpress-link.html é referenciado pelo guia. Os outros relatórios removidos são saídas históricas ou geradas pelos testes, não entradas de execução. Docker/Caddy/Compose pertencem à implantação de servidor anterior e não são usados pelos workflows Pages. A implantação Docker anterior não faz parte deste pacote otimizado.

Comparação byte a byte com o ZIP Beta: todos os 17 arquivos públicos e os dois workflows permanecem idênticos. Coletor, fontes de dados e identidade visual não foram modificados. As alterações são documentação, .gitignore e seleção/raiz do empacotamento; tests/run_checks.py também passa a criar docs/ quando necessário para gravar resultados.

## Segurança

Não foram identificadas credenciais reais nos arquivos selecionados. Foram verificadas extensões/caminhos privados, padrões de chaves privadas e tokens GitHub/AWS/OpenAI, exemplos de configuração e atribuições de credenciais. .env.example tem campos de credenciais vazios; valores sentinela dos testes são fictícios. Nenhum .env real, banco SQLite, log, chave privada, ambiente virtual, dependência instalada, cache ou backup entra no ZIP. Os dois certificados PEM encontrados nas dependências locais são cadeias públicas de autoridades certificadoras, não credenciais privadas, e também não entram no pacote.

.gitignore foi ampliado para variantes .env (com exceção de .env.example), bancos e auxiliares, logs, certificados/chaves, arquivos de credenciais, backups e resultados temporários. O empacotador usa seleção explícita, não inclui pastas antigas e rejeita links simbólicos. .gitignore não remove arquivos já versionados; antes do primeiro commit, confira a seleção mostrada pelo GitHub Desktop/Git. Nenhuma integração exigiu recomendação de rotação por credencial encontrada. Esta inspeção não é uma certificação de segurança de todos os arquivos privados da máquina.

O resultado anterior de pip-audit, conservado em docs/dependency-audit-pages.json, não identificou vulnerabilidades conhecidas nas dependências de execução consultadas. Não houve nova consulta de vulnerabilidades nesta otimização; requirements foi preservado e o workflow executa a auditoria novamente.

## Testes realmente executados no conteúdo extraído

Extração em var/publication-verify, separada da origem, com caminhos conferidos e sem pasta adicional. As dependências instaladas foram reutilizadas por PYTHONPATH, sem importar o backend da pasta de origem.

- python tests/run_checks.py: 103 testes Python e 49 JavaScript aprovados; sintaxe JavaScript e compilação Python aprovadas. Incluem testes dos coletores, validação, preservação de históricos em falhas e configuração dos workflows.
- python -m backend.pages --validate-only: JSON público válido.
- python tests/pages_static_smoke.py: 22 verificações HTTP reais aprovadas sob /repo/, com recursos públicos acessíveis e API, backend, .env e banco retornando 404.
- python -m backend.build_pages --output var/static-preview/markets --no-direct-fx: 18 arquivos estáticos construídos, 30 históricos disponíveis.
- Navegador real em /markets/, servido somente por HTTP estático: início com 12 cartões e 30 indicadores; USD/BRL com gráfico e tabela em 5,4325 BRL, referência 30/10/2026. Seleção 1M mostrou 22 datas. Complemento FX direto desativado apenas no artefato de teste, para comprovar independência de API/backend. A configuração pública de origem permanece idêntica.
- Computador: viewport 1280 px, conteúdo 1265 px; celular simulado: área útil 375 px e largura de conteúdo 375 px, sem transbordamento horizontal. Navegação e gráfico permaneceram disponíveis. Evidência visual local: var/optimization-mobile.png (fora do pacote).

A primeira execução HTTP foi bloqueada por permissões locais (WinError 10013); os testes foram repetidos com a permissão necessária e passaram. Isso não foi tratado como falha da aplicação. Não houve nova coleta ao vivo de indicadores: os 30 históricos reais e todas as observações foram preservados integralmente do pacote Beta e validados, sem inventar dados. Os relatórios de coleta e navegação anteriores mantidos em docs são evidências históricas, não novas execuções remotas.

Os logs completos desta execução ficam em var/publication-verify/docs na pasta de trabalho e são regenerados ao executar os testes. Foram excluídos do ZIP para reduzir arquivos. Conferência final do ZIP: CRC, quantidade, caminhos na raiz e igualdade de cada entrada com a origem selecionada.

## Pendências e publicação

O pacote pode ser enviado pelo navegador: 83 arquivos, abaixo do limite de 100 por envio. Extraia em pasta limpa e envie o conteúdo extraído, nunca apenas o ZIP. Confirme que .github/workflows/pages.yml e update-data.yml aparecem no repositório. Se o seletor ocultar .github, use GitHub Desktop ou Git. Para manutenção recorrente, GitHub Desktop é recomendado.

Referência: [Adicionar arquivos ao repositório — GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository); [fonte oficial com limite de 100 arquivos](https://github.com/github/docs/blob/main/content/repositories/working-with-files/managing-files/adding-a-file-to-a-repository.md).

Siga GUIA-GITHUB-PAGES.md: configurar Pages com Source GitHub Actions, habilitar/executar workflows e conferir a URL HTTPS pública. Nenhum workflow foi executado no GitHub e nenhum deploy externo foi realizado aqui; permissões da conta, branch protection e comportamento de provedores no runner só poderão ser confirmados nessa execução.

Os 137 instrumentos indisponíveis continuam identificados, com restrições de licença/chaves/revisão das fontes e falha anterior BCE. A otimização não habilita essas integrações. O agendamento é periódico, não tempo real. Link WordPress depende da URL publicada. O backend opcional permanece no código; Docker/Caddy/Compose não estão incluídos.

## Entradas removidas do pacote anterior

Não foram apagadas da pasta de trabalho; somente excluídas do ZIP. Caches, bancos, instalações locais e backups já estavam fora do ZIP Beta e continuam fora. ZIPs antigos de entrega são retirados após a validação do novo, com cópia de recuperação privada em var/recovery.

- `.dockerignore`
- `AUDITORIA-PUBLICACAO.md`
- `RELATORIO-FINAL.md`
- `STATUS-DA-PLATAFORMA.md`
- `deploy/.env.production.example`
- `deploy/Caddyfile`
- `deploy/Dockerfile`
- `deploy/compose.yaml`
- `docs/ALTERACOES-DADOS-CORRIGIDOS.json`
- `docs/ALTERACOES-GRAFICOS.json`
- `docs/API.md`
- `docs/ARQUIVOS-ALTERADOS.json`
- `docs/ARQUIVOS-CORRIGIDOS.json`
- `docs/AUDITORIA-DADOS-CORRIGIDOS.md`
- `docs/AUDITORIA-DADOS-FINAL.md`
- `docs/AUDITORIA-DADOS-INICIAL.md`
- `docs/AUDITORIA-FINAL.md`
- `docs/AUDITORIA-GRAFICOS.md`
- `docs/AUDITORIA-INICIAL.md`
- `docs/BACKEND-PYTHON.md`
- `docs/CATALOGO-AUDITADO.csv`
- `docs/CORRECOES-DADOS.md`
- `docs/CORRECOES.md`
- `docs/DIAGNOSTICO-INTERFACE.md`
- `docs/DISPONIBILIDADE-POR-ATIVO.csv`
- `docs/DISPONIBILIDADE-POR-ATIVO.json`
- `docs/EXECUCAO-LOCAL.md`
- `docs/FEED-LICENCIADO.md`
- `docs/FONTES.md`
- `docs/INSTALACAO.md`
- `docs/LIMITACOES.md`
- `docs/LIVE-SERVER.md`
- `docs/PRESERVACAO-VISUAL.json`
- `docs/RELATORIO-CORRECOES-INTERFACE.md`
- `docs/WORDPRESS.md`
- `docs/antes-live-server.png`
- `docs/api-indisponivel-calendario.png`
- `docs/auditoria-desktop.png`
- `docs/auditoria-smartphone.png`
- `docs/backend-tests.txt`
- `docs/browser-interface-results.json`
- `docs/browser-results.json`
- `docs/checks-results.json`
- `docs/corrigido-com-backend.png`
- `docs/corrigido-mobile-com-backend.png`
- `docs/desktop-comparador.png`
- `docs/diagnostico-carregamento.json`
- `docs/frontend-tests.txt`
- `docs/graficos-api-real.json`
- `docs/graficos-eurbrl-desktop.png`
- `docs/graficos-eurbrl-mobile.png`
- `docs/graficos-final.png`
- `docs/graficos-navegador-real.json`
- `docs/graficos-persistencia-real.json`
- `docs/http-cache-real.json`
- `docs/http-results.json`
- `docs/live-results-integracao-anterior.json`
- `docs/live-results.json`
- `docs/live-server-mobile-sem-backend.png`
- `docs/live-server-sem-backend.png`
- `docs/mobile-comparador.png`
- `docs/pages-beta-fx.png`
- `docs/pages-beta-home.png`
- `docs/pages-beta-mobile.png`
- `docs/pages-static-http.json`
- `docs/static-loading-results.json`
- `docs/syntax-app.txt`
- `docs/syntax-chart.txt`
- `docs/syntax-python.txt`
- `docs/worker-coverage.json`

## Integridade dos históricos

SHA256 de public/data/market-data.json, idêntico ao Beta: `1ce47867f48f25c0783701e17b5a2ac03162a9983c25da66ffc5f33bbacb50e9`.
