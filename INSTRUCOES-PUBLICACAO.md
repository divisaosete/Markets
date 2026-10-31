# Publicar o dashboard correto — Markets

## Substituir a estrutura incorreta

1. Extraia **New-Era-Markets-GitHub-Corrigido.zip** em pasta vazia. Dentro dela devem aparecer **index.html**, **.nojekyll**, **.github**, **public**, **backend**, **tests**, requirements e guias. Não envie a pasta que contém esses itens: envie os itens diretamente para a raiz de Markets.
2. Recomendado: no GitHub Desktop, clone https://github.com/divisaosete/Markets e use Repository → Show in Explorer. Copie o conteúdo extraído para essa pasta do repositório, substituindo o README anterior e arquivos correspondentes. Preserve a pasta local .git.
3. Remova somente a subpasta antiga **PUBLICAR-NO-GITHUB** da cópia clonada. Confira a lista de alterações antes do commit: a raiz agora terá index.html, public/ e .github/workflows/. Não apague public/, backend/ ou tests/ novos. Faça o commit e o push quando estiver pronto.
4. Se usar o navegador: envie o conteúdo extraído na raiz (87 arquivos no pacote). Confirme a inclusão das pastas ocultas e dos dois arquivos .github/workflows/pages.yml e .github/workflows/update-data.yml. Remova a pasta remota PUBLICAR-NO-GITHUB apenas depois de conferir os novos arquivos. Se a interface não permitir administrar a pasta ou ocultar .github, prefira GitHub Desktop. O ZIP sozinho não é extraído pelo GitHub.

Nenhum arquivo remoto foi removido nem enviado automaticamente nesta preparação.

## Configurar GitHub Pages e executar

1. Abra https://github.com/divisaosete/Markets/settings/pages.
2. Em Build and deployment → Source, escolha **GitHub Actions**. Não escolha Deploy from a branch como método definitivo: a coleta automática deve publicar o build atualizado.
3. Abra Actions. Deve aparecer **Publicar beta no GitHub Pages**. Se não aparecer, confira .github/workflows/pages.yml na raiz e habilite Actions se a conta solicitar.
4. Execute Run workflow na branch main. O job build verifica e gera _site/index.html com o dashboard e todos os recursos. O job deploy publica somente _site pelo mecanismo oficial do Pages. Espere os dois ficarem verdes.
5. Mantenha também **Atualizar dados públicos** em .github/workflows/update-data.yml: coleta periódica e manual, preservação dos históricos em falhas e chamada do mesmo workflow de publicação. Não crie outro workflow Jekyll/Pages concorrente; se já houver um workflow adicional de implantação no repositório, revise/desative-o antes de publicar. Os únicos dois workflows deste pacote são complementares.

A conta precisa permitir Actions, o ambiente github-pages e as permissões contents:write (coleta), pages:write e id-token:write (deploy). A beta padrão não exige Secrets; não coloque tokens no código ou JSON.

## Verificar o resultado

Abra https://divisaosete.github.io/Markets/ após o deploy verde e recarregue com Ctrl+F5. Confirme fundo escuro, menu, cartões, USD/BRL, histórico, comparador e fontes. Em ferramentas de rede, CSS/JS/JSON devem retornar 200 sob /Markets/. Indicadores indisponíveis continuam indicados sem valores inventados.

O index.html da raiz já contém o dashboard verdadeiro e referencia ./public/styles.css e ./public/bootstrap.js; não é uma apresentação nem redirecionamento. Os módulos resolvem seus imports e public/data/market-data.json relativamente ao próprio arquivo. .nojekyll evita a geração por Jekyll. Isso também permite abrir a raiz em uma prévia estática, mas o método de atualização recomendado e validado é GitHub Actions → _site.

Se continuar aparecendo somente Markets/README, confira: URL correta; commit novo na main; ausência de pasta intermediária; Source GitHub Actions; execução mais recente verde. Uma mensagem de erro no workflow precisa ser analisada pelo log, não corrigida apagando os dados.

## Estrutura

```text
(raiz do repositório Markets)
├── index.html                 # dashboard completo, entrada de segurança da raiz
├── .nojekyll
├── .github/workflows/
│   ├── pages.yml              # build e deploy oficial de _site
│   └── update-data.yml        # coleta e reutilização do deploy
├── public/                    # interface original e dados; fonte do build
│   ├── index.html
│   ├── styles.css
│   ├── bootstrap.js
│   └── data/market-data.json
├── backend/                   # coletores e build
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── INSTRUCOES-PUBLICACAO.md
```

Os demais arquivos de manutenção, modelos e evidências permanecem no pacote. Não envie _site, var, dependências instaladas, ZIPs ou pastas de versões anteriores. Para atualizar a entrada da raiz após futuras alterações de HTML, execute python tools_finalize.py; a origem continua sendo public/index.html. O workflow sempre constrói a partir de public/.
