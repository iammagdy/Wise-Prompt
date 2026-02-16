
## 2025-02-18 - Crawler Queue Optimization
**Learning:** In synthetic benchmarks of the crawler, `BeautifulSoup` parsing overhead dominates execution time, often masking algorithmic improvements in queue management unless the queue size is large (e.g., >2000 links/page).
**Action:** When optimizing the crawler, verify if parsing is the bottleneck before algorithmic queue changes. Consider switching to `lxml` parser if dependencies allow.
