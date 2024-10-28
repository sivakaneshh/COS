# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app


RUN pip install --upgrade pip
RUN pip install -r requirements.txt  # Make sure you have all dependencies listed here

RUN mkdir -p /app/staticfiles && \
    chmod -R 755 /app/staticfiles


RUN python manage.py collectstatic --noinput




EXPOSE 8000


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "canteen_ordering_sys.wsgi.application"]
