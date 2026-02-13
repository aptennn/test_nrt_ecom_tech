import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, sum, rank
from pyspark.sql.window import Window
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_spark_session():
    spark_builder = SparkSession.builder \
        .appName("StoreAnalyticsETL") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .master("local[*]")

    if not Config.LOCAL_MODE:
        spark_builder = spark_builder \
            .config("spark.hadoop.fs.s3a.endpoint", Config.S3_ENDPOINT) \
            .config("spark.hadoop.fs.s3a.access.key", Config.S3_ACCESS_KEY) \
            .config("spark.hadoop.fs.s3a.secret.key", Config.S3_SECRET_KEY) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    return spark_builder.getOrCreate()


def read_parquet_files(spark):
    stores_df = spark.read.parquet(Config.STORE_PATH)
    orders_df = spark.read.parquet(Config.ORDER_PATH)
    users_df = spark.read.parquet(Config.USER_PATH)

    return stores_df, orders_df, users_df


def transform_data(stores_df, orders_df, users_df):
    users_2025 = users_df.filter(year(col("created_at")) == 2025)

    joined_df = users_2025 \
        .join(orders_df, users_2025.id == orders_df.user_id, "inner") \
        .join(stores_df, orders_df.store_id == stores_df.id, "inner")

    aggregated_df = joined_df.groupBy(
        stores_df.city.alias("city"),
        stores_df.name.alias("store_name")
    ).agg(
        sum(orders_df.amount).alias("target_amount")
    )

    window_spec = Window.partitionBy("city") \
        .orderBy(col("target_amount").desc())

    result_df = aggregated_df \
        .withColumn("rank", rank().over(window_spec)) \
        .filter(col("rank") <= 3) \
        .drop("rank") \
        .orderBy("city", col("target_amount").desc())

    return result_df


def save_result(result_df):
    result_df.write \
        .mode("overwrite") \
        .parquet(Config.RESULT_PATH)

    print("Результат успешно сохранен")


def main():
    print("Запущено")

    try:
        spark = create_spark_session()
        print("Spark сессия создана")
        stores_df, orders_df, users_df = read_parquet_files(spark)
        result_df = transform_data(stores_df, orders_df, users_df)
        result_df.show(20, truncate=False)
        save_result(result_df)
        spark.stop()


    except Exception as e:
        print(f"Ошибка в ETL процессе: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()