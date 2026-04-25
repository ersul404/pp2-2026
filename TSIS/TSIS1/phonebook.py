"""
TSIS 1 — Extended PhoneBook
Builds on Practice 7 (CRUD, CSV) and Practice 8 (procedures, pagination).
New features: groups, multiple phones, email, birthday,
JSON import/export, advanced search/filter/sort.
"""

import csv
import json
from datetime import datetime
from connect import get_connection


# ================================================================
# HELPERS
# ================================================================

def _row_to_dict(row, cursor):
    """Turn a cursor row into a dict using column names."""
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


def _get_all_phones(conn, contact_id):
    """Return list of {phone, type} for a contact."""
    cur = conn.cursor()
    cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (contact_id,))
    rows = cur.fetchall()
    cur.close()
    return [{"phone": r[0], "type": r[1]} for r in rows]


def _ensure_group(conn, group_name):
    """Return group id, inserting if needed."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    gid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return gid


def _print_contact(c):
    """Pretty-print a contact dict."""
    phones = c.get("phones", [])
    phone_str = ", ".join(f"{p['phone']} ({p['type']})" for p in phones) if phones else "—"
    print(f"  ID       : {c.get('id', '?')}")
    print(f"  Name     : {c.get('first_name', '')}")
    print(f"  Email    : {c.get('email') or '—'}")
    print(f"  Birthday : {c.get('birthday') or '—'}")
    print(f"  Group    : {c.get('group_name') or '—'}")
    print(f"  Phones   : {phone_str}")
    print()


# ================================================================
# 3.1 — ADD / UPDATE CONTACT (console)
# ================================================================

def insert_from_console():
    name     = input("  Имя         : ").strip()
    email    = input("  Email       : ").strip() or None
    birthday = input("  Дата рожд. (YYYY-MM-DD, Enter — пропустить): ").strip() or None
    group    = input("  Группа (Family/Work/Friend/Other): ").strip() or "Other"

    conn = get_connection()
    try:
        gid = _ensure_group(conn, group)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contacts (first_name, email, birthday, group_id) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (name, email, birthday, gid)
        )
        cid = cur.fetchone()[0]
        conn.commit()

        # Add phones
        while True:
            phone = input("  Телефон (Enter — завершить): ").strip()
            if not phone:
                break
            ptype = input("  Тип (home/work/mobile): ").strip()
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (cid, phone, ptype)
            )
        conn.commit()
        cur.close()
        print("✅ Контакт добавлен!")
    finally:
        conn.close()


# ================================================================
# 3.2 — FILTER BY GROUP
# ================================================================

def filter_by_group():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cur.fetchall()
    print("  Доступные группы:")
    for g in groups:
        print(f"    [{g[0]}] {g[1]}")
    gid = input("  Введите ID группы: ").strip()

    cur.execute(
        """
        SELECT c.id, c.first_name, c.email, c.birthday, g.name AS group_name
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  c.group_id = %s
        ORDER  BY c.first_name
        """,
        (gid,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("  Контакты не найдены.")
        return
    for r in rows:
        contact = {
            "id": r[0], "first_name": r[1], "email": r[2],
            "birthday": r[3], "group_name": r[4]
        }
        conn2 = get_connection()
        contact["phones"] = _get_all_phones(conn2, r[0])
        conn2.close()
        _print_contact(contact)


# ================================================================
# 3.2 — SEARCH BY EMAIL
# ================================================================

def search_by_email():
    query = input("  Введите часть email: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.first_name, c.email, c.birthday, g.name
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  c.email ILIKE %s
        ORDER  BY c.first_name
        """,
        (f"%{query}%",)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("  Не найдено.")
        return
    for r in rows:
        contact = {
            "id": r[0], "first_name": r[1], "email": r[2],
            "birthday": r[3], "group_name": r[4]
        }
        conn2 = get_connection()
        contact["phones"] = _get_all_phones(conn2, r[0])
        conn2.close()
        _print_contact(contact)


# ================================================================
# 3.2 — SORT CONTACTS
# ================================================================

def list_sorted():
    print("  Сортировка: 1) По имени  2) По дате рождения  3) По дате добавления")
    choice = input("  Выбор: ").strip()
    order = {
        "1": "c.first_name",
        "2": "c.birthday NULLS LAST",
        "3": "c.created_at"
    }.get(choice, "c.first_name")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT c.id, c.first_name, c.email, c.birthday, g.name
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        ORDER  BY {order}
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    for r in rows:
        contact = {
            "id": r[0], "first_name": r[1], "email": r[2],
            "birthday": r[3], "group_name": r[4]
        }
        conn2 = get_connection()
        contact["phones"] = _get_all_phones(conn2, r[0])
        conn2.close()
        _print_contact(contact)


# ================================================================
# 3.2 — PAGINATED NAVIGATION (uses DB function from Practice 8)
# ================================================================

def paginated_navigation():
    page_size = 3
    offset    = 0
    while True:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (page_size, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            print("  (больше контактов нет)")
            break

        print(f"\n  === Страница (записи {offset + 1}–{offset + len(rows)}) ===")
        for r in rows:
            contact = {
                "id": r[0], "first_name": r[1], "email": r[2],
                "birthday": r[3], "group_name": r[4]
            }
            conn2 = get_connection()
            contact["phones"] = _get_all_phones(conn2, r[0])
            conn2.close()
            _print_contact(contact)

        nav = input("  [next / prev / quit]: ").strip().lower()
        if nav == "next":
            offset += page_size
        elif nav == "prev":
            offset = max(0, offset - page_size)
        elif nav == "quit":
            break


# ================================================================
# 3.3 — EXPORT TO JSON
# ================================================================

def export_to_json():
    filename = input("  Имя файла (например contacts.json): ").strip() or "contacts.json"
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.first_name, c.email,
               c.birthday::TEXT, g.name AS group_name
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        ORDER  BY c.first_name
        """
    )
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        contact = {
            "id":         r[0],
            "first_name": r[1],
            "email":      r[2],
            "birthday":   r[3],
            "group":      r[4],
            "phones":     _get_all_phones(conn, r[0])
        }
        result.append(contact)
    conn.close()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Экспортировано {len(result)} контактов → {filename}")


# ================================================================
# 3.3 — IMPORT FROM JSON
# ================================================================

def import_from_json():
    filename = input("  Имя JSON файла: ").strip()
    try:
        with open(filename, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"  ❌ Файл {filename} не найден.")
        return

    conn = get_connection()
    cur  = conn.cursor()

    added = skipped = overwritten = 0

    for c in contacts:
        name = c.get("first_name", "").strip()
        if not name:
            continue

        # Check duplicate
        cur.execute("SELECT id FROM contacts WHERE first_name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            choice = input(
                f"  Контакт «{name}» уже существует. [s]kip / [o]verwrite? "
            ).strip().lower()
            if choice != "o":
                skipped += 1
                continue
            # Overwrite: delete old phones, update fields
            gid = _ensure_group(conn, c.get("group") or "Other")
            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                (c.get("email"), c.get("birthday"), gid, existing[0])
            )
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))
            for ph in c.get("phones", []):
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (existing[0], ph.get("phone"), ph.get("type", "mobile"))
                )
            overwritten += 1
        else:
            gid = _ensure_group(conn, c.get("group") or "Other")
            cur.execute(
                "INSERT INTO contacts (first_name, email, birthday, group_id) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (name, c.get("email"), c.get("birthday"), gid)
            )
            cid = cur.fetchone()[0]
            for ph in c.get("phones", []):
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (cid, ph.get("phone"), ph.get("type", "mobile"))
                )
            added += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Импорт завершён: добавлено {added}, перезаписано {overwritten}, пропущено {skipped}.")


# ================================================================
# 3.3 — EXTENDED CSV IMPORT (Practice 7 updated)
# ================================================================

def insert_from_csv():
    filename = input("  Имя CSV файла: ").strip()
    try:
        f = open(filename, encoding="utf-8")
    except FileNotFoundError:
        print(f"  ❌ Файл {filename} не найден.")
        return

    conn = get_connection()
    cur  = conn.cursor()
    reader = csv.DictReader(f)
    added = 0

    for row in reader:
        name  = row.get("first_name", "").strip()
        if not name:
            continue

        email    = row.get("email", "").strip() or None
        birthday = row.get("birthday", "").strip() or None
        group    = row.get("group", "Other").strip() or "Other"
        phone    = row.get("phone", "").strip() or None
        ptype    = row.get("phone_type", "mobile").strip() or "mobile"
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"

        gid = _ensure_group(conn, group)

        # Upsert contact
        cur.execute("SELECT id FROM contacts WHERE first_name = %s", (name,))
        existing = cur.fetchone()
        if existing:
            cid = existing[0]
            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                (email, birthday, gid, cid)
            )
        else:
            cur.execute(
                "INSERT INTO contacts (first_name, email, birthday, group_id) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (name, email, birthday, gid)
            )
            cid = cur.fetchone()[0]

        if phone:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (cid, phone, ptype)
            )
        added += 1

    conn.commit()
    cur.close()
    conn.close()
    f.close()
    print(f"✅ CSV импортирован: обработано {added} записей.")


# ================================================================
# 3.4 — CALL STORED PROCEDURES
# ================================================================

def call_add_phone():
    name  = input("  Имя контакта   : ").strip()
    phone = input("  Новый телефон  : ").strip()
    ptype = input("  Тип (home/work/mobile): ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("✅ Телефон добавлен!")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


def call_move_to_group():
    name  = input("  Имя контакта : ").strip()
    group = input("  Новая группа : ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"✅ Контакт перемещён в группу «{group}»!")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


def call_search_contacts():
    query = input("  Поиск (имя / email / телефон): ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows  = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("  Ничего не найдено.")
        return

    # Group rows by contact_id for clean display
    contacts_map = {}
    for r in rows:
        cid = r[0]
        if cid not in contacts_map:
            contacts_map[cid] = {
                "id": r[0], "first_name": r[1], "email": r[2],
                "birthday": r[3], "group_name": r[4], "phones": []
            }
        if r[5]:
            contacts_map[cid]["phones"].append({"phone": r[5], "type": r[6]})
    for c in contacts_map.values():
        _print_contact(c)


# ================================================================
# MAIN MENU
# ================================================================

def menu():
    while True:
        print("""
╔══════════════════════════════════╗
║     PhoneBook — TSIS 1 Menu     ║
╠══════════════════════════════════╣
║  1. Добавить контакт (консоль)  ║
║  2. Фильтр по группе            ║
║  3. Поиск по email              ║
║  4. Список (с сортировкой)      ║
║  5. Постраничная навигация      ║
║  6. Экспорт в JSON              ║
║  7. Импорт из JSON              ║
║  8. Импорт из CSV               ║
║  9. Добавить телефон (процедура)║
║ 10. Переместить в группу        ║
║ 11. Расширенный поиск (DB fn)   ║
║  0. Выход                       ║
╚══════════════════════════════════╝""")

        choice = input("Выбор: ").strip()

        if   choice == "1":  insert_from_console()
        elif choice == "2":  filter_by_group()
        elif choice == "3":  search_by_email()
        elif choice == "4":  list_sorted()
        elif choice == "5":  paginated_navigation()
        elif choice == "6":  export_to_json()
        elif choice == "7":  import_from_json()
        elif choice == "8":  insert_from_csv()
        elif choice == "9":  call_add_phone()
        elif choice == "10": call_move_to_group()
        elif choice == "11": call_search_contacts()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    menu()