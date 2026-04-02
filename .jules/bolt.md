## 2024-06-03 - [Optimized URL Queue Containment and Lookup]
**Learning:** In crawler loops with high load, using a standard O(N) list containment check (`in queue`) and O(N) `pop(0)` operation combined with expensive string parsing inside inner loops causes massive execution spikes (e.g., from ~2s down to milliseconds).
**Action:** Always prefer `collections.deque` for FIFO operations and maintain an auxiliary `set` (e.g., `queued_urls`) for O(1) containment checks. Prioritize fast boolean or O(1) checks before executing slower parsing operations like `urlparse(url).netloc == domain`.
