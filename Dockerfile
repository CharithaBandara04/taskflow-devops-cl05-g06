
# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application requirements
COPY requirements.txt .

# Install Python dependencies and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Create an unprivileged user to run the application
RUN useradd --create-home --uid 10001 appuser \
    && chown appuser:appuser /app

# Copy application files, owned by the unprivileged user
COPY --chown=appuser:appuser . .

# Run everything after this point as the unprivileged user
USER appuser

# Expose application port
EXPOSE 5000

# Start Flask using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
