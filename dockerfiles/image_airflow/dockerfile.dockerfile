FROM apache/airflow:latest

ENV MY_DOCKER_PATH=/opt/airflow/rakuten

COPY /Rakuten/requirements.txt /

RUN apt-get update && apt-get install python3-pip -y && pip install --no-cache-dir -r /requirements.txt
RUN python3 -m nltk.downloader stopwords

ADD /Rakuten/Pipeline_prediction.py /opt/airflow/
ADD /Rakuten/Mongodb_connect.py /opt/airflow/

VOLUME /opt/airflow/rakuten

EXPOSE 7000:7000