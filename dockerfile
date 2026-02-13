FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y python3 && ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /opt/spark/jars
RUN curl -f -L -o /opt/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -f -L -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/ /app

WORKDIR /app

CMD ["python", "main.py"]