
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit"].set_page_config = MagicMock()
sys.modules["streamlit"].markdown = MagicMock()
sys.modules["streamlit"].sidebar = MagicMock()
sys.modules["streamlit"].title = MagicMock()
sys.modules["streamlit"].tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
sys.modules["streamlit"].text_input = MagicMock()
sys.modules["streamlit"].selectbox = MagicMock()
sys.modules["streamlit"].button = MagicMock(return_value=False)
sys.modules["streamlit"].progress = MagicMock()
sys.modules["streamlit"].empty = MagicMock()

# Correctly mock st.columns
def mock_columns(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

sys.modules["streamlit"].columns = MagicMock(side_effect=mock_columns)

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import recursive_crawl

class TestRecursiveCrawl(unittest.TestCase):
    @patch("requests.Session")
    def test_recursive_crawl_structure(self, mock_session_cls):
        # Setup mock session
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><title>Test Page</title></head><body><p>Hello World</p><a href='/page2'>Link</a></body></html>"
        mock_session.get.return_value = mock_response

        # Enter context manager
        mock_session.__enter__.return_value = mock_session

        # Call the function
        start_url = "http://example.com"
        combined_text, site_structure, final_assets, global_stats = recursive_crawl(start_url, max_pages=1)

        # Assert requests.Session.get was called
        mock_session.get.assert_called()
        self.assertIn("Test Page", combined_text)

    @patch("requests.Session")
    def test_recursive_crawl_uses_session(self, mock_session_cls):
        # Setup mock session
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><p>Content</p></body></html>"
        mock_session.get.return_value = mock_response
        mock_session.__enter__.return_value = mock_session

        # Verify requests.get is NOT called
        with patch("requests.get") as mock_get:
            start_url = "http://example.com"
            recursive_crawl(start_url, max_pages=1)
            mock_get.assert_not_called()

        # Verify session.get IS called
        mock_session.get.assert_called()

if __name__ == "__main__":
    unittest.main()
