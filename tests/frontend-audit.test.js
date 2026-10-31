import test from 'node:test';
import assert from 'node:assert/strict';
import {Chart,xRatio,nearestDate,hasOHLC} from '../public/chart.js';
import {filterAssets,selectionFor,curveModel,variation,futureEvents} from '../public/analytics.js';
import {Poller} from '../public/polling.js';
import {createApiClient} from '../public/data.js';
test('regional filter updates graph selection and handles no matches',()=>{const items=[{id:'us',country:'US',region:'Américas',name:'S&P'},{id:'de',country:'DE',region:'Europa',name:'DAX'}];assert.equal(selectionFor(filterAssets(items,'Europa'),'us'),'de');assert.equal(selectionFor(filterAssets(items,'','missing'),'us'),'')});
test('tooltip uses elapsed time with irregular dates',()=>{const dates=['2025-01-01','2025-01-02','2025-12-31'];assert.ok(xRatio(dates[1],dates)<.01);assert.equal(nearestDate(.02,dates),'2025-01-02')});
test('curve and 10Y minus 2Y use latest common observations',()=>{const catalog=[{id:'2',country:'US',tenor:2},{id:'10',country:'US',tenor:10}];const rows=[{id:'2',points:[{date:'2025-01-01',value:4},{date:'2025-01-02',value:4.2}]},{id:'10',points:[{date:'2025-01-01',value:4.5}]}];const m=curveModel(rows,catalog,'US');assert.equal(m.date,'2025-01-01');assert.equal(m.spread,.5);assert.equal(m.points.length,2);assert.equal(curveModel(rows,catalog,'BR').points.length,0)});
test('rates are identified in basis points and crypto in actual 24h',()=>{assert.match(variation({category:'rates'},{change:.25,change_bps:25},String),/25 pb/);assert.equal(variation({category:'crypto'},{change:100},String),'24h indisponível');assert.equal(variation({category:'crypto'},{change_24h:2},String),'2% em 24h')});
test('future calendar respects actual event instant and selected timezone',()=>{const events=[{country:'US',status:'confirmado',date:'2026-10-30T00:00:00Z'},{country:'US',status:'confirmado',date:'2026-10-31T00:00:00Z'}];assert.equal(futureEvents(events,{now:new Date('2026-10-30T12:00:00Z')}).length,1)});
test('polling pauses hidden tabs and resumes without overlapping requests',async()=>{
  const doc={hidden:false,listeners:new Map(),addEventListener(k,f){this.listeners.set(k,f)},removeEventListener(k){this.listeners.delete(k)}};
  let interval,resolve,calls=0;const p=new Poller(async()=>{calls++;if(calls===1)await new Promise(r=>resolve=r)},{document:doc,setInterval:f=>(interval=f,1),clearInterval:()=>{}});
  const first=p.refresh();await p.refresh();assert.equal(calls,1);doc.hidden=true;resolve();await first;interval();assert.equal(calls,1);
  doc.hidden=false;await doc.listeners.get('visibilitychange')();await Promise.resolve();assert.equal(calls,2);p.stop();interval();assert.equal(calls,2)
});
test('concurrent reads for the same series issue one HTTP request',async()=>{
  let calls=0;const api=createApiClient({baseURL:'https://backend.invalid/api/',fetch:async()=>{calls++;return {ok:true,json:async()=>({value:1})}}});
  const [a,b]=await Promise.all([api('audit-dedup'),api('audit-dedup')]);assert.equal(calls,1);assert.deepEqual(a,b)
});

class Element {
  constructor(tag='div'){this.tag=tag;this.children=[];this.attrs={};this.handlers={};this.style={};this.clientWidth=900;this.className='';this._html=''}
  addEventListener(type,fn){(this.handlers[type]??=[]).push(fn)}
  setAttribute(k,v){this.attrs[k]=String(v)}
  getAttribute(k){return this.attrs[k]}
  append(n){this.children.push(n)}
  replaceChildren(){this.children=[]}
  querySelector(selector){return selector==='.tooltip'?this.children.find(n=>n.className==='tooltip'):null}
  getBoundingClientRect(){return {left:0,width:this.clientWidth}}
  set innerHTML(s){this._html=s}
  get innerHTML(){return this._html}
}
function fakeChart(){const el=new Element();const original=globalThis.document;globalThis.document={createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag)};return {el,c:new Chart(el),restore:()=>globalThis.document=original}}
test('chart preserves zoom across refresh and pan changes visible range',()=>{
  const {el,c,restore}=fakeChart();try{const points=Array.from({length:100},(_,i)=>({date:String(i).padStart(3,'0'),value:i}));c.set([{id:'x',points}]);c.zoom(.5);const range=[...c.range];c.set([{id:'x',points}]);assert.deepEqual(c.range,range);el.handlers.pointerdown[0]({button:0,clientX:400});c.move({clientX:500});assert.ok(c.range[0]<range[0]);el.handlers.pointerup[0]();c.reset();assert.deepEqual(c.range,[0,1])}finally{restore()}
});
test('chart tooltip displays exact observed value',()=>{const {el,c,restore}=fakeChart();try{c.set([{id:'USD/BRL',points:[{date:'2025-01-01',value:5},{date:'2025-01-02',value:6},{date:'2025-12-31',value:7}]}],'BRL');c.move({clientX:80});assert.ok(el.querySelector('.tooltip').innerHTML.includes('02/01/2025'));assert.ok(el.querySelector('.tooltip').innerHTML.includes('6 BRL'))}finally{restore()}});
test('candles require genuine consistent OHLC and price-only data stays line',()=>{const {el,c,restore}=fakeChart();try{const series=[{id:'fixture explicit',points:[{date:'2025-01-01',value:10,open:9,high:11,low:8,close:10}]}];assert.ok(hasOHLC(series));c.type='candles';c.set(series);assert.equal(c.type,'candles');assert.ok(el.children[0].children.some(n=>n.tag==='rect'));c.set([{id:'price-only',points:[{date:'2025-01-01',value:10}]}]);assert.equal(c.type,'line')}finally{restore()}});
test('negative and positive bars share a true zero baseline',()=>{const {el,c,restore}=fakeChart();try{c.type='bar';c.set([{id:'x',points:[{date:'2025-01-01',value:-2},{date:'2025-01-02',value:3}]}]);const bars=el.children[0].children.filter(n=>n.tag==='rect');const baseline=c.y(0);assert.equal(Number(bars[0].attrs.y),baseline);assert.ok(Number(bars[1].attrs.y)<baseline);assert.ok(Math.abs(Number(bars[1].attrs.y)+Number(bars[1].attrs.height)-baseline)<1e-8)}finally{restore()}});

test('one real observation renders an exact dated marker and no invented curve',()=>{
 const {el,c,restore}=fakeChart();try{c.set([{id:'single-fixture',name:'Single fixture',source:'Official fixture',points:[{date:'2025-01-02',value:5.4325}]}],'BRL');const svg=el.children[0];assert.equal(svg.children.filter(n=>n.tag==='path').length,0);const marker=svg.children.find(n=>n.tag==='circle');assert.equal(marker.attrs['data-value'],'5.4325');assert.equal(marker.attrs['data-date'],'2025-01-02');assert.equal(marker.attrs['data-source'],'Official fixture');assert.match(marker.children[0].textContent,/5,4325 BRL/)}finally{restore()}
});
test('chart sorts real observations without adding or replacing their values',()=>{
 const {el,c,restore}=fakeChart();try{const points=[{date:'2025-01-03',value:7},{date:'2025-01-01',value:5}];c.set([{id:'unordered-fixture',points}]);assert.deepEqual(c.model.rows[0].points.map(p=>p.date),['2025-01-01','2025-01-03']);assert.equal(c.model.rows[0].points.length,2);assert.equal(points[0].date,'2025-01-03')}finally{restore()}
});
test('tooltip includes exact reference, unit and escaped source; empty refresh clears old curve',()=>{
 const {el,c,restore}=fakeChart();try{c.set([{id:'x',source:'<source>',points:[{date:'2025-01-01',value:.123456}]}],'USD');c.move({clientX:80});const tip=el.querySelector('.tooltip').innerHTML;assert.match(tip,/01\/01\/2025/);assert.match(tip,/0,123456 USD/);assert.ok(tip.includes('&lt;source&gt;'));c.set([]);assert.equal(c.model,null);assert.match(el.innerHTML,/Série ainda indisponível/)}finally{restore()}
});
test('monthly references never shift into the previous month through timezone conversion',async()=>{const {dateLabel}=await import('../public/data.js');assert.equal(dateLabel('2025-01'),'01/2025');assert.equal(dateLabel('2025'),'2025')});
