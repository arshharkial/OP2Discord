FROM python:3.11.3-slim

WORKDIR /app

RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn requests

EXPOSE 8080

COPY OPWebhook.py OPWebhook.py
CMD ["python3", "OPWebhook.py"]