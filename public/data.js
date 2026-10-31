import {config} from './config.js';
import {SERVICE_MESSAGE} from './offline.js';
import {createStaticClient,hybridClient} from './static-data.js';
export function resolveApiBase(configured='',meta='',pageURL=globalThis.location?.href||'http://localhost/'){
  const value=configured.trim()||meta.trim();if(!value)return '';
  const url=new URL(value,pageURL);
  if(!['https:','http:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw Error('Configuração da API inválida');
  return url.href.endsWith('/')?url.href:url.href+'/';
}
export function createApiClient({baseURL='',fetch:request=(...args)=>globalThis.fetch(...args),timeoutMs=15000}={}){
  const inflight=new Map(),recent=new Map();
  return async function read(path,signal){
    if(!baseURL){const e=Error(SERVICE_MESSAGE);e.code='OFFLINE';throw e}
    if(!/^[a-z][a-z0-9/-]*(?:\?.*)?$/.test(path)||path.includes('..'))throw Error('Caminho de API inválido');
    const cached=recent.get(path);if(cached&&Date.now()-cached.at<1500)return cached.data;
    if(inflight.has(path))return inflight.get(path);
    const job=(async()=>{
      let r;
      try{r=await request(baseURL+path,{signal:signal||AbortSignal.timeout(timeoutMs),credentials:'omit'})}catch(cause){const e=Error(cause?.name==='TimeoutError'?'A consulta à API excedeu o tempo de espera.':'Não foi possível conectar à API nesta consulta. Verifique o endereço e a conexão.');e.code='CONNECTION';throw e}
      let data;try{data=await r.json()}catch{const e=Error('A API respondeu em formato inválido; era esperado JSON.');e.code='RESPONSE';throw e}
      if(!r.ok){const e=Error(r.status===429?'Limite de consultas à API; aguarde a próxima atualização.':`A API respondeu com erro HTTP ${r.status||'desconhecido'}.`);e.code='HTTP';e.status=r.status;throw e}
      if(recent.size>100)recent.clear();recent.set(path,{data,at:Date.now()});return data;
    })().finally(()=>inflight.delete(path));
    inflight.set(path,job);return job;
  }
}
export function healthLabel(data,error,configured=true){
  if(error)return !configured?'● Interface local · serviço de dados não conectado':error.code==='CONNECTION'?'● Conexão com a API não confirmada nesta consulta':'● API com erro de resposta · consulte o diagnóstico';
  if(data?.api==='static')return `● Dados publicados · ${data.available} indicadores · ${data.package_error?(data.available?'histórico preservado / complemento direto':'pacote indisponível'):'atualização periódica'}`;
  if(data?.api!=='ok')return '● API com resposta de saúde inválida';
  return `● API conectada · Agendador ${data.worker==='active'?'ativo':'sem sinal'} · ${new Date().toLocaleTimeString('pt-BR',{timeZone:'America/Sao_Paulo'})} BRT`;
}
let base='';try{base=resolveApiBase(config.apiBase,globalThis.document?.querySelector('meta[name="markets-api-base"]')?.content||'')}catch{}
export const apiConfigured=Boolean(base)||config.staticData;
export const api=hybridClient(base?createApiClient({baseURL:base,timeoutMs:config.timeoutMs}):null,createStaticClient({dynamicFx:config.dynamicFx}));
export const fmt=(v,max=2)=>v==null?'—':new Intl.NumberFormat('pt-BR',{maximumFractionDigits:max}).format(v);
export const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function dateLabel(value){if(!value)return '—';if(/^\d{4}$/.test(value))return value;if(/^\d{4}-\d{2}$/.test(value))return value.split('-').reverse().join('/');if(/^\d{4}-\d{2}-\d{2}$/.test(value))return value.split('-').reverse().join('/');return new Date(value).toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});}
export function safeURL(value){try{const u=new URL(value);return u.protocol==='https:'?u.href:'#'}catch{return '#'}}
