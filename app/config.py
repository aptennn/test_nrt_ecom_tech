# НАСТРОЙКИ
# ЛОКАЛЬНЫЙ РЕЖИМ, при запуске из docker = false, при запуске из консоли = true
LOCAL_MODE = False


# Настройки для создания данных для примера
stores_n = 30        # кол-во магазинов
users_n = 30         # кол-во пользователей
orders_min = 3       # мин кол-во заказов на пользователя
orders_max = 12      # макс кол-во заказов на пользователя

import os

from pyarrow import StructType
from pyspark.sql.types import *


STORE_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("city", StringType(), nullable=True)
])

ORDER_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("amount", DecimalType(10, 2), nullable=True),
    StructField("user_id", IntegerType(), nullable=True),
    StructField("store_id", IntegerType(), nullable=True),
    StructField("status", StringType(), nullable=True),
    StructField("created_at", TimestampType(), nullable=True)
])

USER_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("phone", StringType(), nullable=True),
    StructField("created_at", TimestampType(), nullable=True)
])

class Config:

    # Пути к файлам
    if LOCAL_MODE:
        STORE_PATH = "data/store.parquet"
        ORDER_PATH = "data/order.parquet"
        USER_PATH = "data/user.parquet"
        RESULT_PATH = "data/result.parquet"
    else:
        # S3/MinIO пути
        S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
        S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
        S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
        S3_BUCKET = os.getenv("S3_BUCKET", "data-bucket")

        BASE_PATH = f"s3a://{S3_BUCKET}"
        STORE_PATH = f"{BASE_PATH}/store.parquet"
        ORDER_PATH = f"{BASE_PATH}/order.parquet"
        USER_PATH = f"{BASE_PATH}/user.parquet"
        RESULT_PATH = f"{BASE_PATH}/result.parquet"