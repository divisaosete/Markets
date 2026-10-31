# New Era Markets — Beta para GitHub Pages

A versão atual funciona como site estático, com dados reais em JSON e câmbio direto opcional, sem chaves no navegador. Mantém o tema, gráficos e módulos existentes. Não foi publicada remotamente nesta preparação.

**Para abrir no computador:** dê dois cliques em **VISUALIZAR-BETA.cmd** ou **INICIAR-NEW-ERA.cmd**. Python serve somente os arquivos estáticos de prévia; não inicia API ou worker. A janela mostra o endereço (normalmente http://127.0.0.1:8080/). Encerre com Ctrl+C. Não abra por file://.

**Para publicar:** siga [GUIA-GITHUB-PAGES.md](GUIA-GITHUB-PAGES.md). O workflow gera `_site` somente com recursos públicos e publica esse diretório. Os caminhos relativos funcionam no subdiretório do repositório. A hospedagem final não precisa de Python permanente. Nenhuma chave é necessária para as fontes padrão.

## Correção da publicação

Siga [INSTRUCOES-PUBLICACAO.md](INSTRUCOES-PUBLICACAO.md). O conteúdo do ZIP vai diretamente na raiz de Markets. index.html na raiz é o dashboard completo, com recursos relativos em public/. O build oficial continua public/ → _site, com Source GitHub Actions. Remova a subpasta remota antiga PUBLICAR-NO-GITHUB depois de conferir a substituição. Consulte [RELATORIO-CORRECAO-PAGES.md](RELATORIO-CORRECAO-PAGES.md).

## Cobertura atual

30 históricos reais: dez pares FX de referência, Selic, Canadá, PIB/crescimento de sete economias e Treasury 2/5/10/30 anos. A página inicial prioriza disponíveis. Índices, commodities, FRED/cripto e séries ainda sem revisão ficam identificados; não impedem a beta e não foram substituídos por proxies.

Fontes e direitos: [FONTES-DE-DADOS.md](FONTES-DE-DADOS.md) e public/DATA-LICENSES.md. Câmbio e rendimentos são referências diárias, não preços intradiários. Indicadores WDI são anuais. Datas de coleta e de observação são distintas. Não há valores, candles ou séries artificiais.

## Coleta e construção

`python -m backend.pages` atualiza somente fontes aprovadas, validando e preservando o último histórico em falhas. `--force` reconsulta dentro dos intervalos. `--validate-only` confere o JSON. Nunca exporta o banco SQLite privado.

`python -m backend.build_pages` cria `_site` por lista explícita. `PUBLIC_API_BASE` opcional deve ser HTTPS sem credenciais; vazio mantém a beta padrão. `ENABLE_DIRECT_FX=false` desativa o complemento de câmbio. No GitHub, são Repository Variables, nunca campos para segredos.

Os workflows em .github/workflows incluem coleta a cada seis horas e execução manual. Cada fonte tem seu intervalo. Não há commit quando o conteúdo público não muda. Execuções agendadas podem atrasar; não prometem tempo real. O cache de coleta nunca vira artefato Pages.

## Testes e documentação

### Energia: validação local, sem autorização de publicação

Brent, WTI, Henry Hub e óleo de aquecimento estão bloqueados no JSON público, no coletor de produção e no backend opcional até comprovar os direitos de redistribuição EIA/Refinitiv-LSEG. O build rejeita observações dessas séries; uma credencial não libera a publicação.

Para testar localmente, instale `requirements.txt`, execute `python -m backend.energy_validation --force` e depois `python -m backend.preview_energy`. Abra `http://127.0.0.1:8081/Markets/`. Essa prévia tem aviso **NÃO PUBLICAR**, escuta somente em `127.0.0.1` e grava dados/relatórios exclusivamente em `var/`, ignorado pelo Git. Não envie essa pasta ao GitHub ou Pages. Sem `--force`, o coletor local respeita 24 horas desde a última coleta bem-sucedida.

O comando normal `python -m backend.preview_pages` usa apenas o pacote público com 30 históricos. Consulte [o teste final](docs/final-market-test.md) para resultados, capturas locais e alternativas de fontes.

Instale requirements.txt e requirements-dev.txt para os testes completos; o coletor e a prévia estáticos usam apenas Python padrão. Execute `python tests/run_checks.py`. Há teste HTTP estático em tests/pages_static_smoke.py, relatórios de coleta real e auditoria de dependências em docs. CI usa Python 3.12 e Node 22. No Python 3.15/Windows, PyYAML pode precisar da instalação pura com a variável PYYAML_FORCE_LIBYAML=0; não é necessário instalar compilador para abrir a beta.

- [Fontes e permissões](FONTES-DE-DADOS.md)
- [Guia de publicação](GUIA-GITHUB-PAGES.md)
- [Otimização, verificações e pendências](RELATORIO-OTIMIZACAO.md)

Pacote: **New-Era-Markets-GitHub-Corrigido.zip**. Extraia em pasta limpa: os arquivos já estão na raiz correta, sem pasta adicional. Envie o conteúdo extraído, incluindo `.github/workflows`. Não envie o ZIP como se fosse o site. A raiz Markets permanece a versão de trabalho atual; não é necessário extrair sobre ela.

O backend anterior permanece opcional: `python run.py local`. Os dois modelos WordPress ficam em deploy. O pacote exclui bancos, credenciais, caches, dependências instaladas e relatórios históricos; preserva todos os testes e scripts de coleta.

New Era Labs — Ciência além do horizonte. *Per Vitam, Ad Astra.*
