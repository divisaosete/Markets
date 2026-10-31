import io,json,os,tempfile,time,unittest
from datetime import date
from unittest.mock import patch
from backend.cache import Cache
from backend.service import Service,compare,start_date
from backend.catalog import ASSETS,BY_ID
from backend.calendar import parse_ics
from backend import app as web

class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.cache=Cache(self.tmp.name+'/test.sqlite3');self.calls=0
        def fetch(a,start,end):
            self.calls+=1
            return {'points':[{'date':'2025-01-01','value':10},{'date':'2025-01-02','value':12}], 'source':'Mock explícito','source_url':'https://example.org','unit':a['unit']}
        self.service=Service(self.cache,fetch)
    def tearDown(self):self.tmp.cleanup()
    def call(self,path,query='',**extra):
        status=[];headers=[]
        def start(s,h):status.append(s);headers.extend(h)
        with patch.object(web,'cache',self.cache),patch.object(web,'service',self.service):
            body=b''.join(web.app({'PATH_INFO':path,'QUERY_STRING':query,'REQUEST_METHOD':'GET','REMOTE_ADDR':'test','wsgi.input':io.BytesIO(),**extra},start))
        return status[0],dict(headers),body
    def test_catalog_counts(self):
        counts={k:sum(a['category']==k for a in ASSETS) for k in ['indices','commodities','fx','crypto','rates','macro','yields']}
        self.assertEqual(counts,dict(indices=27,commodities=27,fx=11,crypto=8,rates=13,macro=49,yields=32));self.assertEqual(len(BY_ID),len(ASSETS))
    def test_real_series_values_and_change(self):
        s=self.service.series('selic','1A',True);self.assertEqual(s['change'],2);self.assertEqual(s['change_pct'],20)
    def test_persistent_cache_restart(self):
        self.cache.put('x',{'value':42});self.assertEqual(Cache(self.cache.path).get('x')[0]['value'],42)
    def test_single_owner_and_release(self):
        owner=self.cache.claim('x');self.assertTrue(owner);self.assertIsNone(self.cache.claim('x'));self.cache.finish('x','wrong',0);self.assertIsNone(self.cache.claim('x'));self.cache.finish('x',owner,0);self.assertTrue(self.cache.claim('x'))
    def test_expired_lease_recovers(self):
        self.cache.claim('x',-1);self.assertTrue(self.cache.claim('x'))
    def test_backoff_survives_restart(self):
        owner=self.cache.claim('x');self.cache.finish('x',owner,0,'failure');self.assertIsNone(Cache(self.cache.path).claim('x'));self.assertEqual(self.cache.diagnostics()['jobs'][0]['failures'],1)
    def test_read_does_not_contact_provider(self):
        self.service.series('selic');self.assertEqual(self.calls,0)
    def test_failure_keeps_cache(self):
        self.service.series('selic','1A',True)
        with self.cache.connect() as db:db.execute('UPDATE jobs SET next=0')
        self.service.fetcher=lambda *_:(_ for _ in ()).throw(TimeoutError('secret'))
        result=self.service.series('selic','1A',True);self.assertEqual(result['status'],'stale');self.assertEqual(len(result['points']),2);self.assertNotIn('secret',result['message'])
    def test_period_not_capped_to_year(self):
        self.assertGreater((date.today()-start_date('5A')).days,1800);self.assertEqual(start_date('MAX',category='fx'),date(1999,1,1))
    def test_compare_common_dates(self):
        s=[{'id':'a','points':[{'date':'a','value':10},{'date':'b','value':20},{'date':'c','value':30}]},{'id':'b','points':[{'date':'b','value':4},{'date':'c','value':8}]}]
        result=compare(s);self.assertEqual(result[0]['points'][0],{'date':'b','value':100});self.assertEqual(result[1]['points'][1]['value'],200)
    def test_compare_zero_missing_and_basis_points(self):
        self.assertEqual(compare([{'id':'x','points':[]}]),[])
        self.assertEqual(compare([{'id':'x','points':[{'date':'a','value':0}]}]),[])
        points=[{'date':'a','value':2},{'date':'b','value':2.25}]
        self.assertEqual(compare([{'id':'x','points':points}],'bps')[0]['points'][-1]['value'],25)
    def test_calendar_utc_cancelled_and_floating(self):
        text='BEGIN:VEVENT\nUID:1\nDTSTART:20261030T140000Z\nSUMMARY:CPI\nSTATUS:CANCELLED\nEND:VEVENT\nBEGIN:VEVENT\nDTSTART:20261031T140000\nEND:VEVENT'
        events=parse_ics(text);self.assertEqual(len(events),1);self.assertEqual(events[0]['status'],'cancelado');self.assertTrue(events[0]['date'].endswith('+00:00'))
    def test_calendar_tz_and_fold(self):
        from zoneinfo import ZoneInfoNotFoundError,ZoneInfo
        try:ZoneInfo('America/New_York')
        except ZoneInfoNotFoundError:self.skipTest('tzdata não instalado')
        events=parse_ics('BEGIN:VEVENT\nDTSTART;TZID=America/New_York:20261106T083000\nSUMMARY:Employ\n ment\nEND:VEVENT');self.assertEqual(events[0]['name'],'Employment')
    def test_api_catalog(self):
        status,_,body=self.call('/api/catalog');self.assertEqual(status,'200 OK');self.assertEqual(len(json.loads(body)['assets']),len(ASSETS))
    def test_api_reject_unknown_period(self):self.assertTrue(self.call('/api/series','id=selic&period=no')[0].startswith('400'))
    def test_api_reject_unknown_asset(self):self.assertTrue(self.call('/api/series','id=malicious')[0].startswith('400'))
    def test_api_compare_limits_and_units(self):
        self.assertTrue(self.call('/api/compare','ids=selic,fed,ecb,boe,boj,pboc')[0].startswith('400'));self.assertTrue(self.call('/api/compare','ids=bitcoin&mode=pp')[0].startswith('400'))
    def test_api_admin_protected(self):
        with patch.object(web,'ADMIN_TOKEN','test-token'):
            self.assertTrue(self.call('/api/admin/diagnostics')[0].startswith('401'));self.assertTrue(self.call('/api/admin/diagnostics',HTTP_AUTHORIZATION='Bearer test-token')[0].startswith('200'))
    def test_origin_and_method(self):
        self.assertTrue(self.call('/api/catalog',HTTP_ORIGIN='https://evil.invalid')[0].startswith('403'));self.assertTrue(self.call('/api/catalog',REQUEST_METHOD='POST')[0].startswith('405'))
    def test_path_traversal_and_security_headers(self):
        self.assertTrue(self.call('/../backend/config.py')[0].startswith('404'));status,h,b=self.call('/');self.assertIn('frame-ancestors',h['Content-Security-Policy']);self.assertIn(b'New Era Markets',b)
    def test_rate_limit(self):
        ip='dedicated-limit-test'
        for _ in range(120):self.assertFalse(web.limited(ip))
        self.assertTrue(web.limited(ip))
    def test_worker_without_visitors(self):
        from backend.scheduler import tick
        with patch('backend.scheduler.ASSETS',[BY_ID['selic']]),patch('backend.scheduler.fetch_calendar',return_value={'events':[]}):tick(self.cache,self.service)
        self.assertEqual(self.calls,1);self.assertIsNotNone(self.cache.get('worker'));self.assertIsNotNone(self.cache.get('calendar'))
    def test_demand_processed_by_worker(self):
        from backend.scheduler import tick
        self.service.queue('usdbrl','5A')
        with patch('backend.scheduler.ASSETS',[]),patch('backend.scheduler.fetch_calendar',return_value={'events':[]}):tick(self.cache,self.service)
        self.assertIsNotNone(self.cache.get('series:usdbrl:5A'))
    def test_licensed_feed_rejects_proxy(self):
        from backend.providers import fetch,Unavailable
        path=self.tmp.name+'/feed.json'
        with open(path,'w') as f:json.dump({'assets':{'ibov':{'source':'x','source_url':'https://source.org','unit':'pt','reference':'ETF','frequency':'daily','instrument_id':'x','currency':'BRL','market':'x','points':[]}}},f)
        with patch.dict(os.environ,{'LICENSED_FEED_PATH':path,'LICENSED_REDISTRIBUTION_APPROVED':'yes'}):
            with self.assertRaises(Unavailable):fetch(BY_ID['ibov'],date(2025,1,1),date.today())
    def test_failed_status_is_visible_on_subsequent_read(self):
        self.service.fetcher=lambda *_:(_ for _ in ()).throw(TimeoutError())
        self.service.series('selic','1A',True)
        self.assertEqual(self.service.series('selic','1A')['status'],'unavailable')
if __name__=='__main__':unittest.main()
