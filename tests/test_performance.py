import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# --- MOCK SETUP START ---
st = MagicMock()

def columns_side_effect(spec, *args, **kwargs):
    if isinstance(spec, int):
        count = spec
    elif isinstance(spec, list):
        count = len(spec)
    else:
        count = 1
    return [MagicMock() for _ in range(count)]

st.columns.side_effect = columns_side_effect
st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
st.button.return_value = False
st.text_input.return_value = "test_key"

class MockSessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return MagicMock()
    def __setattr__(self, key, value):
        self[key] = value

st.session_state = MockSessionState()
sys.modules["streamlit"] = st
sys.modules["google.generativeai"] = MagicMock()
# --- MOCK SETUP END ---

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

class TestPerformance(unittest.TestCase):

    @patch('app.requests.Session')
    def test_recursive_crawl_uses_session(self, mock_session_cls):
        # Setup mock session and response
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        # Minimal HTML content
        mock_response.content = b"<html><head><title>Test</title></head><body><a href='http://test.com/page2'>link</a></body></html>"
        mock_session.get.return_value = mock_response

        # Call function
        app.recursive_crawl("http://test.com", max_pages=1)

        # Verify session was instantiated
        mock_session_cls.assert_called()

        # Verify session.get was called instead of requests.get
        mock_session.get.assert_called()

if __name__ == '__main__':
    unittest.main()
