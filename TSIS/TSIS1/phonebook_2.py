import psycopg2
import json
from psycopg2.extras import RealDictCursor
from TSIS.TSIS1.config import load_config

def get_connection():
    return psycopg2.connect(**load_config())

# --- 3.2 Advanced Console Search & Filter ---
def list_contacts(group_filter=None, sort_by="name", limit=5, offset=0):
    # 1. Start with the base query
    query = """
        SELECT c.name, c.email, c.birthday, g.name as group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """
    params = []

    # 2. Add Filter (This adds ONE %s)
    if group_filter:
        query += " WHERE g.name = %s"
        params.append(group_filter)
    
    # 3. Add Sorting (No %s here, columns can't be parameterized)
    sort_map = {"name": "c.name", "birthday": "c.birthday", "date": "c.created_at"}
    query += f" ORDER BY {sort_map.get(sort_by, 'c.name')}"

    # 4. Add Pagination (This adds TWO %s)
    query += " LIMIT %s OFFSET %s"
    params.append(limit)  # This matches the first %s in this line
    params.append(offset) # This matches the second %s in this line

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # cur.execute will now see 2 params (limit, offset) 
            # OR 3 params (group, limit, offset) correctly.
            cur.execute(query, params)
            return cur.fetchall()
# --- 3.3 Import / Export JSON ---
def export_to_json():
    query = """
        SELECT c.name, c.email, CAST(c.birthday AS TEXT) as birthday, g.name as group,
               json_agg(json_build_object('phone', p.phone, 'type', p.type)) as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            data = cur.fetchall()
    
    with open('contacts.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Exported to contacts.json")

def import_from_json():
    try:
        with open('contacts.json', 'r') as f:
            data = json.load(f)
        with get_connection() as conn:
            with conn.cursor() as cur:
                for item in data:
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
                    if cur.fetchone():
                        choice = input(f"Duplicate {item['name']}! (S)kip or (O)verwrite? ").lower()
                        if choice == 's': continue
                        cur.execute("DELETE FROM contacts WHERE name = %s", (item['name'],))
                    
                    cur.execute("INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s)",
                                (item['name'], item.get('email'), item.get('birthday')))
                    cur.execute("CALL public.move_to_group(%s, %s)", (item['name'], item.get('group', 'Other')))
                    for p in item.get('phones', []):
                        if p.get('phone'):
                            cur.execute("CALL public.add_phone(%s, %s, %s)", (item['name'], p['phone'], p['type']))
            conn.commit()
            print("Import complete.")
    except FileNotFoundError: print("contacts.json not found.")

# --- 3.2 Paginated Navigation Loop ---
def interactive_pagination():
    limit, offset = 3, 0
    while True:
        results = list_contacts(limit=limit, offset=offset)
        print("\n--- CONTACTS PAGE ---")
        for r in results:
            print(f"Name: {r['name']} | Email: {r['email']} | Group: {r['group_name']}")
        
        cmd = input("\n[N]ext | [P]rev | [Q]uit: ").lower()
        if cmd == 'n' and len(results) == limit: offset += limit
        elif cmd == 'p': offset = max(0, offset - limit)
        elif cmd == 'q': break
def add_phone_interactively():
    """Interface for Task 3.4: Procedure add_phone"""
    name = input("Enter contact name: ")
    phone = input("Enter new phone number: ")
    ptype = input("Enter type (home, work, mobile): ").lower()
    
    if ptype not in ['home', 'work', 'mobile']:
        print("Invalid type! Use home, work, or mobile.")
        return

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL public.add_phone(%s, %s, %s);", (name, phone, ptype))
            conn.commit()
            print(f"Successfully added {ptype} phone to {name}.")
    except Exception as e:
        print(f"Error: {e}")

def move_group_interactively():
    """Interface for Task 3.4: Procedure move_to_group"""
    name = input("Enter contact name: ")
    group = input("Enter new group name (Family, Work, Friend, Other): ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL public.move_to_group(%s, %s);", (name, group))
            conn.commit()
            print(f"Contact {name} moved to group '{group}'.")
    except Exception as e:
        print(f"Error: {e}")
def create_contact():
    name = input("Name: ")
    email = input("Email: ")
    bday = input("Birthday (YYYY-MM-DD): ")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s)", 
                            (name, email, bday))
            conn.commit()
            print(f"Contact {name} created! Now you can add phones to them.")
    except Exception as e:
        print(f"Error: {e}")
def main():
    while True:
        print("\n=== CONTACT MANAGER ===")
        print("1. Search (Name/Email/Phone)")
        print("2. Browse (Pagination)")
        print("3. Export JSON")
        print("4. Import JSON")
        print("5. Advanced Search (All fields)")
        print("6. Add New Phone to Contact")
        print("7. Move Contact to Group")
        print("8. Exit")
        
        choice = input("Select: ")
        
        if choice == '1' or choice == '5':
            q = input("Query: ")
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.search_contacts(%s)", (q,))
                    results = cur.fetchall()
                    for row in results:
                        print(row)
        elif choice == '2':
            interactive_pagination()
        elif choice == '3':
            export_to_json()
        elif choice == '4':
            import_from_json()
        elif choice == '6':
            add_phone_interactively()
        elif choice == '7':
            move_group_interactively()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()