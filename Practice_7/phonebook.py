import psycopg2
import csv
import os
from config import load_config

def get_connection():
    """Establish connection using the parameters from config.py"""
    params = load_config()
    return psycopg2.connect(**params)

def get_file_path(filename):
    """Helper to find files in the same directory as this script"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL
    );
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


def insert_from_csv(filename='contacts.csv'):
    file_path = get_file_path(filename)
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    query = "INSERT INTO phonebook (username, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING;"
    
    try:
        count = 0
        with get_connection() as conn:
            with conn.cursor() as cur:
                with open(file_path, mode='r') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        cur.execute(query, (row[0], row[1]))
                        count += 1
            conn.commit()
            print(f"Successfully processed {count} rows from CSV.")
    except Exception as e:
        print(f"CSV Import Error: {e}")


def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    query = "INSERT INTO phonebook (username, phone) VALUES (%s, %s);"
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, phone))
            conn.commit()
            print("Contact added.")
    except Exception as e:
        print(f"Insert Error: {e}")


def update_contact():
    target = input("Enter the EXACT current username to update: ")
    print("Update: 1. Name | 2. Phone | 3. Both")
    choice = input("> ")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if choice in ['1', '3']:
                    new_name = input("New Name: ")
                    cur.execute("UPDATE phonebook SET username = %s WHERE username = %s", (new_name, target))
                if choice in ['2', '3']:
                    new_phone = input("New Phone: ")
                    cur.execute("UPDATE phonebook SET phone = %s WHERE username = %s", (new_phone, target))
            conn.commit()
            print("Contact updated successfully.")
    except Exception as e:
        print(f"Update Error: {e}")


def search_contacts():
    print("Search by: 1. Name (partial) | 2. Phone Prefix")
    choice = input("> ")
    val = input("Enter search term: ")
    
    query = "SELECT * FROM phonebook WHERE username ILIKE %s" if choice == '1' else "SELECT * FROM phonebook WHERE phone LIKE %s"
    param = (f"%{val}%",) if choice == '1' else (f"{val}%",)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, param)
                rows = cur.fetchall()
                print(f"\nFound {len(rows)} results:")
                for r in rows:
                    print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
    except Exception as e:
        print(f"Search Error: {e}")


def delete_contact():
    val = input("Enter Name or Phone to delete: ")
    query = "DELETE FROM phonebook WHERE username = %s OR phone = %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (val, val))
            conn.commit()
            print(f"Deleted records matching '{val}'.")
    except Exception as e:
        print(f"Delete Error: {e}")


if __name__ == '__main__':
    create_table() 
    while True:
        print("\n--- POSTGRES PHONEBOOK ---")
        print("1. Upload CSV")
        print("2. Add Contact (Console)")
        print("3. Update Contact")
        print("4. Search")
        print("5. Delete")
        print("6. Exit")
        
        move = input("Choice: ")
        if move == '1': insert_from_csv()
        elif move == '2': insert_from_console()
        elif move == '3': update_contact()
        elif move == '4': search_contacts()
        elif move == '5': delete_contact()
        elif move == '6': break
        else: print("Invalid Choice.")