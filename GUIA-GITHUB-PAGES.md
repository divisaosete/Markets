# Publicar a beta no GitHub Pages

Nenhum envio ou deploy remoto foi feito nesta preparação. A versão local já contém dados reais; os passos abaixo ativam a hospedagem na sua conta.

## Conferir no computador

Dê dois cliques em **VISUALIZAR-BETA.cmd** ou **INICIAR-NEW-ERA.cmd** desta pasta. Python é necessário apenas para essa prévia de arquivos estáticos; não inicia API ou worker. O endereço normalmente é http://127.0.0.1:8080/. Encerre com Ctrl+C. Se a porta estiver ocupada, encerre a prévia anterior.

A origem da interface é public/index.html. A raiz também contém o dashboard completo em index.html com recursos relativos a public/; veja INSTRUCOES-PUBLICACAO.md para corrigir o repositório existente. Não abra com file://. `python -m backend.build_pages` gera `_site`, pasta publicada pelo workflow. O GitHub Pages hospeda esse resultado sem Python permanente.

## Criar e publicar o repositório

1. Crie um repositório com branch principal **main**, por exemplo New-Era-Markets. Repositório público funciona com GitHub Free; privados dependem do plano.
2. Extraia New-Era-Markets-GitHub-Corrigido.zip em pasta limpa e envie o **conteúdo extraído da raiz**, incluindo `.github/workflows`, public, backend, tests, requirements e guias. Não envie somente o ZIP nem acrescente outra pasta acima desses arquivos. São 87 arquivos, abaixo do limite de 100 por envio pelo navegador. Confira se a pasta oculta `.github` e seus dois workflows foram enviados; se o seletor os omitir, use GitHub Desktop ou Git. Desktop também facilita atualizações posteriores.
3. Antes do commit/envio, confira a lista: .gitignore exclui .env, caches/bancos, builds, dependências instaladas e ZIPs. O pacote já os exclui. Em repositório público, código versionado fica visível; nunca commite segredos.
4. No GitHub, vá a **Settings → Pages → Build and deployment → Source → GitHub Actions**.
5. Em **Actions**, habilite workflows se solicitado. Execute **Publicar beta no GitHub Pages → Run workflow** na main. Ele verifica, constrói, envia somente `_site` e publica no ambiente github-pages.
6. Use a URL retornada pelo job deploy/Settings → Pages. Para projeto, costuma ter formato `https://SEU-USUARIO.github.io/New-Era-Markets/`. Verifique **Enforce HTTPS** quando exibido. Se o primeiro push falhou porque Pages ainda não estava ativado, ative e execute novamente.
7. Na URL pública, confira início, USD/BRL, EUR/BRL, períodos, comparador, fontes e celular. Essa validação externa ainda não foi executada nesta entrega.

Não escolha a raiz do repositório como pasta de site: `_site` isola recursos públicos de backend e arquivos privados. [Workflows Pages oficiais](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Atualização automática

Execute **Atualizar dados públicos → Run workflow**. Force reconsulta fontes dentro do intervalo. O agendamento `23 */6 * * *` usa UTC e a branch padrão. Intervalos por fonte: câmbio/Treasury 6h, Selic/Canadá/BCE 24h e WDI 7 dias. O estado de execução em cache evita consultas desnecessárias; falhas de cache podem exigir nova coleta, mantendo limites do provedor.

O job collect precisa de **contents: write** para registrar mudanças somente em public/data/market-data.json. Regras da organização ou branch protection podem impedir esse commit: revise a permissão e reexecute, sem force push. Não coloque um token no código. Sem mudança no JSON não há commit nem deploy.

Havendo mudança, o workflow chama o deploy reutilizável com o SHA novo. Não depende de um push do GITHUB_TOKEN iniciar outro workflow. [Regra oficial de disparo por token](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow). Build é de leitura; somente collect pode escrever conteúdo; somente deploy tem pages:write e id-token:write. Actions oficiais estão fixadas por SHA.

GitHub pode atrasar/descartar schedules e desativá-los em repositórios públicos sem atividade por 60 dias. Confira Actions e reative/execute manualmente se necessário. [Limites do schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). Não é tempo real.

## Variáveis e Secrets

**A beta padrão não precisa de Secrets.** Todas as fontes publicadas são sem chave. Em **Settings → Secrets and variables → Actions → Variables**:

- `ENABLE_DIRECT_FX=false` desabilita o complemento direto de câmbio. Vazio/true habilita.
- `PUBLIC_API_BASE` deve ficar vazio para a beta padrão. Só configure um proxy HTTPS autorizado, normalmente terminado em /api/. O build rejeita credenciais/query de token, fragmentos, HTTP e IPs privados.

Após mudar variáveis, execute o workflow de publicação para reconstruir config.js. Para integrações futuras, use **Actions → Secrets → New repository secret**, ou o ambiente secreto do proxy. FRED_API_KEY e COINGECKO_API_KEY são nomes do backend legado; não habilitam automaticamente exportação pública. Primeiro revise direitos/plano e a lista aprovada. Nunca use essas chaves em Variables, URLs, config.js ou JSON.

## Link no WordPress

Após validar a URL HTTPS real, adicione um botão/item de menu “New Era Markets” no WordPress apontando para ela. Link direto dispensa iframe e hospedagem Python no WordPress. Se abrir outra aba, use noopener. deploy/wordpress-link.html é um modelo; substitua o endereço antes de usar.

## Recuperação e manutenção

Falha por fonte preserva o histórico anterior e sinaliza disponibilidade. Falha de validação/build interrompe o deploy; o site já hospedado permanece. Não apague JSONs nem preencha preços manualmente para corrigir rede. Para recuperar, restaure um commit de dados confiável e publique novamente.

Comandos locais: `python -m backend.pages`, `python -m backend.pages --validate-only`, `python -m backend.build_pages`, `python tests/run_checks.py`. Testes completos usam requirements.txt e requirements-dev.txt; prévia e coletor estáticos usam só a biblioteca padrão. CI usa Python 3.12 e Node 22. Revise periodicamente licenças, limites, Actions e dependências.
