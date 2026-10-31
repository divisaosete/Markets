import sqlite3,json,time,uuid
from contextlib import contextmanager
from backend.config import DB

class Cache:
    def __init__(self,path=DB):
        self.path=str(path)
        from pathlib import Path
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL, updated REAL NOT NULL); CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, owner TEXT, until REAL, next REAL DEFAULT 0, failures INTEGER DEFAULT 0, error TEXT);')
            db.executescript('CREATE TABLE IF NOT EXISTS provider_budget(host TEXT PRIMARY KEY, next REAL NOT NULL); CREATE TABLE IF NOT EXISTS provider_usage(host TEXT, month TEXT, count INTEGER NOT NULL, PRIMARY KEY(host,month));')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15)
        try:
            yield db
            db.commit()
        finally: db.close()
    def get(self,key):
        with self.connect() as db:
            row=db.execute('SELECT payload,updated FROM cache WHERE key=?',(key,)).fetchone()
            return (json.loads(row[0]),row[1]) if row else None
    @contextmanager
    def read_session(self):
        """One consistent read transaction for bulk diagnostics; no write API."""
        with self.connect() as db:
            db.execute('BEGIN')
            yield ReadSession(db)
    def put(self,key,value):
        with self.connect() as db: db.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)',(key,json.dumps(value,allow_nan=False),time.time()))
    def claim(self,key,lease=900):
        owner=uuid.uuid4().hex
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT OR IGNORE INTO jobs(key) VALUES (?)',(key,))
            cur=db.execute('UPDATE jobs SET owner=?,until=? WHERE key=? AND (until IS NULL OR until<?) AND next<=?',(owner,time.time()+lease,key,time.time(),time.time()))
            return owner if cur.rowcount else None
    def renew(self,key,owner,lease=900):
        with self.connect() as db:
            return bool(db.execute('UPDATE jobs SET until=? WHERE key=? AND owner=? AND until>?',(time.time()+lease,key,owner,time.time())).rowcount)
    def publish(self,key,owner,value,interval):
        """Fence writes: only a live owner can publish and finish atomically."""
        payload=json.dumps(value,allow_nan=False)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT 1 FROM jobs WHERE key=? AND owner=? AND until>?',(key,owner,time.time())).fetchone()
            if not row:return False
            db.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)',(key,payload,time.time()))
            db.execute('UPDATE jobs SET owner=NULL,until=NULL,next=?,failures=0,error=NULL WHERE key=? AND owner=?',(time.time()+interval,key,owner))
            return True
    def job(self,key):
        with self.connect() as db:
            row=db.execute('SELECT next,failures,error,until FROM jobs WHERE key=?',(key,)).fetchone()
            return dict(zip(['next','failures','error','until'],row)) if row else None
    def request_slot(self,host,delay,monthly_limit=0):
        from datetime import datetime,timezone
        month=datetime.now(timezone.utc).strftime('%Y-%m')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT count FROM provider_usage WHERE host=? AND month=?',(host,month)).fetchone()
            if monthly_limit and row and row[0]>=monthly_limit:return None
            row=db.execute('SELECT next FROM provider_budget WHERE host=?',(host,)).fetchone()
            now=time.time();slot=max(now,row[0] if row else now)
            if slot-now>30:return -1
            db.execute('INSERT OR REPLACE INTO provider_budget VALUES (?,?)',(host,slot+delay))
            db.execute('INSERT INTO provider_usage VALUES (?,?,1) ON CONFLICT(host,month) DO UPDATE SET count=count+1',(host,month))
            return max(0,slot-now)
    def defer_provider(self,host,seconds):
        with self.connect() as db:
            db.execute('INSERT INTO provider_budget VALUES (?,?) ON CONFLICT(host) DO UPDATE SET next=max(next,excluded.next)',(host,time.time()+seconds))
    def finish(self,key,owner,interval,error=None,retry_after=0):
        with self.connect() as db:
            row=db.execute('SELECT failures FROM jobs WHERE key=? AND owner=?',(key,owner)).fetchone()
            if not row:return
            failures=row[0]+1 if error else 0
            delay=min(86400,60*2**min(failures,10)) if error else interval
            delay=max(delay,retry_after)
            db.execute('UPDATE jobs SET owner=NULL,until=NULL,next=?,failures=?,error=? WHERE key=? AND owner=?',(time.time()+delay,failures,error,key,owner))
    def diagnostics(self):
        with self.connect() as db:
            return {'entries':db.execute('SELECT count(*) FROM cache').fetchone()[0], 'provider_usage':[dict(zip(['host','month','requests'],r)) for r in db.execute('SELECT host,month,count FROM provider_usage')], 'updates':[{'key':r[0],'updated':r[1]} for r in db.execute('SELECT key,updated FROM cache')], 'jobs':[dict(zip(['key','lease_until','next','failures','error'],r)) for r in db.execute('SELECT key,until,next,failures,error FROM jobs')]}

class ReadSession:
    def __init__(self,db):self.db=db
    @contextmanager
    def connect(self):yield self.db
    def get(self,key):
        row=self.db.execute('SELECT payload,updated FROM cache WHERE key=?',(key,)).fetchone()
        return (json.loads(row[0]),row[1]) if row else None
