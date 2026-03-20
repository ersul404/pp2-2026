import csv
from connect import get_connection

# ---------------- Вставка из CSV ----------------
def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute("INSERT INTO contacts (first_name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    cur.close()
    conn.close()
    print("Данные из CSV добавлены!")

# ---------------- Вставка с консоли ----------------
def insert_from_console():
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (first_name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Контакт добавлен!")

# ---------------- Обновление контакта ----------------
def update_contact():
    name = input("Введите имя контакта для обновления: ")
    new_phone = input("Введите новый номер телефона: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE contacts SET phone=%s WHERE first_name=%s", (new_phone, name))
    conn.commit()
    cur.close()
    conn.close()
    print("Контакт обновлен!")

# ---------------- Поиск контактов ----------------
def search_contacts():
    query = input("Поиск по имени или номеру (начало): ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE first_name LIKE %s OR phone LIKE %s", (f'{query}%', f'{query}%'))
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"ID: {row[0]}, Имя: {row[1]}, Телефон: {row[2]}")
    else:
        print("Контакты не найдены.")
    cur.close()
    conn.close()

# ---------------- Удаление контакта ----------------
def delete_contact():
    query = input("Введите имя или номер для удаления: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE first_name=%s OR phone=%s", (query, query))
    conn.commit()
    cur.close()
    conn.close()
    print("Контакт удален!")

# ---------------- Меню пользователя ----------------
def menu():
    while True:
        print("""
1. Вставка из CSV
2. Вставка с консоли
3. Обновление контакта
4. Поиск контактов
5. Удаление контакта
6. Выход
""")
        choice = input("Выберите пункт: ")
        if choice == '1':
            filename = input("Введите имя CSV файла: ")
            insert_from_csv(filename)
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            search_contacts()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            print("Выход.")
            break
        else:
            print("Неверный выбор.")

# ---------------- Запуск ----------------
if __name__ == "__main__":
    menu()