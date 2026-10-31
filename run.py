"""python run.py api | worker | sync | live-tests"""
import sys
from pathlib import Path
vendor=Path(__file__).resolve().parent/'.vendor'
if vendor.exists():sys.path.insert(0,str(vendor))
if __name__=='__main__':
    from backend.environment import load_env
    load_env(Path(__file__).resolve().parent/'.env')
    command=sys.argv[1] if len(sys.argv)>1 else 'api'
    if command=='api':
        from backend.app import main
        main()
    elif command=='local':
        from backend.local import main
        main(open_browser='--no-browser' not in sys.argv[2:])
    elif command=='worker':
        from backend.scheduler import main
        main()
    elif command=='sync':
        from backend.cache import Cache
        from backend.service import Service
        from backend.scheduler import tick
        cache=Cache();tick(cache,Service(cache))
    elif command in ('live-tests','http-tests'):
        import runpy
        runpy.run_path('tests/live.py' if command=='live-tests' else 'tests/http_smoke.py',run_name='__main__')
    elif command=='health-worker':
        import time
        from backend.cache import Cache
        record=Cache().get('worker')
        raise SystemExit(0 if record and time.time()-record[1]<180 else 1)
    else:raise SystemExit('Use local, api, worker, sync, live-tests ou http-tests')
