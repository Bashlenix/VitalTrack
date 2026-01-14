# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set /app as the default directory inside the container
WORKDIR /app

# Set environment variables
# Prevent creation of .pyc files, Keep container clean
# Ensures logs appear immediately in Docker logs (for debugging)
# Define the Flask entry point
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Note: No MySQL client libraries needed since we use mysql-connector-python
# which is a pure Python package that doesn't require compilation

# Copy requirements file first for better caching
# Dependencies are only reinstalled when requirements.txt changes
# This significantly speeds up rebuilds during development.
COPY requirements.txt .

# Install Python dependencies, avoids leaving unnecessary cache files inside the image.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy everything from project directory into the container
COPY . .

# Create directory for uploads if it doesn't exist
RUN mkdir -p static/uploads/radiology

# Expose port 5000 for Flask
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
