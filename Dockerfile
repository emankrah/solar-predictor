# Base image
FROM python:3.10-slim

# Create working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

# Expose port and run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
