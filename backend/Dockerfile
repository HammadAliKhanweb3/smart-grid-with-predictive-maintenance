FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Adjust for your framework
CMD ["uvicorn", "app:main_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]  # For dev with reload
# For production: CMD ["uvicorn", "app:main_app", "--host", "0.0.0.0", "--port", "8000"]