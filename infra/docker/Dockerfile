# Secure Base Image (Distroless would be better, but slim is common start)
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root info
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER 1000

# Set Read-Only where possible (optional hardening)
# ENV READ_ONLY_FS=true

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
