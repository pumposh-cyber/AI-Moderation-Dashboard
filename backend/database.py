"""Database setup and connection logic supporting SQLite and PostgreSQL."""
import os
import sqlite3
import logging
from typing import List, Optional, Union, Any
from contextlib import contextmanager

from backend.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Determine database type from URL
_is_postgres = settings.database_url.startswith("postgresql://") or settings.database_url.startswith("postgres://")

if _is_postgres:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor, DictCursor
        from psycopg2.pool import ThreadedConnectionPool
    except ImportError:
        logger.error("PostgreSQL support requires psycopg2-binary. Install with: pip install psycopg2-binary")
        raise


# Connection pool for PostgreSQL
_postgres_pool: Optional[Any] = None


def _init_postgres_pool():
    """Initialize PostgreSQL connection pool."""
    global _postgres_pool
    if _postgres_pool is None:
        try:
            _postgres_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.database_url
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise


@contextmanager
def get_db_connection():
    """Get a database connection (context manager)."""
    if _is_postgres:
        if _postgres_pool is None:
            _init_postgres_pool()
        conn = _postgres_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            _postgres_pool.putconn(conn)
    else:
        # SQLite
        conn = sqlite3.connect(settings.database_url.replace("sqlite:///", ""))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()


def init_db() -> None:
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if _is_postgres:
            # PostgreSQL table creation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flagged_items (
                    id SERIAL PRIMARY KEY,
                    content_type VARCHAR(20) NOT NULL CHECK(content_type IN ('message', 'image', 'report')),
                    content TEXT NOT NULL,
                    priority VARCHAR(10) NOT NULL CHECK(priority IN ('high', 'medium', 'low')),
                    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'escalated')),
                    ai_summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_priority ON flagged_items(priority)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON flagged_items(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON flagged_items(created_at)
            """)
        else:
            # SQLite table creation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flagged_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL CHECK(content_type IN ('message', 'image', 'report')),
                    content TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('high', 'medium', 'low')),
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'escalated')),
                    ai_summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_priority ON flagged_items(priority)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON flagged_items(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON flagged_items(created_at)
            """)
        
        conn.commit()
        logger.info("Database initialized successfully")


def get_flag_by_id(flag_id: int) -> Optional[dict]:
    """Get a flagged item by ID."""
    with get_db_connection() as conn:
        if _is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM flagged_items WHERE id = %s", (flag_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM flagged_items WHERE id = ?", (flag_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


def get_all_flags() -> List[dict]:
    """Get all flagged items."""
    with get_db_connection() as conn:
        if _is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        cursor.execute("SELECT * FROM flagged_items ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def create_flag(content_type: str, content: str, priority: str, ai_summary: str) -> int:
    """Create a new flagged item and return its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if _is_postgres:
            cursor.execute("""
                INSERT INTO flagged_items (content_type, content, priority, status, ai_summary)
                VALUES (%s, %s, %s, 'pending', %s)
                RETURNING id
            """, (content_type, content, priority, ai_summary))
            flag_id = cursor.fetchone()[0]
        else:
            cursor.execute("""
                INSERT INTO flagged_items (content_type, content, priority, status, ai_summary)
                VALUES (?, ?, ?, 'pending', ?)
            """, (content_type, content, priority, ai_summary))
            flag_id = cursor.lastrowid
        conn.commit()
        return flag_id


def update_flag_status(flag_id: int, status: str) -> bool:
    """Update the status of a flagged item."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if _is_postgres:
            cursor.execute("""
                UPDATE flagged_items 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, flag_id))
        else:
            cursor.execute("""
                UPDATE flagged_items 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, flag_id))
        updated = cursor.rowcount > 0
        conn.commit()
        return updated


def delete_flag(flag_id: int) -> bool:
    """Delete a flagged item."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if _is_postgres:
            cursor.execute("DELETE FROM flagged_items WHERE id = %s", (flag_id,))
        else:
            cursor.execute("DELETE FROM flagged_items WHERE id = ?", (flag_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted


def get_stats() -> dict:
    """Get statistics using SQL aggregation for better performance."""
    with get_db_connection() as conn:
        if _is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_flags,
                COALESCE(SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END), 0) as high_priority,
                COALESCE(SUM(CASE WHEN priority = 'medium' THEN 1 ELSE 0 END), 0) as medium_priority,
                COALESCE(SUM(CASE WHEN priority = 'low' THEN 1 ELSE 0 END), 0) as low_priority,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END), 0) as pending_status,
                COALESCE(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END), 0) as approved_status,
                COALESCE(SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END), 0) as rejected_status,
                COALESCE(SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END), 0) as escalated_status
            FROM flagged_items
        """)
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Ensure all values are integers (handle None cases)
            return {
                'total_flags': result.get('total_flags', 0) or 0,
                'high_priority': result.get('high_priority', 0) or 0,
                'medium_priority': result.get('medium_priority', 0) or 0,
                'low_priority': result.get('low_priority', 0) or 0,
                'pending_status': result.get('pending_status', 0) or 0,
                'approved_status': result.get('approved_status', 0) or 0,
                'rejected_status': result.get('rejected_status', 0) or 0,
                'escalated_status': result.get('escalated_status', 0) or 0,
            }
        else:
            return {
                'total_flags': 0, 'high_priority': 0, 'medium_priority': 0, 'low_priority': 0,
                'pending_status': 0, 'approved_status': 0, 'rejected_status': 0, 'escalated_status': 0
            }
