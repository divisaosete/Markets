"""Run and capture deterministic checks; no APIs or browser are simulated as real."""
import subprocess,sys,json,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
    (ROOT/'docs').mkdir(exist_ok=True)
    commands=[('backend-tests.txt',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v']),('frontend-tests.txt',['node','--test','tests/frontend.test.js','tests/frontend-audit.test.js','tests/frontend-loading.test.js','tests/frontend-integration.test.js','tests/frontend-pages.test.js']),('syntax-app.txt',['node','--check','public/app.js']),('syntax-chart.txt',['node','--check','public/chart.js']),('syntax-python.txt',[sys.executable,'-m','compileall','-q','backend'])]
    results=[];env=os.environ.copy();vendor=ROOT/'.vendor'
    if (ROOT/'.vendor-security').is_dir():env['PYTHONPATH']=str(ROOT/'.vendor-security')+os.pathsep+env.get('PYTHONPATH','')
    if vendor.is_dir():env['PYTHONPATH']=str(vendor)+os.pathsep+env.get('PYTHONPATH','')
    for name,cmd in commands:
        run=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=180)
        (ROOT/'docs'/name).write_text(run.stdout+run.stderr,encoding='utf8');results.append({'check':name,'exit_code':run.returncode});print(name+': '+('PASS' if run.returncode==0 else 'FAIL'),flush=True)
    (ROOT/'docs'/'checks-results.json').write_text(json.dumps({'executed_at':time.time(),'type':'Unitários com fixtures explícitas e verificações estáticas','results':results},ensure_ascii=False,indent=2),encoding='utf8')
    raise SystemExit(0 if all(r['exit_code']==0 for r in results) else 1)
if __name__=='__main__':main()
