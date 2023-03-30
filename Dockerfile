FROM python:3.10-bullseye

WORKDIR /app
COPY app/ .
RUN pip3 install -U -r requirements.txt
CMD ["python3", "run.py"]

ENV SERVER_PORT 8001
EXPOSE 8001/tcp
