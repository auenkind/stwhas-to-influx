# syntax=docker/dockerfile:1
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY stwhas-to-influx.py ./
RUN chmod 755 entry.sh
ENTRYPOINT [ "python", "stwhas-to-influx.py" ]