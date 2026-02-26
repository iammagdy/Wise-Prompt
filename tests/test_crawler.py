
import sys
import unittest
import os
from unittest.mock import MagicMock
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Mocking Setup ---
st_mock = MagicMock()
st_mock.tabs.side_effect = lambda n: [MagicMock() for _ in n]
st_mock.columns.side_effect = lambda s: [MagicMock() for _ in range(s if isinstance(s, int) else len(s))] if isinstance(s, (int, list)) else [MagicMock(), MagicMock()]
st_mock.sidebar.__enter__.return_value = MagicMock()
st_mock.text_input.return_value = "dummy_api_key"
st_mock.button.return_value = False
st_mock.chat_input.return_value = None
st_mock.session_state = MagicMock()

sys.modules['streamlit'] = st_mock
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

import builtins
original_open = builtins.open
builtins.open = MagicMock()

try:
    import app
except Exception as e:
    print(f"Error importing app: {e}")
finally:
    builtins.open = original_open

import requests

class TestCrawler(unittest.TestCase):
    def test_recursive_crawl_structure(self):
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="/page2">Link to Page 2</a>
                <img src="logo.png" />
            </body>
        </html>
        """

        def side_effect(url, headers=None, timeout=None):
            resp = MagicMock()
            resp.status_code = 200
            if "page2" in url:
                resp.content = b"<html><body>Page 2</body></html>"
            else:
                resp.content = html_content.encode('utf-8')
            return resp

        # Patch the requests module used by app
        app.requests.get = MagicMock(side_effect=side_effect)
        app.time.sleep = MagicMock()

        combined_text, site_structure, assets, stats = app.recursive_crawl("http://example.com", max_pages=5)

        expected_img = "http://example.com/logo.png"
        self.assertIn(expected_img, assets['icons'])

if __name__ == '__main__':
    unittest.main()
