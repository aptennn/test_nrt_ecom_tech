# src/data_generator.py
#pip install minio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import config

MINIO_ENDPOINT = os.getenv("S3_ENDPOINT", "localhost:9000").replace("http://", "")
MINIO_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("S3_BUCKET", "data-bucket")

try:
    from minio import Minio
    from minio.error import S3Error
    import io

    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    print("Установи pip install minio")


def generate_test_data():
    print("Внимание! Создание данных может занимать некоторое время")

    available_cities = ['Moscow', 'Krasnodar', 'Rostov-On-Don',
                        'Kazan', 'Novosibirsk', 'Vladivostok']
    cities = np.random.choice(available_cities, config.stores_n)

    stores = pd.DataFrame({
        'id': list(range(1, config.stores_n + 1)),
        'name': [f'Store_{i}' for i in range(1, config.stores_n + 1)],
        'city': cities
    })

    created_at_dates = []
    for _ in range(config.users_n):
        year = np.random.randint(2022, 2026)  # 2022..2025
        month = np.random.randint(1, 13)
        day = np.random.randint(1, 29)
        created_at_dates.append(datetime(year, month, day))

    users = pd.DataFrame({
        'id': list(range(1, config.users_n + 1)),
        'name': [f'User_{i}' for i in range(1, config.users_n + 1)],
        'phone': [f'+7999000{i:04d}' for i in range(1, config.users_n + 1)],
        'created_at': created_at_dates
    })

    orders_data = []
    order_id = 1
    max_date = datetime(2026, 12, 31)

    user_reg_dates = dict(zip(users['id'], users['created_at']))
    for user_id in range(1, config.users_n + 1):
        user_reg_date = user_reg_dates[user_id]
        if user_reg_date > max_date:
            available_days = 0
        else:
            available_days = (max_date - user_reg_date).days

        num_orders = np.random.randint(config.orders_min, config.orders_max)
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
                'store_id': np.random.randint(1, config.stores_n + 1),
                'status': np.random.choice(['completed', 'pending', 'cancelled']),
                'created_at': order_date
            })
            order_id += 1

    orders = pd.DataFrame(orders_data)

    if not os.path.exists("data"):
        os.makedirs("data")
        print("Папка 'data' создана")

    stores.to_parquet("data/store.parquet", index=False)
    users.to_parquet("data/user.parquet", index=False)
    orders.to_parquet("data/order.parquet", index=False)
    print(" Локальные файлы сохранены папка data")

    if MINIO_AVAILABLE:
        try:

            client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False
            )

            if not client.bucket_exists(MINIO_BUCKET):
                client.make_bucket(MINIO_BUCKET)
                print(f"🪣  Bucket '{MINIO_BUCKET}' создан")

            def upload_df(df, object_name):

                parquet_bytes = df.to_parquet(
                    index=False,
                    engine='pyarrow',
                    coerce_timestamps='us',  # микросекунды
                    allow_truncated_timestamps=True  # разрешить усечение
                )
                parquet_stream = io.BytesIO(parquet_bytes)
                client.put_object(
                    MINIO_BUCKET,
                    object_name,
                    parquet_stream,
                    length=len(parquet_bytes),
                    content_type='application/parquet'
                )
                print(f"{object_name} загружен в MinIO (timestamps as microseconds)")

            upload_df(stores, "store.parquet")
            upload_df(users, "user.parquet")
            upload_df(orders, "order.parquet")
            print("Все файлы загружены в MinIO")

        except Exception as e:
            print("   Проверьте, запущен ли MinIO (docker-compose up -d minio)")
    else:
        print("error MinIO SDK загрузка")

    users_2025 = users[users['created_at'].dt.year == 2025]
    print(f"   Пользователей 2025 года: {len(users_2025)} ({len(users_2025) / len(users) * 100:.1f}%)")
    orders_from_2025 = orders[orders['user_id'].isin(users_2025['id'])]
    print(f"   Заказов от пользователей 2025: {len(orders_from_2025)}")

    return stores, users, orders


if __name__ == "__main__":
    generate_test_data()
