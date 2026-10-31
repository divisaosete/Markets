import os,json,tempfile,unittest,time
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
from backend.cache import Cache
from backend.service import Service
from backend.catalog import BY_ID
from backend.providers import fetch,Unavailable
from backend.validation import normalize_points
from backend.calendar import parse_ics
from backend.environment import load_env
from backend.maintenance import backup
from test_backend import PlatformTests

class AuditData(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.cache=Cache(Path(self.tmp.name)/'data.sqlite3')
    def tearDown(self):self.tmp.cleanup()
    def test_expired_owner_cannot_overwrite_new_result(self):
        a=self.cache.claim('job',-1);b=self.cache.claim('job');self.assertTrue(self.cache.publish('job',b,{'value':2},0));self.assertFalse(self.cache.publish('job',a,{'value':1},0));self.assertEqual(self.cache.get('job')[0]['value'],2)
    def test_worker_global_lease_blocks_duplicate_cycle(self):
        from backend.scheduler import tick
        self.cache.claim('_scheduler',180)
        with patch('backend.scheduler.fetch_calendar') as fetcher:self.assertFalse(tick(self.cache,Service(self.cache)));fetcher.assert_not_called()
    def test_worker_respects_stop_between_jobs(self):
        from backend.scheduler import tick
        calls=[];service=Service(self.cache,lambda *a:calls.append(a))
        with patch('backend.scheduler.fetch_calendar',return_value={'events':[]}):tick(self.cache,service,lambda:False)
        self.assertEqual(calls,[])
    def test_budget_survives_restart_and_caps_calls(self):
        self.assertIsNotNone(self.cache.request_slot('host',2,1));self.assertIsNone(Cache(self.cache.path).request_slot('host',2,1))
    def test_retry_after_defers_without_spending_more_budget(self):
        self.cache.defer_provider('host',3600);self.assertEqual(self.cache.request_slot('host',2,8000),-1);self.assertEqual(self.cache.diagnostics()['provider_usage'],[])
    def test_credentials_cannot_follow_redirect_to_another_host(self):
        from backend.providers import SameHostRedirect
        from urllib.request import Request
        with self.assertRaises(Unavailable):SameHostRedirect().redirect_request(Request('https://api.stlouisfed.org/?api_key=fixture'),None,302,'Found',{},'https://other.invalid/')
    def test_rate_limit_reclaims_expired_addresses_at_capacity(self):
        from collections import defaultdict,deque
        from backend import app as web
        addresses=defaultdict(deque,{str(i):deque([time.monotonic()-61]) for i in range(10000)})
        with patch.object(web,'_requests',addresses):self.assertFalse(web.limited('new-client'));self.assertEqual(len(addresses),1)
    def test_references_older_than_threshold_are_flagged(self):
        s=Service(self.cache,lambda *a:{'points':[{'date':'2001-01-01','value':12}], 'unit':'BRL'})
        result=s.series('usdbrl','1A',True);self.assertTrue(result['reference_stale']);self.assertEqual(result['status'],'stale')
    def test_one_year_crypto_fits_demo_and_snapshot_failure_keeps_history(self):
        today=date.today();timestamp=int(time.time()*1000)
        with patch.dict(os.environ,{'COINGECKO_API_KEY':'test','COINGECKO_HISTORY_DAYS':'365'}),patch('backend.providers._crypto_markets',(0,{})),patch('backend.providers.request',side_effect=[{'prices':[[timestamp,100]]},TimeoutError()] ) as req:
            r=fetch(BY_ID['bitcoin'],today-timedelta(days=365),today);self.assertEqual(len(r['points']),1);self.assertIn('days=365',req.call_args_list[0].args[0]);self.assertIsNotNone(r['quote_error'])
    def test_crypto_max_uses_configured_plan(self):
        seen=[]
        s=Service(self.cache,lambda a,b,e:(seen.append((b,e)) or {'points':[]}))
        with patch.dict(os.environ,{'COINGECKO_HISTORY_DAYS':'365'}):s.series('bitcoin','MAX',True)
        self.assertEqual((seen[0][1]-seen[0][0]).days,365)
    def test_points_reject_conflicts_nonfinite_and_future(self):
        for points in [[{'date':'2020-01-01','value':float('nan')}],[{'date':'2999-01-01','value':1}],[{'date':'2020-01-01','value':1},{'date':'2020-01-01','value':2}]]:
            with self.assertRaises(ValueError):normalize_points(points)
    def test_ohlc_validation_no_synthetic_candles(self):
        p={'date':'2020-01-01','value':10,'open':9,'close':10,'high':11,'low':8};self.assertEqual(normalize_points([p])[0]['high'],11)
        with self.assertRaises(ValueError):normalize_points([{**p,'high':7}])
        with self.assertRaises(ValueError):normalize_points([{'date':'2020-01-01','value':10,'open':9}])
    def test_equivalent_timestamps_normalized_without_duplicate(self):
        r=normalize_points([{'date':'2020-01-01T00:00:00Z','value':10},{'date':'2019-12-31T21:00:00-03:00','value':10}]);self.assertEqual(len(r),1)
    def test_calendar_uid_update_and_cancellation_no_duplicate(self):
        blocks=['BEGIN:VEVENT\nUID:one\nDTSTART:20261101T140000Z\nSEQUENCE:1\nSUMMARY:Old\nEND:VEVENT','BEGIN:VEVENT\nUID:one\nDTSTART:20261102T140000Z\nSEQUENCE:2\nSTATUS:CANCELLED\nSUMMARY:New\nEND:VEVENT']
        events=parse_ics('\n'.join(blocks));self.assertEqual(len(events),1);self.assertEqual(events[0]['status'],'cancelado');self.assertIn('2026-11-02',events[0]['date'])
    def test_calendar_tentative_not_confirmed(self):
        events=parse_ics('BEGIN:VEVENT\nDTSTART:20261101T140000Z\nSTATUS:TENTATIVE\nEND:VEVENT');self.assertEqual(events[0]['status'],'estimado')
    def test_env_is_literal_and_does_not_replace_export(self):
        p=Path(self.tmp.name)/'.env';p.write_text('AUDIT_VALUE="$(do-not-run)"\nAUDIT_EXISTING=new\nFRAME_ANCESTORS="\'self\'"',encoding='utf8')
        with patch.dict(os.environ,{'AUDIT_EXISTING':'old'},clear=True):load_env(p);self.assertEqual(os.environ['AUDIT_VALUE'],'$(do-not-run)');self.assertEqual(os.environ['AUDIT_EXISTING'],'old');self.assertEqual(os.environ['FRAME_ANCESTORS'],"'self'")
    def test_consistent_backup_and_restore_to_new_file(self):
        self.cache.put('x',{'value':1});target=Path(self.tmp.name)/'backup.db';backup(self.cache.path,target);restored=Path(self.tmp.name)/'restored.db';backup(target,restored);self.assertEqual(Cache(restored).get('x')[0]['value'],1)
        with self.assertRaises(ValueError):backup(self.cache.path,target)
    def test_policy_metadata_rejects_estimated_meeting_and_calculates_basis_points(self):
        from backend.validation import policy_metadata
        with self.assertRaises(ValueError):policy_metadata({'next_meeting':{'date':'2026-12-01','status':'estimated','source_url':'https://bank.invalid'}})
        data=policy_metadata({'source_url':'https://bank.invalid','decisions':[{'date':'2025-01-01','value':4.5,'previous_value':4.25}]});self.assertEqual(data['decisions'][0]['change_bps'],25)
    def test_wordpress_generator_uses_one_https_url_for_iframe_and_link(self):
        from backend.wordpress import embed
        result=embed('https://markets.invalid/?a=1&b=2');self.assertIn('a=1&amp;b=2',result);self.assertEqual(result.count('https://markets.invalid'),2)
        for url in ['javascript:alert(1)','http://markets.invalid','https://user:secret@markets.invalid']:
            with self.assertRaises(ValueError):embed(url)
    def test_production_configuration_fails_closed(self):
        from backend.check_config import errors
        self.assertTrue(errors({}))
        self.assertEqual(errors({'ADMIN_TOKEN':'x'*32,'ALLOWED_ORIGINS':'https://markets.invalid','FRAME_ANCESTORS':"'self' https://wordpress.invalid",'CACHE_PATH':self.cache.path}),[])
    def test_all_periods_reach_provider_with_requested_window(self):
        from backend.config import PERIODS
        seen=[]
        service=Service(self.cache,lambda a,b,e:(seen.append((b,e)) or {'points':[]}))
        for period,days in PERIODS.items():
            service.series('usdbrl',period,True)
            if days is not None:self.assertEqual((seen[-1][1]-seen[-1][0]).days,days)
    def test_daily_comparison_aligns_intraday_with_daily_without_interpolation(self):
        from backend.service import compare
        series=[{'id':'fx','points':[{'date':'2025-01-01','value':5},{'date':'2025-01-02','value':6}]},{'id':'crypto','points':[{'date':'2025-01-01T10:00:00+00:00','value':90},{'date':'2025-01-01T23:00:00+00:00','value':100},{'date':'2025-01-02T12:00:00+00:00','value':110}]}]
        self.assertEqual(compare(series),[])
        aligned=compare(series,alignment='daily');self.assertEqual(aligned[1]['points'][0]['value'],100);self.assertAlmostEqual(aligned[1]['points'][1]['value'],110)

class AuditAPI(PlatformTests):
    # Inherits API fixture helpers. load_tests below selects only new tests to avoid re-running base suite.
    def test_reject_duplicate_empty_unknown_ids_and_parameters(self):
        for query in ['id=selic&id=fed','id=','id=selic&unknown=1','id=selic,fed']:
            self.assertTrue(self.call('/api/series',query)[0].startswith('400'))
        self.assertTrue(self.call('/api/compare','ids=selic,selic')[0].startswith('400'))
    def test_non_ascii_token_is_unauthorized_not_server_error(self):
        with patch('backend.app.ADMIN_TOKEN','secret'):self.assertTrue(self.call('/api/admin/diagnostics',HTTP_AUTHORIZATION='Bearer inválido')[0].startswith('401'))
    def test_calendar_recent_failure_visible_with_cache(self):
        self.cache.put('calendar',{'events':[],'directory':[]});owner=self.cache.claim('calendar');self.cache.finish('calendar',owner,86400,'fonte indisponível')
        response=json.loads(self.call('/api/calendar')[2]);self.assertTrue(response['stale']);self.assertEqual(response['error'],'fonte indisponível')

def load_tests(loader,tests,pattern):
    suite=loader.loadTestsFromTestCase(AuditData)
    for name in ['test_reject_duplicate_empty_unknown_ids_and_parameters','test_non_ascii_token_is_unauthorized_not_server_error','test_calendar_recent_failure_visible_with_cache']:suite.addTest(AuditAPI(name))
    return suite
