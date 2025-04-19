# Use an official Python image
FROM python:3.10-slim

# Install FFmpeg and dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port for Flask
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
