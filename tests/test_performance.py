import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# --- MOCKING STREAMLIT & GENAI ---
st_mock = MagicMock()

# Helper for st.columns and st.tabs
def mock_unpackable(spec, *args, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

st_mock.columns.side_effect = mock_unpackable
st_mock.tabs.side_effect = mock_unpackable

# Important: st.button must return False to prevent execution of button-click logic on import
st_mock.button.return_value = False

# st.text_input should return a string so it can be used as a dict key
st_mock.text_input.return_value = "mock_api_key"

# Session state needs to support dot access AND dict-like 'in' checks
class SessionStateMock(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

st_mock.session_state = SessionStateMock()

sys.modules["streamlit"] = st_mock
sys.modules["google.generativeai"] = MagicMock()

# --- IMPORT APP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.start_url = "http://example.com"
        self.html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <p>Hello world of optimization</p>
                <a href="http://example.com/page2">Link</a>
                <button>Click Me</button>
            </body>
        </html>
        """

    @patch('requests.Session')
    def test_recursive_crawl_logic(self, mock_session_cls):
        """
        Verify that recursive_crawl works correctly with mocked requests using Session.
        """
        # Setup mock session and response
        mock_session = mock_session_cls.return_value
        # Mocking context manager behavior if needed, though app.py doesn't use 'with session:' yet
        # But if we want to be safe for future:
        mock_session.__enter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')

        # Configure session.get to return the response
        mock_session.get.return_value = mock_response

        # Run crawl
        combined_text, structure, assets, global_stats = app.recursive_crawl(self.start_url, max_pages=1)

        # Assertions
        self.assertIn("Hello world of optimization", combined_text)
        self.assertIn("Test Page", structure[self.start_url]['title'])
        self.assertEqual(global_stats['buttons'], 1)
        self.assertEqual(global_stats['links'], 1)
        self.assertEqual(global_stats['words'], 9)

        # Verify Session was instantiated and used
        self.assertTrue(mock_session_cls.called, "requests.Session() was not instantiated")
        self.assertTrue(mock_session.get.called, "session.get() was not called")

if __name__ == '__main__':
    unittest.main()
