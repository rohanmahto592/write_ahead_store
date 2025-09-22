# KV Store (Write-Ahead Logging)

A simple **Key-Value Store** written in Python with:

- **Write-Ahead Logging (WAL)** for durability
- **Crash Recovery** support
- **Concurrent Access** with file locking
- **Snapshotting** (planned)
- **Custom Logging** for debug and error tracking

---

## Features

- ✅ `set(key, value)` → Insert or update a key  
- ✅ `get(key)` → Retrieve a value  
- ✅ `delete(key)` → Remove a key  
- ✅ `recovery()` → Replay WAL and rebuild in-memory store after crash  
- ✅ File locking with **portalocker** to avoid race conditions  
- ✅ Thread-safe operations with Python `threading`  

---

## Installation

```bash
git clone https://github.com/yourname/kvstore-wal.git
