import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
mock_st = MagicMock()
# Ensure st.tabs returns 4 values
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
# Ensure st.columns returns 2 values
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.columns.side_effect = lambda x: [MagicMock() for _ in range(x)] if isinstance(x, int) else [MagicMock() for _ in x]
# Prevent buttons from triggering actions during import
mock_st.button.return_value = False
mock_st.chat_input.return_value = False
mock_st.file_uploader.return_value = None

sys.modules["streamlit"] = mock_st

# Mock google.generativeai
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# Import the app module
import app

class TestAppPerformance(unittest.TestCase):
    @patch('app.requests')
    def test_recursive_crawl_uses_session(self, mock_requests):
        """
        Verifies that recursive_crawl uses a requests.Session for connection reuse.
        """
        # Setup the mock session
        mock_session = MagicMock()
        # requests.Session() returns a context manager, so we mock __enter__
        mock_requests.Session.return_value.__enter__.return_value = mock_session

        # Setup a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><title>Test</title></head><body><a href='p2'>Link</a></body></html>"

        # Configure the session.get to return our mock response
        mock_session.get.return_value = mock_response

        # Configure requests.get to also return response (for the unoptimized version)
        mock_requests.get.return_value = mock_response

        # Call the function
        app.recursive_crawl("http://example.com", max_pages=1)

        # Assert that Session() was instantiated and used
        # This is expected to FAIL before the optimization
        mock_requests.Session.assert_called()
        mock_session.get.assert_called()

if __name__ == '__main__':
    unittest.main()
