import csv
import json
import os
from datetime import datetime

from connect import connect


VALID_PHONE_TYPES = {"home", "work", "mobile"}
SORT_OPTIONS = {
    "name": "c.name",
    "birthday": "c.birthday NULLS LAST, c.name",
    "date": "c.created_at, c.name",
}


def read_sql_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found")
        return None

    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def parse_birthday(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def normalize_phone_type(value):
    phone_type = (value or "mobile").strip().lower()
    if phone_type not in VALID_PHONE_TYPES:
        raise ValueError("Phone type must be home, work, or mobile")
    return phone_type


def get_or_create_group_id(cur, group_name):
    group_name = (group_name or "Other").strip() or "Other"
    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,),
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    return cur.fetchone()[0]


def upsert_contact(cur, name, email=None, birthday=None, group_name="Other"):
    group_id = get_or_create_group_id(cur, group_name)
    cur.execute(
        """
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE
        SET email = COALESCE(EXCLUDED.email, contacts.email),
            birthday = COALESCE(EXCLUDED.birthday, contacts.birthday),
            group_id = EXCLUDED.group_id
        RETURNING id
        """,
        (name, email, birthday, group_id),
    )
    return cur.fetchone()[0]


def add_phone_record(cur, contact_id, phone, phone_type):
    cur.execute(
        """
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (contact_id, phone) DO UPDATE
        SET type = EXCLUDED.type
        """,
        (contact_id, phone, phone_type),
    )


def print_contacts(rows):
    if not rows:
        print("No contacts found")
        return

    for row in rows:
        print(
            f"id={row[0]}, name={row[1]}, email={row[2] or '-'}, "
            f"birthday={row[3] or '-'}, group={row[4] or '-'}, "
            f"phones={row[5] or '-'}, created_at={row[6]}"
        )


def fetch_contacts(cur, where_clause="", params=(), order_by="c.id"):
    query = f"""
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name,
        COALESCE(
            STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone),
            ''
        ) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    {where_clause}
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY {order_by}
    """
    cur.execute(query, params)
    return cur.fetchall()


# ----------------------
# 1. Create table
# ----------------------
def create_table():
    """Creates the extended phonebook schema if it does not exist"""
    sql = read_sql_file("schema.sql")
    if sql is None:
        return

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Schema created successfully")


def create_db_objects():
    """Creates PostgreSQL functions and procedures from SQL file"""
    sql = read_sql_file("procedures.sql")
    if sql is None:
        return

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Functions and procedures created successfully")


def search_by_pattern():
    pattern = input("Enter search pattern: ").strip()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            print_contacts(cur.fetchall())


def insert_or_update_user_py():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))

    print("User inserted or updated")


def insert_many_users_py():
    n = int(input("How many users do you want to add? "))

    names = []
    phones = []

    for i in range(n):
        print(f"\nUser {i + 1}")
        name = input("Enter name: ").strip()
        phone = input("Enter phone: ").strip()
        names.append(name)
        phones.append(phone)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_many_users(%s, %s)", (names, phones))
            cur.execute("SELECT * FROM incorrect_data")
            incorrect_rows = cur.fetchall()

    if incorrect_rows:
        print("\nIncorrect data:")
        for row in incorrect_rows:
            print(f"name={row[0]}, phone={row[1]}, reason={row[2]}")
    else:
        print("All users inserted successfully")


def query_with_pagination():
    limit = int(input("Enter page size: "))
    offset = 0

    while True:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_phonebook_paginated(%s, %s)", (limit, offset))
                rows = cur.fetchall()

        if rows:
            print_contacts(rows)
        else:
            print("No records found")

        command = input("Enter next / prev / quit: ").strip().lower()
        if command == "next":
            if len(rows) == limit:
                offset += limit
            else:
                print("You are already on the last page")
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Invalid command")


def delete_by_username_or_phone():
    value = input("Enter username or phone to delete: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_from_phonebook(%s)", (value,))

    print("Delete procedure completed")


# ----------------------
# 2. Insert contact from console
# ----------------------
def insert_from_console():
    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip() or None
    birthday_text = input("Enter birthday (YYYY-MM-DD): ").strip()
    group_name = input("Enter group: ").strip() or "Other"
    phone = input("Enter phone number: ").strip()
    phone_type = normalize_phone_type(input("Enter phone type (home/work/mobile): "))

    with connect() as conn:
        with conn.cursor() as cur:
            contact_id = upsert_contact(cur, name, email, parse_birthday(birthday_text), group_name)
            add_phone_record(cur, contact_id, phone, phone_type)
    print("Contact added")


# ----------------------
# 3. Insert contacts from CSV
# ----------------------
def insert_from_csv(filename="contacts.csv"):
    # 1. Get the absolute path to the directory where phonebook_2.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Join it with your filename to get the full path
    full_path = os.path.join(base_dir, filename)

    if not os.path.exists(full_path):
        print(f"Error: {full_path} not found.")
        return
    with connect() as conn:
        with conn.cursor() as cur:
            with open(filename, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contact_id = upsert_contact(
                        cur,
                        row["name"].strip(),
                        (row.get("email") or "").strip() or None,
                        parse_birthday((row.get("birthday") or "").strip()),
                        (row.get("group") or "Other").strip(),
                    )
                    add_phone_record(
                        cur,
                        contact_id,
                        row["phone"].strip(),
                        normalize_phone_type(row.get("type")),
                    )
    print("Contacts from CSV added")


# ----------------------
# 4. Update contact
# ----------------------
def update_contact():
    old_name = input("Enter the name of the contact to update: ").strip()
    new_name = input("New name (leave empty if no change): ").strip()
    new_email = input("New email (leave empty if no change): ").strip()
    new_birthday = input("New birthday YYYY-MM-DD (leave empty if no change): ").strip()
    new_group = input("New group (leave empty if no change): ").strip()

    updates = []
    values = []

    if new_name:
        updates.append("name = %s")
        values.append(new_name)
    if new_email:
        updates.append("email = %s")
        values.append(new_email)
    if new_birthday:
        updates.append("birthday = %s")
        values.append(parse_birthday(new_birthday))
    if new_group:
        with connect() as conn:
            with conn.cursor() as cur:
                group_id = get_or_create_group_id(cur, new_group)
                updates.append("group_id = %s")
                values.append(group_id)
                if updates:
                    values.append(old_name)
                    cur.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE name = %s", values)
        print("Contact updated")
        return

    if not updates:
        print("Nothing to update")
        return

    with connect() as conn:
        with conn.cursor() as cur:
            values.append(old_name)
            cur.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE name = %s", values)
    print("Contact updated")


# ----------------------
# 5. Query contacts
# ----------------------
def query_contacts():
    print("1 - By name")
    print("2 - By phone prefix")
    choice = input("Choice: ")

    with connect() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Enter name to search: ").strip()
                rows = fetch_contacts(cur, "WHERE c.name ILIKE %s", (f"%{name}%",), "c.name")
            elif choice == "2":
                prefix = input("Enter phone prefix: ").strip()
                rows = fetch_contacts(
                    cur,
                    "WHERE EXISTS (SELECT 1 FROM phones p2 WHERE p2.contact_id = c.id AND p2.phone LIKE %s)",
                    (f"{prefix}%",),
                    "c.name",
                )
            else:
                print("Invalid choice")
                return

    print_contacts(rows)


# ----------------------
# 6. Delete contact
# ----------------------
def delete_contact():
    print("Delete by: 1 - name, 2 - phone number")
    choice = input("Choice: ")

    with connect() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Enter name: ").strip()
                cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
            elif choice == "2":
                phone = input("Enter phone number: ").strip()
                cur.execute(
                    "DELETE FROM contacts WHERE id IN (SELECT contact_id FROM phones WHERE phone = %s)",
                    (phone,),
                )
            else:
                print("Invalid choice")
                return
    print("Contact deleted")


def filter_by_group():
    group_name = input("Enter group name: ").strip()
    with connect() as conn:
        with conn.cursor() as cur:
            rows = fetch_contacts(cur, "WHERE g.name ILIKE %s", (group_name,), "c.name")
    print_contacts(rows)


def search_by_email():
    pattern = input("Enter email pattern: ").strip()
    with connect() as conn:
        with conn.cursor() as cur:
            rows = fetch_contacts(cur, "WHERE c.email ILIKE %s", (f"%{pattern}%",), "c.name")
    print_contacts(rows)


def sort_contacts():
    print("Sort by: name / birthday / date")
    choice = input("Choice: ").strip().lower()
    order_by = SORT_OPTIONS.get(choice)
    if not order_by:
        print("Invalid sort option")
        return

    with connect() as conn:
        with conn.cursor() as cur:
            rows = fetch_contacts(cur, "", (), order_by)
    print_contacts(rows)


def export_to_json(filename="contacts_export.json"):
    with connect() as conn:
        with conn.cursor() as cur:
            rows = fetch_contacts(cur, "", (), "c.name")
            result = []
            for row in rows:
                cur.execute(
                    """
                    SELECT phone, type
                    FROM phones
                    WHERE contact_id = %s
                    ORDER BY id
                    """,
                    (row[0],),
                )
                phones = [{"phone": phone, "type": phone_type} for phone, phone_type in cur.fetchall()]
                result.append(
                    {
                        "name": row[1],
                        "email": row[2],
                        "birthday": row[3].isoformat() if row[3] else None,
                        "group": row[4],
                        "created_at": row[6].isoformat() if row[6] else None,
                        "phones": phones,
                    }
                )

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)
    print(f"Contacts exported to {filename}")


def import_from_json(filename="contacts_import.json"):
    # Get the folder where phonebook_2.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    if not os.path.exists(file_path):
        print(f"File {file_path} not found")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        contacts = json.load(file)
    # ... rest of the code

    with connect() as conn:
        with conn.cursor() as cur:
            for contact in contacts:
                name = contact["name"].strip()
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()

                if existing:
                    decision = input(f"Contact '{name}' exists. Enter skip or overwrite: ").strip().lower()
                    if decision == "skip":
                        continue
                    if decision != "overwrite":
                        print(f"Unknown choice for {name}. Contact skipped.")
                        continue
                    cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))

                contact_id = upsert_contact(
                    cur,
                    name,
                    contact.get("email"),
                    parse_birthday(contact.get("birthday")),
                    contact.get("group", "Other"),
                )
                for phone_data in contact.get("phones", []):
                    add_phone_record(
                        cur,
                        contact_id,
                        phone_data["phone"].strip(),
                        normalize_phone_type(phone_data.get("type")),
                    )
    print("Contacts imported from JSON")


def add_phone():
    contact_name = input("Enter contact name: ").strip()
    phone = input("Enter phone: ").strip()
    phone_type = normalize_phone_type(input("Enter phone type (home/work/mobile): "))

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
    print("Phone added")


def move_to_group():
    contact_name = input("Enter contact name: ").strip()
    group_name = input("Enter new group name: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
    print("Contact moved to another group")


# ----------------------
# 7. Main menu
# ----------------------
def menu():
    while True:
        print("\n--- PhoneBook Menu ---")
        print("1. Create table")
        print("2. Create functions and procedures")
        print("3. Add contact via console")
        print("4. Add contacts from CSV")
        print("5. Update contact")
        print("6. Search contacts (old)")
        print("7. Delete contact (old)")
        print("8. Search by pattern")
        print("9. Insert or update user")
        print("10. Insert many users")
        print("11. Query with pagination")
        print("12. Delete by username or phone")
        print("13. Filter by group")
        print("14. Search by email")
        print("15. Sort contacts")
        print("16. Export contacts to JSON")
        print("17. Import contacts from JSON")
        print("18. Add phone")
        print("19. Move contact to group")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            create_db_objects()
        elif choice == "3":
            insert_from_console()
        elif choice == "4":
            insert_from_csv()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            query_contacts()
        elif choice == "7":
            delete_contact()
        elif choice == "8":
            search_by_pattern()
        elif choice == "9":
            insert_or_update_user_py()
        elif choice == "10":
            insert_many_users_py()
        elif choice == "11":
            query_with_pagination()
        elif choice == "12":
            delete_by_username_or_phone()
        elif choice == "13":
            filter_by_group()
        elif choice == "14":
            search_by_email()
        elif choice == "15":
            sort_contacts()
        elif choice == "16":
            export_to_json()
        elif choice == "17":
            import_from_json()
        elif choice == "18":
            add_phone()
        elif choice == "19":
            move_to_group()
        elif choice == "0":
            print("Exiting program")
            break
        else:
            print("Invalid choice, please try again")


if __name__ == "__main__":
    menu()