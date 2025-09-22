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

- **Simple API**  
  ```python
  kv = WriteAheadStore()
  kv.set("key1", "value1")
  value = kv.get("key1")
  kv.delete("key1")

