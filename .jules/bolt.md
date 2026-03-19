## 2024-05-24 - [O(n) Array Lookups vs Set Membership]
**Learning:** In the `recursive_crawl` function, we maintain a `queue` of URLs to visit. Originally, this was a list and containment checks (`url not in queue`) were O(n). During heavy link loads (like 10000 per page), the queue grows to hundreds of thousands of items, and O(n) checking spikes execution time.
**Action:** Replace `queue` list with `collections.deque` for O(1) pops, and maintain a separate `queued_urls` set for O(1) membership testing when avoiding double queueing.
