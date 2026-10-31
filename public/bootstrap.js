export async function startApp(importer=()=>import('./app.js'),doc=globalThis.document){
  try{await importer();return true}catch(error){
    const notice=doc?.querySelector('#notice'),health=doc?.querySelector('#health');
    if(notice)notice.textContent='Não foi possível iniciar os controles. Recarregue a página pelo Live Server ou pelo backend. O layout foi preservado.';
    if(health)health.textContent='Controles indisponíveis · layout preservado';
    console.error('New Era Markets: falha na inicialização dos módulos.',error);
    return false;
  }
}
if(globalThis.document)startApp();
