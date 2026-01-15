
import unittest
from unittest.mock import MagicMock, patch
import sys
import time

# --- MOCK STREAMLIT ---
# We need to mock streamlit before importing app, because app.py has top-level st calls.
mock_st = MagicMock()

def side_effect_columns(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()] # Fallback

def side_effect_tabs(spec):
    return [MagicMock() for _ in range(len(spec))]

mock_st.columns.side_effect = side_effect_columns
mock_st.tabs.side_effect = side_effect_tabs
mock_st.button.return_value = False # Default button state
mock_st.text_input.return_value = "dummy" # Default text input
mock_st.session_state = MagicMock() # Needs to be an object for attribute access
sys.modules["streamlit"] = mock_st

# --- MOCK GOOGLE GENERATIVE AI ---
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# --- IMPORT APP ---
# Now we can safely import the app (which will run the top-level code but against mocks)
try:
    import app
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

# --- REPRODUCTION SCRIPT ---

class TestPerformance(unittest.TestCase):
    def test_recursive_crawl_performance(self):
        """
        Benchmarks recursive_crawl logic (excluding network latency via mocks).
        """

        # Mock requests.get to return a dummy response instantly
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            # A moderate HTML content to parse
            html_content = """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <p>Some text content here.</p>
                    <a href="http://example.com/page1">Link 1</a>
                    <a href="http://example.com/page2">Link 2</a>
                    <button>Click me</button>
                    <img src="image.png" />
                </body>
            </html>
            """
            mock_response.content = html_content.encode('utf-8')
            mock_get.return_value = mock_response

            # Run the crawler
            start_time = time.time()
            # Crawl 50 pages (mocked)
            # We mock time.sleep to avoid waiting 0.3s per page
            with patch('time.sleep'):
                 app.recursive_crawl("http://example.com", max_pages=50)

            end_time = time.time()
            duration = end_time - start_time
            print(f"Crawled 50 pages (mocked) in {duration:.4f} seconds")

if __name__ == "__main__":
    unittest.main()
