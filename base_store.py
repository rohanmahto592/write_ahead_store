from abc import ABC, abstractmethod


class BaseStore(ABC):
    """Base interface for all Key-Value Stores"""

    @property
    @abstractmethod
    def store(self) -> dict:
        """Returns the in-memory store"""
        pass
    @abstractmethod
    def set_log_file_path(self, file_path: str) -> None:
        """Set the log file path"""
        pass
    @abstractmethod
    def set_recovery_file_path(self, file_path: str) -> None:
        """Set the recovery file path"""
        pass
    @abstractmethod
    def set(self, key: str, value: str) -> bool:
        """Set a key with value"""
        pass

    @abstractmethod
    def get(self, key: str) -> bytes | None:
        """Get a key’s value"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key"""
        pass

    @abstractmethod
    def recovery(self) -> None:
        """Recover state from log file"""
        pass

