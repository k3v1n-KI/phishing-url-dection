# Use an official lightweight Python 3.12 image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first (to leverage Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get install -y chromium-browser

# Copy the rest of the application code
COPY . .

# Expose port 8000 for Cloud Run
EXPOSE 8000

# Run the application using Gunicorn with four workers
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
