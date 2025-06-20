"""Console water delivery bot."""

import csv
import json
import os
from datetime import datetime


CLIENTS_FILE = "clients.json"
ORDERS_FILE = "orders.csv"
PRICE_PER_BOTTLE = 100


def load_clients() -> dict:
    if os.path.exists(CLIENTS_FILE):
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_clients(clients: dict) -> None:
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)


def load_last_order(phone: str) -> dict | None:
    if not os.path.exists(ORDERS_FILE):
        return None
    last = None
    with open(ORDERS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("phone") == phone:
                last = {
                    "date": row["date"],
                    "name": row["name"],
                    "district": row["district"],
                    "phone": row["phone"],
                    "count": int(row["count"]),
                    "total": int(row["total"]),
                }
    return last


def append_order(order: dict) -> None:
    file_exists = os.path.exists(ORDERS_FILE)
    with open(ORDERS_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["date", "name", "district", "phone", "count", "total"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(order)


def ask_bottle_count() -> int:
    while True:
        try:
            count = int(input("Сколько бутылей вы хотите заказать? "))
            if count <= 0:
                print("Количество должно быть больше нуля.")
                continue
            return count
        except ValueError:
            print("Введите число.")


def print_invoice(order: dict) -> None:
    print("\n==== Итоговый счёт ====")
    print(f"Клиент: {order['name']} ({order['phone']})")
    print(f"Район доставки: {order['district']}")
    print(f"Количество бутылей: {order['count']}")
    print(f"Итого к оплате: {order['total']} ₽")
    print("======================")


def start_call(phone: str) -> None:
    print("\n📞 Incoming call from", phone)

    clients = load_clients()
    client = clients.get(phone)
    if client:
        name = client["name"]
        district = client["district"]
        print(f"Здравствуйте, {name} из района {district}!")
        last_order = load_last_order(phone)
        if last_order:
            ans = input(
                f"Повторить прошлый заказ ({last_order['count']} бутылей за {last_order['total']} ₽)? [y/n] "
            ).strip().lower()
            if ans == "y":
                order = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "name": name,
                    "district": district,
                    "phone": phone,
                    "count": last_order["count"],
                    "total": last_order["total"],
                }
                append_order(order)
                print_invoice(order)
                return
    else:
        print("Здравствуйте! Вы новый клиент. Давайте зарегистрируемся.")
        name = input("Как вас зовут? ")
        district = input("Укажите ваш район: ")
        clients[phone] = {"name": name, "district": district}
        save_clients(clients)

    print("\nНаш прайс-лист:")
    print(f" - Бутыль 19L: {PRICE_PER_BOTTLE} ₽")

    count = ask_bottle_count()
    total = count * PRICE_PER_BOTTLE
    order = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name": name,
        "district": district,
        "phone": phone,
        "count": count,
        "total": total,
    }
    append_order(order)
    print_invoice(order)


if __name__ == "__main__":
    start_call("+79991234567")
