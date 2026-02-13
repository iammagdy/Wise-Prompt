## 2026-02-13 - BeautifulSoup Overhead Masks Algorithmic Issues
**Learning:** In the `recursive_crawl` function, the overhead of BeautifulSoup parsing is so high that it can mask O(N^2) queue operations on small to medium datasets (up to 200 pages). The algorithmic bottleneck only becomes apparent on larger crawls or synthetic benchmarks with minimal parsing overhead.
**Action:** When profiling crawling logic, use synthetic benchmarks that mock the parsing step to isolate queue management performance.
