
# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application requirements
COPY requirements.txt .

# Install Python dependencies and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY . .

# Expose application port
EXPOSE 5000

# Start Flask using Gunicorn
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
