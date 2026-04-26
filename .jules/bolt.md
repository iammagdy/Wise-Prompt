## 2024-05-24 - [O(n) list containment overhead in loops]
**Learning:** Checking `item not in queue` where `queue` is a list inside a loop causes execution time to scale quadratically with queue length. In my benchmark, this caused execution time to jump from 0.6s to 7.5s for 50k links.
**Action:** Always maintain an auxiliary `set()` for containment checks when enqueuing items.

## 2024-05-24 - [Expensive url parsing in loops]
**Learning:** Using `urlparse(full_url).netloc == base_domain` *before* checking `visited` caches means we parse strings for domains even when we already know we've processed the URL.
**Action:** Order conditionals carefully: do O(1) set lookups (`not in visited and not in queued`) *before* expensive string manipulation or parsing operations.

## 2024-05-24 - [List pop(0) vs deque popleft()]
**Learning:** `queue.pop(0)` is O(n) because it shifts all elements in the list. Over large queues, this introduces significant overhead.
**Action:** Replace `list` queues with `collections.deque` and use `popleft()` for O(1) removals.
