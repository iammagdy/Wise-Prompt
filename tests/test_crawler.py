
import unittest
import sys
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit"].tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
sys.modules["streamlit"].columns.side_effect = lambda x: [MagicMock() for _ in range(x)] if isinstance(x, int) else [MagicMock() for _ in x]
sys.modules["streamlit"].button.return_value = False
# Mock session state to be accessible
sys.modules["streamlit"].session_state = MagicMock()

# Import app
import app

class TestCrawler(unittest.TestCase):
    def test_recursive_crawl(self):
        # Mock requests.Session
        with patch("app.requests.Session") as mock_session_cls:
            mock_session = mock_session_cls.return_value
            # Make the session context manager work if used (though implementation might not use context manager yet, it's good practice)
            mock_session.__enter__.return_value = mock_session

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"<html><head><title>Test Page</title></head><body><p>Hello World</p><a href='/page2'>Link</a></body></html>"
            mock_session.get.return_value = mock_response

            # Mock st.empty and st.progress
            app.st.empty.return_value = MagicMock()
            app.st.progress.return_value = MagicMock()

            # Run crawl
            text, structure, assets, stats = app.recursive_crawl("http://example.com", max_pages=1)

            # Assertions
            self.assertIn("Test Page", text)
            self.assertEqual(stats["pages"], 1)
            # Verify session.get was called
            self.assertTrue(mock_session.get.called)

if __name__ == '__main__':
    unittest.main()
