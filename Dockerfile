# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Collect static files and set appropriate permissions
RUN mkdir -p /app/staticfiles && \
    chmod -R 755 /app/staticfiles && \
    python manage.py collectstatic --noinput

# Expose Django's default port
EXPOSE 8000

# Environment variables for Django settings (Update with actual settings or secrets if needed)
ENV DJANGO_SETTINGS_MODULE=canteen_ordering_sys.settings
ENV PYTHONUNBUFFERED=1

# Command to start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "canteen_ordering_sys.wsgi:application"]

# Optional: Command to initialize Celery worker (uncomment to add Celery)
# CMD ["celery", "-A", "canteen_ordering_sys", "worker", "--loglevel=info"]
