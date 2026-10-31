# Recuperação do New Era Markets Beta — 31/10/2026

## Diagnóstico

A execução 41209672057, no commit b2aed12, encerrou o build após
`backend-tests.txt: FAIL`; os quatro outros grupos passaram. O workflow não
publicava os detalhes dos testes, portanto o log remoto não contém os tracebacks.
Na mesma revisão, a reprodução local confirmou a ausência de `.nojekyll` e de
`.github/workflows/update-data.yml`, exigidos pelos testes de publicação.
PyYAML já estava declarado para CI, mas precisava ser instalado no ambiente local.
O teste de hardlinks requer permissões locais que o ambiente restrito não oferece;
ele passou ao executar com as permissões necessárias, sem ser removido ou ignorado.

Foi encontrada também uma condição intermitente no teste do heartbeat: a espera
por polling de dois segundos podia terminar antes da gravação pelo thread no
Windows. O teste agora aguarda um Event após a gravação real e continua exigindo
renovação da lease, heartbeat persistido e liberação da lease ao encerrar.

## Correções

- Restaurado `.nojekyll` na raiz, mantendo o dashboard e seus recursos relativos.
- Adicionado `.gitignore` para segredos locais, bancos, dependências e resultados temporários.
- Restaurado o coletor agendado a cada seis horas (UTC), com execução manual,
  cache dos intervalos por fonte, validação do JSON e build antes do commit.
- O coletor registra somente `public/data/market-data.json`; falhas das fontes
  preservam o histórico e são resumidas no Actions. Não há cotações inventadas.
- O deploy reutilizável recebe o SHA do commit de dados, sem depender de um
  novo evento de push do GITHUB_TOKEN. Proteções da main continuam sendo respeitadas.
- Pull Requests passam pelo build e testes; o deploy fica restrito à main.
- Adicionada verificação HTTP de recursos em `/Markets/` ao build do Actions.
- Falhas dos testes passam a exibir os detalhes no log do Actions.
- Teste do heartbeat sincronizado por evento, mantendo suas asserções.

## Validação local

- `python tests/run_checks.py`: 104 testes Python, 49 JavaScript e sintaxes aprovados.
- `python -m backend.build_pages`: 18 arquivos públicos, 30 séries com histórico.
- `python tests/pages_static_smoke.py`: 41 verificações HTTP aprovadas,
  incluindo `/Markets/`, fallback da raiz e ausência de arquivos privados.
- `python tests/ui_loading_smoke.py`: 28 recursos essenciais aprovados.
- `python -m tests.http_smoke`: 13 verificações HTTP do backend aprovadas.
- `python -m pip_audit -r requirements.txt --no-deps --disable-pip`:
  nenhuma vulnerabilidade conhecida encontrada na consulta.

Os testes locais usam Python 3.15 no Windows; CI usa Python 3.12 e Node 22
no Linux. Testes com fixtures são separados das consultas de fontes reais.

`python -m tests.live` consultou fontes reais: passaram Selic, USD/BRL, PIB dos
EUA, taxa do Canadá, Treasury de 2/5/10/30 anos e calendário BoE. O BCE falhou
com URLError e o calendário BLS com HTTPError nesta tentativa. Bitcoin e Fed
reportaram dependência de credenciais/licenças. Esses resultados não equivalem
a sucesso de todas as fontes; o teste não alterou o JSON público de cotações.

## Resultado remoto

- Branch enviada: `fix/new-era-markets-deployment`.
- [Pull Request #1](https://github.com/divisaosete/Markets/pull/1), direcionado à main.
- [Actions 41213402171](https://github.com/divisaosete/Markets/actions/runs/41213402171):
  sucesso no build do Pull Request em Linux, incluindo testes, auditoria e HTTP estático.
- O deploy do PR é ignorado por projeto. O workflow agendado só executará após merge.
- Consulta a `https://divisaosete.github.io/Markets/` retornou HTTP 404 nesta entrega.
  A publicação pública corrigida ainda não ocorreu.
- Próximo passo: o usuário revisar e aprovar o merge do PR; depois conferir o
  workflow de publicação e a URL pública. Nenhum merge foi realizado pelo agente.

## Publicação e operação

O repositório usa Git Credential Manager e a autenticação existente confirmou
permissão de escrita. GitHub Pages já está configurado com `build_type: workflow`.
As mudanças devem ser revisadas no Pull Request antes de integrar à main.
Nenhum merge é autorizado automaticamente. O deploy corrigido só pode ser
confirmado após essa integração e sua execução bem-sucedida.

O agendamento só entra em operação na branch padrão. Regras que impeçam o bot
de gravar na main interrompem a atualização com erro; não há force push nem
contorno das regras. Fontes sem licença ou credenciais continuam indisponíveis.
O painel exibe referências atualizadas periodicamente, sem garantia de tempo real.

Referências oficiais: [deploy do Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
e [workflows reutilizáveis](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
