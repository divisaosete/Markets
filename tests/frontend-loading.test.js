import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ASSETS,OVERVIEW,DIRECTORY} from '../public/catalog.js';
import {createApiClient,resolveApiBase} from '../public/data.js';
import {SERVICE_MESSAGE,unavailableSeries,unavailableCalendar,unwrapSeries} from '../public/offline.js';
import {startApp} from '../public/bootstrap.js';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
test('HTML is complete and local essential resources resolve from public',()=>{
  const html=readFileSync(resolve(root,'public/index.html'),'utf8');assert.match(html,/<!doctype html>/i);assert.match(html,/<html lang="pt-BR">/);assert.match(html,/charset="utf-8"/);assert.match(html,/name="viewport"/);assert.match(html,/type="module" src="\.\/bootstrap.js"/);assert.match(html,/href="\.\/styles.css"/);
  for(const [,resource] of html.matchAll(/(?:href|src)="(\.\/[^"#]+)"/g))assert.ok(existsSync(resolve(root,'public',resource)),resource);
  for(const id of ['nav','cards','chart','content','health','notice'])assert.ok(html.includes(`id="${id}"`));assert.equal((html.match(/class="card"/g)||[]).length,11)
});
test('all module imports reference existing local files',()=>{
  const files=['bootstrap.js','app.js','chart.js','data.js','offline.js','config.js','catalog.js','analytics.js','polling.js','presentation.js'];
  for(const name of files){const text=readFileSync(resolve(root,'public',name),'utf8');for(const [,path] of text.matchAll(/from\s+['"]([^'"]+)['"]/g)){assert.ok(path.startsWith('./'));assert.ok(existsSync(resolve(root,'public',path)),path)}}
});
test('local catalog contains identities and no invented market observations',()=>{assert.equal(ASSETS.length,167);assert.equal(OVERVIEW.length,11);assert.ok(DIRECTORY.length>=13);for(const a of ASSETS){assert.ok(a.id&&a.name);assert.equal(a.points,undefined);assert.equal(a.price,undefined);assert.equal(a.value,undefined)}});
test('offline client never requests nonexistent static API endpoints',async()=>{let calls=0;const api=createApiClient({fetch:async()=>{calls++}});await assert.rejects(api('snapshot?ids=selic'),{message:SERVICE_MESSAGE,code:'OFFLINE'});assert.equal(calls,0)});
test('server metadata selects same origin and explicit config enables separate backend',()=>{assert.equal(resolveApiBase('','/api/','https://markets.invalid/'),'https://markets.invalid/api/');assert.equal(resolveApiBase('http://127.0.0.1:8000/api','','http://127.0.0.1:5500/public/index.html'),'http://127.0.0.1:8000/api/');assert.equal(resolveApiBase('','','http://127.0.0.1:5500/public/index.html'),'');for(const bad of ['javascript:alert(1)','https://name:secret@api.invalid/','https://api.invalid/?key=secret'])assert.throws(()=>resolveApiBase(bad))});
test('network outage and invalid JSON return clear messages without poisoning retry',async()=>{let calls=0;const api=createApiClient({baseURL:'https://api.invalid/api/',fetch:async()=>{calls++;if(calls===1)throw Error('network');if(calls===2)return {ok:true,json:async()=>{throw Error('html')}};return {ok:true,json:async()=>({series:[]})}}});await assert.rejects(api('snapshot'),{code:'CONNECTION'});await assert.rejects(api('snapshot'),{code:'RESPONSE'});assert.deepEqual(await api('snapshot'),{series:[]});assert.equal(calls,3)});
test('unavailable components have source, no price and a usable official calendar directory',()=>{for(const id of OVERVIEW){const a=ASSETS.find(a=>a.id===id),s=unavailableSeries(a);assert.equal(s.status,'unavailable');assert.equal(s.latest,null);assert.deepEqual(s.points,[]);assert.ok(s.source)}const c=unavailableCalendar(DIRECTORY);assert.deepEqual(c.events,[]);assert.equal(c.directory.length,DIRECTORY.length);assert.ok(c.stale)});
test('partial API response cannot remove catalog components',()=>{const assets=OVERVIEW.map(id=>ASSETS.find(a=>a.id===id));const rows=unwrapSeries({series:[{id:'selic',points:[],status:'empty'}]},assets);assert.equal(rows.length,11);assert.equal(rows.find(s=>s.id==='bitcoin').status,'unavailable');assert.throws(()=>unwrapSeries({error:'broken'},assets))});
test('module startup failure keeps static layout and provides a readable recovery message',async()=>{const nodes={'#notice':{textContent:''},'#health':{textContent:''}};const old=console.error;console.error=()=>{};try{assert.equal(await startApp(async()=>{throw Error('missing module')},{querySelector:s=>nodes[s]}),false);assert.match(nodes['#notice'].textContent,/layout foi preservado/);assert.equal(await startApp(async()=>{},{}),true)}finally{console.error=old}});
