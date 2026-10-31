import unittest,tempfile,os
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
from backend.cache import Cache
from backend.service import Service
from backend.providers import Unavailable
from backend.scheduler import tick

class DataCorrection(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.cache=Cache(Path(self.folder.name)/'test.db')
    def seed(self,id='usdbrl',period='1A'):
        today=date.today();points=[{'date':(today-timedelta(days=i)).isoformat(),'value':5+i/100} for i in [100,20,3,0]]
        self.cache.put(f'series:{id}:{period}',{'id':id,'status':'ok','points':points,'source':'fixture explicit','unit':'BRL','synced_at':today.isoformat()})
    def test_short_window_is_filtered_from_existing_history_without_network(self):
        self.seed();s=Service(self.cache,lambda *_:self.fail('Read must not fetch'))
        data=s.series('usdbrl','1M');self.assertEqual(len(data['points']),3);self.assertEqual(data['cache_source_period'],'1A');self.assertEqual(data['change_reference'],data['points'][-2]['date']);self.assertEqual(data['status'],'ok')
    def test_never_extrapolate_longer_history_or_other_asset(self):
        self.seed();s=Service(self.cache)
        self.assertFalse(s.series('usdbrl','MAX')['points']);self.assertFalse(s.series('eurbrl','1M')['points'])
    def test_empty_short_period_does_not_fabricate_points(self):
        self.cache.put('series:usdbrl:1A',{'status':'ok','points':[{'date':(date.today()-timedelta(days=10)).isoformat(),'value':5}]})
        self.assertEqual(Service(self.cache).series('usdbrl','1D')['status'],'empty')
    def test_annual_macro_history_is_reused_by_reference_year_without_synthetic_dates(self):
        year=date.today().year
        self.cache.put('series:USA-NY.GDP.MKTP.CD:MAX',{'status':'ok','points':[{'date':str(year-3),'value':10},{'date':str(year-1),'value':20}]})
        result=Service(self.cache).series('USA-NY.GDP.MKTP.CD','1A')
        self.assertEqual(result['points'],[{'date':str(year-1),'value':20}]);self.assertEqual(result['latest']['date'],str(year-1));self.assertEqual(result['cache_source_period'],'MAX')
    def test_batch_demand_uses_one_transaction_and_preserves_asset_period(self):
        requests=[('usdbrl','1M'),('eurbrl','5D'),('USA-NY.GDP.MKTP.CD','MAX')]
        with patch.object(self.cache,'connect',wraps=self.cache.connect) as connection:
            Service(self.cache).queue_many(requests);self.assertEqual(connection.call_count,1)
        for id,period in requests:self.assertEqual(self.cache.get(f'demand:{id}:{period}')[0],{'id':id,'period':period})
    def test_legacy_annual_dates_and_empty_window_recover_real_reference_year(self):
        year=date.today().year-1
        self.cache.put('series:USA-NY.GDP.MKTP.CD:MAX',{'status':'ok','points':[{'date':f'{year}-01-01','value':20}]})
        self.cache.put('series:USA-NY.GDP.MKTP.CD:1A',{'status':'empty','points':[]})
        service=Service(self.cache)
        self.assertEqual(service.series('USA-NY.GDP.MKTP.CD','MAX')['latest'],{'date':str(year),'value':20})
        self.assertEqual(service.series('USA-NY.GDP.MKTP.CD','1A')['points'],[{'date':str(year),'value':20}])
    def test_failure_preserves_covering_cache_with_stale_status(self):
        self.seed()
        def fail(*_):raise Unavailable('Fonte em pausa após limite de uso')
        data=Service(self.cache,fail).series('usdbrl','1M',True)
        self.assertEqual(data['status'],'stale');self.assertEqual(len(data['points']),3)
    def test_missing_credentials_and_licenses_are_explicit_on_series(self):
        with patch.dict(os.environ,{},clear=True):
            s=Service(self.cache)
            self.assertEqual(s.series('bitcoin')['reason'],'credential_required');self.assertEqual(s.series('ibov')['reason'],'license_required')
    def test_one_provider_failure_does_not_stop_next_asset(self):
        calls=[]
        def fetch(a,*_):
            calls.append(a['id'])
            if a['id']=='usdbrl':raise Unavailable('upstream unavailable')
            return {'points':[{'date':date.today().isoformat(),'value':2}],'source':'fixture explicit'}
        from backend.catalog import BY_ID
        with patch('backend.scheduler.ASSETS',[BY_ID['usdbrl'],BY_ID['eurbrl']]),patch('backend.scheduler.fetch_calendar',side_effect=Unavailable('offline')):
            tick(self.cache,Service(self.cache,fetch))
        self.assertEqual(calls,['usdbrl','eurbrl']);self.assertEqual(Service(self.cache).series('eurbrl')['status'],'ok')
    def test_bulk_availability_uses_one_read_connection_without_jobs(self):
        from backend.availability import report
        with patch.object(self.cache,'connect',wraps=self.cache.connect) as connection:
            result=report(Service(self.cache));self.assertEqual(connection.call_count,1)
        self.assertEqual(len(result['instruments']),167)
        with self.cache.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0],0)
    def test_worker_renews_lease_while_an_upstream_is_slow(self):
        import time
        def slow(*_):
            deadline=time.monotonic()+2
            while not self.cache.get('worker') and time.monotonic()<deadline:time.sleep(.005)
            self.assertIsNotNone(self.cache.get('worker'));return True
        with patch('backend.scheduler.HEARTBEAT_SECONDS',.01),patch('backend.scheduler._cycle',side_effect=slow),patch.object(self.cache,'renew',wraps=self.cache.renew) as renew:
            self.assertTrue(tick(self.cache,Service(self.cache)));self.assertGreater(renew.call_count,0)
        self.assertIsNone(self.cache.job('_scheduler')['until'])
