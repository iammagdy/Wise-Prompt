## 2024-05-24 - Python Crawler Queue O(N) Bottleneck
**Learning:** Using a list as a queue (`pop(0)`) combined with $O(N)$ list containment checks (`url not in queue`) and expensive operations (`urlparse().netloc`) inside inner loops creates massive performance spikes under load (e.g., jumping from milliseconds to over 15 seconds for 5,000 links).
**Action:** Always use `collections.deque` for $O(1)$ pop operations, maintain an auxiliary `set` for $O(1)$ queue containment checks, and order conditionals to perform fast string/membership checks *before* calling expensive parsing functions.
