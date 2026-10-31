"""EIA's explicitly published XLS downloads, not HTML scraping or futures proxies."""
from datetime import date
from backend.validation import normalize_points

# Fixed filenames and exact workbook labels bind identity, geography and units.
SERIES = {
    'brent': ('pet', 'RBRTEd', 'Europe Brent Spot Price FOB (Dollars per Barrel)', 'USD/barril'),
    'wti': ('pet', 'RWTCd', 'Cushing, OK WTI Spot Price FOB (Dollars per Barrel)', 'USD/barril'),
    'commodity-29': ('ng', 'RNGWHHDd', 'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)', 'USD/MMBtu'),
    'commodity-31': ('pet', 'EER_EPD2F_PF4_Y35NY_DPGd', 'New York Harbor No. 2 Heating Oil Spot Price FOB (Dollars per Gallon)', 'USD/galão EUA'),
}

def parse_workbook(raw, expected, start, end):
    import xlrd
    book = xlrd.open_workbook(file_contents=raw)
    try:
        sheet = book.sheet_by_name('Data 1')
        if sheet.ncols != 2 or sheet.cell_value(2, 0) != 'Date' or sheet.cell_value(2, 1) != expected:
            raise ValueError('Identidade ou unidade EIA divergente')
        points = []
        for row in range(3, sheet.nrows):
            d, v = sheet.cell(row, 0), sheet.cell(row, 1)
            if d.ctype == xlrd.XL_CELL_EMPTY and v.ctype == xlrd.XL_CELL_EMPTY:
                continue
            if d.ctype != xlrd.XL_CELL_DATE:
                raise ValueError('Data EIA inválida')
            observed = xlrd.xldate_as_datetime(d.value, book.datemode).date()
            if observed > date.today():
                raise ValueError('Observação EIA futura')
            if v.ctype == xlrd.XL_CELL_EMPTY or v.value in ('', 'NA', '-'):
                continue
            if v.ctype != xlrd.XL_CELL_NUMBER:
                raise ValueError('Preço EIA inválido')
            if start <= observed <= end:
                points.append({'date': observed.isoformat(), 'value': v.value})
        points = normalize_points(points, end)
        if not points:
            raise ValueError('Histórico EIA vazio')
        return points
    finally:
        book.release_resources()

def fetch(a, start, end, request):
    section, code, label, unit = SERIES[a['id']]
    url = f'https://www.eia.gov/dnav/{section}/hist_xls/{code}.xls'
    points = parse_workbook(request(url, output='bytes'), label, start, end)
    return {'points': points, 'source': 'U.S. Energy Information Administration · EIA',
            'source_url': f'https://www.eia.gov/dnav/{section}/hist/{code}.htm',
            'unit': unit, 'frequency': 'diária (dias publicados)',
            'reference': label + '; spot, sem contrato futuro', 'instrument': label,
            'attribution': 'Source: U.S. Energy Information Administration; consulta em ' + date.today().isoformat()}
