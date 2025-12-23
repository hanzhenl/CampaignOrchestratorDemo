"""
Atomic session storage operations with file locking.
Provides thread-safe read and write operations for dialog sessions.
"""
import json
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager

from .file_lock import FileLock, FileLockError

logger = logging.getLogger(__name__)

# Get the backend directory (parent of utils)
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
SESSION_FILE = DATA_DIR / "dialog_sessions.json"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def load_sessions() -> List[Dict[str, Any]]:
    """
    Load dialog sessions from file with read lock.
    
    Returns:
        List of session dictionaries. Returns empty list if file doesn't exist.
    
    Raises:
        FileLockError: If lock cannot be acquired
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not SESSION_FILE.exists():
        return []
    
    try:
        with FileLock(str(SESSION_FILE), timeout=5.0, exclusive=False) as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.warning("Session file does not contain a list, returning empty list")
                    return []
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in session file: {str(e)}")
                raise
    except FileLockError as e:
        logger.error(f"Failed to acquire read lock: {str(e)}")
        raise


def save_sessions(sessions: List[Dict[str, Any]]) -> None:
    """
    Save dialog sessions to file with write lock.
    
    Args:
        sessions: List of session dictionaries to save
    
    Raises:
        FileLockError: If lock cannot be acquired
        IOError: If file cannot be written
    """
    try:
        # For write operations, we need to open in write mode
        # FileLock will handle the locking, but we need to ensure file exists
        if not SESSION_FILE.exists():
            # Create empty file first
            SESSION_FILE.touch()
        
        with FileLock(str(SESSION_FILE), timeout=5.0, exclusive=True) as f:
            # Truncate file and write new content
            f.seek(0)
            f.truncate()
            json.dump(sessions, f, indent=2)
            f.flush()  # Ensure data is written
            os.fsync(f.fileno())  # Force write to disk
    except FileLockError as e:
        logger.error(f"Failed to acquire write lock: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error saving sessions: {str(e)}")
        raise


@contextmanager
def atomic_session_operation():
    """
    Context manager for atomic read-modify-write operations on sessions.
    
    Loads sessions, yields them for modification, then automatically saves.
    Ensures the entire operation is atomic with proper locking.
    The lock is held throughout the entire operation (read, modify, write).
    
    Yields:
        List of session dictionaries (can be modified in-place)
    
    Raises:
        FileLockError: If lock cannot be acquired
        json.JSONDecodeError: If file contains invalid JSON
    
    Example:
        with atomic_session_operation() as sessions:
            new_session = {...}
            sessions.append(new_session)
            # Sessions are automatically saved on exit
    """
    # Ensure file exists
    if not SESSION_FILE.exists():
        SESSION_FILE.touch()
    
    # Acquire write lock for the entire operation (read-modify-write)
    # The lock is held throughout the entire with block, including during yield
    with FileLock(str(SESSION_FILE), timeout=5.0, exclusive=True) as f:
        # Load sessions
        try:
            f.seek(0)
            content = f.read()
            if content.strip():
                data = json.loads(content)
                sessions = data if isinstance(data, list) else []
            else:
                sessions = []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in session file: {str(e)}")
            sessions = []  # Start fresh if file is corrupted
        
        # Yield sessions for modification (lock is still held)
        try:
            yield sessions
        except Exception as e:
            # If modification fails, don't save
            logger.error(f"Error during session modification: {str(e)}")
            raise
        else:
            # Save sessions on successful exit
            f.seek(0)
            f.truncate()
            json.dump(sessions, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

