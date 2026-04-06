
## 2024-05-24 - O(N) Queue Membership and Expensive String Checks in Crawler
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment (`in queue`) and pop (`pop(0)`) operations cause significant execution time spikes. Furthermore, evaluating expensive string parsing operations like `urlparse(url).netloc` *before* fast O(1) set membership checks creates an unnecessary bottleneck.
**Action:** Always use `collections.deque` for O(1) pops and an auxiliary `set` for O(1) lookups when managing a queue. When conditionally checking items in tight loops, explicitly order conditions to perform fast O(1) boolean or set checks before executing more complex logic or string parsing.
