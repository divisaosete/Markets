# Correção do GitHub Pages — 31/10/2026

## Causa confirmada

A inspeção pública de https://github.com/divisaosete/Markets mostrou PUBLICAR-NO-GITHUB/ e README.md na raiz, sem index.html e sem .github/workflows na raiz. O GitHub procura workflows somente no caminho próprio da raiz; os arquivos aninhados não ativam a implantação. A captura enviada mostra a página gerada a partir do README, e não o dashboard. A configuração privada de Settings/Pages não foi acessada, portanto a seleção exata anterior de Source não foi confirmada.

Fontes: [repositório inspecionado](https://github.com/divisaosete/Markets) e [publicação oficial por workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Correções realizadas

- ZIP com 87 arquivos diretamente na raiz; nenhuma pasta intermediária PUBLICAR-NO-GITHUB.
- index.html da raiz contém o dashboard completo original, com apenas três referências ajustadas para ./public/favicon.svg, ./public/styles.css e ./public/bootstrap.js. Não é apresentação nem redirecionamento.
- .nojekyll na raiz; o artefato gerado também contém .nojekyll. Não há dependência de Jekyll.
- Todos os 17 arquivos de public/ estão idênticos ao pacote otimizado anterior, incluindo estilos, módulos, gráficos, configurações e dados. As 30 séries disponíveis e seus históricos não foram alterados nem substituídos por dados artificiais. A data original de coleta é conservada; não houve nova consulta financeira ao vivo nesta correção.
- pages.yml permanece em .github/workflows/, constrói public/ em _site/ e envia somente esse artefato, com index.html e 17 outros recursos estáticos. Foram acrescentados index.html e .nojekyll ao filtro de disparo por alteração. configure-pages, upload-pages-artifact e deploy-pages oficiais estão preservados, com ações fixadas por SHA.
- Deploy depende de build e tem pages:write, id-token:write e ambiente github-pages. Build tem leitura do conteúdo. Coleta tem contents:write e reutiliza o mesmo workflow de deploy após alteração de dados. Não existem workflows locais duplicados de implantação: pages.yml e update-data.yml são complementares. A presença de qualquer outro workflow remoto deve ser conferida após a substituição.
- Atualização automática preservada: fonte canônica public/data/market-data.json; coleta e workflow update-data.yml idênticos ao pacote anterior. A entrada da raiz usa esses mesmos dados, sem cópia paralela do histórico.
- Empacotador gera a entrada da raiz a partir de public/index.html para manter consistência em futuras entregas; a pasta antiga PUBLICAR-NO-GITHUB fica ignorada pelo Git.

## Estrutura final

```text
index.html
.nojekyll
.github/workflows/pages.yml
.github/workflows/update-data.yml
public/index.html
public/styles.css
public/*.js
public/data/market-data.json
backend/
tests/
deploy/
docs/
requirements.txt
requirements-dev.txt
README.md
INSTRUCOES-PUBLICACAO.md
RELATORIO-CORRECAO-PAGES.md
```

A árvore é resumida. O ZIP contém também configurações, licenças, exemplos seguros e documentação essencial. O método oficial é Source GitHub Actions → _site. A raiz também oferece o dashboard completo ao servir estaticamente o conteúdo do repositório, com recursos relativos a public/. Não se recomenda manter publicação pela branch, pois o workflow controla variáveis, segurança e isolamento do artefato.

## Testes executados

O primeiro ZIP desta correção foi extraído em var/pages-corrected-preview/Markets, sem importar arquivos de origem externos; somente dependências previamente instaladas foram reutilizadas por PYTHONPATH.

- python tests/run_checks.py: **104 testes Python aprovados**, incluindo teste novo que verifica identidade do dashboard da raiz com a origem e os três caminhos relativos; **49 testes JavaScript aprovados**. Sintaxe JavaScript e compilação Python aprovadas.
- python -m backend.pages --validate-only: JSON válido.
- python tests/pages_static_smoke.py: **41 verificações HTTP reais aprovadas**. Simulação do artefato publicado em /Markets/ e da entrada de repositório em /fallback/Markets/, servindo HTML, CSS, módulos, JSON e .nojekyll. No artefato oficial, API, backend, .env e banco não são expostos. A conferência do HTML exige o título New Era Markets | New Era Labs e os módulos reais, impedindo considerar README como dashboard.
- python -m backend.build_pages: **18 arquivos estáticos**, **30 séries disponíveis**, caminhos relativos e configuração pública sem API local obrigatória. Os módulos JavaScript usam imports relativos; o JSON é resolvido relativamente a import.meta.url de public/static-data.js, preservando /Markets/.
- Comparação byte a byte: os 17 arquivos públicos e o workflow de coleta são idênticos ao ZIP anterior. CRC e caminhos de extração verificados, sem arquivo fora do destino e sem diretório intermediário.

Limitação nesta rodada: a prévia persistente na porta 8085 teve conexão recusada/timeout; a ferramenta de navegador também falhou ao anexar a aba. Uma sondagem separada dessa prévia expirou. Não foi possível registrar nova validação visual desktop/celular. Os testes HTTP com servidor temporário próprio passaram nas 41 verificações; não devem ser confundidos com o navegador que falhou. A interface pública não sofreu alterações e a validação visual anterior permanece apenas evidência histórica.

Logs desta execução: var/pages-corrected-preview/Markets/docs/backend-tests.txt, frontend-tests.txt, checks-results.json e pages-static-http.json, fora do ZIP final. São regeneráveis pelos comandos acima. O relatório de otimização e evidências antigos incluídos no pacote descrevem a entrega anterior (83 arquivos/103 Python/22 HTTP); este relatório descreve a correção atual (87/104/41).

## Envio, remoção e pendências

Envie **todo o conteúdo extraído de New-Era-Markets-GitHub-Corrigido.zip diretamente à raiz do repositório Markets**, incluindo os arquivos ocultos .github, .nojekyll e .gitignore. Não envie somente o ZIP e não selecione a pasta externa que contém esses itens. O pacote está abaixo de 100 arquivos; GitHub Desktop é recomendado para revisar substituições e remover a pasta antiga com segurança.

Depois de conferir os novos caminhos, remova a subpasta remota antiga **PUBLICAR-NO-GITHUB/** e substitua o README antigo pelo incluído. Preserve quaisquer arquivos alheios ao projeto. A remoção remota é uma ação do usuário: nenhum arquivo remoto foi excluído e nenhum push/deploy foi realizado por esta preparação.

Ative Settings → Pages → Source GitHub Actions. Execute Publicar beta no GitHub Pages na main; espere build/deploy verdes. Confira https://divisaosete.github.io/Markets/ com atualização forçada, fundo escuro, cartões, gráficos, comparador e fonte/data das referências. O guia INSTRUCOES-PUBLICACAO.md detalha o procedimento, incluindo preservação dos dois workflows.

A confirmação da URL HTTPS pública e execução real de Actions permanece pendente, assim como restrições de licença/chaves dos 137 instrumentos indisponíveis. Essas restrições não foram modificadas por esta correção. Nenhum segredo, .env real, banco, dependência instalada ou cache foi incluído.

SHA256 do histórico público preservado: `1ce47867f48f25c0783701e17b5a2ac03162a9983c25da66ffc5f33bbacb50e9`.
