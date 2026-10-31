# Fontes e licenças dos dados publicados

Cada registro JSON identifica fonte, licença, unidade, referência e coleta. Esta coleção reúne conjuntos independentes; não transfere para todos eles a licença de um único provedor. New Era Labs não é endossado por essas instituições.

- **BCB — SGS 432 / Meta Selic:** ODbL 1.0, atribuição Banco Central do Brasil / Copom. Os dados desta série e suas adaptações são disponibilizados sob a mesma ODbL. Fonte e aviso: https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom . Licença: https://opendatacommons.org/licenses/odbl/1-0/ .
- **Câmbio Frankfurter / BCE:** referência diária, não preço de execução. Reprodução com atribuição ao BCE, informando alterações; informações disponíveis gratuitamente na fonte. API intermediária: https://frankfurter.dev/ . Termos: https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html .
- **Banco Mundial / WDI — PIB e crescimento do PIB:** CC BY 4.0, com termos adicionais do Banco Mundial. Fonte: World Bank, World Development Indicators; PIB em USD correntes e crescimento percentual anual. Termos: https://datacatalog.worldbank.org/public-licenses . Outras séries WDI permanecem em revisão na beta pública, por possíveis direitos de terceiros.
- **Canadá — target for overnight rate:** Bank of Canada / Valet, reprodução conforme termos, sem logotipo e sem sugestão de endosso; informação disponível gratuitamente na fonte. https://www.bankofcanada.ca/terms/ .
- **Treasury — Daily Par Yield Curve:** dados oficiais do governo dos EUA, com atribuição US Treasury; não incluir material de terceiros nem logotipos como se fossem licenciados. https://home.treasury.gov/treasury-daily-interest-rate-xml-feed .

Transformações: datas normalizadas para sua frequência original; seleção de janelas, variações e base 100 calculadas; nenhuma interpolação, expectativa ou observação inventada. Fonte e dados originais prevalecem; estes cálculos não são publicação oficial do provedor.

- **EIA — Brent, WTI, Henry Hub e óleo de aquecimento:** downloads XLS oficiais, domínio público com atribuição U.S. Energy Information Administration. Referências spot diárias, sem futuros: Europa Brent FOB e Cushing WTI FOB em USD/barril; Henry Hub em USD/MMBtu; New York Harbor No. 2 Heating Oil FOB em USD/galão dos EUA. Datas são as observações publicadas, sem preenchimento de feriados. Consulta diária no Actions, nunca tempo real. Política: https://www.eia.gov/about/copyrights_reuse.php .

FRED, CoinGecko, índices e as demais commodities não entram automaticamente na publicação. Chave de API não equivale a licença de redistribuição. Históricos sem autorização permanecem indisponíveis. Não são substituídos por ETFs ou outros instrumentos.
Nos pares com base diferente de EUR, a conversão de base/câmbio cruzado é fornecida pelo Frankfurter a partir das referências BCE; não é uma cotação intradiária de execução.
