import sys
import unittest
from unittest.mock import MagicMock
import requests

# Mock Streamlit and other dependencies that might cause side effects on import
mock_streamlit = MagicMock()
mock_streamlit.progress.return_value = MagicMock()
mock_streamlit.empty.return_value = MagicMock()

def columns_side_effect(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()] # Default fallback

mock_streamlit.columns.side_effect = columns_side_effect
mock_streamlit.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
mock_streamlit.set_page_config = MagicMock()
mock_streamlit.markdown = MagicMock()
mock_streamlit.title = MagicMock()
mock_streamlit.header = MagicMock()
mock_streamlit.caption = MagicMock()
mock_streamlit.divider = MagicMock()
mock_streamlit.text_input.return_value = "dummy_key"
mock_streamlit.selectbox.return_value = "gemini-pro"
mock_streamlit.sidebar = MagicMock()
mock_streamlit.sidebar.__enter__.return_value = MagicMock()
mock_streamlit.button.return_value = False # Avoid triggering logic
mock_streamlit.session_state = MagicMock()

# Mock Google Generative AI
mock_genai = MagicMock()

sys.modules['streamlit'] = mock_streamlit
sys.modules['google.generativeai'] = mock_genai

# Add project root to path
sys.path.append(".")

# Now import the app
from app import recursive_crawl

class TestPerformance(unittest.TestCase):
    def setUp(self):
        # Create a large dummy response content
        self.dummy_html = """
        <html>
            <head>
                <title>Test Page</title>
                <link href="styles.css" rel="stylesheet">
                <script src="script.js"></script>
            </head>
            <body>
                <h1>Welcome to the test page</h1>
                <p>This is some content that will be repeated to make it large.</p>
                """ + "<p>More content here to simulate a real page.</p>" * 100 + """
                <a href="page1.html">Link 1</a>
                <a href="page2.html">Link 2</a>
                <img src="image1.png">
                <button>Click me</button>
            </body>
        </html>
        """
        self.requests_count = 0

    def mock_get_dynamic(self, url, headers=None, timeout=None):
        self.requests_count += 1
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Generate unique links to keep the queue full
        unique_id = self.requests_count
        new_links = f"""
        <a href="http://example.com/page{unique_id}_a.html">Link A</a>
        <a href="http://example.com/page{unique_id}_b.html">Link B</a>
        """

        content = self.dummy_html + new_links
        mock_response.content = content.encode('utf-8')
        mock_response.text = content
        return mock_response

    def test_recursive_crawl_performance(self):
        import time
        start_time = time.time()

        # Mock Session
        with unittest.mock.patch('requests.Session') as MockSession:
            mock_session_instance = MockSession.return_value
            mock_session_instance.__enter__.return_value = mock_session_instance
            mock_session_instance.get.side_effect = self.mock_get_dynamic

            with unittest.mock.patch('time.sleep', return_value=None):
                crawled_text, structure, assets, stats = recursive_crawl("http://example.com", max_pages=50)

        end_time = time.time()
        duration = end_time - start_time

        print(f"Time taken to crawl {stats['pages']} pages (simulated): {duration:.4f} seconds")
        print(f"Total requests: {self.requests_count}")

        # Verify it actually did something
        self.assertGreater(stats['pages'], 0)
        self.assertGreater(len(crawled_text), 1000)

if __name__ == '__main__':
    unittest.main()
