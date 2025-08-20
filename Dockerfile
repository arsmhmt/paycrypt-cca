# Use the official lightweight Python image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Expose the port Cloud Run will use
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run the web server
CMD ["gunicorn", "run:app", "-b", ":8080", "--timeout", "120"]
