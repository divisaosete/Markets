import test from 'node:test';
import assert from 'node:assert/strict';
import {ASSETS} from '../public/catalog.js';
import {validatePublished,createStaticClient,seriesWindow,comparePublished,hybridClient,preferredOverview} from '../public/static-data.js';
import {createDirectFx} from '../public/direct-fx.js';
import {readFileSync} from 'node:fs';
const now=()=>new Date('2026-10-31T12:00:00Z');
test('public bundle contains no unapproved energy observations',async()=>{
 const data=validatePublished(JSON.parse(readFileSync(new URL('../public/data/market-data.json',import.meta.url),'utf8')));
 for(const row of data.series.filter(r=>r.provider==='eia')){
  assert.deepEqual(row.points,[]);assert.equal(row.latest,null);assert.equal(row.reason,'publication_review');
  assert.match(row.message,/Refinitiv/);
 }
 assert.ok(!preferredOverview(data.series).includes('brent'));
});
test('explicit local energy fixtures support windows and comparisons',()=>{
 const energy=['brent','wti'].map((id,i)=>({id,provider:'eia',category:'commodities',source:'Explicit test fixture, not market data',unit:'USD/barril',currency:'USD',points:[{date:'2026-10-29',value:10+i},{date:'2026-10-30',value:11+i}]}));
 assert.equal(seriesWindow(energy[0],'1A',now()).points.length,2);
 assert.equal(comparePublished(energy).length,2);
});
function fixture(){return {schema_version:1,generated_at:now().toISOString(),series:ASSETS.map(a=>({...a,status:'unavailable',reason:'license_required',source:'Explicit unit-test fixture',points:[],latest:null})).map(r=>r.id==='usdbrl'?{...r,status:'ok',reason:'available',points:[{date:'2026-10-29',value:5},{date:'2026-10-30',value:6}],latest:{date:'2026-10-30',value:6}}:r)}}
test('static client works below a repository path without requesting any Python endpoint',async()=>{
 const urls=[],read=createStaticClient({dataURL:'https://example.github.io/markets/data/market-data.json',now,fetch:async url=>(urls.push(url),{ok:true,json:async()=>fixture()})});
 const row=(await read('series?id=usdbrl&period=1M')).series[0];assert.equal(row.latest.value,6);assert.equal(row.unit,'BRL');assert.equal((await read('health')).api,'static');assert.deepEqual(urls,['https://example.github.io/markets/data/market-data.json']);assert.deepEqual((await read('catalog')).overview,['usdbrl']);
});
test('failed JSON refresh retains last valid published history and marks it stale',async()=>{
 let time=now(),calls=0;const read=createStaticClient({now:()=>time,ttl:1,fetch:async()=>{if(calls++)throw Error('offline');return {ok:true,json:async()=>fixture()}}});
 await read('series?id=usdbrl');time=new Date(time.getTime()+100);const result=await read('series?id=usdbrl');assert.equal(result.series[0].latest.value,6);assert.equal(result.series[0].status,'stale');
});
test('annual and daily windows retain original reference precision and empty windows stay empty',()=>{
 const row={...fixture().series.find(r=>r.id==='usdbrl'),category:'macro',points:[{date:'2024',value:1},{date:'2025',value:2}]};assert.deepEqual(seriesWindow(row,'1A',now()).points,[{date:'2025',value:2}]);assert.equal(seriesWindow(row,'1D',now()).points.length,0);
});
test('base100 aligns real common observations without interpolation',()=>{
 const series=[{id:'a',points:[{date:'2025',value:2},{date:'2026',value:3}]},{id:'b',points:[{date:'2025',value:4},{date:'2026',value:8}]}];assert.deepEqual(comparePublished(series).map(s=>s.points.map(p=>p.value)),[[100,150],[100,200]]);
 assert.deepEqual(comparePublished([{id:'x',points:[]}]),[]);
});
test('public JSON rejects duplicate IDs, null observations and invalid schema',()=>{
 const data=fixture();assert.equal(validatePublished(data),data);const duplicate=structuredClone(data);duplicate.series[1].id=duplicate.series[0].id;assert.throws(()=>validatePublished(duplicate));const bad=fixture();bad.series.find(r=>r.id==='usdbrl').points[0].value=null;assert.throws(()=>validatePublished(bad));assert.throws(()=>validatePublished({schema_version:2,series:[]}));
});
test('either modality can fail while the other keeps a valid series',async()=>{
 const fallback=async()=>({series:[{id:'usdbrl',points:[{date:'2026-10-30',value:6}]}]});assert.equal((await hybridClient(async()=>{throw Error('API down')},fallback)('series?id=usdbrl')).series[0].points.length,1);
 const read=hybridClient(async()=>({series:[{id:'usdbrl',points:[]}]}),fallback);assert.equal((await read('series?id=usdbrl')).series[0].points[0].value,6);
 assert.equal(await hybridClient(async()=>42,async()=>{throw Error('static down')})('health'),42);
});
test('direct FX has a fixed HTTPS host, no credentials, caches requests and validates pair identity',async()=>{
 let calls=0;const asset=ASSETS.find(a=>a.id==='usdbrl');const read=createDirectFx({now,fetch:async(url,options)=>{calls++;assert.equal(new URL(url).host,'api.frankfurter.dev');assert.equal(options.credentials,'omit');assert.ok(!url.includes('key'));return {ok:true,json:async()=>[{date:'2026-10-30',base:'USD',quote:'BRL',rate:6}]}}});assert.equal((await read(asset,'2026-10-01')).latest.value,6);await read(asset,'2026-10-01');assert.equal(calls,1);
 for(const invalid of [[{date:'2026-10-30',base:'EUR',quote:'BRL',rate:6}],[{date:'2026-02-31',base:'USD',quote:'BRL',rate:6}],[{date:'2026-10-30',base:'USD',quote:'BRL',rate:6},{date:'2026-10-30',base:'USD',quote:'BRL',rate:7}]]){
 const bad=createDirectFx({now,fetch:async()=>({ok:true,json:async()=>invalid})});await assert.rejects(bad(asset,'2026-10-01'));
 }
});
test('initial static history does not wait for a blocked dynamic connection',async()=>{
 const read=createStaticClient({now,dynamicFx:true,fetch:async url=>url.includes('frankfurter')?new Promise(()=>{}):{ok:true,json:async()=>fixture()}});const result=await read('series?id=usdbrl&period=1A');assert.equal(result.series[0].latest.value,6);
});
test('overview prioritizes available histories instead of empty licensed cards',()=>{const data=fixture();assert.deepEqual(preferredOverview(data.series),['usdbrl']);assert.ok(!preferredOverview(data.series).includes('ibov'))});

test('direct modality can recover FX on first visit even when the published JSON is down',async()=>{
 const read=createStaticClient({now,dynamicFx:true,fetch:async url=>url.includes('frankfurter')?{ok:true,json:async()=>[{date:'2026-10-30',base:'USD',quote:'BRL',rate:6}]}:Promise.reject(Error('static down'))});
 assert.deepEqual((await read('catalog')).overview,['usdbrl']);const row=(await read('series?id=usdbrl&period=1A')).series[0];assert.equal(row.latest.value,6);assert.equal(row.delivery,'dynamic_reference');assert.equal(row.status,'ok');
});
test('when both modalities fail no quote is fabricated',async()=>{
 const read=createStaticClient({now,dynamicFx:true,fetch:async()=>{throw Error('offline')}});const row=(await read('series?id=usdbrl')).series[0];assert.equal(row.latest,null);assert.equal(row.points.length,0);assert.equal(row.status,'unavailable');
});
