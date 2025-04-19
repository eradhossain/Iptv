# Use Python 3.10 base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install FFmpeg and other dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    apt-get clean

# Set work directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for Flask
EXPOSE 5000

# Start the bot
CMD ["python", "main.py"]
