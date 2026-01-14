import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
mock_st = MagicMock()

def mock_columns(spec):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = mock_columns
mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
mock_st.button.return_value = False
mock_st.text_input.return_value = "dummy_key"
mock_st.session_state = MagicMock()

# Mock google.generativeai
sys.modules["streamlit"] = mock_st
sys.modules["google.generativeai"] = MagicMock()

# Import app
import app

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.start_url = "http://example.com"
        self.html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="http://example.com/page1">Link 1</a>
                <a href="http://example.com/page2">Link 2</a>
                <button>Click me</button>
                <img src="image.jpg">
                <p>Some text content here.</p>
            </body>
        </html>
        """

    @patch('requests.Session')
    def test_recursive_crawl_performance(self, mock_session_cls):
        # Setup mock session
        mock_session = mock_session_cls.return_value
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')
        mock_session.get.return_value = mock_response

        # Measure time
        start_time = time.time()

        # Run crawl with max_pages=50 to simulate load
        # We mock requests so it won't actually hit network,
        # but string concatenation logic will run.
        app.recursive_crawl(self.start_url, max_pages=50)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nExecution time for 50 pages: {duration:.4f} seconds")

        # Verify it actually ran
        self.assertGreaterEqual(mock_session.get.call_count, 1)

    @patch('requests.Session')
    def test_session_usage(self, mock_session_cls):
        # This test checks if requests.Session is used
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.html_content.encode('utf-8')
        mock_session.get.return_value = mock_response

        # Mocking __enter__ and __exit__ for context manager support
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None

        # We also need to patch requests.get in case the implementation still uses it
        with patch('requests.get') as mock_get:
            app.recursive_crawl(self.start_url, max_pages=1)

            if mock_session.get.called:
                print("\n✅ requests.Session() is being used!")
            else:
                print("\n❌ requests.Session() is NOT being used yet.")

if __name__ == '__main__':
    unittest.main()
