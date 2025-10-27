FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential\
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

ENV SECRET_KEY='django-insecure-dev-only-&*#@!%^)(_+=-0987654321qwertyuiopasdfghjklzxcvbnm'
ENV DEBUG=False

RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "myportfolio.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]