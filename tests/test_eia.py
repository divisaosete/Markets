import json, tempfile, unittest
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from unittest.mock import patch, Mock
import xlrd
from backend.providers.eia import SERIES, parse_workbook, fetch
from backend.catalog import BY_ID
from backend.pages import collect

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
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'data.json';state=Path(temp)/'state.json'
            now=datetime(2020,5,1,tzinfo=timezone.utc)
            def run(points):
                return collect(out,lambda *_:{'points':points},now=now,ids={'wti'},force=True,state_path=state)
            run([{'date':'2020-04-20','value':-36.98},{'date':'2020-04-21','value':8.91}])
            run([{'date':'2020-04-21','value':9}])
            row=next(r for r in json.loads(out.read_text(encoding='utf8'))['series'] if r['id']=='wti')
            self.assertEqual(row['points'],[{'date':'2020-04-20','value':-36.98},{'date':'2020-04-21','value':9}])
            self.assertEqual(row['currency'],'USD');self.assertEqual(row['license'],'US public domain; EIA attribution')

if __name__=='__main__':unittest.main()
