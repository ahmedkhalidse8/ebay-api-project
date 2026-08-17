import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent.parent
ORDERS_FILE = BASE_DIR / "raw" / "orders.json"


with open(ORDERS_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


orders = data["data"]["orders"]


buyers = []

for order in orders:

    buyer = order.get("buyer", {})
    username = buyer.get("username")

    if username:
        buyers.append(username)


counter = Counter(buyers)


print("=" * 60)
print("CUSTOMER ANALYSIS CHECK")
print("=" * 60)

print("Total orders:", len(orders))
print("Orders with buyer username:", len(buyers))
print("Unique buyers:", len(counter))
print()


print("BUYER ORDER COUNTS")
print("-" * 60)

for username, order_count in counter.most_common():

    print(
        f"{username:<30} {order_count} order(s)"
    )


print()
print("=" * 60)

repeat_buyers = {
    username: count
    for username, count in counter.items()
    if count > 1
}

print("Repeat buyers:", len(repeat_buyers))
print("One-time buyers:", len(counter) - len(repeat_buyers))