# Bolt's Journal

## 2024-05-23 - Initial Setup
**Learning:** Performance optimization often requires balancing theoretical gains with measurable real-world impact.
**Action:** Always verify optimizations with tests, even if they seem obvious.

## 2024-05-23 - Mocking Context Managers
**Learning:** When mocking `requests.Session()` used as a context manager (`with requests.Session() as s:`), the mock object's `__enter__` method must return the mock object itself (`mock_session.__enter__.return_value = mock_session`). Otherwise, the variable bound in the `as` clause will be a new Mock object, disconnecting it from your configuration.
**Action:** Always verify mock configuration for context managers when testing session-based networking code.
