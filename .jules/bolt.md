## 2024-05-24 - Short-circuiting and set checks in algorithmic loops
**Learning:** In python loops handling URLs, such as `recursive_crawl`, placing fast O(1) set membership checks (`url not in visited`) before expensive string parsing operations (`urlparse(url).netloc`) can measurably reduce execution time by avoiding parsing for already visited links.
**Action:** Always order conditions from fastest/cheapest (like O(1) set lookups) to slowest (like O(N) list search or string parsing). Use `deque` instead of list for queues.
