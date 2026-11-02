export function filterAssets(items,filter='',search=''){
  return items.filter(a=>(!filter||a.region===filter||a.country===filter)&&(!search||a.name.toLocaleLowerCase('pt-BR').includes(search.toLocaleLowerCase('pt-BR'))));
}
export function selectionFor(items,current){return items.some(a=>a.id===current)?current:items[0]?.id||''}
export function navigationState(hash,catalog,sections,period='1A'){
  const [requested,raw]=hash.replace(/^#/,'').split('/');
  const section=sections.includes(requested)?requested:'overview';
  let selected='';try{selected=decodeURIComponent(raw||'')}catch{}
  const target=catalog.find(a=>a.id===selected);
  // The destination determines the panel, independent of the previously open tab.
  const sub=section==='rates'&&target?.category==='yields'?'yields':'rates';
  if(section==='macro'&&['1D','5D','1M','3M','6M','1A'].includes(period))period='5A';
  return {section,selected,sub,period};
}
export function curveModel(rows,catalog,country){
  const meta=new Map(catalog.map(a=>[a.id,a]));
  const available=rows.filter(s=>meta.get(s.id)?.country===country&&s.points?.length).sort((a,b)=>meta.get(a.id).tenor-meta.get(b.id).tenor);
  if(!available.length)return {points:[],date:null,spread:null};
  let common=new Set(available[0].points.map(p=>p.date));
  for(const s of available.slice(1))common=new Set(s.points.map(p=>p.date).filter(d=>common.has(d)));
  const date=[...common].sort().at(-1);if(!date)return {points:[],date:null,spread:null};
  const points=available.map(s=>({date:String(meta.get(s.id).tenor).padStart(2,'0')+' anos',value:s.points.find(p=>p.date===date).value,tenor:meta.get(s.id).tenor}));
  const y2=points.find(p=>p.tenor===2),y10=points.find(p=>p.tenor===10);
  return {points,date,spread:y2&&y10?y10.value-y2.value:null};
}
export function variation(a,s,fmt){
  if(a.category==='crypto')return s.change_24h==null?'24h indisponível':`${fmt(s.change_24h)}% em 24h`;
  if(['rates','yields'].includes(a.category))return s.change_bps==null?'Variação indisponível':`${fmt(s.change_bps)} pb (${fmt(s.change)} p.p.)`;
  return s.change==null?'Variação indisponível':`${s.change>=0?'+':''}${fmt(s.change)} · ${fmt(s.change_pct)}%`;
}
export function futureEvents(events,{country='',status='',zone='America/Sao_Paulo',now=new Date()}={}){
  const today=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
  return events.filter(e=>(!country||country===e.country)&&(!status||status===e.status)&&(e.date.length===10?e.date>=today:new Date(e.date)>=now)).sort((a,b)=>a.date.localeCompare(b.date));
}
