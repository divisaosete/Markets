import {fmt,dateLabel,escape} from './data.js';
export const COLORS=['#53d4ee','#52d6a1','#e7bc76','#b39cf5','#f17f91'];
const NS='http://www.w3.org/2000/svg';
const axisLabel=d=>/^\d{4}-/.test(d)?dateLabel(d).split(' ')[0]:d;
const referenceLabel=d=>/^\d+ anos$/.test(d)?d:dateLabel(d);
export function chartValue(value,unit='',axis=false){
  if(value==null||!Number.isFinite(value))return '—';
  if(axis&&Math.abs(value)>=1e6)return new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(value);
  return fmt(value,Math.abs(value)>0&&Math.abs(value)<1?6:['BRL','USD','EUR','GBP','CHF','CAD','CNY','MXN','AUD'].includes(unit)?4:2);
}
export function xRatio(d,dates){
  if(dates.length<2)return .5;
  if(dates.every(v=>/^\d+ anos$/.test(v))){const first=parseInt(dates[0]),last=parseInt(dates.at(-1));return last>first?(parseInt(d)-first)/(last-first):.5}
  const first=Date.parse(dates[0]),last=Date.parse(dates.at(-1)),value=Date.parse(d);
  return Number.isFinite(first)&&Number.isFinite(last)&&Number.isFinite(value)&&last>first?(value-first)/(last-first):dates.indexOf(d)/(dates.length-1);
}
export function nearestDate(ratio,dates){return dates.reduce((best,d)=>Math.abs(xRatio(d,dates)-ratio)<Math.abs(xRatio(best,dates)-ratio)?d:best,dates[0])}
export function hasOHLC(series){return series.length===1&&series[0].points?.length>0&&series[0].points.every(p=>['open','high','low','close'].every(k=>Number.isFinite(p[k]))&&p.low<=Math.min(p.open,p.close)&&p.high>=Math.max(p.open,p.close))}
export function chartModel(series,range=[0,1]){
  const all=series.flatMap(s=>s.points).filter(p=>Number.isFinite(p.value));
  if(!all.length)return null;
  const dates=[...new Set(all.map(p=>p.date))].sort();
  const left=Math.floor(range[0]*Math.max(0,dates.length-1)),right=Math.max(left+1,Math.ceil(range[1]*(dates.length-1)));
  const visible=dates.slice(left,right+1);const allowed=new Set(visible);
  const rows=series.map(s=>({...s,points:s.points.filter(p=>allowed.has(p.date)&&Number.isFinite(p.value)).toSorted((a,b)=>a.date.localeCompare(b.date))}));
  const values=rows.flatMap(s=>s.points.map(p=>p.value));if(!values.length)return null;
  let min=Infinity,max=-Infinity;for(const v of values){min=Math.min(min,v);max=Math.max(max,v)}const pad=(max-min)*.1||Math.abs(max)*.02||1;
  return {dates:visible,rows,min:min-pad,max:max+pad};
}
export class Chart{
  constructor(el){this.el=el;this.range=[0,1];this.type='line';this.series=[];this.unit='';this.drag=null;
    el.addEventListener('wheel',e=>{if(!e.ctrlKey)return;e.preventDefault();this.zoom(e.deltaY>0?1.3:.75)}, {passive:false});
    el.addEventListener('pointerdown',e=>{if(e.button!==0)return;this.drag={x:e.clientX,range:[...this.range]};el.setPointerCapture?.(e.pointerId)});
    el.addEventListener('pointerup',()=>this.drag=null);el.addEventListener('pointercancel',()=>this.drag=null);
    el.addEventListener('pointermove',e=>this.move(e));el.addEventListener('pointerleave',()=>{el.querySelector('.tooltip')?.setAttribute('hidden','')});
    if(typeof ResizeObserver!=='undefined'){
      this.observer=new ResizeObserver(entries=>{const width=entries[0]?.contentRect.width;if(width&&width!==this.lastWidth){this.lastWidth=width;this.draw()}});this.observer.observe(el);
    }
  }
  dispose(){this.observer?.disconnect()}
  set(series,unit='',reset=false){this.series=series;this.unit=unit;if(reset)this.range=[0,1];this.draw()}
  zoom(factor){const center=(this.range[0]+this.range[1])/2;const width=Math.min(1,Math.max(.02,(this.range[1]-this.range[0])*factor));const start=Math.max(0,Math.min(1-width,center-width/2));this.range=[start,start+width];this.draw()}
  reset(){this.range=[0,1];this.draw()}
  draw(){
    const m=chartModel(this.series,this.range);this.model=m;
    this.el.replaceChildren();
    if(!m){this.el.innerHTML='<div class="empty-state"><strong>Série ainda indisponível</strong><span>Nenhum ponto foi estimado. Consulte o estado da fonte abaixo.</span></div>';return}
    const W=Math.max(240,Math.min(1000,this.el.clientWidth||900)),H=320,L=64,R=24,T=26,B=42;this.geometry={W,H,L,R,T,B};
    if(this.type==='candles'&&!hasOHLC(m.rows))this.type='line';
    if(this.type==='bar'){m.min=Math.min(0,m.min);m.max=Math.max(0,m.max)}
    if(this.type==='candles'){
      const extremes=m.rows.flatMap(s=>s.points.flatMap(p=>[p.low,p.high]));
      for(const v of extremes){m.min=Math.min(m.min,v);m.max=Math.max(m.max,v)}
    }
    const x=d=>L+xRatio(d,m.dates)*(W-L-R);
    const y=v=>T+(m.max-v)/(m.max-m.min)*(H-T-B);this.y=y;
    const svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',`Gráfico ${this.unit}; ${m.dates.length} datas de referência`);
    const node=(tag,attrs,text)=>{const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!=null)n.textContent=text;svg.append(n);return n};
    for(let i=0;i<5;i++){const v=m.min+(m.max-m.min)*i/4;node('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),stroke:'#203043','stroke-dasharray':'3 5'});node('text',{x:L-8,y:y(v)+4,fill:'#8c9eb2','text-anchor':'end','font-size':10},chartValue(v,this.unit,true))}
    const labels=[...new Set([0,Math.floor((m.dates.length-1)/2),m.dates.length-1])];for(const i of labels)node('text',{x:x(m.dates[i]),y:H-12,fill:'#8c9eb2','text-anchor':'middle','font-size':10},axisLabel(m.dates[i]));
    m.rows.forEach((s,i)=>{const color=COLORS[i%COLORS.length];const d=s.points.map((p,j)=>`${j?'L':'M'}${x(p.date)},${y(p.value)}`).join(' ');
      if(this.type==='candles'){
        const width=Math.max(2,Math.min(14,(W-L-R)/m.dates.length*.6));
        s.points.forEach(p=>{const c=p.close>=p.open?'#52d6a1':'#f17f91';node('line',{x1:x(p.date),x2:x(p.date),y1:y(p.low),y2:y(p.high),stroke:c});node('rect',{x:x(p.date)-width/2,y:Math.min(y(p.open),y(p.close)),width,height:Math.max(1,Math.abs(y(p.open)-y(p.close))),fill:c})});
      }else if(this.type==='bar'){const width=Math.max(2,Math.min(24,(W-L-R)/m.dates.length/m.rows.length-2));s.points.forEach(p=>node('rect',{x:Math.min(W-R-width,Math.max(L,x(p.date)+(i-(m.rows.length-1)/2)*width-width/2)),y:Math.min(y(0),y(p.value)),width,height:Math.max(1,Math.abs(y(0)-y(p.value))),fill:color,opacity:.8}))}
      else {if(this.type==='area'&&s.points.length>1)node('path',{d:d+` L${x(s.points.at(-1).date)},${H-B} L${x(s.points[0].date)},${H-B} Z`,fill:color,opacity:.08});if(s.points.length>1)node('path',{d,fill:'none',stroke:color,'stroke-width':2,'stroke-linejoin':'round'})}
      const last=s.points.at(-1);
      if(last){const marker=node('circle',{cx:x(last.date),cy:y(last.value),r:4,fill:color,'data-series-id':s.id||'','data-date':last.date,'data-value':last.value,'data-unit':this.unit,'data-source':s.source||'Fonte não informada'});const title=document.createElementNS(NS,'title');title.textContent=`${s.name||s.id}: ${chartValue(last.value,this.unit)} ${this.unit} · ${referenceLabel(last.date)} · ${s.source||'Fonte não informada'}`;marker.append(title)}
    });
    node('text',{x:L,y:14,fill:'#8c9eb2','font-size':10},this.unit);
    this.el.append(svg);const tip=document.createElement('div');tip.className='tooltip';tip.hidden=true;this.el.append(tip);
  }
  move(e){
    if(this.drag){const w=this.range[1]-this.range[0];const shift=(this.drag.x-e.clientX)/this.el.clientWidth*w;const start=Math.max(0,Math.min(1-w,this.drag.range[0]+shift));this.range=[start,start+w];this.draw();return}
    const m=this.model;if(!m)return;const rect=this.el.getBoundingClientRect(),g=this.geometry;const ratio=Math.max(0,Math.min(1,((e.clientX-rect.left)/rect.width*g.W-g.L)/(g.W-g.L-g.R)));const d=nearestDate(ratio,m.dates);
    const tip=this.el.querySelector('.tooltip');if(!tip)return;tip.innerHTML=`<strong>${escape(referenceLabel(d))}</strong>`+m.rows.map((s,i)=>{const p=s.points.find(p=>p.date===d);return `<div>${escape(s.name||s.id)}: ${chartValue(p?.value,this.unit)} ${escape(this.unit)}<br>${escape(s.source||'Fonte não informada')}${this.type==='candles'&&p?`<br>O ${fmt(p.open)} · H ${fmt(p.high)} · L ${fmt(p.low)} · C ${fmt(p.close)}`:''}</div>`}).join('');tip.hidden=false;tip.style.left=Math.min(Math.max(0,e.clientX-rect.left+12),Math.max(0,rect.width-240))+'px';tip.style.top='18px';
  }
}
