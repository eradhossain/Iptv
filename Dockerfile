FROM python:3.10-slim

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg wget curl git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "main.py"]
