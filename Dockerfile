FROM python:slim

WORKDIR /app

COPY *.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD python action-blagues.py 