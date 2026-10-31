import os,tempfile,unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
from backend.providers.official import parse_treasury,treasury,ecb,boc
from backend.catalog import BY_ID
from backend.availability import classify
from backend.local import worker_environment

class OfficialSources(unittest.TestCase):
    def test_treasury_preserves_dates_and_missing_maturities(self):
        xml='<feed xmlns:d="urn:d"><entry><d:NEW_DATE>2026-01-02T00:00:00</d:NEW_DATE><d:BC_2YEAR>4.1</d:BC_2YEAR><d:BC_10YEAR>4.5</d:BC_10YEAR></entry></feed>'
        points=parse_treasury(xml,10,date(2026,1,1),date(2026,1,3));self.assertEqual(points,[{'date':'2026-01-02','value':4.5}]);self.assertEqual(parse_treasury(xml,30,date(2026,1,1),date(2026,1,3)),[])
    def test_treasury_rejects_entities_and_wrong_tenor(self):
        with self.assertRaises(ValueError):parse_treasury('<!DOCTYPE x><feed/>',10,date(2026,1,1),date(2026,1,3))
        with self.assertRaises(ValueError):parse_treasury('<feed/>',7,date(2026,1,1),date(2026,1,3))
    def test_treasury_long_period_requests_each_year(self):
        calls=[]
        treasury(BY_ID['yield-Estados Unidos-10'],date(2021,1,1),date(2026,1,1),lambda u:(calls.append(u) or '<feed/>'))
        self.assertEqual(len(calls),6);self.assertIn('field_tdr_date_value=2021',calls[0]);self.assertIn('field_tdr_date_value=2026',calls[-1])
    def test_treasury_persistent_upstream_cache_is_shared_across_maturities(self):
        from backend.cache import Cache
        with tempfile.TemporaryDirectory() as folder:
            cache=Cache(Path(folder)/'cache.db');calls=[]
            get=lambda u:(calls.append(u) or '<feed/>')
            treasury(BY_ID['yield-Estados Unidos-2'],date(2026,1,1),date(2026,1,2),get,cache)
            treasury(BY_ID['yield-Estados Unidos-10'],date(2026,1,1),date(2026,1,2),get,Cache(cache.path));self.assertEqual(len(calls),1)
    def test_ecb_identity_and_change_dates_not_decisions(self):
        csv='KEY,TIME_PERIOD,OBS_VALUE\nFM.D.U2.EUR.4F.KR.DFR.LEV,2026-01-01,2.0\n'
        data=ecb(BY_ID['ecb'],date(2025,1,1),date(2026,1,2),lambda _:csv);self.assertEqual(data['points'][0]['value'],2);self.assertEqual(data['reference'],'policy_change');self.assertNotIn('decision_date',data)
        with self.assertRaises(ValueError):ecb(BY_ID['ecb'],date(2025,1,1),date(2026,1,2),lambda _:csv.replace('FM.D.U2.EUR.4F.KR.DFR.LEV','WRONG'))
    def test_boc_checks_target_instrument_in_metadata(self):
        data={'seriesDetail':{'V39079':{'label':'Target for the overnight rate'}},'observations':[{'d':'2026-01-02','V39079':{'v':'2.25'}}]}
        result=boc(BY_ID['boc'],date(2025,1,1),date(2026,1,3),lambda _:data);self.assertEqual(result['points'][0]['value'],2.25)
        data['seriesDetail']['V39079']['label']='Bank Rate'
        with self.assertRaises(ValueError):boc(BY_ID['boc'],date(2025,1,1),date(2026,1,3),lambda _:data)
    def test_reasons_distinguish_missing_key_license_and_source_failure(self):
        state={'status':'unavailable','points':[],'message':'source down'}
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(classify(BY_ID['bitcoin'],state)['reason'],'credential_required');self.assertEqual(classify(BY_ID['ibov'],state)['reason'],'license_required');self.assertEqual(classify(BY_ID['usdbrl'],state)['reason'],'source_failure')
    def test_availability_never_exposes_key_value(self):
        state={'status':'pending','points':[]}
        with patch.dict(os.environ,{'COINGECKO_API_KEY':'secret-value'}):self.assertNotIn('secret-value',str(classify(BY_ID['bitcoin'],state)))
    def test_local_stop_path_is_explicit_and_environment_preserved(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'TEST_EXISTING':'kept'}):
            env=worker_environment(Path(folder)/'stop');self.assertEqual(env['TEST_EXISTING'],'kept');self.assertTrue(Path(env['LOCAL_STOP_FILE']).is_absolute())
    def test_local_worker_detects_terminated_parent(self):
        from backend.processes import parent_alive
        self.assertTrue(parent_alive(str(os.getpid())));self.assertTrue(parent_alive(''));self.assertFalse(parent_alive('-1'));self.assertFalse(parent_alive('invalid'));self.assertFalse(parent_alive('999999999'))
if __name__=='__main__':unittest.main()
