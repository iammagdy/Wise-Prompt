import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. Mock streamlit
st_mock = MagicMock()
# Configure tabs to return 4 mocks
st_mock.tabs.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())
# Configure text_input to return a key so st.stop() isn't called
st_mock.text_input.return_value = "test_key"
st_mock.button.return_value = False
st_mock.chat_input.return_value = None

# Configure columns
def mock_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()] # Fallback

st_mock.columns.side_effect = mock_columns

class SessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

st_mock.session_state = SessionState()

sys.modules['streamlit'] = st_mock

# 2. Mock google and google.generativeai
google_mock = MagicMock()
sys.modules['google'] = google_mock
genai_mock = MagicMock()
sys.modules['google.generativeai'] = genai_mock
google_mock.generativeai = genai_mock

# 3. Mock builtins.open
with patch('builtins.open', MagicMock()):
    try:
        import app
    except ImportError as e:
        print(f"Import failed: {e}")
    except Exception as e:
        print(f"App execution warning: {e}")

class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.start_url = "http://example.com"

    @patch('app.requests.get')
    def test_recursive_crawl_structure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <a href="http://example.com/page2">Link 1</a>
                    <a href="http://example.com">Self Link</a>
                    <button>Click me</button>
                    <script src="script.js"></script>
                </body>
            </html>
        """
        mock_get.return_value = mock_response

        with patch('app.time.sleep'):
            full_text, structure, assets, stats = app.recursive_crawl(self.start_url, max_pages=2)

        self.assertIn(self.start_url, structure)
        self.assertEqual(structure[self.start_url]['title'], "Test Page")
        # Should be 2 because mock returns new links for every page (we didn't vary content based on URL)
        # But wait, we are returning SAME content for ALL URLs.
        # So page2 will have link to page2 and start_url.
        # queue logic:
        # 1. Start URL. Pop.
        # 2. Add page2.
        # 3. Pop page2.
        # 4. Find page2 (visited), start_url (visited). No new links.
        # So queue empty.
        self.assertEqual(stats['pages'], 2)

    @patch('app.requests.get')
    def test_queue_optimization(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html></html>"
        mock_get.return_value = mock_response

        with patch('app.time.sleep'):
            full_text, structure, assets, stats = app.recursive_crawl(self.start_url, max_pages=5)

        self.assertEqual(stats['pages'], 1)

if __name__ == '__main__':
    unittest.main()
