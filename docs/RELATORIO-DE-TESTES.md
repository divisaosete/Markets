# Atualização — correção Pages

Pacote isolado: 104 Python, 49 JavaScript e 41 HTTP aprovados; sintaxe e build de 18 recursos aprovados. Nova verificação visual bloqueada por falha da prévia/navegador. Consulte [RELATORIO-CORRECAO-PAGES.md](../RELATORIO-CORRECAO-PAGES.md).

## Registro anterior da otimização

# Testes — pacote otimizado / 31/10/2026

No conteúdo extraído do ZIP: 103 testes Python, 49 JavaScript, sintaxe e compilação aprovados. JSON público validado. 22 verificações HTTP reais sob /repo/ aprovadas. Build estático com 18 arquivos e 30 séries disponíveis.

Navegador real sob /markets/: início com 12 cartões, gráfico USD/BRL e período 1M (22 observações); computador e celular sem transbordamento horizontal. Prévia sem API e sem complemento FX direto; fonte pública original não modificada.

Os resultados e limitações desta execução estão em [RELATORIO-OTIMIZACAO.md](../RELATORIO-OTIMIZACAO.md). Logs detalhados são gerados em docs ao executar python tests/run_checks.py e python tests/pages_static_smoke.py; não acompanham o ZIP.

pages-collection-results.json e pages-browser-results.json conservam evidências anteriores da Beta, incluindo coleta real e navegação ampliada. pages-publication-manifest.json é o manifesto anterior, não o inventário do pacote otimizado. dependency-audit-pages.json registra a consulta anterior, sem vulnerabilidades conhecidas nas dependências verificadas. Essas evidências não representam execução remota de Actions nem publicação HTTPS.
