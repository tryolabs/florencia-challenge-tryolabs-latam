# syntax=docker/dockerfile:1.2
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y build-essential gcc libssl-dev

# Copy requirements files for the container
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt -r requirements-dev.txt

# Copy the entire project into the container
COPY . .

# Expose port
EXPOSE 8000

# Run the application inside the container
CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8000"]
