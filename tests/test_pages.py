import copy,json,os,tempfile,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
from backend.pages import collect,validate_document,DEFAULT
from backend.build_pages import build,public_api

class PagesExport(unittest.TestCase):
    def test_repository_root_is_real_dashboard_with_relative_public_assets(self):
        root=Path(__file__).resolve().parent.parent
        expected=(root/'public/index.html').read_text(encoding='utf8')
        for asset in ('favicon.svg','styles.css','bootstrap.js'):
            expected=expected.replace('./'+asset,'./public/'+asset)
        self.assertEqual((root/'index.html').read_text(encoding='utf8'),expected)
        self.assertTrue((root/'.nojekyll').is_file())
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.output=self.root/'data.json';self.state=self.root/'state.json';self.now=datetime.now(timezone.utc)
    def fixture(self,a,*_):return {'points':[{'date':self.now.date().isoformat(),'value':5.1234}],'source':'Explicit unit-test fixture','source_url':'https://example.invalid/data','api_key':'DO-NOT-PUBLISH','private_path':'C:/private/secret'}
    def run_collect(self,fetch=None,**kw):return collect(self.output,fetch or self.fixture,now=kw.pop('now',self.now),ids={'usdbrl'},force=kw.pop('force',True),state_path=self.state,**kw)
    def row(self):return next(r for r in json.loads(self.output.read_text(encoding='utf8'))['series'] if r['id']=='usdbrl')
    def test_only_allowlisted_fields_and_no_environment_secrets(self):
        with patch.dict(os.environ,{'FRED_API_KEY':'SENTINEL-SECRET'}):self.run_collect()
        raw=self.output.read_text(encoding='utf8');self.assertNotIn('SENTINEL',raw);self.assertNotIn('DO-NOT-PUBLISH',raw);self.assertNotIn('C:/private',raw);self.assertEqual(self.row()['latest']['value'],5.1234);self.assertEqual(self.row()['currency'],'BRL')
    def test_failure_preserves_last_valid_observations_without_exception_text(self):
        self.run_collect();before=self.row()['points']
        def fail(*_):raise ValueError('SENTINEL secret URL')
        report=self.run_collect(fail);self.assertEqual(self.row()['points'],before);self.assertEqual(self.row()['status'],'stale');self.assertNotIn('SENTINEL',json.dumps(report)+self.output.read_text(encoding='utf8'))
    def test_unchanged_success_makes_no_public_change_or_timestamp_churn(self):
        self.run_collect();before=self.output.read_bytes();report=self.run_collect(now=self.now+timedelta(minutes=1));self.assertFalse(report['changed']);self.assertEqual(before,self.output.read_bytes())
    def test_frequency_skips_collection_until_due(self):
        self.run_collect()
        def forbidden(*_):self.fail('Not due')
        self.assertFalse(self.run_collect(forbidden,force=False,now=self.now+timedelta(minutes=1))['changed'])
    def test_unlicensed_and_unreviewed_assets_are_never_fetched(self):
        def forbidden(*_):self.fail('Not authorized')
        collect(self.output,forbidden,ids={'ibov','bitcoin','BRA-GC.DOD.TOTL.GD.ZS'},force=True,state_path=self.state)
        self.assertTrue(all(not r['points'] for r in json.loads(self.output.read_text(encoding='utf8'))['series']))
    def test_empty_and_invalid_points_preserve_previous_history(self):
        self.run_collect();before=self.row()['points']
        self.run_collect(lambda *_:{'points':[]});self.assertEqual(self.row()['points'],before)
        self.run_collect(lambda *_:{'points':[{'date':self.now.date().isoformat(),'value':float('nan')}]});self.assertEqual(self.row()['points'],before)
    def test_corrupt_existing_json_is_not_overwritten(self):
        self.output.write_text('{bad');before=self.output.read_bytes()
        with self.assertRaises(ValueError):self.run_collect()
        self.assertEqual(before,self.output.read_bytes())
    def test_invalid_metadata_is_isolated_and_never_publishes_a_token_url(self):
        self.run_collect();before=self.row()['points']
        def fetch(a,*args):
            result=self.fixture(a,*args)
            if a['id']=='usdbrl':result['source_url']='https://example.invalid/?key=LEAK-ME'
            return result
        collect(self.output,fetch,now=self.now,ids={'usdbrl','eurbrl'},force=True,state_path=self.state)
        raw=self.output.read_text(encoding='utf8');self.assertNotIn('LEAK-ME',raw);self.assertEqual(self.row()['points'],before)
        self.assertTrue(next(r for r in json.loads(raw)['series'] if r['id']=='eurbrl')['points'])
    def test_validate_rejects_unapproved_data_and_extra_secret_fields(self):
        self.run_collect();data=json.loads(self.output.read_text(encoding='utf8'));bad=copy.deepcopy(data);bad['series'][0]['api_key']='bad'
        with self.assertRaises(ValueError):validate_document(bad)
        bad=copy.deepcopy(data);bad['series'][0]['points']=[{'date':self.now.date().isoformat(),'value':1}];bad['series'][0]['latest']=bad['series'][0]['points'][0]
        with self.assertRaises(ValueError):validate_document(bad)
    def test_real_public_bundle_valid_and_build_contains_no_private_files(self):
        validate_document(json.loads(DEFAULT.read_text(encoding='utf8')));dest=self.root/'repo';report=build(dest)
        self.assertGreater(report['available'],0)
        self.assertFalse(any(p.suffix in ('.py','.sqlite3','.zip') or p.name=='.env' for p in dest.rglob('*')))
        self.assertIn('./bootstrap.js',(dest/'index.html').read_text(encoding='utf8'));self.assertIn('staticData',(dest/'config.js').read_text());self.assertNotIn('127.0.0.1',(dest/'config.js').read_text())
    def test_builder_rejects_secret_urls_and_nonpublic_proxy(self):
        for bad in ['http://api.invalid/api/','https://name:secret@api.invalid/api/','https://api.invalid/?key=secret','https://127.0.0.1/api/','https://10.0.0.1/api/']:
            with self.assertRaises(ValueError):public_api(bad)
        self.assertEqual(public_api('https://api.example.invalid/api'),'https://api.example.invalid/api/')
    def test_build_refuses_unknown_existing_files_instead_of_publishing_them(self):
        dest=self.root/'site';dest.mkdir();(dest/'.env').write_text('SECRET')
        with self.assertRaises(ValueError):build(dest)
    def test_build_refuses_hardlinked_destination_without_overwriting_target(self):
        dest=self.root/'site';dest.mkdir();private=self.root/'private.txt';private.write_text('PRIVATE_SENTINEL');os.link(private,dest/'app.js')
        with self.assertRaises(ValueError):build(dest)
        self.assertEqual(private.read_text(),'PRIVATE_SENTINEL')

class Workflows(unittest.TestCase):
    def test_workflows_parse_and_permissions_and_refs_are_restricted(self):
        import yaml,re
        root=Path(__file__).resolve().parent.parent
        for name in ('pages.yml','update-data.yml'):
            raw=(root/'.github/workflows'/name).read_text();doc=yaml.load(raw,Loader=yaml.BaseLoader)
            self.assertIn('workflow_dispatch',doc['on']);self.assertEqual(doc['permissions'],{'contents':'read'})
            self.assertNotIn('pull_request_target',raw)
            for ref in re.findall(r'uses: (actions/[^\s]+)',raw):self.assertRegex(ref,r'@[a-f0-9]{40}$')
        data=yaml.load((root/'.github/workflows/update-data.yml').read_text(),Loader=yaml.BaseLoader)
        self.assertIn('schedule',data['on']);self.assertEqual(data['jobs']['collect']['permissions'],{'contents':'write'})
        page=yaml.load((root/'.github/workflows/pages.yml').read_text(),Loader=yaml.BaseLoader)
        self.assertEqual(page['jobs']['deploy']['needs'],'build');self.assertEqual(page['jobs']['build']['steps'][-1]['with']['path'],'_site')
