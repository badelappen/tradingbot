# Simple Dockerfile for the trading bot web application.
# This image installs the required Python packages and starts the FastAPI
# application using uvicorn. Adjust the Python version as needed.

FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image
COPY . .

# Expose port 8000 for the FastAPI service
EXPOSE 8000

# Default command to start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]