# TTL Cache with LRU Eviction

Cache with LRU eviction policy that automatically removes cache entries after TTL seconds

---

## Features

- **Automatic TTL Expiration**  
  Entries expire after the specified seconds (TTL) automatically with `threading.Timer` and min-heap priority queue.

- **LRU Eviction Policy**  

- **Lazy Cleanup** of expired items from the internal heap.

---

### `LRU.py`
- `pushback(key)` — pushes key to the back moves to the back
- `popfront()` — removes and returns least recently used key
- `discard(key)` — removes key if present

### `Cache.py`
Implementation of the cache

- `addLine(item, data, TTL)` — insert the line with key (item, TTL) and value (exptime, data)
- `get(item, TTL)` — retrieve and refresh LRU

---

## Example

```python
from Cache import Cache

cache = Cache(maxSize=16)

for i in range(16): cache.addLine("A", i, TTL=60+i)
print(cache)

cache.get("A", 60)
print(cache)
