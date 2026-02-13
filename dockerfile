FROM apache/spark:3.5.0

USER root

# Устанавливаем curl (на всякий случай, но в образе он уже может быть)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Скачиваем JAR-файлы для S3A в директорию с библиотеками Spark
RUN curl -L -o /opt/bitnami/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# Копируем requirements.txt и устанавливаем Python-зависимости
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Копируем весь код приложения
COPY app/ /app

WORKDIR /app

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["python", "main.py"]