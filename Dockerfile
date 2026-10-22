#The Dockerfile defines how the Flask application image is built

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

# Install Python dependencies without keeping pip's download cache in the image.
# pip, setuptools and wheel are only needed to install packages. They carry
# known vulnerabilities in their vendored libraries, so remove them afterwards.
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y setuptools wheel pip

# Copy everything from project directory into the container
COPY . .

# Run as an unprivileged user: code stays read-only for it (permissions are
# normalised so the image does not depend on the host's file modes), and it
# only gets write access to the uploads folder (kept outside static/, which
# Flask serves without login)
RUN chmod -R u=rwX,go=rX /app && \
    useradd --create-home --uid 10001 vitaltrack && \
    mkdir -p uploads/radiology && \
    chown -R vitaltrack:vitaltrack uploads
USER vitaltrack

# Expose port 5000 for Flask
EXPOSE 5000

# Production WSGI server instead of the Flask development server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
