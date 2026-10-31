"""One local command; production keeps API/worker independently supervised."""
import os,sys,time,threading,subprocess,webbrowser,signal
from pathlib import Path
from urllib.request import urlopen
from backend.config import ROOT

def worker_environment(stop_file):
    env=os.environ.copy();env['LOCAL_STOP_FILE']=str(Path(stop_file).resolve());env['LOCAL_PARENT_PID']=str(os.getpid());return env

def main(open_browser=True):
    from backend.app import main as serve
    os.environ['HOST']='127.0.0.1'
    port=int(os.getenv('PORT','8000'));url=f'http://127.0.0.1:{port}/'
    import socket
    try:
        with socket.socket() as probe:probe.bind(('127.0.0.1',port))
    except OSError:raise SystemExit(f'Não foi possível usar a porta {port}. Feche a sessão anterior ou configure outra porta no .env.')
    runtime=ROOT/'var';runtime.mkdir(exist_ok=True)
    stop=runtime/f'local-stop-{os.getpid()}'
    stop.unlink(missing_ok=True)
    log=(runtime/'worker-local.log').open('a',encoding='utf8')
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    worker=subprocess.Popen([sys.executable,str(ROOT/'run.py'),'worker'],cwd=ROOT,env=worker_environment(stop),stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
    ending=threading.Event()
    def browser_when_ready():
        for _ in range(60):
            if ending.is_set():return
            try:
                with urlopen(url+'api/health',timeout=1) as response:
                    if response.status==200:
                        if open_browser:webbrowser.open(url)
                        return
            except Exception:pass
            ending.wait(.5)
    if open_browser:threading.Thread(target=browser_when_ready,daemon=True).start()
    def interrupt(*_):raise KeyboardInterrupt
    previous=signal.signal(signal.SIGTERM,interrupt)
    print('NEW ERA MARKETS — aplicação e atualização automática iniciadas.',flush=True)
    print('Abra: '+url+'  |  Para encerrar: Ctrl+C nesta janela.',flush=True)
    print('Fontes sem credenciais/licença permanecem identificadas; logs em var/worker-local.log.',flush=True)
    try:serve()
    except KeyboardInterrupt:pass
    finally:
        ending.set();stop.touch()
        try:worker.wait(timeout=60)
        except subprocess.TimeoutExpired:
            worker.terminate()
            try:worker.wait(timeout=5)
            except subprocess.TimeoutExpired:worker.kill();worker.wait(timeout=5)
        stop.unlink(missing_ok=True);log.close();signal.signal(signal.SIGTERM,previous)
        print('API e processo de atualização desta sessão encerrados.',flush=True)
