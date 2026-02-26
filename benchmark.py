
import sys
import time
from unittest.mock import MagicMock
import json

# Create a custom mock for streamlit
st_mock = MagicMock()

# Setup side effects for unpacking
def tabs_side_effect(names):
    return [MagicMock() for _ in names]

def columns_side_effect(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in spec]
    else:
        return [MagicMock(), MagicMock()] # Fallback

st_mock.tabs.side_effect = tabs_side_effect
st_mock.columns.side_effect = columns_side_effect
st_mock.sidebar.__enter__.return_value = MagicMock()

# Mock text_input to avoid early termination if app logic checks return value
st_mock.text_input.return_value = "dummy_api_key"
st_mock.button.return_value = False
st_mock.chat_input.return_value = None

class SessionStateMock(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

st_mock.session_state = SessionStateMock()

sys.modules['streamlit'] = st_mock
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

import builtins
original_open = builtins.open
def mock_open(file, mode='r', *args, **kwargs):
    if "god_mode_history.json" in str(file):
        if 'r' in mode:
            m = MagicMock()
            m.__enter__.return_value.read.return_value = "{}"
            m.read.return_value = "{}"
            return m
        else:
            m = MagicMock()
            return m
    return original_open(file, mode, *args, **kwargs)

builtins.open = mock_open

try:
    import app
except Exception as e:
    print(f"Error importing app: {e}")
    pass
finally:
    builtins.open = original_open

import requests
from urllib.parse import urlparse

# --- Benchmark Setup ---

NUM_LINKS_PER_PAGE = 200  # More links per page to bloat the queue faster
MAX_PAGES = 500           # More pages to visit

class MockResponse:
    def __init__(self, url):
        self.status_code = 200
        self.url = url
        self._content = self._generate_content(url)

    @property
    def content(self):
        return self._content

    def _generate_content(self, url):
        links_html = []
        base_url = "http://example.com"
        import hashlib
        for i in range(NUM_LINKS_PER_PAGE):
            unique_str = f"{url}-{i}"
            h = hashlib.md5(unique_str.encode()).hexdigest()[:8]
            new_url = f"{base_url}/page/{h}"
            links_html.append(f'<a href="{new_url}">Link {i}</a>')

        html = f"""
        <html>
            <head><title>Mock Page {url}</title></head>
            <body>
                <p>Some content here.</p>
                {''.join(links_html)}
            </body>
        </html>
        """
        return html.encode('utf-8')

def mock_requests_get(url, headers=None, timeout=None):
    return MockResponse(url)

app.requests.get = mock_requests_get
app.time.sleep = lambda x: None

def run_benchmark():
    print("Starting benchmark with heavy load...")
    start_time = time.time()
    try:
        app.recursive_crawl("http://example.com", max_pages=MAX_PAGES)
    except Exception as e:
        print(f"Crawler failed: {e}")
        import traceback
        traceback.print_exc()

    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken: {duration:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
