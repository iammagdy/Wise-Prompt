## 2025-05-15 - O(N^2) Crawler Queue Bottleneck
**Learning:** Checking `url in queue` with a list is an O(N) operation inside a loop, making the crawl O(N^2) in the number of pages. For crawling even moderate numbers of pages (e.g., 50), this becomes a bottleneck if pages have many links.
**Action:** Use `collections.deque` for O(1) pops and maintain a separate `seen_urls` set for O(1) membership checks to keep the entire process O(N).
