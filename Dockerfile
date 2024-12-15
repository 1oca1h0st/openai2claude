FROM python:3.10-slim

WORKDIR /app

COPY openai2claude.py .

RUN pip install --no-cache-dir flask flask_cors requests

EXPOSE 5001

CMD ["python", "openai2claude.py"]
