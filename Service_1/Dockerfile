# Start with a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose the port your app runs on
EXPOSE 8001

# Command to run the app
CMD ["python", "app.py"]
