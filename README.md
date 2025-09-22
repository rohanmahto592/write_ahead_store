# Write-Ahead Key-Value Store (KV Store)

A **lightweight, durable, thread-safe key-value store** in Python with **O(1) operations** for in-memory access, powered by a **write-ahead log (WAL)** for crash recovery.

---

## Features

- **O(1) Operations**  
  All `set`, `get`, and `delete` operations run in **constant time** for in-memory access.

- **Durable Storage**  
  Every write (`set`/`delete`) is appended to a **write-ahead log**, ensuring durability and recoverability after crashes.

- **Crash Recovery**  
  Call `recovery()` to rebuild the in-memory store from the WAL automatically.

- **Thread-Safe**  
  Supports multiple threads safely using **thread locks** for in-memory operations and **file locks** for WAL writes.

- **Concurrent Reads**  
  Multiple threads can read simultaneously using **shared locks**, without blocking each other.
- **Performance highlight** <br>
  *1M insertions in ~70s using 100 threads*

- **How It Works**

Write-Ahead Log (WAL)

Every operation is appended to a log file first.

Format: [timestamp, key_length, value_length] + key_bytes + value_bytes

value_length = 0 → indicates deletion.

In-Memory Store

Python dictionary { key: (offset, is_set) }

Provides O(1) get, set, delete operations.

Recovery

On startup, WAL is replayed to rebuild in-memory store.

Ensures data is not lost in case of crashes.

Concurrency

Thread lock ensures safe updates to in-memory dictionary.

File locks:

Exclusive → write operations

Shared → concurrent reads

- **Simple API**  
  ```python
  kv = WriteAheadStore()
  kv.set("key1", "value1")
  value = kv.get("key1")
  kv.delete("key1")

- **Installation**  
  git clone https://github.com/rohanmahto592/write_ahead_store.git <br>
  cd write-ahead-store

- **Python Packages**
  - `portalocker` - For cross-platform file locking
  - `struct`, `time`, `threading` (standard library)

```bash
pip install portalocker

