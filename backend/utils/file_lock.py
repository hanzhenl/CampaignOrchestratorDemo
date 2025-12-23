"""
File locking utility using fcntl for Unix/Mac systems.
Provides context manager support for safe file locking with timeout and retry logic.
"""
import fcntl
import time
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class FileLockError(Exception):
    """Raised when file lock operations fail"""
    pass


@contextmanager
def FileLock(filepath: str, timeout: float = 5.0, max_retries: int = 3, exclusive: bool = True):
    """
    Context manager for file locking using fcntl.flock().
    
    Args:
        filepath: Path to the file to lock
        timeout: Maximum time to wait for lock (seconds)
        max_retries: Maximum number of retry attempts
        exclusive: If True, use exclusive lock (LOCK_EX), else shared lock (LOCK_SH)
    
    Yields:
        File handle (opened in appropriate mode)
    
    Raises:
        FileLockError: If lock cannot be acquired within timeout
        IOError: If file cannot be opened
    
    Example:
        with FileLock("data.json") as f:
            data = json.load(f)
            # modify data
            f.seek(0)
            json.dump(data, f)
    """
    lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    file_handle = None
    
    try:
        # Open file in appropriate mode
        mode = 'r+' if exclusive else 'r'
        file_handle = open(filepath, mode)
        
        # Try to acquire lock with retries
        lock_acquired = False
        retry_count = 0
        start_time = time.time()
        
        while not lock_acquired and retry_count < max_retries:
            try:
                # Try non-blocking lock first
                fcntl.flock(file_handle.fileno(), lock_type | fcntl.LOCK_NB)
                lock_acquired = True
                logger.debug(f"Lock acquired for {filepath}")
            except IOError:
                # Lock is held by another process
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise FileLockError(
                        f"Timeout waiting for lock on {filepath} after {timeout}s"
                    )
                
                # Exponential backoff: wait before retry
                wait_time = min(0.1 * (2 ** retry_count), 0.5)  # Max 0.5s wait
                time.sleep(wait_time)
                retry_count += 1
                
                # If we've exhausted retries, try one more blocking attempt
                if retry_count >= max_retries:
                    remaining_time = timeout - elapsed
                    if remaining_time > 0:
                        try:
                            # Blocking lock with remaining timeout
                            fcntl.flock(file_handle.fileno(), lock_type)
                            lock_acquired = True
                            logger.debug(f"Lock acquired for {filepath} after blocking wait")
                        except IOError:
                            raise FileLockError(
                                f"Failed to acquire lock on {filepath} after {max_retries} retries"
                            )
                    else:
                        raise FileLockError(
                            f"Timeout waiting for lock on {filepath} after {timeout}s"
                        )
        
        if not lock_acquired:
            raise FileLockError(f"Failed to acquire lock on {filepath}")
        
        # Yield file handle to caller
        yield file_handle
        
    except FileLockError:
        raise
    except Exception as e:
        logger.error(f"Error in FileLock context manager: {str(e)}")
        raise FileLockError(f"Unexpected error acquiring lock: {str(e)}")
    finally:
        # Always release lock and close file
        if file_handle:
            try:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
                logger.debug(f"Lock released for {filepath}")
            except Exception as e:
                logger.warning(f"Error releasing lock: {str(e)}")
            finally:
                try:
                    file_handle.close()
                except Exception as e:
                    logger.warning(f"Error closing file: {str(e)}")

