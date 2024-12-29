# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY summarizer_app.py .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "summarizer_app.py"]