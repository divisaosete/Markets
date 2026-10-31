import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DB=Path(os.getenv('CACHE_PATH',str(ROOT/'var'/'markets.sqlite3')))
if not DB.is_absolute():DB=ROOT/DB
ADMIN_TOKEN=os.getenv('ADMIN_TOKEN','')
ORIGINS={s.strip() for s in os.getenv('ALLOWED_ORIGINS','http://127.0.0.1:8000,http://localhost:8000').split(',') if s.strip()}
FRAME_ANCESTORS=os.getenv('FRAME_ANCESTORS',"'self'")
PERIODS={'1D':1,'5D':5,'1M':30,'3M':90,'6M':180,'1A':365,'3A':1095,'5A':1825,'10A':3650,'MAX':None}
INTERVALS={k:max(60,int(os.getenv('SYNC_'+k.upper(),v))) for k,v in dict(indices=300,commodities=900,fx=3600,crypto=3600,rates=86400,macro=86400,yields=3600,calendar=86400).items()}
# Observation age differs from cache age; thresholds include weekends/publication delays.
MAX_AGE_DAYS={'indices':7,'commodities':7,'fx':7,'crypto':2,'rates':7,'yields':7,'macro':1100}
