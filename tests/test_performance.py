import sys
import time
import unittest
from unittest.mock import MagicMock, patch
import requests

# Mock streamlit before importing app
mock_st = MagicMock()

def columns_side_effect(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()]

mock_st.columns.side_effect = columns_side_effect
mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
mock_st.button.return_value = False
mock_st.text_input.return_value = "test"
sys.modules["streamlit"] = mock_st

# Mock google.generativeai
sys.modules["google.generativeai"] = MagicMock()

# Now import app
import app

class TestPerformance(unittest.TestCase):
    def test_string_concatenation_performance(self):
        # We will mock requests.get to return a large content instantly
        # This focuses the benchmark on the string processing part

        large_content = "word " * 5000 # ~25KB text
        # Add links to ensure queue doesn't empty
        # We need to ensure that the crawler finds new URLs to add to the queue
        # The crawler checks: if full_url not in visited and full_url not in queue:
        # Since we use the same response for every request, we need a way to generate new URLs?
        # Actually, the logic is:
        # for link in soup.find_all('a', href=True):
        #    href = link['href']
        #    full_url = urljoin(url, href)

        # If the response is static, it will always return the same links.
        # So we need to ensure the links are unique enough or just enough of them?
        # If page 1 has links to page 2, 3. Page 2 has links to page 4, 5.

        # Simulating this with a static response is hard because all pages will look identical and have same links.
        # But wait, if page 1 returns links to "page2", "page3".
        # Then "page2" is popped. It returns links to "page2", "page3".
        # "page2" is visited. "page3" is in queue.
        # So we won't discover NEW pages after the first batch.

        # We need dynamic response or just enough links in the first page to fill the queue?
        # No, it's BFS.

        # Let's use side_effect for requests.get to return different content or just allow a huge queue from start?
        # No, queue starts with [start_url].

        # Easiest: The response includes links to http://example.com/{random_uuid}.
        # But if response is static...

        # We can use side_effect to generate unique links based on the requested URL or just a counter?

        # Or simpler: Just ensure the first page returns 1000 links.
        # Then the queue has 1000 items.
        # The loop runs `while queue and count < max_pages`.
        # Even if subsequent pages have no links (or visited links), the queue has 1000 items from the start.
        # That works!

        links = "".join([f"<a href='/page_{i}'>link_{i}</a>" for i in range(1000)])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = f"<html><body>{large_content}{links}</body></html>".encode('utf-8')

        # Mock st functions used in recursive_crawl
        app.st.progress = MagicMock()
        app.st.empty = MagicMock()

        # Mock time.sleep to run fast
        with patch('time.sleep', return_value=None):
            # Patch requests.Session to return a mock session
            with patch('requests.Session') as mock_session_cls:
                mock_session = mock_session_cls.return_value
                mock_session.__enter__.return_value = mock_session
                mock_session.get.return_value = mock_response

                start_time = time.time()
                # Run for 200 pages.
                # (1000 links in queue is enough for 200 pages)
                app.recursive_crawl("http://example.com", max_pages=200)
                duration = time.time() - start_time
                print(f"\n[Benchmark] Recursive crawl (200 pages, large content) took: {duration:.4f}s")

if __name__ == "__main__":
    unittest.main()
