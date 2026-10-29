# Use Python 3.13
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy application requirements
COPY requirements.txt .

# Install Python dependencies and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Create an unprivileged user
RUN useradd --create-home --uid 10001 appuser \
    && chown appuser:appuser /app

# Copy application files
COPY --chown=appuser:appuser . .

# Run the application as a non-root user
USER appuser

# Initialize the database before starting Gunicorn
ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]

# Expose application port
EXPOSE 5000

# Start Gunicorn after database initialization
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "run:app"]