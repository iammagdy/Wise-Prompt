
## 2026-04-16 - [O(1) lookups in recursive_crawl]
**Learning:** In the recursive crawler, using standard python lists for the queue and relying on `list.pop(0)` combined with `not in queue` caused an O(N) bottleneck that severely hampered performance when crawling deep nested structures.
**Action:** Use `collections.deque` for O(1) popping. Combine it with a mirroring auxiliary Set (e.g. `queued_urls`) for O(1) containment checks instead of checking against the list/deque itself.
