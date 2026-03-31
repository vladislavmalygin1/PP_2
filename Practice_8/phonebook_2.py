import psycopg2
from config import load_config

def get_connection():
    return psycopg2.connect(**load_config())

def search_with_function(pattern):
    with get_connection() as conn:
        with conn.cursor() as cur:
            
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            return cur.fetchall()

def upsert_user(name, phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            
            cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
        conn.commit()

def bulk_insert(users_list):
    """Expects list of tuples: [('name', 'phone'), ...]"""
    names = [u[0] for u in users_list]
    phones = [u[1] for u in users_list]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL bulk_insert_contacts(%s, %s);", (names, phones))
        conn.commit()

def get_paged(limit, offset):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paged(%s, %s);", (limit, offset))
            return cur.fetchall()

def delete_user(identifier):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact_proc(%s);", (identifier,))
        conn.commit()

if __name__ == "__main__":
    
    upsert_user("John Wick", "7778889900")
    
    
    data = [("Alice", "1234567890"), ("Bob", "123")]
    bulk_insert(data)
    
    
    print("Page 1 (first 2):", get_paged(2, 0))
    
    
    print("Search 'Wick':", search_with_function("Wick"))