import unittest,os,json,tempfile
from datetime import date
from unittest.mock import patch
from backend.providers import fetch,Unavailable
from backend.catalog import BY_ID
class Providers(unittest.TestCase):
    def test_bcb_multi_window_and_dates(self):
        with patch('backend.providers.request',return_value=[{'data':'01/01/2000','valor':'19.00'}]) as req:
            data=fetch(BY_ID['selic'],date(1996,7,1),date(2026,10,30));self.assertEqual(req.call_count,4);self.assertEqual(data['points'][0]['date'],'2000-01-01')
    def test_fx_reference_provider_and_window(self):
        with patch('backend.providers.request',return_value=[{'date':'2026-01-02','rate':5.5}]) as req:
            data=fetch(BY_ID['usdbrl'],date(2021,1,1),date(2026,1,3));self.assertIn('providers=ecb',req.call_args.args[0]);self.assertIn('from=2021-01-01',req.call_args.args[0]);self.assertEqual(data['points'][0]['value'],5.5)
    def test_worldbank_missing_values_not_filled(self):
        with patch('backend.providers.request',return_value=[{},[{'date':'2024','value':None},{'date':'2023','value':12}]]):
            data=fetch(BY_ID['USA-NY.GDP.MKTP.CD'],date(1960,1,1),date(2026,1,1));self.assertEqual(len(data['points']),1);self.assertIsNone(data['publication_date'])
    def test_fred_missing_values_and_no_effective_rate(self):
        with patch.dict(os.environ,{'FRED_API_KEY':'fixture-not-secret'}),patch('backend.providers.request',return_value={'observations':[{'date':'2026-01-01','value':'.'},{'date':'2026-01-02','value':'4.5'}]}) as req:
            data=fetch(BY_ID['fed'],date(2026,1,1),date(2026,1,3));self.assertEqual(len(data['points']),1);self.assertIn('DFEDTARU',req.call_args.args[0])
    def test_crypto_plan_rejects_before_network(self):
        with patch.dict(os.environ,{'COINGECKO_API_KEY':'fixture','COINGECKO_HISTORY_DAYS':'365'}),patch('backend.providers.request') as req:
            with self.assertRaises(Unavailable):fetch(BY_ID['bitcoin'],date(2020,1,1),date(2026,1,1))
            req.assert_not_called()
    def test_licensed_future_contract_required(self):
        with tempfile.TemporaryDirectory() as folder:
            path=folder+'/feed.json'
            record=dict(source='Licensed fixture',source_url='https://source.org',unit='USD/bbl',currency='USD',market='ICE',reference='future',frequency='daily',instrument_id='contract',points=[])
            with open(path,'w') as f:json.dump({'assets':{'brent':record}},f)
            with patch.dict(os.environ,{'LICENSED_FEED_PATH':path,'LICENSED_REDISTRIBUTION_APPROVED':'yes'}):
                with self.assertRaises(Unavailable):fetch({**BY_ID['brent'],'provider':'licensed'},date(2026,1,1),date(2026,1,3))
    def test_treasury_maturity_is_not_policy_rate(self):
        a=BY_ID['yield-Estados Unidos-10'];self.assertEqual(a['code'],'BC_10YEAR');self.assertEqual(a['provider'],'treasury');self.assertEqual(a['category'],'yields');self.assertEqual(a['tenor'],10)
if __name__=='__main__':unittest.main()
