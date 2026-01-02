
import sys
import unittest
from unittest.mock import MagicMock, patch

# --- MOCKING STREAMLIT ---
# We must mock streamlit in sys.modules BEFORE importing app.py,
# because app.py has top-level calls to st.set_page_config, st.markdown, etc.

mock_st = MagicMock()

# Configure columns to return lists of mocks
def columns_side_effect(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()]

mock_st.columns.side_effect = columns_side_effect
# Configure tabs to return 4 mocks
mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
# Configure button to return False so blocks don't run
mock_st.button.return_value = False
# Configure text_input to return something non-empty for API key
mock_st.text_input.return_value = "dummy_key"
# Configure selectbox
mock_st.selectbox.return_value = "gemini-2.0-flash-exp"

# Configure session_state
class MockSessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = MockSessionState()

sys.modules["streamlit"] = mock_st

# --- MOCKING GOOGLE GENAI ---
# app.py calls genai.configure at top level
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai


# Now we can import app
sys.path.append(".")
import app

class TestCrawler(unittest.TestCase):
    def test_recursive_crawl_basics(self):
        """Test that crawler visits pages and respects limits."""

        # Mock responses using requests.Session
        with patch('requests.Session') as mock_session_cls:
            mock_session = mock_session_cls.return_value
            mock_session.__enter__.return_value = mock_session

            # Setup mock response side effects
            def side_effect(url, **kwargs):
                r = MagicMock()
                r.status_code = 200
                if url == "http://test.com":
                    # Link to p2
                    r.content = b"<html><title>Home</title><body><a href='/p2'>Link to P2</a></body></html>"
                elif url == "http://test.com/p2":
                    # Link to p3
                    r.content = b"<html><title>Page 2</title><body><a href='/p3'>Link to P3</a></body></html>"
                elif url == "http://test.com/p3":
                    r.content = b"<html><title>Page 3</title><body></body></html>"
                else:
                    r.content = b"<html><title>Other</title><body></body></html>"
                return r

            mock_session.get.side_effect = side_effect

            # Run crawler
            combined_text, site_structure, final_assets, global_stats = app.recursive_crawl("http://test.com", max_pages=3)

            # Verify results
            self.assertEqual(global_stats['pages'], 3)
            self.assertIn("http://test.com", site_structure)
            self.assertIn("http://test.com/p2", site_structure)
            self.assertIn("http://test.com/p3", site_structure)

            # Verify text accumulation
            self.assertIn("Home", combined_text)
            self.assertIn("Page 2", combined_text)
            self.assertIn("Page 3", combined_text)

            # Verify Session usage
            mock_session_cls.assert_called()
            self.assertEqual(mock_session.get.call_count, 3)

if __name__ == '__main__':
    unittest.main()
