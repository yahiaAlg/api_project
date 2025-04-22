# -----------------------------
# Builder stage
# -----------------------------
FROM python:3.10-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# -----------------------------
# Runner stage
# -----------------------------
FROM python:3.10-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy only the wheels from the builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install the packages from wheels
RUN pip install --no-cache /wheels/*

# Copy project files
COPY --chown=appuser:appuser . .

# Create required directories
RUN mkdir -p staticfiles media

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]