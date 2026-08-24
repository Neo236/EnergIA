FROM python:3.10-slim

RUN pip install --no-cache-dir flask

COPY mock_ml_server.py /app/mock_ml_server.py

WORKDIR /app

EXPOSE 8000

CMD ["python", "mock_ml_server.py"]
