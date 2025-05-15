# Use the official Python 3.9 image as the base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
# Copy the Django project files
COPY . .

# Run the Django server
CMD ["gunicorn", "social_media_generator.wsgi:application", "--bind", "0.0.0.0:8000", "--workers","4"]