export const SERVICE_MESSAGE='Interface sem API configurada. Abra pelo INICIAR-NEW-ERA.cmd para conectar o serviço de dados.';
const SOURCES={bcb:['Banco Central do Brasil · SGS','https://dadosabertos.bcb.gov.br/'],fx:['Frankfurter · BCE','https://frankfurter.dev/'],worldbank:['World Bank · WDI','https://data.worldbank.org/'],fred:['FRED','https://fred.stlouisfed.org/'],coingecko:['CoinGecko','https://www.coingecko.com/'],treasury:['US Treasury','https://home.treasury.gov/treasury-daily-interest-rate-xml-feed'],ecb:['Banco Central Europeu','https://data.ecb.europa.eu/'],boc:['Bank of Canada','https://www.bankofcanada.ca/']};
export function unavailableSeries(a,message=SERVICE_MESSAGE){const source=SOURCES[a.provider];return {id:a.id,status:'unavailable',points:[],latest:null,unit:a.unit,source:source?.[0]||'Provedor licenciado necessário',source_url:source?.[1]||a.source_url,message}}
export function unavailableCalendar(directory,message=SERVICE_MESSAGE){return {events:[],directory,limitation:message+' Consulte também as agendas oficiais abaixo.',synced_at:null,stale:true,error:null}}
export function unwrapSeries(result,assets){
  if(!result||!Array.isArray(result.series))throw Error('Resposta de dados inválida. A interface foi preservada.');
  const allowed=new Set(assets.map(a=>a.id));
  return assets.map(a=>{const row=result.series.find(s=>s&&allowed.has(s.id)&&s.id===a.id);return row&&Array.isArray(row.points)?row:unavailableSeries(a,'Série ausente na resposta da fonte')});
}
