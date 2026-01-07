
import sys
import unittest
from unittest.mock import MagicMock, patch

# --- MOCKING STREAMLIT & GENAI BEFORE IMPORT ---
# This is necessary because app.py has side effects at module level
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
mock_st.button.return_value = False
sys.modules["streamlit"] = mock_st

mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# Now we can safely import app
# We need to make sure we don't hit the `if not api_key: st.stop()` block
# We can do this by mocking st.text_input to return something
mock_st.text_input.return_value = "dummy_key"
mock_st.sidebar.text_input.return_value = "dummy_key"

import app

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.start_url = "http://example.com"
        self.html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <link rel="stylesheet" href="style.css">
                <link rel="icon" href="favicon.ico">
            </head>
            <body>
                <h1>Hello World</h1>
                <p>This is a test.</p>
                <a href="http://example.com/page2">Link</a>
                <img src="image.png">
                <button>Click</button>
            </body>
        </html>
        """

    @patch('app.requests.Session')
    def test_recursive_crawl_logic(self, mock_session_cls):
        # Setup mock session
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')

        mock_session.get.return_value = mock_response

        # Run the function
        combined_text, structure, assets, stats = app.recursive_crawl(self.start_url, max_pages=1)

        # Verify results
        self.assertIn("Hello World", combined_text)
        self.assertIn(self.start_url, structure)
        self.assertEqual(structure[self.start_url]["title"], "Test Page")
        self.assertEqual(stats["pages"], 1)
        self.assertEqual(stats["buttons"], 1)

        # Verify session.get was called (since requests.get is patched, but we are using session.get now)
        # Note: Since we are mocking requests package, we can't easily distinguish between requests.get and session.get
        # unless we mock Session class specifically. See next test.

    @patch('app.requests.Session')
    def test_recursive_crawl_uses_session(self, mock_session_cls):
        # Setup mock session
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # Mock the context manager behavior of Session
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')

        mock_session.get.return_value = mock_response

        # Run the function
        app.recursive_crawl(self.start_url, max_pages=1)

        # Verify Session was instantiated and used
        mock_session_cls.assert_called()
        mock_session.get.assert_called()

if __name__ == '__main__':
    unittest.main()
