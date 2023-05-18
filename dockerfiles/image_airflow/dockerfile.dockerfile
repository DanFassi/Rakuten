FROM ubuntu:20.04

ADD files/requirements.txt files/api_rak.py files/Pipeline_prediction.py ./

#ADD requirements.txt main.py ./
#COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install python3-pip -y &&  && pip install -r requirements.txt

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0