import struct
import time
import portalocker
import threading
from logger import Logger
from base_store import BaseStore

from enum import Enum

class LOCK_STATE(Enum):
    EXCLUSIVE = "exclusive"
    SHARED = "shared"

class WriteAheadStore(BaseStore):

    def __init__(self):
        """
        Initializes the key-value store instance.

        - Sets up an internal dictionary to store key-value pairs.
        - Initializes a Logger instance for logging operations.
        - Sets the file path for the write-ahead log.
        - Default log file_path is "write_ahead.log".
        - Opens the write-ahead log file in append-binary mode.
        - Creates a thread lock to ensure thread-safe operations.
        - Calls the recovery method to restore state from the write-ahead log.
        """
        self.__store = {}
        self.__logger = Logger()
        self.__write_ahead_log_file_path = "write_ahead.log"
        self.__file = open(self.__write_ahead_log_file_path, "ab+")
        self.__thread_lock = threading.Lock() 
        self.recovery()

    @property
    def store(self):
        return self.__store

    def __lock_file(self, file, mode: LOCK_STATE):
        """
        Acquire a lock on the underlying file object.

        Args:
            file: The file object to lock.
            mode (LOCK_STATE): The locking mode to use.
                - LOCK_STATE.EXCLUSIVE: Acquire an exclusive lock for writing.
                - LOCK_STATE.SHARED: Acquire a shared lock for reading.

        Uses the `portalocker` library to lock the file. An exclusive lock prevents other processes from accessing the file,
        while a shared lock allows concurrent read access.

        Raises:
            portalocker.exceptions.LockException: If the lock cannot be acquired.
        """
        if not file:
            raise ValueError("File object is required for locking")
        if mode == LOCK_STATE.EXCLUSIVE:
            portalocker.lock(file, portalocker.LOCK_EX)
        elif mode == LOCK_STATE.SHARED:
            portalocker.lock(file, portalocker.LOCK_SH)

    def __unlock_file(self,file):
        """
        Release the lock on the underlying file object.

        Uses the `portalocker` library to unlock the file after a lock has been acquired.
        Should be called in a finally block to ensure the file is always unlocked.
        """
        if not file:
            raise ValueError("File object is required for unlocking")
        portalocker.unlock(file)

    def set_log_file_path(self, file_path):
        """
        Sets the log file path for the Logger instance.

        Args:
            file_path (str): The path to the log file.

        Raises:
            ValueError: If the file path is empty.
        """
        if not file_path:
            raise ValueError("File path cannot be empty")
        self.__logger = Logger(log_file=file_path)

    def set_recovery_file_path(self, file_path):
        """
        Sets the file path for the write-ahead log used during recovery.

        Args:
            file_path (str): The path to the write-ahead log file.

        Raises:
            ValueError: If the file path is empty.
        """
        if not file_path:
            raise ValueError("File path cannot be empty")
        self.__write_ahead_log_file_path = file_path
        self.__file.close()
        self.__file = open(self.__write_ahead_log_file_path, "ab+")


    def recovery(self):
        """
        Attempts to recover the key-value store state from the write-ahead log.

        Calls the internal __recovery method to restore the in-memory store from the log file.
        Logs an error if recovery fails.
        """
        try:
            self.__recovery()
        except Exception as e:
            self.__logger.error(f"Error during recovery: {e}")

    def __recovery(self):
        """
        Internal method to restore the in-memory store from the write-ahead log.

        - Reads the log file sequentially.
        - For each record, unpacks the header to get key and value lengths.
        - Decodes the key and checks if the value exists (value_length > 0).
        - Updates the in-memory store with the key, its offset, and set/delete status.
        - Handles corrupted records by raising exceptions.
        - Logs completion of recovery.

        Raises:
            Exception: If a corrupted key or value is detected in the log.
        """
        offset = 0
        self.__store = {}
        with open(self.__write_ahead_log_file_path, "rb") as f:
            try:
                self.__lock_file(f,LOCK_STATE.SHARED)
                while True:
                    header = f.read(12)
                    if not header or len(header) < 12:
                        break
                    _, key_length, value_length = struct.unpack("III", header)
                    key_bytes = f.read(key_length)
                    if len(key_bytes) < key_length:
                        raise Exception(f"Corrupted key at offset {offset}")
                    key = key_bytes.decode()
                    if value_length >0:
                        value_bytes = f.read(value_length)
                        if len(value_bytes) < value_length:
                            raise Exception(f"Corrupted value at offset {offset}")
                        self.__store[key] = (offset, True)
                    else:
                        self.__store.pop(key, None)
                    offset += 12 + key_length + value_length
                self.__logger.info("Recovery completed successfully")
            finally:
                self.__unlock_file(f)

    def set(self, key: str, value: str) -> bool:
        """
        Sets the value for a given key in the key-value store.

        - Acquires a thread lock to ensure thread-safe operation.
        - Acquires an exclusive file lock to prevent concurrent writes.
        - Encodes the key and value as bytes.
        - Packs a header with the current timestamp, key length, and value length.
        - Writes the header, key, and value to the write-ahead log.
        - Updates the in-memory store with the key, its offset, and set status.
        - Logs the operation and returns True on success.
        - Handles exceptions by logging errors and returns False on failure.
        - Always releases the file lock in a finally block.

        Args:
            key (str): The key to set.
            value (str): The value to associate with the key.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if not key or not value or not isinstance(key, str) or not isinstance(value, str):
            self.__logger.error("Key and value must be non-empty strings")
            raise ValueError("Key and value must be non-empty strings")
        with self.__thread_lock:
            try:
                self.__lock_file(self.__file,LOCK_STATE.EXCLUSIVE)
                offset = self.__file.tell()
                key_bytes = key.encode()
                value_bytes = value.encode()
                header = struct.pack("III", int(time.time()), len(key_bytes), len(value_bytes))
                header += key_bytes + value_bytes
                self.__file.write(header)
                self.__file.flush()
                self.__store[key] = (offset, True)
                self.__logger.info(f"Set key '{key}' successfully")
                return True
            except Exception as e:
                self.__logger.error(f"Error setting key '{key}': {e}")
                return False
            finally:
                self.__unlock_file(self.__file)

    def get(self, key: str) -> bytes | None:
        """
        Retrieves the value associated with the given key from the key-value store.

        - Checks if the key exists in the in-memory store and is set.
        - Acquires a shared file lock to allow concurrent reads.
        - Seeks to the offset in the log file where the key-value pair is stored.
        - Reads and unpacks the header to get key and value lengths.
        - Reads the key and value bytes from the log file.
        - Verifies the key matches the requested key.
        - Returns the value bytes if found, otherwise logs an error or warning.

        Args:
            key (str): The key to retrieve.

        Returns:
            bytes | None: The value associated with the key, or None if not found or deleted.
        """
        if not isinstance(key, str) or not key:
            self.__logger.error("Key must be a non-empty string")
            raise ValueError("Key must be a non-empty string")
        if key not in self.__store:
            self.__logger.warning(f"Key '{key}' not found")
            return None
        offset, is_set = self.__store[key]
        if not is_set:
            self.__logger.warning(f"Key '{key}' is not set")
            return None
        with open(self.__write_ahead_log_file_path, "rb") as log_file:
            try:
                self.__lock_file(log_file,LOCK_STATE.SHARED)
                log_file.seek(offset)
                header = log_file.read(12)
                _, key_length, value_length = struct.unpack("III", header)
                key_bytes = log_file.read(key_length)
                value_bytes = log_file.read(value_length)
                key_decode = key_bytes.decode()
                if key_decode == key:
                    return value_bytes
                self.__logger.error(f"Key mismatch at offset {offset}: expected {key}, found {key_decode}")
                return None
            except Exception as e:
                self.__logger.error(f"Error getting key '{key}': {e}")
                return None
            finally:
                self.__unlock_file(log_file)

    def delete(self, key: str) -> bool:
        """
        Deletes the given key from the key-value store.

        - Acquires a thread lock to ensure thread-safe operation.
        - Acquires an exclusive file lock to prevent concurrent writes.
        - Encodes the key as bytes.
        - Packs a header with the current timestamp, key length, and a value length of 0 (indicating deletion).
        - Writes the header and key to the write-ahead log.
        - Updates the in-memory store with the key, its offset, and delete status.
        - Logs the operation and returns True on success.
        - Handles exceptions by logging errors and returns False on failure.
        - Always releases the file lock in a finally block.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if not isinstance(key, str) or not key:
            self.__logger.error("Key must be a non-empty string")
            raise ValueError("Key must be a non-empty string")
        with self.__thread_lock:
            try:
                self.__lock_file(self.__file,LOCK_STATE.EXCLUSIVE)
                offset = self.__file.tell()
                key_bytes = key.encode()
                header = struct.pack("III", int(time.time()), len(key_bytes), 0)
                header += key_bytes
                self.__file.write(header)
                self.__file.flush()
                self.__store[key] = (offset, False)
                self.__logger.info(f"Deleted key '{key}' successfully")
                return True
            except Exception as e:
                self.__logger.error(f"Error deleting key '{key}': {e}")
                return False
            finally:
                self.__unlock_file(self.__file)

