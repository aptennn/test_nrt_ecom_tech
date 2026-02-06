# src/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
#pip install pyarrow==23.0.0

# Создание тестовых данных для основной программы

# настройки создания parquet-файлов
stores_n = 12 # кол-во магазинов
users_n = 20  # кол-во пользователей
orders_min = 2 # мин кол-во заказов на пользователя
orders_max = 10 # макс кол-во заказов на пользователя

def generate_test_data():
    available_cities = ['Moscow', 'Krasnodar', 'Rostov-On-Don',
                        'Yaroslavl', 'SaintPetersburg',
                        'Kazan', 'Azov',
                        'Novosibirsk', 'Vladivostok', 'NovoRossiysk']
    cities = np.random.choice(available_cities, stores_n)

    stores = pd.DataFrame({
        'id': list(range(1, stores_n+1)),
        'name': [f'Store_{i}' for i in range(1, stores_n+1)],
        'city': cities
    })

    created_at_dates = []
    for i in range(users_n):
        year = np.random.randint(2022, 2026)
        month = np.random.randint(1, 13)
        day = np.random.randint(1, 29)
        created_at_dates.append(datetime(year, month, day))

    users = pd.DataFrame({
        'id': list(range(1, users_n + 1)),
        'name': [f'User_{i}' for i in range(1, users_n + 1)],
        'phone': [f'+7999000{i:04d}' for i in range(1, users_n + 1)],
        'created_at': created_at_dates
    })

    orders_data = []
    order_id = 1
    max_date = datetime(2026, 12, 31)

    # для проверка на дату регистрации пользователя
    user_reg_dates = dict(zip(users['id'], users['created_at']))
    for user_id in range(1, users_n):
        user_reg_date = user_reg_dates[user_id]
        # Если дата регистрации позже максимальной даты заказов, то все заказы будут в дату регистрации
        if user_reg_date > max_date:
            available_days = 0
        else:
            available_days = (max_date - user_reg_date).days

        num_orders = np.random.randint(orders_min, orders_max)

        for _ in range(num_orders):
            if available_days > 0:
                delta_days = np.random.randint(0, available_days + 1)
                order_date = user_reg_date + timedelta(days=delta_days)
            else:
                order_date = user_reg_date

            orders_data.append({
                'id': order_id,
                'amount': float(np.round(np.random.uniform(100, 10000), 2)),
                'user_id': user_id,
                'store_id': np.random.randint(1, 11),
                'status': np.random.choice(['completed', 'pending', 'cancelled']),
                'created_at': order_date
            })
            order_id += 1

    orders = pd.DataFrame(orders_data)


    if not os.path.exists("data"):
        os.makedirs("data")
        print("directory created")

    stores.to_parquet("data/store.parquet", index=False)
    users.to_parquet("data/user.parquet", index=False)
    orders.to_parquet("data/order.parquet", index=False)


    print("\n 1. Stores:")
    print(stores)

    print("\n 2. Users")
    print(users[['id', 'name', 'created_at']])

    print("\n 3. Orders")
    print(orders)

    return stores, users, orders


if __name__ == "__main__":
    generate_test_data()