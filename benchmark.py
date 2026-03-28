import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import collections

# Mock HTML with many links
html = "<html><body>"
for i in range(1000):
    html += f"<a href='http://example.com/page{i}'>Link</a>"
    html += f"<a href='http://other.com/page{i}'>Link</a>"
html += "</body></html>"
soup = BeautifulSoup(html, 'html.parser')
url = "http://example.com"
base_domain = "example.com"

def original():
    visited = set()
    queue = ["http://example.com"]
    start = time.time()
    for _ in range(50):
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == base_domain and full_url not in visited and full_url not in queue:
                queue.append(full_url)
    return time.time() - start

def optimized():
    visited = set()
    queue = collections.deque(["http://example.com"])
    queued_urls = set(["http://example.com"])
    start = time.time()
    for _ in range(50):
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            # Fast checks first
            if full_url not in visited and full_url not in queued_urls:
                if urlparse(full_url).netloc == base_domain:
                    queue.append(full_url)
                    queued_urls.add(full_url)
    return time.time() - start

print(f"Original: {original():.4f}s")
print(f"Optimized: {optimized():.4f}s")
