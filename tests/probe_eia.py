"""Manual network check, not a fixture test: python -m tests.probe_eia."""
from backend.providers.eia import SERIES, parse_workbook
from backend.providers import request
from datetime import date, timedelta

if __name__ == '__main__':
    import xlrd
    for id, (section, code, label, unit) in SERIES.items():
        try:
            raw = request(f'https://www.eia.gov/dnav/{section}/hist_xls/{code}.xls', output='bytes')
            book = xlrd.open_workbook(file_contents=raw)
            print(id, book.sheet_by_name('Data 1').row_values(2))
            points = parse_workbook(raw, label, date.today()-timedelta(days=1826), date.today())
            print('PASS', len(points), points[-1])
        except Exception as error:
            print(id, type(error).__name__, getattr(error, 'code', ''))
