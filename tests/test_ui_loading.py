import json,re,unittest
from pathlib import Path
from html.parser import HTMLParser
from backend.config import ROOT
from backend.export_frontend import generate
from test_backend import PlatformTests
class References(HTMLParser):
    def __init__(self):super().__init__();self.local=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if tag=='script' and data.get('src'):self.local.append(data['src'])
        if tag=='link' and data.get('href'):self.local.append(data['href'])
class UILoading(unittest.TestCase):
    def test_index_is_present_and_references_resolve_in_both_static_roots(self):
        path=ROOT/'public'/'index.html';self.assertTrue(path.is_file());parser=References();parser.feed(path.read_text(encoding='utf8'))
        for ref in parser.local:
            self.assertTrue(ref.startswith('./'));self.assertTrue((path.parent/ref).is_file());self.assertNotIn('C:',ref)
    def test_exported_metadata_exactly_matches_backend(self):
        self.assertEqual((ROOT/'public'/'catalog.js').read_text(encoding='utf8'),generate())
    def test_shell_is_local_before_async_public_coverage_load(self):
        app=(ROOT/'public'/'app.js').read_text(encoding='utf8');self.assertNotIn("await api('catalog')",app.split('async function load()')[0]);self.assertIn('catalog=ASSETS',app);self.assertIn('route();',app)
class BackendPage(PlatformTests):
    def test_python_backend_enables_same_origin_api_without_static_config(self):
        status,headers,body=self.call('/');self.assertTrue(status.startswith('200'));self.assertIn(b'<meta name="markets-api-base" content="/api/">',body)
        static=(ROOT/'public'/'index.html').read_bytes();self.assertIn(b'<meta name="markets-api-base" content="">',static)
    def test_all_essential_frontend_resources_are_served(self):
        for name in ['styles.css','bootstrap.js','app.js','chart.js','data.js','catalog.js','offline.js','config.js','analytics.js','polling.js','favicon.svg']:
            self.assertTrue(self.call('/'+name)[0].startswith('200'),name)
    def test_cors_does_not_block_public_modules_but_protects_api(self):
        origin='http://127.0.0.1:5553'
        self.assertTrue(self.call('/app.js',HTTP_ORIGIN=origin)[0].startswith('200'))
        self.assertTrue(self.call('/api/catalog',HTTP_ORIGIN=origin)[0].startswith('403'))
def load_tests(loader,tests,pattern):
    suite=loader.loadTestsFromTestCase(UILoading)
    for name in ['test_python_backend_enables_same_origin_api_without_static_config','test_all_essential_frontend_resources_are_served','test_cors_does_not_block_public_modules_but_protects_api']:suite.addTest(BackendPage(name))
    return suite
