import {ASSETS,OVERVIEW,DIRECTORY} from './catalog.js';
import {createDirectFx} from './direct-fx.js';
const META=new Map(ASSETS.map(a=>[a.id,a]));
const DAYS={'1D':1,'5D':5,'1M':30,'3M':90,'6M':180,'1A':365,'3A':1095,'5A':1825,'10A':3650};
export function validatePublished(data){
  if(data?.schema_version!==1||!Array.isArray(data.series)||data.series.length!==ASSETS.length)throw Error('Pacote de dados inválido.');
  const seen=new Set();for(const r of data.series){
    if(!META.has(r.id)||seen.has(r.id)||!Array.isArray(r.points)||r.points.length>100000)throw Error('Série pública inválida.');seen.add(r.id);
    let previous='';for(const p of r.points){if(typeof p.date!=='string'||!/^\d{4}(?:-\d{2}(?:-\d{2})?)?$/.test(p.date)||!Number.isFinite(p.value)||p.date<=previous||!Number.isFinite(Date.parse(p.date))||p.date.length===10&&new Date(p.date+'T00:00:00Z').toISOString().slice(0,10)!==p.date)throw Error('Observação pública inválida.');previous=p.date}
  }return data;
}
export function seriesWindow(row,period='1A',now=new Date(),failed=false){
  if(period!=='MAX'&&!(period in DAYS))throw Error('Período inválido.');
  const start=period==='MAX'?'1900-01-01':new Date(now.getTime()-DAYS[period]*86400000).toISOString().slice(0,10),end=now.toISOString().slice(0,10);
  const points=row.points.filter(p=>p.date.length===4?+p.date>=+start.slice(0,4)&&+p.date<=+end.slice(0,4):p.date>=start&&p.date<=end);
  const result={...row,points,latest:points.at(-1)||null};delete result.change;delete result.change_pct;delete result.change_bps;delete result.change_reference;
  if(points.length){
    const date=points.at(-1).date,ref=new Date(date.length===4?date+'-12-31':date.length===7?date+'-28':date);
    const age=Math.max(0,Math.floor((now-ref)/86400000));const limit=row.max_age_days||(row.category==='macro'?1100:row.provider==='ecb'?36525:7);
    result.reference_age_days=age;result.reference_stale=age>limit;
    if(failed||row.status==='stale'||age>limit){result.status='stale';result.reason=age>limit?'reference_stale':'cached_after_failure';result.message=age>limit?'Referência antiga; consulte a data da observação.':'Últimos dados publicados preservados após falha de atualização.'}
    else {result.status='ok';result.reason='available'}
    if(points.length>1){const previous=points.at(-2).value,change=points.at(-1).value-previous;result.change=change;result.change_pct=previous?change/previous*100:null;result.change_reference=points.at(-2).date;if(['rates','yields'].includes(row.category))result.change_bps=change*100}
  }else if(row.points.length){result.status='empty';result.reason='no_observations';result.message='Sem observações neste período; experimente um período maior, respeitando a frequência da fonte.'}
  return result;
}
export function comparePublished(series,mode='base100',alignment='daily'){
  if(!['base100','percent','pp','bps'].includes(mode)||!['daily','exact'].includes(alignment))throw Error('Comparação inválida.');
  const available=series.filter(s=>s.points.length).map(s=>({...s,points:alignment==='daily'?[...new Map(s.points.map(p=>[p.date.slice(0,10),{...p,date:p.date.slice(0,10)}])).values()]:s.points}));
  if(!available.length)return [];
  let common=new Set(available[0].points.map(p=>p.date));for(const s of available.slice(1))common=new Set(s.points.map(p=>p.date).filter(d=>common.has(d)));
  const dates=[...common].sort();if(!dates.length)return [];
  return available.flatMap(s=>{const values=new Map(s.points.map(p=>[p.date,p.value])),base=values.get(dates[0]);if(base===0&&['base100','percent'].includes(mode))return [];return [{id:s.id,source:s.source,points:dates.map(date=>({date,value:mode==='base100'?values.get(date)/base*100:mode==='percent'?(values.get(date)/base-1)*100:(values.get(date)-base)*(mode==='bps'?100:1)}))}]});
}
export function preferredOverview(rows){
  const rank=['usdbrl','eurbrl','eurusd','selic','boc','ecb','yield-Estados Unidos-10','USA-NY.GDP.MKTP.CD','BRA-NY.GDP.MKTP.CD','gbpusd','usdjpy'];
  return rows.filter(r=>r.points.length).sort((a,b)=>(rank.includes(a.id)?rank.indexOf(a.id):100)-(rank.includes(b.id)?rank.indexOf(b.id):100)).slice(0,12).map(r=>r.id);
}
export function createStaticClient({dataURL=new URL('./data/market-data.json',import.meta.url).href,fetch:request=(...a)=>globalThis.fetch(...a),now=()=>new Date(),ttl=300000,dynamicFx=false}={}){
  let last=null,at=0,pending=null,failed=false;const overlays=new Map(),direct=createDirectFx({fetch:request,now});
  const emptyPackage=()=>({schema_version:1,generated_at:null,note:'Pacote publicado temporariamente indisponível.',series:ASSETS.map(a=>({...a,source:a.provider==='fx'?'Frankfurter · BCE':a.provider,source_url:a.provider==='fx'?'https://frankfurter.dev/':a.source_url,delivery:'static',update_type:a.category==='macro'?'periodic_release':'daily_reference',points:[],latest:null,status:'unavailable',reason:a.provider==='licensed'?'license_required':['fred','coingecko'].includes(a.provider)?'credential_required':'package_unavailable',message:'JSONs publicados não carregaram. Consultas diretas de câmbio podem continuar quando habilitadas.'}))});
  async function dataset(){
    if(last&&now().getTime()-at<ttl)return last;
    if(pending)return pending;
    pending=(async()=>{try{const response=await request(dataURL,{cache:'no-cache',credentials:'omit',signal:AbortSignal.timeout(15000)});if(!response.ok)throw Error('Published data unavailable');last=validatePublished(await response.json());failed=false;at=now().getTime();return last}catch{failed=true;at=now().getTime();if(last)return last;if(dynamicFx){last=emptyPackage();return last}throw Error('Não foi possível carregar os dados publicados. Verifique a conexão e tente novamente.')}finally{pending=null}})();return pending;
  }
  return async function read(path){
    if(!/^[a-z][a-z0-9/-]*(?:\?.*)?$/.test(path)||path.includes('..'))throw Error('Consulta inválida.');
    const [endpoint,query='']=path.split('?'),q=new URLSearchParams(query),data=await dataset();
    const rows=data.series.map(r=>overlays.get(r.id)||r),overview=preferredOverview(rows);
    if(endpoint==='catalog')return {assets:ASSETS,overview:overview.length?overview:failed&&dynamicFx?['usdbrl']:[],static:true,covered:overview.length,unavailable:rows.filter(r=>!r.points.length).length};
    if(endpoint==='health')return {api:'static',generated_at:data.generated_at,package_error:failed,available:rows.filter(r=>r.points.length).length};
    if(endpoint==='calendar')return {events:[],directory:DIRECTORY,limitation:'Calendário automático não incluído na beta estática; consulte as agendas oficiais.',synced_at:null,stale:false};
    if(endpoint==='availability')return {generated_at:data.generated_at,instruments:rows.map(r=>({...r,points:undefined,detail:r.message,latest_reference:r.latest?.date,identifier:r.symbol})),note:data.note};
    if(!['series','snapshot','compare'].includes(endpoint))throw Error('Consulta não suportada na versão estática.');
    const ids=(q.get('ids')||q.get('id')||(overview.length?overview:OVERVIEW).join(',')).split(',');
    if(ids.some(id=>!META.has(id))||new Set(ids).size!==ids.length||ids.length>(endpoint==='compare'?5:60))throw Error('Ativos inválidos.');
    const period=q.get('period')||'1A',mode=q.get('mode')||'base100';
    if(period!=='MAX'&&!(period in DAYS)||endpoint==='series'&&ids.length!==1)throw Error('Consulta de histórico inválida.');
    if(['pp','bps'].includes(mode)&&ids.some(id=>!['rates','yields'].includes(META.get(id).category)))throw Error('Pontos percentuais/base exigem taxas.');
    const selected=await Promise.all(ids.map(async id=>{
      let row=rows.find(r=>r.id===id);if(!row)throw Error('Série pública ausente.');
      const actual=endpoint==='snapshot'&&row.category==='macro'?'MAX':period;
      if(endpoint==='series'&&dynamicFx&&META.get(id).provider==='fx'){
        const start=period==='MAX'?'1999-01-01':new Date(now().getTime()-(DAYS[period]||365)*86400000).toISOString().slice(0,10);
        const published=row;
        // Never hold the first render hostage to another origin. A completed
        // direct update is picked up by the next normal refresh.
        const update=async()=>{const live=await direct(META.get(id),start),points=[...new Map([...published.points,...live.points].map(p=>[p.date,p])).values()].sort((a,b)=>a.date.localeCompare(b.date));const merged={...published,...live,points,latest:points.at(-1)};overlays.set(id,merged);return merged};
        if(!published.points.length&&failed){try{row=await update()}catch{row={...published,message:'Pacote publicado e consulta direta indisponíveis; nenhum valor foi estimado.',dynamic_error:true}}}
        else update().catch(()=>overlays.set(id,{...published,message:'Consulta direta indisponível; histórico publicado preservado.',dynamic_error:true}));
      }
      return seriesWindow(row,actual,now(),failed&&row.delivery!=='dynamic_reference');
    }));
    return {series:selected,comparison:endpoint==='compare'?comparePublished(selected,mode,q.get('alignment')||'daily'):null,period,alignment:'Datas comuns; dados reais, sem interpolação. Atualização periódica, não intradiária.'};
  }
}
export function hybridClient(primary,fallback){return async(path,...args)=>{
  if(path==='catalog')try{return await fallback(path,...args)}catch{}
  if(primary)try{
    const result=await primary(path,...args);
    if(result.series?.some(r=>!r.points?.length))try{
      const backup=await fallback(path,...args),series=result.series.map(r=>r.points?.length?r:backup.series.find(s=>s.id===r.id&&s.points?.length)||r);
      const q=new URLSearchParams(path.split('?')[1]||'');return {...result,series,comparison:path.startsWith('compare?')?comparePublished(series,q.get('mode')||'base100',q.get('alignment')||'daily'):result.comparison};
    }catch{}
    return result;
  }catch{}
  return fallback(path,...args);
}}
