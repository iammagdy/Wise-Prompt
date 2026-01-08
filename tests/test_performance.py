import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock libraries before import
st_mock = MagicMock()

# Handle st.columns unpacking
def mock_columns(spec):
    # spec can be int or list of ints/ratios
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    else:
        # if list, return equal number of mocks
        return [MagicMock() for _ in range(len(spec))]

st_mock.columns.side_effect = mock_columns
st_mock.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
st_mock.button.return_value = False
st_mock.text_input.return_value = "dummy_key"

sys.modules["streamlit"] = st_mock
sys.modules["google.generativeai"] = MagicMock()

import app

class TestPerformance(unittest.TestCase):
    @patch('app.requests.Session')
    def test_recursive_crawl_uses_session(self, mock_session_cls):
        """Verify that recursive_crawl uses a session for requests."""
        # Setup mock session
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><p>hello</p></body></html>"
        mock_session.get.return_value = mock_response

        # Configure the context manager behavior for Session
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        # We also need to mock requests.get just in case it's still used,
        # but we want to fail if it IS used instead of session.
        with patch('app.requests.get') as mock_requests_get:
            mock_requests_get.return_value = mock_response

            # Execute
            app.recursive_crawl("http://example.com", max_pages=1)

            # Verify
            # For the RED phase (before optimization), we expect this test to FAIL
            # because the code uses requests.get, not Session.

            # Assert Session was instantiated
            if mock_session_cls.call_count == 0:
                 self.fail("requests.Session() was not instantiated! Optimization missing.")

            mock_session_cls.assert_called()
            # Assert session.get was called
            mock_session.get.assert_called()
            # Assert requests.get was NOT called
            mock_requests_get.assert_not_called()

if __name__ == '__main__':
    unittest.main()
