FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY build/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/back/ .
RUN mkdir -p /app/uploads/covers

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
