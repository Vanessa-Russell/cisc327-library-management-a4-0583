# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by Playwright
RUN apt-get update && \
    apt-get install -y wget gnupg unzip && \
    apt-get clean

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + browsers
RUN pip install playwright && \
    playwright install --with-deps chromium

# Copy the entire project
COPY . .

# Expose Flask port (required)
EXPOSE 5000

# Run the app on port 5000 using correct entry point
CMD ["python", "-m", "app"]