# Use the official lightweight Python image
FROM python:3.10-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (useful if using webhooks, optional otherwise)
EXPOSE 8080

# Run the bot
CMD ["python3", "bot.py"]
