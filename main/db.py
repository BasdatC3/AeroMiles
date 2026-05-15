"""
Database utility module using psycopg2 for raw SQL queries.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings


def get_connection():
    """Get a database connection using settings from Django settings."""
    db_config = settings.DATABASES['default']
    return psycopg2.connect(
        host=db_config.get('HOST', ''),
        port=db_config.get('PORT', 5432),
        database=db_config.get('NAME', ''),
        user=db_config.get('USER', ''),
        password=db_config.get('PASSWORD', ''),
        sslmode=db_config.get('OPTIONS', {}).get('sslmode', 'require'),
    )


def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Execute a SQL query and return results.

    Args:
        query: SQL query string
        params: Tuple of parameters
        fetch_one: If True, return single row
        fetch_all: If True, return all rows

    Returns:
        List of dicts (row as dict) or single dict or None
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return None
    finally:
        conn.close()


def execute_write(query, params=None):
    """
    Execute a SQL write query (INSERT, UPDATE, DELETE).

    Args:
        query: SQL query string
        params: Tuple of parameters

    Returns:
        True if successful
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_write_get_id(query, params=None):
    """
    Execute a SQL write query and return the inserted row id.

    Returns:
        id of inserted row
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            # Get the last inserted id
            cursor.execute("SELECT lastval()")
            return cursor.fetchone()[0]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()