// Only the existing, keyless ECB reference provider; no secret or arbitrary URL.
export function createDirectFx({fetch:request=(...a)=>globalThis.fetch(...a),now=()=>new Date(),ttl=1800000}={}){
  const cache=new Map(),pending=new Map(),failures=new Map();
  return async function read(asset,start){
    if(asset.provider!=='fx')return null;
    const key=asset.id+':'+start,old=cache.get(key);if(old&&now().getTime()-old.at<ttl)return old.row;
    if(now().getTime()<(failures.get(key)||0))throw Error('Direct reference deferred');
    if(pending.has(key))return pending.get(key);
    const job=(async()=>{
      const [base,quote]=asset.code.split('/');const url=new URL('https://api.frankfurter.dev/v2/rates');
      url.search=new URLSearchParams({base,quotes:quote,providers:'ecb',from:start,to:now().toISOString().slice(0,10)});
      const response=await request(url.href,{credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',signal:AbortSignal.timeout(12000)});
      if(!response.ok)throw Error('Direct reference unavailable');const data=await response.json();
      if(!Array.isArray(data)||data.length>100000)throw Error('Invalid direct data');
      const sorted=data.map(r=>{if(r.base!==base||r.quote!==quote||!/^\d{4}-\d{2}-\d{2}$/.test(r.date)||new Date(r.date+'T00:00:00Z').toISOString().slice(0,10)!==r.date||!Number.isFinite(r.rate)||r.rate<=0||r.date>now().toISOString().slice(0,10))throw Error('Invalid reference observation');return {date:r.date,value:r.rate}}).sort((a,b)=>a.date.localeCompare(b.date));
      if(sorted.some((p,i)=>i&&p.date===sorted[i-1].date&&p.value!==sorted[i-1].value))throw Error('Conflicting observations');
      const points=[...new Map(sorted.map(p=>[p.date,p])).values()];
      if(!points.length)throw Error('No direct observations');
      const row={id:asset.id,points,latest:points.at(-1),source:'Frankfurter · BCE',source_url:'https://frankfurter.dev/',unit:quote,currency:quote,frequency:'diária',reference:'Referência diária BCE; não é cotação intradiária',delivery:'dynamic_reference',synced_at:now().toISOString(),status:'ok',reason:'available'};
      cache.set(key,{at:now().getTime(),row});return row;
    })().catch(e=>{failures.set(key,now().getTime()+300000);throw e}).finally(()=>pending.delete(key));pending.set(key,job);return job;
  }
}
