import sqlite3
import threading
from queue import Queue
from typing import Optional
from config.settings import DATABASE_PATH

class ConnectionPool:
    """Simple SQLite connection pool for better performance"""
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # Initialize pool with connections
        for _ in range(pool_size):
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool"""
        return self.pool.get()
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool"""
        if conn:
            self.pool.put(conn)
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

# Global connection pool instance
_connection_pool: Optional[ConnectionPool] = None

def get_connection_pool() -> ConnectionPool:
    """Get the global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool

def get_pooled_connection() -> sqlite3.Connection:
    """Get a pooled database connection"""
    return get_connection_pool().get_connection()

def return_pooled_connection(conn: sqlite3.Connection):
    """Return a pooled connection"""
    get_connection_pool().return_connection(conn)