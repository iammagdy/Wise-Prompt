import app
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
mock_st = MagicMock()


def columns_side_effect(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()]


mock_st.columns.side_effect = columns_side_effect
mock_st.tabs.return_value = [
    MagicMock(), MagicMock(), MagicMock(), MagicMock()]
mock_st.button.return_value = False
mock_st.text_input.return_value = "dummy_key"
sys.modules["streamlit"] = mock_st

# Mock google.generativeai
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# Now import app


class TestPerformance(unittest.TestCase):
    @patch('requests.Session')
    def test_recursive_crawl_uses_session(self, mock_session_cls):
        """Test that the implementation now uses requests.Session."""
        # Setup mock session
        mock_session_instance = mock_session_cls.return_value
        mock_session_instance.__enter__.return_value = mock_session_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><title>Test</title></head><body><a href='http://example.com/2'>Link</a></body></html>"
        mock_session_instance.get.return_value = mock_response

        # Run crawl
        text, structure, assets, stats = app.recursive_crawl(
            "http://example.com", max_pages=2)

        # Verify Session was used
        self.assertTrue(mock_session_cls.called,
                        "requests.Session() should be called")
        self.assertTrue(mock_session_instance.get.called,
                        "session.get() should be called")

        # Verify result structure (basic check)
        self.assertIsInstance(text, str)
        self.assertIn("--- PAGE: Test", text)
        self.assertEqual(stats["pages"], 2)


if __name__ == '__main__':
    unittest.main()
