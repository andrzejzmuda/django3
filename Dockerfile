FROM python:3.8
ENV PYTHONBUFFERED=1
WORKDIR /django3
COPY requirements.txt /django3/
RUN pip install -r requirements.txt
COPY . /django3/