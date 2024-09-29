FROM python:3.11
LABEL authors="roman"

WORKDIR module

COPY . .

RUN pip install -r req.txt

