# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Project setup requires manual installation of dev tools like `autopep8` as they are not in requirements.txt.
**Action:** Always check for dev dependencies and install if missing.

## 2024-05-22 - Crawler Benchmarking
**Learning:** `recursive_crawl` contains deliberate `time.sleep(0.3)` calls which mask performance improvements in logic or network overhead.
**Action:** When benchmarking the crawler, mock `time.sleep` to 0 to reveal actual processing speed improvements.
