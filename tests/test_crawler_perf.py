
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
# Ensure buttons return False so we don't trigger actions on import
mock_st.button.return_value = False
# Ensure text inputs return a string so parsing doesn't fail if called
mock_st.text_input.return_value = "http://example.com"
mock_st.selectbox.return_value = "gemini-pro"

sys.modules["streamlit"] = mock_st

# Add current directory to path so we can import app
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app
import requests

class TestCrawler(unittest.TestCase):
    @patch('app.requests.Session')
    def test_recursive_crawl(self, mock_session_cls):
        # Setup mock session
        mock_session = mock_session_cls.return_value

        # Mock responses
        def side_effect(url, headers=None, timeout=None):
            response = MagicMock()
            response.status_code = 200

            if "example.com" in url and "page1" not in url:
                content = """
                <html>
                    <head><title>Home</title></head>
                    <body>
                        <a href="page1">Page 1</a>
                        <a href="http://external.com">External</a>
                    </body>
                </html>
                """
            elif "page1" in url:
                content = """
                <html>
                    <head><title>Page 1</title></head>
                    <body>
                        <p>Content of page 1</p>
                    </body>
                </html>
                """
            else:
                content = "<html></html>"

            response.content = content.encode('utf-8')
            return response

        mock_session.get.side_effect = side_effect

        # Run crawler
        text, structure, assets, stats = app.recursive_crawl("http://example.com", max_pages=2)

        # Verify
        self.assertEqual(stats['pages'], 2)
        self.assertIn("Home", text)
        self.assertIn("Page 1", text)

        # Check that we called session.get twice
        self.assertEqual(mock_session.get.call_count, 2)

if __name__ == '__main__':
    unittest.main()
