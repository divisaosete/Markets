import unittest
from unittest.mock import patch
from backend.calendar import parse_boe,fetch_calendar
class BoECalendar(unittest.TestCase):
    def test_only_confirmed_sections_and_no_inferred_time(self):
        text='<h2>2026 confirmed dates</h2><table><tr><td>Thursday 5 November</td></tr><tr><td>Thursday 17 December</td></tr></table><h2>2027 confirmed dates</h2><p>Thursday 4 February</p><h2>Monetary Policy Committee Reports and announcements</h2><p>Thursday 5 November</p>'
        events=parse_boe(text);self.assertEqual(len(events),3);self.assertEqual(events[0]['date'],'2026-11-05');self.assertEqual(events[0]['timezone'],'data sem horário');self.assertIsNone(events[0]['result'])
    def test_changed_format_and_inconsistent_weekday_fail_safely(self):
        for html in ['<h1>No confirmed calendar</h1>','<h2>2026 confirmed dates</h2><p>Monday 5 November</p>']:
            with self.assertRaises(ValueError):parse_boe(html)
    def test_partial_source_outage_keeps_success_explicit(self):
        event={'id':'one','date':'2026-11-05','source_id':'boe'}
        with patch('backend.calendar.fetch_bls',side_effect=TimeoutError()),patch('backend.calendar.fetch_boe',return_value=[event]):
            result=fetch_calendar();self.assertTrue(result['partial']);self.assertEqual(result['events'],[event]);self.assertEqual(result['sources'][0]['status'],'unavailable');self.assertEqual(result['sources'][1]['status'],'ok')
    def test_all_sources_unavailable_does_not_replace_cache_with_empty_success(self):
        with patch('backend.calendar.fetch_bls',side_effect=TimeoutError()),patch('backend.calendar.fetch_boe',side_effect=TimeoutError()):
            with self.assertRaises(RuntimeError):fetch_calendar()
    def test_calendar_adapter_migration_releases_old_backoff_without_clearing_active_lease(self):
        import tempfile,time
        from pathlib import Path
        from backend.cache import Cache
        from backend.scheduler import reconcile_connectors
        with tempfile.TemporaryDirectory() as folder:
            cache=Cache(Path(folder)/'cache.db');owner=cache.claim('calendar');cache.finish('calendar',owner,86400,'old failure');reconcile_connectors(cache);self.assertEqual(cache.job('calendar')['next'],0)
            owner=cache.claim('calendar');cache.put('connector:calendar','old version');reconcile_connectors(cache);self.assertIsNone(cache.claim('calendar'))
