import time
import urllib.parse
from collections import deque
from urllib.parse import urlparse, urljoin
import sys

# Mock setup
class MockSoup:
    def __init__(self, num_links):
        self.num_links = num_links

    def find_all(self, tag, **kwargs):
        if tag == 'a':
            return [{'href': f'/page{i}'} for i in range(self.num_links)]
        return []

def benchmark_original(num_pages, links_per_page):
    visited = set()
    queue = ["http://example.com/start"]
    base_domain = "example.com"
    count = 0

    start_time = time.time()

    while queue and count < num_pages:
        url = queue.pop(0)
        if url in visited: continue

        visited.add(url)
        count += 1

        # Simulate link parsing
        soup = MockSoup(links_per_page)
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == base_domain and full_url not in visited and full_url not in queue:
                queue.append(full_url)

    return time.time() - start_time

def benchmark_optimized(num_pages, links_per_page):
    visited = set()
    queue = deque(["http://example.com/start"])
    queued_urls = {"http://example.com/start"}
    base_domain = "example.com"
    count = 0

    start_time = time.time()

    while queue and count < num_pages:
        url = queue.popleft()
        if url in visited: continue

        visited.add(url)
        count += 1

        # Simulate link parsing
        soup = MockSoup(links_per_page)
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if full_url not in visited and full_url not in queued_urls:
                if urlparse(full_url).netloc == base_domain:
                    queue.append(full_url)
                    queued_urls.add(full_url)

    return time.time() - start_time

if __name__ == "__main__":
    print("Running benchmarks...")
    orig_time = benchmark_original(100, 2000)
    print(f"Original Time: {orig_time:.4f}s")

    opt_time = benchmark_optimized(100, 2000)
    print(f"Optimized Time: {opt_time:.4f}s")
