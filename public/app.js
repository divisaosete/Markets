import {api,apiConfigured,fmt,escape as esc,dateLabel,safeURL,healthLabel} from './data.js';
import {ASSETS,OVERVIEW,DIRECTORY} from './catalog.js';
import {SERVICE_MESSAGE,unavailableSeries,unavailableCalendar,unwrapSeries} from './offline.js';
import {Chart,COLORS,hasOHLC,chartValue} from './chart.js';
import {filterAssets,selectionFor,navigationState,curveModel,variation,futureEvents} from './analytics.js';
import {Poller} from './polling.js';
import {STATUS_LABELS,statusMarkup,cardMarkup,failureNotice,comparisonHelpMarkup} from './presentation.js';
const MODULES=[['overview','◈','Visão Geral','Uma leitura integrada dos mercados globais.'],['indices','▥','Bolsas Globais','27 índices. Identidade, região e fonte preservadas.'],['commodities','◇','Commodities','Energia, metais, agricultura e pecuária.'],['fx','⇄','Câmbio','Referências diárias de câmbio; sem promessa de tempo real.'],['crypto','₿','Criptomoedas','Preços agregados, capitalização e volume.'],['macro','◎','Macroeconomia','Economias em perspectiva. Indicadores anuais oficiais WDI.'],['rates','⌁','Juros Globais','Instrumentos de política monetária e rendimentos soberanos.'],['compare','⊞','Comparador de Ativos','Até cinco séries, alinhadas sem interpolação.'],['calendar','▦','Calendário Econômico','Eventos oficiais e próximos marcos de divulgação.'],['sources','≋','Fontes e Metodologia','Origem, frequência, cobertura e limitações dos dados.']];
let catalog=ASSETS,overview=OVERVIEW,section='overview',selected='',period='1A',filter='',search='',selectedCompare=['usdbrl','eurbrl'],mode='base100',chart=null,rows=[],generation=0,sub='rates',curveCountry='Estados Unidos',rateSort='desc',rateCountries=new Set(),curveChart=null,poller=null;
let futureCoverage=0;
const $=s=>document.querySelector(s),content=$('#content');
const stateLabel=STATUS_LABELS;
function asset(id){return catalog.find(a=>a.id===id)}
function status(s){return statusMarkup(s)}
function periods(){return `<div class="periods">${['1D','5D','1M','3M','6M','1A',...(section==='rates'?['3A']:[]),'5A',...(section==='rates'?['10A']:[]),'MAX'].map(p=>`<button data-period="${p}" class="${p===period?'active':''}">${p==='MAX'?'Máx.':p}</button>`).join('')}</div>`}
function card(a,s){return cardMarkup(a,s)}
function chartPanel(){return `<section class="panel"><div class="panel-head"><div><h2 id="chart-title">Histórico</h2><p id="chart-caption">Observações reais; intervalos sem dados não são preenchidos.</p></div>${periods()}</div><div class="toolbar"><label>Visualização <select id="chart-type"><option value="line">Linha</option><option value="area">Área</option><option value="bar">Barras</option><option value="candles" disabled>Candles (OHLC real)</option></select></label><button data-zoom="in" aria-label="Aproximar gráfico">+</button><button data-zoom="out" aria-label="Afastar gráfico">−</button><button data-zoom="reset">Restaurar</button><span class="subtle">Arraste para mover · Ctrl + rolagem para zoom</span></div><div class="legend" id="legend"></div><div id="chart" class="chart"></div><div id="series-meta" class="meta"></div></section>`}
function wireChart(){chart=new Chart($('#chart'));$('#legend').insertAdjacentHTML('afterend','<p id="chart-loading" class="subtle" role="status" hidden>Carregando o período selecionado…</p>');$('#chart-type').onchange=e=>{chart.type=e.target.value;chart.draw()}}
function setChart(data,unit){const option=$('#chart-type option[value="candles"]');if(option)option.disabled=!hasOHLC(data);if(chart?.type==='candles'&&!hasOHLC(data)){chart.type='line';$('#chart-type').value='line'}chart?.set(data,unit);$('#legend').innerHTML=data.map((s,i)=>{const last=s.points?.toSorted((a,b)=>a.date.localeCompare(b.date)).at(-1);return `<span><i class="swatch" style="background:${COLORS[i]}"></i>${esc(s.name||asset(s.id)?.name||s.id)}${last?` · Última do período: <strong>${chartValue(last.value,unit)} ${esc(unit)}</strong> · ${esc(dateLabel(last.date))}`:''}</span>`}).join('')}
function controls(items){const groups=[...new Set(items.map(a=>a.region||a.country).filter(Boolean))];return `<div class="toolbar"><label>Filtrar <select id="filter"><option value="">Todos</option>${groups.map(g=>`<option ${filter===g?'selected':''}>${esc(g)}</option>`).join('')}</select></label><label>Buscar <input id="search" type="search" placeholder="Nome do ativo" value="${esc(search)}"></label><label>Ativo <select id="asset-select">${items.filter(matches).map(a=>`<option value="${esc(a.id)}" ${selected===a.id?'selected':''}>${esc(a.name)}${a.country?' · '+esc(a.country):''}</option>`).join('')}</select></label></div>`}
function matches(a){return filterAssets([a],filter,search).length>0}
function table(items){return `<section class="panel"><div class="panel-head"><h2>Universo acompanhado</h2><span class="subtle">${items.length} instrumentos</span></div><div class="table-wrap"><table><thead><tr><th>ATIVO</th><th>PAÍS / GRUPO</th><th>VALOR</th><th>VARIAÇÃO</th><th>REFERÊNCIA</th><th>FONTE / ESTADO</th></tr></thead><tbody id="asset-table">${items.map(a=>`<tr data-row="${esc(a.id)}"><td><button class="table-action" data-select="${esc(a.id)}">${esc(a.name)}</button><div class="meta">${esc(a.instrument||a.reference||a.exchange||'')}</div></td><td>${esc(a.country||a.region||'Global')}</td><td data-value>—</td><td data-change>—</td><td data-date>—</td><td data-state>Aguardando</td></tr>`).join('')}</tbody></table></div></section>`}
function wireControls(){if($('#filter'))$('#filter').onchange=e=>{filter=e.target.value;selected='';render()};if($('#search'))$('#search').onchange=e=>{search=e.target.value;selected='';render()};if($('#asset-select'))$('#asset-select').onchange=e=>{selected=e.target.value;generation++;chart?.reset();requestLoad()}}
function showSources(){content.innerHTML=`<div class="sources">${[
['Banco Central do Brasil','Meta Selic SGS 432. Dados diários; atualização conforme publicação. Sem chave. Não confundir meta com Selic efetiva.','https://dadosabertos.bcb.gov.br/'],
['Frankfurter · BCE','Câmbio de referência diário, provider ECB explícito. Sem chave. Não representa preço de execução nem cotação intradiária.','https://frankfurter.dev/'],
['World Bank · WDI','Sete economias. A beta pública distribui PIB e crescimento do PIB anuais; outras séries ficam em revisão de redistribuição. Lacunas e revisões preservadas. CC BY 4.0 com termos adicionais e possíveis exceções por conjunto.','https://datahelpdesk.worldbank.org/knowledgebase/articles/889392'],
['FRED · Federal Reserve Bank of St. Louis','Requer chave no backend. Faixa alvo Fed: limite superior DFEDTARU; não é federal funds efetiva. Treasuries usam fonte direta Treasury nesta versão. Direitos variam por série.','https://fred.stlouisfed.org/docs/api/fred/'],
['US Treasury','Curva par nominal diária, 2/5/10/30 anos quando publicados. API oficial XML sem chave. Não equivale a rendimento real indexado à inflação nem a preço intradiário.','https://home.treasury.gov/treasury-daily-interest-rate-xml-feed'],
['Banco Central Europeu','Facilidade de depósito DFR. Datas de alteração de vigência; observações não são datas de decisão presumidas. Fonte oficial sem chave.','https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV'],
['Bank of Canada','Target for the overnight rate, série V39079 via Valet. Identidade conferida pelos metadados, sem chave.','https://www.bankofcanada.ca/valet-api-how-to/'],
['CoinGecko','Chave Demo/Pro necessária. Histórico limitado pelo plano configurado; volume e capitalização agregados. Variação de 24h vem do snapshot do provedor; limites e redistribuição dependem do plano.','https://www.coingecko.com/en/api'],
['Calendário · fontes oficiais','Na beta estática, consulte o diretório de agendas oficiais. O backend opcional pode sincronizar BoE/BLS conforme disponibilidade; não há promessa de calendário global nem resultados inventados.','https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates'],
['Índices e commodities','Catálogo completo. Cotações exigem feed licenciado configurado no servidor e validação dos identificadores. Não há scraping nem substituição por ETFs.','https://www.b3.com.br/'],
['Metodologia','Variação: última observação menos a anterior da série selecionada. Base 100 usa primeira data comum exata. Sem interpolação ou preenchimento. Máximo consulta desde o início suportado pelo conector; limites por fonte documentados.','']].map(([name,desc,url])=>`<article class="panel"><p class="eyebrow">DADOS & TRANSPARÊNCIA</p><h2>${name}</h2><p>${desc}</p>${url?`<a class="source-link" href="${url}" target="_blank" rel="noopener">Documentação oficial ↗</a>`:''}</article>`).join('')}</div><div class="notice">Publicação pública depende de revisão de licença e autorização de redistribuição por provedor. Cache de leitura não garante que o dado de referência seja recente. Não constitui recomendação de investimento.</div>`}
function render(){
  generation++;const module=MODULES.find(m=>m[0]===section)||MODULES[0];section=module[0];$('#title').textContent=module[2];$('#description').textContent=module[3];$('#nav').innerHTML=MODULES.map(([id,icon,name])=>`<a href="#${id}" class="${section===id?'active':''}" ${section===id?'aria-current="page"':''}><span>${icon}</span>${name}</a>`).join('');
  chart?.dispose();curveChart?.dispose();chart=null;curveChart=null;$('#refresh').disabled=false;$('#refresh').hidden=false;$('#notice').classList.remove('error');$('#notice').textContent=DEFAULT_NOTICE;
  if(section==='sources'){showSources();content.insertAdjacentHTML('afterbegin','<div class="notice">Beta híbrida: JSONs publicados e câmbio de referência direto opcional, sem chave no navegador. Coleta e observação têm datas distintas; nenhuma modalidade promete tempo real. <a href="./DATA-LICENSES.md" target="_blank" rel="noopener">Licenças e atribuições ↗</a></div>');content.insertAdjacentHTML('beforeend','<section class="panel"><details><summary>Disponibilidade dos instrumentos e motivos</summary><div id="availability-content"><p class="subtle">Consultando disponibilidade das fontes…</p></div></details></section>');requestLoad();return}
  if(section==='overview'){
    selected=selectionFor(overview.map(asset).filter(matches),selected||'usdbrl');content.innerHTML=`<div class="grid" id="cards" hidden></div>${controls(overview.map(asset))}${chartPanel()}`;wireChart();wireControls();
    if(futureCoverage)$('#cards').insertAdjacentHTML('afterend',`<details class="panel"><summary>Cobertura futura · ${futureCoverage} instrumentos ainda indisponíveis</summary><p>Índices, commodities e outras séries continuam nas categorias e em Fontes e Metodologia, com seus motivos. A página inicial prioriza históricos reais disponíveis.</p><a href="#sources">Consultar fontes e cobertura ↗</a></details>`);
  }else if(section==='compare'){
    const onlyRates=selectedCompare.length>0&&selectedCompare.every(id=>['rates','yields'].includes(asset(id)?.category));
    if(!onlyRates&&['pp','bps'].includes(mode))mode='base100';
    content.innerHTML=`<div class="panel"><h2>Construa sua comparação</h2><p class="subtle">Apenas datas presentes em todas as séries disponíveis; séries ausentes são indicadas.</p><div class="toolbar"><label>Adicionar ativo <select id="compare-add"><option value="">Selecione…</option>${catalog.map(a=>`<option value="${esc(a.id)}">${esc(a.name)} · ${esc(a.country||a.category)}</option>`).join('')}</select></label><label>Escala <select id="compare-mode">${[['base100','Base 100'],['percent','Retorno acumulado (%)'],['pp','Variação em p.p. (taxas)'],['bps','Variação em pontos-base (taxas)']].map(([v,n])=>`<option value="${v}" ${mode===v?'selected':''}>${n}</option>`).join('')}</select></label></div><div class="tag-list">${selectedCompare.map(id=>`<button data-remove="${esc(id)}">${esc(asset(id).name)} ×</button>`).join('')}</div><p id="compare-message" class="subtle"></p></div>${chartPanel()}`;
    $('#compare-mode').closest('label').insertAdjacentHTML('afterend',comparisonHelpMarkup());
    for(const value of ['pp','bps'])$('#compare-mode option[value="'+value+'"]').disabled=!onlyRates;
    wireChart();$('#compare-add').onchange=e=>{if(!e.target.value)return;if(selectedCompare.length>=5){$('#compare-message').textContent='Limite de cinco séries.';return}if(!selectedCompare.includes(e.target.value))selectedCompare.push(e.target.value);render()};$('#compare-mode').onchange=e=>{mode=e.target.value;generation++;requestLoad()};
  }else if(section==='calendar'){
    content.innerHTML=`<div class="toolbar"><label>País <select id="calendar-country"><option value="">Todos</option>${[...new Set(catalog.map(a=>a.country).filter(Boolean))].map(c=>`<option>${esc(c)}</option>`).join('')}</select></label><label>Estado <select id="calendar-status"><option value="">Todos</option><option value="confirmado">Confirmado</option><option value="cancelado">Cancelado</option><option value="estimado">Estimado</option></select></label><label>Fuso <select id="timezone"><option value="America/Sao_Paulo">Brasília</option><option value="UTC">UTC</option><option value="America/New_York">Nova York</option></select></label></div><div id="calendar-events"></div><div id="official-directory" class="sources"></div>`;
    ['#calendar-country','#calendar-status','#timezone'].forEach(id=>$(id).onchange=()=>{generation++;requestLoad()});
  }else{
    let items=catalog.filter(a=>a.category===(section==='rates'?sub:section));
    selected=selectionFor(items.filter(matches),selected);
    let extra='';
    if(section==='rates')extra=`<div class="toolbar"><button data-sub="rates" class="${sub==='rates'?'active':''}">Política monetária</button><button data-sub="yields" class="${sub==='yields'?'active':''}">Rendimentos soberanos</button></div>`;
    content.innerHTML=extra+controls(items)+chartPanel()+(section==='rates'?`<section class="panel"><h2>${sub==='rates'?'Comparação de taxas vigentes':'Curva de juros soberanos'}</h2><div class="toolbar">${sub==='rates'?`<label>Ordenar <select id="rate-sort"><option value="desc">Maior taxa</option><option value="asc" ${rateSort==='asc'?'selected':''}>Menor taxa</option></select></label><div class="tag-list">${items.map(a=>`<label><input type="checkbox" data-country="${esc(a.id)}" ${!rateCountries.size||rateCountries.has(a.id)?'checked':''}>${esc(a.country)}</label>`).join('')}</div>`:`<label>País <select id="curve-country">${[...new Set(items.map(a=>a.country))].map(c=>`<option ${c===curveCountry?'selected':''}>${esc(c)}</option>`).join('')}</select></label>`}</div><div id="rates-bars"></div><div id="curve" class="chart" ${sub==='rates'?'hidden':''}></div><p id="spread" class="subtle"></p></section>${sub==='rates'?'<section class="panel"><h2>Diferenciais internacionais nominais</h2><div id="differentials"></div><p class="subtle">Instrumentos diferentes: comparação nominal, sem equivalência econômica implícita. Datas devem coincidir.</p></section>':''}`:'')+table(items.filter(matches));wireChart();wireControls();
    if($('#rate-sort'))$('#rate-sort').onchange=e=>{rateSort=e.target.value;drawRates()};if($('#curve-country'))$('#curve-country').onchange=e=>{curveCountry=e.target.value;drawRates()};
  }
  if(!selected&&chart&&section!=='compare'){setChart([],'');$('#series-meta').textContent='Nenhum ativo corresponde aos filtros.'}
  showUnavailable(apiConfigured?'Consultando o serviço de dados…':SERVICE_MESSAGE);
  requestLoad();
}
function fillTable(data){for(const row of document.querySelectorAll('[data-row]')){const r=data.find(s=>s.id===row.dataset.row);if(!r)continue;const a=asset(r.id);row.querySelector('[data-value]').textContent=chartValue(r.latest?.value,r.unit||a.unit)+' '+(r.unit||a.unit);row.querySelector('[data-change]').textContent=variation(a,r,fmt);row.querySelector('[data-date]').textContent=dateLabel(r.latest?.date);row.querySelector('[data-state]').innerHTML=esc(r.source||r.message||'')+'<br>'+status(r)+'<div class="meta">Coleta: '+esc(dateLabel(r.synced_at))+'</div>'}}
function drawRates(){
  if(section!=='rates')return;
  if(sub==='rates'){
    const values=rows.filter(r=>r.latest&&(!rateCountries.size||rateCountries.has(r.id))).sort((a,b)=>(rateSort==='desc'?-1:1)*(a.latest.value-b.latest.value));const max=Math.max(1,...values.map(s=>Math.abs(s.latest.value)));
    $('#rates-bars').innerHTML=values.length?values.map(s=>`<div class="bar-row"><span>${esc(asset(s.id).country)}</span><div class="bar-track"><div class="bar-fill ${s.latest.value<0?'negative-bar':''}" style="width:${Math.abs(s.latest.value)/max*100}%"></div></div><span>${fmt(s.latest.value)}%</span></div><p class="meta">${esc(asset(s.id).instrument)} · ${esc(dateLabel(s.latest.date))} · ${status(s)}</p>`).join(''):'<p class="subtle">Taxas indisponíveis: verifique as fontes e credenciais.</p>';
    $('#differentials').innerHTML=[['selic','fed'],['fed','boj'],['ecb','boe'],['fed','pboc']].map(([a,b])=>{const sa=rows.find(s=>s.id===a),sb=rows.find(s=>s.id===b);const dates=sa?.latest?.date===sb?.latest?.date;return `<p class="subtle">${esc(asset(a).country)} − ${esc(asset(b).country)}: <strong>${sa?.latest&&sb?.latest&&dates?fmt(sa.latest.value-sb.latest.value)+' p.p.':'Indisponível em data comum'}</strong><br>${esc(asset(a).instrument)} / ${esc(asset(b).instrument)}</p>`}).join('');
  }else{
    const model=curveModel(rows,catalog,curveCountry);if(!curveChart)curveChart=new Chart($('#curve'));
    curveChart.set(model.points.length?[{id:'curve',name:curveCountry,points:model.points}]:[],'%');
    $('#spread').textContent=model.spread!=null?`Spread 10Y–2Y: ${fmt(model.spread)} p.p. (${fmt(model.spread*100)} pb) · ${dateLabel(model.date)}. Curva apenas com vencimentos publicados na mesma data.`:'Spread indisponível: exige 2Y e 10Y comparáveis na mesma data.';
  }
}
function requestLoad(){if(poller)poller.refresh();else load()}
const DEFAULT_NOTICE='Dados de referência, com frequência e fonte identificadas. Valores indisponíveis nunca são estimados.';
function renderCalendar(data){
      const c=$('#calendar-country').value,st=$('#calendar-status').value,tz=$('#timezone').value;
      const events=futureEvents(data.events,{country:c,status:st,zone:tz});
      $('#calendar-events').innerHTML=`<div class="notice">${esc(data.limitation)} · Última sincronização: ${data.synced_at?dateLabel(new Date(data.synced_at*1000).toISOString()):'—'}${data.partial?' · Atualização parcial':data.stale?' · Cache atrasado':''}${data.error?' · '+esc(data.error):''}</div><div class="panel table-wrap"><table><thead><tr><th>DATA / HORÁRIO</th><th>PAÍS</th><th>EVENTO</th><th>ESTADO</th><th>FONTE</th></tr></thead><tbody>${events.map(e=>`<tr><td>${esc(e.date.length===10?dateLabel(e.date)+' (sem horário)':new Date(e.date).toLocaleString('pt-BR',{timeZone:tz}))}</td><td>${esc(e.country)}</td><td>${esc(e.name)}</td><td>${esc(e.status)}${e.source_stale?' · fonte atrasada':''}</td><td><a href="${safeURL(e.source_url)}" target="_blank" rel="noopener">${esc(e.source)}</a></td></tr>`).join('')||'<tr><td colspan="5">Nenhum evento futuro sincronizado para este filtro. Consulte as agendas oficiais.</td></tr>'}</tbody></table></div>`;
      $('#official-directory').innerHTML=data.directory.filter(e=>!c||e.country===c).map(e=>`<article class="panel"><p class="eyebrow">${esc(e.country)}</p><h3>${esc(e.name)}</h3><a class="source-link" href="${safeURL(e.url)}" target="_blank" rel="noopener">Consultar agenda oficial ↗</a></article>`).join('');
}
function showUnavailable(message=SERVICE_MESSAGE){
  if(section==='sources')return;
  if(section==='calendar'){renderCalendar(unavailableCalendar(DIRECTORY,message));return}
  const items=section==='overview'?overview.map(asset):section==='compare'?selectedCompare.map(asset):catalog.filter(a=>a.category===(section==='rates'?sub:section));
  rows=items.map(a=>unavailableSeries(a,message));
  if(section==='overview')$('#cards').innerHTML=items.map(a=>card(a,rows.find(s=>s.id===a.id))).join('');
  else if(section!=='compare')fillTable(rows);
  if(chart){const selectedRows=section==='compare'?rows:rows.filter(s=>s.id===selected);setChart(selectedRows.map(s=>({...s,name:asset(s.id).name})),section==='compare'?{base100:'base 100',percent:'%',pp:'p.p.',bps:'pb'}[mode]:asset(selected)?.unit||'');$('#series-meta').textContent=message;}
  if(selected&&section!=='compare'){$('#chart-title').textContent=asset(selected)?.name||'Histórico';$('#chart-caption').textContent=asset(selected)?.instrument||asset(selected)?.reference||'Dados de referência'}
  if(section==='rates')drawRates();
}
async function load(){
  const g=generation;$('#refresh').disabled=true;content.setAttribute('aria-busy','true');if($('#chart-loading'))$('#chart-loading').hidden=false;let detailSeries=null;
  try{
    if(section==='overview'){
      const data=await api('catalog');if(g!==generation)return;
      if(data.static){futureCoverage=data.unavailable||0;if(data.overview.join(',')!==overview.join(',')){overview=data.overview;selected=overview.includes(selected)?selected:overview[0]||'';render();return}}
    }
    if(section==='sources'){
      const target=$('#availability-content');
      if(!apiConfigured){target.textContent=SERVICE_MESSAGE;return}
      try{const data=await api('availability');if(g!==generation)return;
        const labels={publication_review:'Revisão de redistribuição',credential_required:'Chave necessária',license_required:'Licença necessária',awaiting_sync:'Aguardando coleta',no_observations:'Janela sem observações',source_failure:'Fonte indisponível',quota_limited:'Limite do provedor',reference_stale:'Referência antiga',cached_after_failure:'Cache atrasado',available:'Disponível'};
        target.innerHTML='<div class="table-wrap"><table><thead><tr><th>ATIVO</th><th>ESTADO</th><th>MOTIVO</th><th>FONTE / REFERÊNCIA</th></tr></thead><tbody>'+data.instruments.map(r=>`<tr><td>${esc(r.name)}<div class="meta">${esc(r.country||r.category)}</div></td><td>${esc(labels[r.reason]||r.status)}</td><td>${esc(r.detail)}</td><td>${esc(r.source||r.provider)}<br>${esc(dateLabel(r.latest_reference))}</td></tr>`).join('')+'</tbody></table></div>';
      }catch(e){if(g===generation)target.textContent=e.message;throw e}return;
    }
    if(!apiConfigured){showUnavailable();$('#notice').textContent=SERVICE_MESSAGE;return}
    if(section==='calendar'){
      const data=await api('calendar');if(g!==generation)return;
      renderCalendar(data);return;
    }
    if(section==='compare'){
      if(!selectedCompare.length){setChart([],'');return}
      const result=await api('compare?'+new URLSearchParams({ids:selectedCompare.join(','),period,mode}));if(g!==generation)return;
      setChart(result.comparison.map(s=>({...s,name:asset(s.id).name,source:result.series.find(r=>r.id===s.id)?.source})),{base100:'base 100',percent:'%',pp:'p.p.',bps:'pb'}[mode]);$('#series-meta').textContent=result.alignment+' · '+result.series.map(s=>asset(s.id).name+': '+(stateLabel[s.status]||s.status)).join(' | ');return;
    }
    const items=section==='overview'?overview.map(asset):catalog.filter(a=>a.category===(section==='rates'?sub:section));
    const results=await Promise.allSettled([
      api('snapshot?'+new URLSearchParams({ids:items.map(a=>a.id).join(','),period:section==='macro'?'MAX':'1A'})),
      selected?api('series?'+new URLSearchParams({id:selected,period})):Promise.resolve(null)
    ]);if(g!==generation)return;
    const failures=[];
    try{if(results[0].status==='rejected')throw results[0].reason;rows=unwrapSeries(results[0].value,items)}catch(e){rows=items.map(a=>unavailableSeries(a,e.message));failures.push('Cartões/tabela: '+e.message)}
    if(section==='overview')$('#cards').innerHTML=items.map(a=>card(a,rows.find(r=>r.id===a.id))).join('');else fillTable(rows);
    if(section==='overview')$('#cards').hidden=!rows.some(r=>r.latest);
    if(section==='rates')drawRates();
    if(selected){let selectedData;try{if(results[1].status==='rejected')throw results[1].reason;selectedData=unwrapSeries(results[1].value,[asset(selected)])[0]}catch(e){selectedData=unavailableSeries(asset(selected),e.message);failures.push('Gráfico: '+e.message)}const s=selectedData,a=asset(selected);detailSeries=s;$('#chart-title').textContent=a.name;$('#chart-caption').textContent=a.instrument||a.reference||'Histórico de referência';setChart([{...s,name:a.name}],s.unit||a.unit);$('#series-meta').innerHTML=`${status(s)} ${esc(s.message||'')} · Fonte: ${s.source_url?`<a href="${safeURL(s.source_url)}" target="_blank" rel="noopener">${esc(s.source)}</a>`:'pendente'} · Sincronização: ${esc(dateLabel(s.synced_at))}<br>${esc(a.frequency||s.frequency||'Frequência conforme fonte')} · Última referência: ${esc(dateLabel(s.latest?.date))} · Variação calculada entre últimas observações disponíveis. ${esc(s.publication_note||'')}`}
    if(detailSeries){
      const s=detailSeries;
      if(section==='overview'&&s.latest)$('#cards').hidden=false;
      rows=rows.map(r=>r.id===s.id?s:r);if(section==='overview')$('#cards').innerHTML=overview.map(asset).map(a=>card(a,rows.find(r=>r.id===a.id))).join('');else fillTable(rows);
      const extra=[s.delivery&&(s.delivery==='dynamic_reference'?'Consulta direta · referência diária':'JSON publicado · atualização periódica'),s.unit&&'Unidade: '+s.unit,s.currency&&'Moeda: '+s.currency,s.market&&'Mercado: '+s.market,s.reference&&'Referência: '+s.reference,s.contract&&'Contrato: '+s.contract,s.expiry&&'Vencimento: '+s.expiry,s.volume!=null&&'Volume 24h (USD): '+fmt(s.volume),s.market_cap!=null&&'Capitalização (USD): '+fmt(s.market_cap),s.change_24h!=null&&'Variação 24h CoinGecko: '+fmt(s.change_24h)+'%',s.quote_time&&'Cotação agregada em: '+dateLabel(s.quote_time),s.quote_price!=null&&'Preço agregado (USD): '+fmt(s.quote_price),s.quote_error,s.publication_date&&'Publicação: '+dateLabel(s.publication_date),s.decision_date&&'Decisão: '+dateLabel(s.decision_date)].filter(Boolean);
      if(extra.length)$('#series-meta').insertAdjacentHTML('beforeend','<br>'+extra.map(esc).join(' · '));
      if(asset(selected).category==='rates'){
        const a=asset(selected),meeting=s.next_meeting;
        const upcoming=meeting?.status==='confirmed'&&meeting.date.slice(0,10)>=new Date().toISOString().slice(0,10);
        const decisions=s.decisions||[];
        $('#series-meta').insertAdjacentHTML('beforeend',`<details class="policy-details"><summary>Decisões de política monetária e fontes oficiais</summary><p>${upcoming?`Próxima reunião confirmada: <a href="${safeURL(meeting.source_url)}" target="_blank" rel="noopener">${esc(dateLabel(meeting.date))}</a>`:'Próxima reunião não integrada; consulte a autoridade monetária.'}</p>${decisions.length?`<div class="table-wrap"><table><thead><tr><th>DECISÃO</th><th>TAXA</th><th>ALTERAÇÃO</th><th>FONTE</th></tr></thead><tbody>${decisions.map(r=>`<tr><td>${esc(dateLabel(r.date))}</td><td>${fmt(r.value)}%</td><td>${r.change_bps==null?'—':fmt(r.change_bps)+' pb'}</td><td><a href="${safeURL(r.source_url)}" target="_blank" rel="noopener">Fonte oficial ↗</a></td></tr>`).join('')}</tbody></table></div>`:'<p>Histórico de decisões não integrado. Observações diárias do gráfico não equivalem a datas de decisão.</p>'}${a.source_url?`<a href="${safeURL(a.source_url)}" target="_blank" rel="noopener">Consultar autoridade monetária ↗</a>`:''}</details>`)
      }
    }
    if(g===generation){$('#notice').textContent=failureNotice(failures,DEFAULT_NOTICE);$('#notice').classList.toggle('error',failures.length>0)}
  }catch(e){if(g===generation){showUnavailable(e.message);$('#notice').textContent=e.message;$('#notice').classList.add('error')}}finally{if(g===generation){$('#refresh').disabled=false;content.setAttribute('aria-busy','false');if($('#chart-loading'))$('#chart-loading').hidden=true}}
}
function route(){({section,selected,sub,period}=navigationState(location.hash,catalog,MODULES.map(m=>m[0]),period));filter='';search='';render()}
content.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.period){period=b.dataset.period;chart?.reset();document.querySelectorAll('[data-period]').forEach(x=>x.classList.toggle('active',x.dataset.period===period));generation++;requestLoad()}if(b.dataset.zoom){if(b.dataset.zoom==='reset')chart.reset();else chart.zoom(b.dataset.zoom==='in'?.7:1.4)}if(b.dataset.select){selected=b.dataset.select;$('#asset-select').value=selected;generation++;chart?.reset();requestLoad();$('#chart-title').scrollIntoView({behavior:'smooth',block:'center'})}if(b.dataset.remove){selectedCompare=selectedCompare.filter(id=>id!==b.dataset.remove);render()}if(b.dataset.sub){sub=b.dataset.sub;selected='';filter='';render()}});
content.addEventListener('change',e=>{if(e.target.dataset.country){rateCountries=new Set([...content.querySelectorAll('[data-country]:checked')].map(el=>el.dataset.country));if(!rateCountries.size)rateCountries.add('__none__');drawRates()}});
async function health(){try{$('#health').textContent=healthLabel(await api('health'))}catch(e){$('#health').textContent=healthLabel(null,e,apiConfigured)}}
$('#refresh').onclick=()=>{generation++;requestLoad()};window.addEventListener('hashchange',route);
// A interface usa identidades locais, sem preços, e nunca aguarda uma API para montar os módulos.
poller=new Poller(async()=>{await Promise.allSettled([load(),health()])});
route();

