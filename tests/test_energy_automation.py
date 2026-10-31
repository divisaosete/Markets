"""Publication and failure simulation, without live network or licensed samples."""
import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import Mock
from backend.pages import collect,DEFAULT,ROOT,validate_document
from backend.providers.eia import SERIES
from backend.energy_validation import collect_energy

class EnergyAutomationTests(unittest.TestCase):
    def test_public_update_failure_and_recovery_keep_energy_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'data.json';state=Path(temp)/'state.json'
            source=json.loads(DEFAULT.read_text(encoding='utf8'))
            output.write_text(json.dumps(source),encoding='utf8')
            now=datetime.now(timezone.utc);ids={'usdbrl',*SERIES}
            def failing(a,*_):
                self.assertEqual(a['id'],'usdbrl')
                raise TimeoutError('PRIVATE-URL-KEY')
            result=collect(output,failing,now=now,ids=ids,force=True,state_path=state)
            data=validate_document(json.loads(output.read_text(encoding='utf8')))
            old=next(r for r in source['series'] if r['id']=='usdbrl')
            fx=next(r for r in data['series'] if r['id']=='usdbrl')
            self.assertEqual(fx['points'],old['points']);self.assertEqual(fx['status'],'stale')
            self.assertNotIn('PRIVATE-URL-KEY',output.read_text(encoding='utf8')+json.dumps(result))
            never=Mock(side_effect=AssertionError('Interval not elapsed'))
            collect(output,never,now=now+timedelta(minutes=1),ids=ids,state_path=state)
            never.assert_not_called()
            collect(output,lambda a,*_: {'points':old['points']},now=now+timedelta(days=1),ids=ids,state_path=state)
            data=validate_document(json.loads(output.read_text(encoding='utf8')))
            self.assertEqual(next(r for r in data['series'] if r['id']=='usdbrl')['status'],'ok')
            self.assertTrue(all(not r['points'] and r['latest'] is None for r in data['series'] if r['id'] in SERIES))
    def test_local_interval_and_partial_outage_preserve_valid_histories(self):
        (ROOT/'var').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'var') as temp:
            output=Path(temp)/'local.json';now=datetime.now(timezone.utc)
            points=[{'date':now.date().isoformat(),'value':1.25}]
            collect_energy(output,lambda *_:{'points':points},now=now,force=True)
            never=Mock(side_effect=AssertionError('Not due'))
            collect_energy(output,never,now=now+timedelta(minutes=5));never.assert_not_called()
            def partial(a,*_):
                if a['id']=='wti':raise TimeoutError('SECRET')
                return {'points':points}
            report=collect_energy(output,partial,now=now+timedelta(days=1))
            data=json.loads(output.read_text(encoding='utf8'))
            self.assertEqual(next(r for r in data['series'] if r['id']=='wti')['status'],'stale')
            self.assertTrue(all(r['points']==points for r in data['series']))
            self.assertEqual([r['result'] for r in report['results']],['PASS','FAIL','PASS','PASS'])
            self.assertNotIn('SECRET',json.dumps(report))
    def test_actions_cache_preserves_provider_deferral_database(self):
        import yaml
        workflow=yaml.load((ROOT/'.github/workflows/update-data.yml').read_text(),Loader=yaml.BaseLoader)
        cache=next(s for s in workflow['jobs']['collect']['steps'] if 'actions/cache@' in s.get('uses',''))
        paths=cache['with']['path'].splitlines()
        self.assertIn('var/pages-state.json',paths);self.assertIn('var/pages.sqlite3',paths)
        self.assertNotIn('energy-validation',cache['with']['path'])
