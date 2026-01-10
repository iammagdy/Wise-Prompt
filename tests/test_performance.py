import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock streamlit before importing app
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()] # Default 4 columns
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
mock_st.button.return_value = False
mock_st.text_input.return_value = "dummy_key" # Ensure api_key is truthy to pass the check
mock_st.sidebar = MagicMock()
mock_st.sidebar.__enter__ = MagicMock(return_value=mock_st.sidebar)
mock_st.sidebar.__exit__ = MagicMock(return_value=None)
mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
mock_st.container.return_value.__exit__ = MagicMock(return_value=None)

# Fix st.columns to return dynamic list based on input or just a list that can be unpacked
def mock_columns(spec):
    if isinstance(spec, list):
        count = len(spec)
    elif isinstance(spec, int):
        count = spec
    else:
        count = 1
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = mock_columns

sys.modules['streamlit'] = mock_st

# Mock google.generativeai
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

# Add current directory to path
sys.path.append(os.getcwd())

import app

class TestPerformance(unittest.TestCase):
    @patch('app.requests.Session')
    @patch('app.requests.get')
    def test_recursive_crawl_optimization(self, mock_get, mock_session_cls):
        # Setup mock session
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # Configure context manager
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><a href='http://example.com/2'>link</a></body></html>"
        mock_session.get.return_value = mock_response

        # Setup mock_get for the unoptimized version
        mock_get.return_value = mock_response

        # Run the function
        # We use a small max_pages to avoid long loops
        app.recursive_crawl("http://example.com", max_pages=1)

        # Verification
        if not mock_session_cls.called:
             print("\nFAIL: requests.Session() was not instantiated.")
        if not mock_session.get.called:
             print("\nFAIL: session.get() was not called.")
        if mock_get.called:
             print("\nFAIL: requests.get() was called (should use session).")

        self.assertTrue(mock_session_cls.called, "requests.Session() should be instantiated for connection pooling")
        self.assertTrue(mock_session.get.called, "session.get() should be used instead of requests.get()")
        self.assertFalse(mock_get.called, "requests.get() should NOT be used directly when a session is available")

if __name__ == '__main__':
    unittest.main()
