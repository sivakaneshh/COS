# Start with a Python base image
FROM python:3.12-slim

# Install system dependencies and MySQL client libraries
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django application code
COPY . /app

# Run database migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Set the default command to run Django using Gunicorn
CMD ["gunicorn", "canteen_ordering_sys.wsgi:application", "--bind", "0.0.0.0:8000"]
