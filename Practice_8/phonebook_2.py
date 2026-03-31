import psycopg2
from config import load_config

def get_connection():
    
    return psycopg2.connect(**load_config())

# 1. Pattern Search Function
def search_by_pattern(pattern):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM public.search_contacts(%s);", (pattern,))
                return cur.fetchall()
    except Exception as e:
        return f"Search Error: {e}"

# 2. Upsert Procedure (Single Insert/Update)
def upsert_user(name, phone):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL public.upsert_contact(%s, %s);", (name, phone))
            conn.commit()
            print(f"Upserted: {name}")
    except Exception as e:
        print(f"Upsert Error: {e}")

# 3. Bulk Insert with Validation & Return Incorrect Data
def bulk_insert_and_report(users_list):
    names = [u[0] for u in users_list]
    phones = [u[1] for u in users_list]
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Execute the procedure logic (fills the temp table)
                cur.execute("CALL public.bulk_insert_with_errors(%s, %s);", (names, phones))
                
                # 2. Fetch the "Update" (the incorrect data)
                cur.execute("SELECT * FROM bulk_errors;")
                invalid_rows = cur.fetchall()
                
                if invalid_rows:
                    print("\n--- ATTENTION: INCORRECT DATA FOUND ---")
                    for row in invalid_rows:
                        print(f"SKIPPED: {row[0]} ({row[1]}) -> Reason: {row[2]}")
                else:
                    print("\nSuccess: All data was correct and inserted.")
                    
            conn.commit()
    except Exception as e:
        print(f"System Error: {e}")

# 4. Pagination Function
def get_paged_contacts(limit, offset):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM public.get_paged(%s, %s);", (limit, offset))
                return cur.fetchall()
    except Exception as e:
        return f"Pagination Error: {e}"

# 5. Delete Procedure
def delete_user(identifier):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL public.delete_by_id(%s);", (identifier,))
            conn.commit()
            print(f"Deleted: {identifier}")
    except Exception as e:
        print(f"Delete Error: {e}")

def interactive_menu():
    while True:
        print("\n--- PHONEBOOK INTERACTIVE MENU ---")
        print("1. Search Contacts (Pattern)")
        print("2. Add/Update Single Contact (Upsert)")
        print("3. Bulk Insert with Validation")
        print("4. View Paged Contacts")
        print("5. Delete Contact")
        print("6. Exit")
        
        choice = input("Select an option (1-6): ")

        if choice == '1':
            pattern = input("Enter name or phone part to search: ")
            results = search_by_pattern(pattern)
            print("Results:", results)

        elif choice == '2':
            name = input("Enter Name: ")
            phone = input("Enter Phone: ")
            upsert_user(name, phone)

        elif choice == '3':
            users = []
            print("Enter contacts (leave Name empty to finish):")
            while True:
                name = input("  Name: ")
                if not name: break
                phone = input("  Phone: ")
                users.append((name, phone))
            if users:
                bulk_insert_and_report(users)

        elif choice == '4':
            limit = int(input("How many records per page? "))
            offset = int(input("Skip how many records (Offset)? "))
            print("Data:", get_paged_contacts(limit, offset))

        elif choice == '5':
            target = input("Enter Name or Phone to delete: ")
            delete_user(target)

        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    interactive_menu()