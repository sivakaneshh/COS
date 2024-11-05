# Example Dockerfile
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "canteen_ordering_sys.wsgi:application"]
