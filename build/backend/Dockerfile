FROM python:3.12

WORKDIR /app

COPY build/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/back/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
