FROM python:3.4.6-alpine

RUN apk upgrade --update --no-cache && apk add g++ make python-dev

EXPOSE 5005
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY . /app

ENTRYPOINT ["python", "FlaskRest.py"]

