## 2024-05-24 - recursive_crawl optimization
**Learning:** In python loops handling URLs, such as recursive_crawl, perform fast O(1) set membership checks (`url not in visited` and `url not in queued_urls`) before executing expensive string parsing operations like `urlparse(url).netloc` to measurably reduce execution time.
**Action:** Always check O(1) set membership before O(N) or expensive string/parsing operations in a loop.
