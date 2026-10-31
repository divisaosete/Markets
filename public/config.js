// Sem API configurada, a beta usa os JSONs públicos relativos ao site.
// O build valida PUBLIC_API_BASE opcional como HTTPS, sem tokens na URL.
// A consulta direta de câmbio é sem chave; nunca inserir segredos neste arquivo.
export const config = Object.freeze({apiBase: '', timeoutMs: 15000, staticData: true, dynamicFx: true});
