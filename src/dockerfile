FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (ffmpeg for audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code
COPY src/ ./src/

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run the bot
COPY src/.env ./src/.env
CMD ["python", "src/bot.py"]