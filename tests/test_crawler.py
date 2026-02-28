import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit before importing app
mock_st = MagicMock()
mock_st.progress.return_value = MagicMock()
mock_st.empty.return_value = MagicMock()
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
def side_effect_columns(args, **kwargs):
    if isinstance(args, list):
        return [MagicMock() for _ in args]
    if isinstance(args, int):
        return [MagicMock() for _ in range(args)]
    return [MagicMock(), MagicMock()]
mock_st.columns.side_effect = side_effect_columns

mock_st.text_input.return_value = "dummy"
mock_st.button.return_value = False # Prevent main loop logic from running at import time

class MockSessionState(dict):
    def __getattr__(self, item):
        return self.get(item)
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = MockSessionState()
mock_st.chat_input.return_value = None

sys.modules['streamlit'] = mock_st

# Mock google before importing app
mock_google = MagicMock()
sys.modules['google'] = mock_google
sys.modules['google.generativeai'] = MagicMock()

import app

class TestCrawler(unittest.TestCase):
    @patch('app.time.sleep', return_value=None)
    @patch('app.requests.get')
    def test_recursive_crawl_basic(self, mock_get, mock_sleep):
        # Mocking 2 pages
        page1 = b"<html><head><title>Page 1</title></head><body><a href='/page2'>Link</a><button>Btn</button></body></html>"
        page2 = b"<html><head><title>Page 2</title></head><body><p>Hello world</p><img src='img.png'></body></html>"

        def side_effect(url, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if url == 'http://example.com':
                mock_response.content = page1
            elif url == 'http://example.com/page2':
                mock_response.content = page2
            else:
                mock_response.status_code = 404
            return mock_response

        mock_get.side_effect = side_effect

        combined_text, site_structure, assets, stats = app.recursive_crawl('http://example.com', max_pages=5)

        self.assertEqual(stats['pages'], 2)
        self.assertEqual(stats['buttons'], 1)
        self.assertEqual(stats['links'], 1)
        self.assertEqual(stats['images'], 1)

        self.assertIn('http://example.com', site_structure)
        self.assertIn('http://example.com/page2', site_structure)

if __name__ == '__main__':
    unittest.main()
