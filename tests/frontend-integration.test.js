import test from 'node:test';
import assert from 'node:assert/strict';
import {cardMarkup,statusMarkup,failureNotice} from '../public/presentation.js';
import {ASSETS} from '../public/catalog.js';
import {xRatio} from '../public/chart.js';
test('disconnected card has one compact status and no repeated technical message in its visible body',()=>{const a=ASSETS.find(a=>a.id==='ibov');const text='Serviço de dados indisponível. Inicie o backend para consultar informações atualizadas.';const markup=cardMarkup(a,{status:'unavailable',points:[],message:text});assert.ok(markup.includes('title="'+text+'"'));assert.equal(markup.replace(/<[^>]*>/g,'').includes(text),false);assert.ok(markup.includes('Indisponível'));assert.ok(markup.includes('—'))});
test('tooltip safely escapes upstream text',()=>{assert.ok(!statusMarkup({status:'unavailable',message:'"><script>bad</script>'}).includes('<script>'))});
test('global notice de-duplicates identical component failures',()=>{assert.equal(failureNotice(['Cartões/tabela: backend indisponível','Gráfico: backend indisponível'],'ok'),'backend indisponível');assert.equal(failureNotice([],'ok'),'ok')});
test('Treasury and policy metadata contain explicit official adapters without fake prices',()=>{for(const id of ['ecb','boc','yield-Estados Unidos-2','yield-Estados Unidos-5','yield-Estados Unidos-10','yield-Estados Unidos-30']){const a=ASSETS.find(a=>a.id===id);assert.ok(['ecb','boc','treasury'].includes(a.provider));assert.ok(a.code);assert.equal(a.price,undefined)}});
test('yield curve uses actual tenor spacing rather than equally spaced categories',()=>{assert.equal(xRatio('05 anos',['02 anos','05 anos','10 anos','30 anos']),3/28)});

test('HTTP failures and API health are independent from provider availability',async()=>{
 const {createApiClient,healthLabel}=await import('../public/data.js');
 const api=createApiClient({baseURL:'https://api.invalid/api/',fetch:async()=>({ok:false,status:503,json:async()=>({error:'provider failed'})})});
 await assert.rejects(api('snapshot'),{code:'HTTP',status:503});
 assert.match(healthLabel({api:'ok',worker:'active'}),/API conectada/);
 assert.match(healthLabel(null,{code:'HTTP'}),/erro de resposta/);
 assert.doesNotMatch(healthLabel(null,{code:'HTTP'}),/Inicie|indisponível/);
 assert.match(healthLabel(null,{code:'CONNECTION'}),/não confirmada/);
});
test('specific reasons are visible without incorrectly declaring backend outage',()=>{
 for(const [reason,label] of [['credential_required','Credencial necessária'],['license_required','Provedor licenciado necessário'],['source_failure','Fonte temporariamente indisponível'],['no_observations','Histórico não disponível']])assert.ok(statusMarkup({status:'unavailable',reason}).includes(label));
});

test('comparison help is keyboard accessible and explains every scale with examples',async()=>{
 const {comparisonHelpMarkup}=await import('../public/presentation.js');const help=comparisonHelpMarkup();
 assert.match(help,/<details/);assert.match(help,/<summary aria-label=/);
 for(const explanation of ['Base 100','110','Retorno acumulado','0%','ponto percentual','100 pontos-base','25 pb','datas comuns'])assert.ok(help.includes(explanation),explanation);
});
