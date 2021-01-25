FROM python:3.8

ENV PYTHONBUFFERED 1

RUN mkdir /django3_apps/

ADD . /django3_apps

WORKDIR /django3_apps

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python3", "manage.py", "runserver"]
