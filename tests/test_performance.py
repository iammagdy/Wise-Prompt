import unittest
from unittest.mock import MagicMock, patch
import sys
import time

# Mock streamlit and google.generativeai before importing app
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st
sys.modules['google.generativeai'] = MagicMock()

# Handle st.columns for different call sites
def columns_side_effect(spec):
    if isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    return [MagicMock(), MagicMock()] # Fallback

mock_st.columns.side_effect = columns_side_effect

# Handle st.tabs
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

mock_st.button.return_value = False
mock_st.text_input.return_value = "dummy_key"
mock_st.session_state = MagicMock()

# Import the app module
import app

class TestRecursiveCrawlPerformance(unittest.TestCase):
    def setUp(self):
        self.url = "http://example.com"
        self.html_content = "<html><body>" + "<p>word </p>" * 1000 + "<a href='http://example.com/page{i}'>link</a>" * 10 + "</body></html>"
        self.max_pages = 50

    @patch('app.requests.Session')
    def test_recursive_crawl_performance(self, mock_session_cls):
        # Create a mock session instance
        mock_session = mock_session_cls.return_value

        # Make the session context manager return itself
        mock_session.__enter__.return_value = mock_session

        # Mock the get method of the session instance
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')
        mock_session.get.return_value = mock_response

        # Mock streamlit components used in the function
        app.st.progress = MagicMock()
        app.st.empty = MagicMock()

        start_time = time.time()
        app.recursive_crawl(self.url, max_pages=self.max_pages)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nPerformance Test - Duration: {duration:.4f} seconds for {self.max_pages} pages")

if __name__ == '__main__':
    unittest.main()
