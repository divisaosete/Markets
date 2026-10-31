import json, tempfile, unittest
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from unittest.mock import patch, Mock
import xlrd
from backend.providers.eia import SERIES, parse_workbook, fetch
from backend.catalog import BY_ID
from backend.pages import collect,ROOT,validate_document
from backend.energy_validation import collect_energy

class EiaTests(unittest.TestCase):
    def workbook(self, label=None, values=None):
        label = label or SERIES['wti'][2]
        values = values or [(date(2020,4,20), -36.98), (date(2020,4,21), 8.91)]
        sheet = Mock(ncols=2, nrows=3+len(values))
        sheet.cell_value.side_effect=lambda r,c: 'Date' if c==0 else label
        def cell(r,c):
            d,v=values[r-3]
            return Mock(ctype=xlrd.XL_CELL_DATE if c==0 else xlrd.XL_CELL_NUMBER,
                        value=(d-date(1899,12,30)).days if c==0 else v)
        sheet.cell.side_effect=cell
        book=Mock(datemode=0);book.sheet_by_name.return_value=sheet
        return book
    def parse(self,book):
        with patch('xlrd.open_workbook',return_value=book):
            return parse_workbook(b'explicit fixture',SERIES['wti'][2],date(2020,1,1),date(2020,12,31))
    def test_spot_negative_price_and_dates_are_preserved(self):
        pts=self.parse(self.workbook())
        self.assertEqual(pts[0],{'date':'2020-04-20','value':-36.98})
    def test_wrong_market_or_unit_rejected(self):
        with self.assertRaises(ValueError):self.parse(self.workbook(label='Futures USD/ton'))
    def test_conflicting_duplicates_and_future_dates_rejected(self):
        for values in [[(date(2020,4,20),1),(date(2020,4,20),2)],[(date.today()+timedelta(days=1),3)]]:
            with self.assertRaises(ValueError):self.parse(self.workbook(values=values))
    def test_historical_window_ignores_later_valid_observations(self):
        points=self.parse(self.workbook(values=[(date(2020,4,20),1),(date(2021,1,1),2)]))
        self.assertEqual(points,[{'date':'2020-04-20','value':1}])
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):self.parse(self.workbook(values=[(date(2020,1,1),float('nan'))]))
    def test_fixed_download_and_metadata(self):
        get=Mock(return_value=b'fixture')
        with patch('backend.providers.eia.parse_workbook',return_value=[{'date':'2020-04-20','value':-36.98}]):
            result=fetch(BY_ID['wti'],date(2020,1,1),date(2020,12,31),get)
        get.assert_called_once_with('https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls',output='bytes')
        self.assertEqual(result['unit'],'USD/barril');self.assertIn('spot',result['reference'])
    def test_collection_preserves_older_history_and_revises_matching_dates(self):
        (ROOT/'var').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'var') as temp:
            out=Path(temp)/'data.json';state=Path(temp)/'state.json'
            now=datetime(2020,5,1,tzinfo=timezone.utc)
            def run(points):
                return collect_energy(out,lambda *_:{'points':points},now=now,force=True)
            run([{'date':'2020-04-20','value':-36.98},{'date':'2020-04-21','value':8.91}])
            run([{'date':'2020-04-21','value':9}])
            row=next(r for r in json.loads(out.read_text(encoding='utf8'))['series'] if r['id']=='wti')
            self.assertEqual(row['points'],[{'date':'2020-04-20','value':-36.98},{'date':'2020-04-21','value':9}])
            self.assertEqual(row['currency'],'USD');self.assertEqual(row['license'],'Redistribuição pública não confirmada')
    def test_public_collection_never_fetches_energy_even_when_forced(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'data.json'
            forbidden=Mock(side_effect=AssertionError('Unapproved energy was fetched'))
            collect(out,forbidden,ids=set(SERIES),force=True,state_path=Path(temp)/'state.json')
            forbidden.assert_not_called()
            rows=json.loads(out.read_text(encoding='utf8'))['series']
            for row in rows:
                if row['id'] in SERIES:
                    self.assertEqual(row['points'],[]);self.assertIsNone(row['latest'])
                    self.assertEqual(row['reason'],'publication_review')
    def test_optional_backend_cannot_bypass_publication_block(self):
        from backend.providers import fetch as backend_fetch,Unavailable
        with patch('backend.providers.request') as request:
            with self.assertRaises(Unavailable):backend_fetch(BY_ID['wti'],date(2020,1,1),date(2020,12,31))
            request.assert_not_called()
    def test_public_validator_and_builder_reject_reintroduced_energy(self):
        from backend.build_pages import build
        from backend.pages import DEFAULT
        data=json.loads(DEFAULT.read_text(encoding='utf8'))
        row=next(r for r in data['series'] if r['id']=='brent')
        row.update(points=[{'date':'2020-01-02','value':1}],latest={'date':'2020-01-02','value':1})
        with self.assertRaisesRegex(ValueError,'Unapproved'):validate_document(data)
        with tempfile.TemporaryDirectory() as temp,patch('backend.build_pages.json.loads',return_value=data):
            with self.assertRaisesRegex(ValueError,'Unapproved'):build(Path(temp)/'site')
    def test_local_collector_cannot_write_public_or_build_directory(self):
        for path in [ROOT/'public/data/energy.json',ROOT/'_site/data/energy.json']:
            with self.assertRaisesRegex(ValueError,'var/'):collect_energy(path,Mock())
    def test_local_failure_preserves_history_and_hides_exception_details(self):
        (ROOT/'var').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'var') as temp:
            out=Path(temp)/'data.json'
            collect_energy(out,lambda *_:{'points':[{'date':'2020-01-02','value':1}]},force=True)
            report=collect_energy(out,Mock(side_effect=TimeoutError('SENTINEL-SECRET')),force=True)
            self.assertNotIn('SENTINEL',out.read_text(encoding='utf8')+json.dumps(report))
            self.assertTrue(all(r['status']=='stale' and len(r['points'])==1 for r in json.loads(out.read_text(encoding='utf8'))['series']))
    def test_local_preview_is_rejected_as_public_document(self):
        from backend.preview_energy import prepare_preview
        (ROOT/'var').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'var') as temp:
            output=Path(temp)/'local.json'
            collect_energy(output,lambda *_:{'points':[{'date':'2020-01-02','value':1.25}]},force=True)
            target=prepare_preview(output,Path(temp)/'preview/Markets')
            self.assertIn('NÃO PUBLICAR',(target/'index.html').read_text(encoding='utf8'))
            with self.assertRaisesRegex(ValueError,'Unapproved'):
                validate_document(json.loads((target/'data/market-data.json').read_text(encoding='utf8')))
            with self.assertRaisesRegex(ValueError,'var/'):
                prepare_preview(output,ROOT/'_site')
    def test_failure_report_does_not_overwrite_source_comparison_report(self):
        (ROOT/'var').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'var') as temp:
            good=Path(temp)/'energy-validation.json';failed=Path(temp)/'energy-failure.json'
            collect_energy(good,lambda *_:{'points':[{'date':'2020-01-02','value':1.25}]},force=True)
            source_report=good.with_name('energy-validation-report.json').read_bytes()
            failed.write_bytes(good.read_bytes())
            collect_energy(failed,Mock(side_effect=TimeoutError()),force=True)
            self.assertEqual(good.with_name('energy-validation-report.json').read_bytes(),source_report)
            self.assertTrue(failed.with_name('energy-failure-report.json').exists())

if __name__=='__main__':unittest.main()
